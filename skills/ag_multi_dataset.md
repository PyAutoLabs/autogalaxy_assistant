---
name: ag_multi_dataset
description: Fit several datasets of the same galaxy jointly — multi-wavelength bands, repeated exposures in one band, or CCD imaging together with uv-plane visibilities. Covers the `af.AnalysisFactor` + `af.FactorGraphModel` construction that is the only way to combine datasets, deciding what is shared across datasets and what is freed per dataset, parameterising a wavelength relation with prior arithmetic so five bands cost two parameters instead of five, astrometric offsets via `ag.DatasetModel`, a pixelised component across bands, the deliberate one-dataset-at-a-time alternative, and reading the per-dataset result list. Use when more than one dataset of one galaxy must inform one model. Not for a single dataset (`ag_build_imaging_model`), not for one interferometer dataset on its own (`ag_build_interferometer_model`), not for choosing the search (`ag_configure_search`), and not for a population of different galaxies.
---

# Fitting several datasets of one galaxy

A galaxy imaged in four filters is one object seen four ways. The geometry — where it sits, how
elongated it is, how concentrated its light is — is a property of the galaxy and does not change
between bands. The brightness does, and that changing brightness *is* the colour: the
bulge-to-disk ratio at 1.1 µm against 4.4 µm, a red concentrated old population sitting inside a
bluer star-forming disk, a colour gradient that traces an age or metallicity gradient.

Fitting the bands separately throws away the thing that makes them powerful. Four independent
fits give you four loosely-constrained sizes; one joint fit with the geometry shared gives you
one well-constrained size and four amplitudes, and the amplitudes are the measurement. This is
also the statistically honest construction: the joint log likelihood is the sum of the
per-dataset log likelihoods, so every photon in every band constrains the shared parameters at
once, and the errors come out of a single posterior rather than being combined by hand
afterwards.

The same machinery covers datasets that are not different wavelengths at all — undithered
exposures in one band fitted before they are drizzled together, CCD imaging alongside
sub-millimetre visibilities, multi-epoch follow-up. Anything where several measurements of one
galaxy must inform one model.

Read [`../wiki/core/concepts/multi_wavelength.md`](../wiki/core/concepts/multi_wavelength.md)
for the *what is shared* decision in depth, and
[`../wiki/core/api/analysis_objects.md`](../wiki/core/api/analysis_objects.md) for the factor
graph's API surface. The canonical script is
`autogalaxy_workspace:scripts/multi_dataset/start_here.py`.

## Ask

- *"How many datasets, and what distinguishes them?"* Different filters, repeated exposures in
  one filter, or genuinely different instruments — the answer picks the branch, because it
  decides what is shared.
- *"Which parameters do you believe are the same across your datasets, and which must differ?"*
  This is the whole model, and it is a scientific question before it is an API one. If the user
  does not have a view yet, the default below (everything shared, amplitudes free by virtue of
  linear light profiles) is the right place to start.
- *"Do you want them fitted simultaneously, or the best one first and the rest chained off it?"*
  Simultaneous is the default. One-by-one is the deliberate alternative when one dataset is much
  better than the others, and its branch is below.
- *"Are the datasets astrometrically aligned, and do you trust that alignment?"* Sub-pixel
  residuals are normal even after a good reduction, and unmodelled they leak straight into the
  structural parameters.

If any dataset is **real observational data**, the inspection gate in
[`../AGENTS.md`](../AGENTS.md) applies to **every** band, not just the first: contaminants and
mask extent are settled from looking at each one, in
[`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md). A neighbour that is faint at 1.1 µm
can dominate at 4.4 µm.

## Branch — the joint fit

This is the deliverable: one script that loads several bands, states what is shared, and fits
them together. Adapted from `autogalaxy_workspace:scripts/multi_dataset/start_here.py` and
`autogalaxy_workspace:scripts/multi_dataset/modeling.py`.

The example uses the four-band JWST/NIRCam cutout that ships with this repo
(`autogalaxy_assistant:dataset/imaging/cosj100020+015344/`, layout and `info.json` schema in
[`../wiki/core/operations/dataset.md`](../wiki/core/operations/dataset.md)) — a real early-type
galaxy at z = 0.3422 with two short-wave bands at 0.03"/pixel and two long-wave bands at
0.06"/pixel. Point `WAVEBAND_LIST` and `DATASET_PATH` at your own bands and nothing else
changes.

```python
"""
Galaxy Structure: Joint Multi-Band Fit
=====================================

Fit four bands of JWST/NIRCam imaging of one galaxy simultaneously: load and mask each band,
compose a single galaxy whose geometry is shared across every band, and sample the joint
posterior with Nautilus so the shared effective radius and Sersic index are constrained by all
four bands at once while each band solves its own amplitude.

__Contents__

- **Imports:** JAX environment first, then the standard trio.
- **Dataset:** Load one `Imaging` per band, each with its own pixel scale.
- **Mask:** Mask and over-sample each band on the same sky footprint.
- **Model:** One galaxy, with the geometry shared and the amplitudes solved linearly.
- **Analysis:** One analysis per band.
- **Factor Graph:** Pair each analysis with a model copy and combine them.
- **Search:** Configure Nautilus for the joint likelihood.
- **Model-Fit:** Run the fit and announce the output folder.
- **Result:** Read the per-band results back.
"""
from autogalaxy import jax_wrapper  # Sets the JAX environment before other imports

import json
from pathlib import Path

import autofit as af
import autogalaxy as ag
import autogalaxy.plot as aplt

"""
__Dataset__

Each band is loaded as its own `ag.Imaging` (`PyAutoArray:autoarray/dataset/imaging/dataset.py`).
The bands are *not* stacked into one array: they have different PSFs and, here, different pixel
scales, and both of those are properties of the data rather than the galaxy. `pixel_scales` is
read from each band's `info.json` rather than hard-coded, because getting it wrong silently
rescales every length the fit reports.
"""
DATASET_PATH = Path("dataset") / "imaging" / "cosj100020+015344"
WAVEBAND_LIST = ["F115W", "F150W", "F277W", "F444W"]

dataset_list = []

for waveband in WAVEBAND_LIST:
    band_path = DATASET_PATH / "wavebands" / waveband

    info = json.loads((band_path / "info.json").read_text())

    dataset_list.append(
        ag.Imaging.from_fits(
            data_path=band_path / "data.fits",
            noise_map_path=band_path / "noise_map.fits",
            psf_path=band_path / "psf.fits",
            pixel_scales=info["pixel_scale"],
        )
    )

"""
__Mask__

Use the same sky footprint for every band wherever you can. The radii need not agree in pixels —
they cannot, with two pixel scales — but making them agree in arcseconds means each band's fit
is constrained by the same region of the galaxy, which is what makes a colour measured across
bands meaningful. Over-sampling is applied per band, because it is defined on that band's grid
(`ag.util.over_sample.over_sample_size_via_radial_bins_from`).
"""
MASK_RADIUS = 2.2

dataset_masked_list = []

for dataset in dataset_list:
    mask = ag.Mask2D.circular(
        shape_native=dataset.shape_native,
        pixel_scales=dataset.pixel_scales,
        radius=MASK_RADIUS,
    )

    dataset = dataset.apply_mask(mask=mask)

    over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
        grid=dataset.grid,
        sub_size_list=[8, 4, 2],
        radial_list=[0.3, 0.6],
        centre_list=[(0.0, 0.0)],
    )

    dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

    dataset_masked_list.append(dataset)

"""
__Model__

One galaxy, composed once. A linear `Sersic` bulge and a linear `Exponential` disk: because
these are `lp_linear` profiles, `intensity` is solved by linear inversion at every likelihood
evaluation rather than sampled, so each band gets its own amplitude for free and colour
gradients come out correctly with no per-band prior and no extra dimensions
(`PyAutoGalaxy:autogalaxy/profiles/light/linear/sersic.py`,
[`../wiki/core/concepts/linear_light_profiles_and_mge.md`](../wiki/core/concepts/linear_light_profiles_and_mge.md)).

`ag.DatasetModel` is included so the astrometric offset of each band after the first can be
freed below (`PyAutoArray:autoarray/dataset/dataset_model.py`).
"""
bulge = af.Model(ag.lp_linear.Sersic)
disk = af.Model(ag.lp_linear.Exponential)

galaxy = af.Model(ag.Galaxy, redshift=0.3422, bulge=bulge, disk=disk)

dataset_model = af.Model(ag.DatasetModel)

model = af.Collection(
    dataset_model=dataset_model, galaxies=af.Collection(galaxy=galaxy)
)

"""
__Analysis__

One analysis per band. Each holds one dataset and knows how to score a proposed model against
it (`PyAutoGalaxy:autogalaxy/imaging/model/analysis.py`).
"""
analysis_list = [
    ag.AnalysisImaging(dataset=dataset, use_jax=True)
    for dataset in dataset_masked_list
]

"""
__Factor Graph__

Each analysis is paired with a *copy* of the model in an `af.AnalysisFactor`, and the factors are
combined in an `af.FactorGraphModel` whose log likelihood is the sum over factors
(`PyAutoFit:autofit/graphical/declarative/factor/analysis.py`,
`PyAutoFit:autofit/graphical/declarative/collection.py`).

Sharing is expressed entirely through the model, never by special-casing a dataset. With a bare
`model.copy()` and no overrides the graph identifies every prior across the factors, so the whole
model is shared. Overriding a prior on one copy before wrapping it is what frees that parameter
for that dataset — here the grid offset of every band after the first.
"""
analysis_factor_list = []

for i, analysis in enumerate(analysis_list):
    model_analysis = model.copy()

    if i > 0:
        model_analysis.dataset_model.grid_offset.grid_offset_0 = af.UniformPrior(
            lower_limit=-0.2, upper_limit=0.2
        )
        model_analysis.dataset_model.grid_offset.grid_offset_1 = af.UniformPrior(
            lower_limit=-0.2, upper_limit=0.2
        )

    analysis_factor_list.append(
        af.AnalysisFactor(prior_model=model_analysis, analysis=analysis)
    )

factor_graph = af.FactorGraphModel(*analysis_factor_list, use_jax=True)

print(factor_graph.global_prior_model.info)

"""
__Search__

Multi-band fits stay on `Nautilus`. Each band may carry its own pixel scale, so the bands do not
share a grid shape and JAX must compile a separate gradient kernel per band; that compile cost
currently makes the gradient optimizers impractical here, even though they are the default for
single-dataset fits (`autogalaxy_workspace:scripts/multi_dataset/start_here.py`
`__Why Not MultiStartProdigy?__`).
"""
search = af.Nautilus(
    path_prefix=Path("multi_dataset"),
    name="four_band",
    unique_tag="cosj100020+015344",
    n_live=150,
    n_batch=50,
    iterations_per_quick_update=10000,
    live_visual_update=False,
)

"""
__Model-Fit__

Two things differ from a single-dataset fit: the *model* passed to the search is
`factor_graph.global_prior_model`, and the *analysis* is the factor graph itself. Results are
written on the fly, so the output folder is worth opening the moment the search starts.
"""
print(f"Output folder: {search.paths.output_path.resolve()}")

result_list = search.fit(
    model=factor_graph.global_prior_model, analysis=factor_graph
)

"""
__Result__

One result per factor, in the order the factors were built. Shared parameters must be identical
across the results and freed ones must differ — reading them back is the only real confirmation
that the sharing you intended is the sharing you built.
"""
for waveband, result in zip(WAVEBAND_LIST, result_list):
    instance = result.max_log_likelihood_instance
    print(
        f"{waveband}: effective_radius = "
        f"{instance.galaxies.galaxy.bulge.effective_radius:.4f}, "
        f"grid_offset = {instance.dataset_model.grid_offset}"
    )
```

`af.AnalysisFactor` + `af.FactorGraphModel` is **the** construction for combining datasets.
There is no other one, and nothing about the datasets is combined outside the model — if you
want a parameter to differ between two datasets, you override its prior on that dataset's model
copy, and that is the entire mechanism.

Before launching, always `print(factor_graph.global_prior_model.info)`. It prints the shared
block once and then a numbered section per factor showing what that factor overrode. That
printout is the only way to confirm which priors were identified and which were freed, and a
graph that shares the wrong thing produces a confident wrong answer rather than an error.

## Branch — deciding what is shared

Scientific question first, API second.

**Usually shared.** The galaxy's centre, its `ell_comps`, its structural scale (effective
radius, Sersic index), and the mesh and regularisation of any pixelised component. These
describe the object, so a band that wants its own value is usually telling you something about
your model rather than about the galaxy.

**Usually per-dataset.** The PSF and pixel scale (already per-dataset by construction, since they
live on the `Imaging` object rather than in the model), the mask, the sky background level, and
any astrometric offset.

**The interesting middle.** Amplitude *must* vary per band — that is colour, and linear light
profiles give it to you at zero cost. Whether the *radial scale* may vary is a real question
about the galaxy: an old concentrated population inside a bluer disk genuinely has a
wavelength-dependent half-light radius. Freeing it is legitimate; so is tying it to a relation
(next branch); so is fixing it and checking the residuals for the size mismatch you would then
expect to see.

The failure modes are symmetric and neither announces itself. Give a band too much freedom and
it will quietly absorb a modelling failure that a shared parameter would have exposed as
residuals. Give it too little and you will attribute a genuine colour gradient to noise.

To free one parameter per dataset, the workspace's own idiom is a plain override on the copy
(`autogalaxy_workspace:scripts/multi_dataset/modeling.py` `__Analysis Factor__`):

```python
for analysis in analysis_list:
    model_analysis = model.copy()
    model_analysis.galaxies.galaxy.bulge.effective_radius = af.UniformPrior(
        lower_limit=0.0, upper_limit=10.0
    )

    analysis_factor_list.append(
        af.AnalysisFactor(prior_model=model_analysis, analysis=analysis)
    )
```

## Branch — a wavelength relation instead of a parameter per band

Freeing a parameter per band scales badly: five bands means five free effective radii, each
constrained by one band's data. If you expect the parameter to vary *smoothly* with wavelength —
which for a size, an axis ratio or a Sersic index is usually a defensible physical expectation —
parameterise the **relation** and fit its coefficients instead. A linear relation costs two
parameters no matter how many bands you have.

Adapted from
`autogalaxy_workspace:scripts/multi_dataset/features/wavelength_dependence/modeling.py`:

```python
WAVELENGTH_LIST = [1.15, 1.50, 2.77, 4.44]  # microns, one per band

bulge_m = af.UniformPrior(lower_limit=-0.5, upper_limit=0.5)
bulge_c = af.UniformPrior(lower_limit=0.0, upper_limit=5.0)

analysis_factor_list = []

for wavelength, analysis in zip(WAVELENGTH_LIST, analysis_list):
    model_analysis = model.copy()

    model_analysis.galaxies.galaxy.bulge.effective_radius = (
        wavelength * bulge_m
    ) + bulge_c

    analysis_factor_list.append(
        af.AnalysisFactor(prior_model=model_analysis, analysis=analysis)
    )

factor_graph = af.FactorGraphModel(*analysis_factor_list, use_jax=True)
```

The arithmetic on priors is real, not notation: `(wavelength * bulge_m) + bulge_c` builds a
derived prior (`PyAutoFit:autofit/mapper/prior/arithmetic/arithmetic.py`), so `m` and `c` are
the sampled parameters and each band's `effective_radius` is determined by them. The
`global_prior_model.info` for such a graph shows each factor's `effective_radius` as a
`self`-with-`wavelength` entry rather than a prior, which is how you confirm the relation was
built rather than four independent radii.

The scientific payoff is that `m` is *directly* the gradient of size with wavelength, measured
with an error bar, which is usually the quantity the paper wants — rather than four loosely
constrained radii you have to regress afterwards with no covariance information.

The cost is the assumption. If the true variation is not the shape you imposed, the fit distorts
other parameters to compensate. Fit a small number of bands with free per-band values first, look
at whether they lie on a line, and then impose one. Any functional form you can write with prior
arithmetic works — the linear case is the example, not the limit.

## Branch — astrometric offsets

Reduction pipelines align frames, but sub-pixel residuals survive, and telescope pointing
precision leaves an uncertainty of its own. Left unmodelled that misalignment leaks into the
galaxy parameters, and the usual symptom is a model inferred from one band fitting a second band
noticeably worse than it should.

`ag.DatasetModel` carries `grid_offset` (two parameters) and `grid_rotation_angle`
(`PyAutoArray:autoarray/dataset/dataset_model.py`). The offset is applied by shifting the
*image-pixel grid* before the light profiles are evaluated, not by moving the profile centres, so
the galaxy model's geometry is untouched. The default is not a prior but a fixed `(0.0, 0.0)`, so
an offset is opt-in per dataset.

Convention, from
`autogalaxy_workspace:scripts/multi_dataset/features/dataset_offsets/modeling.py`: the first
dataset defines the reference frame and each subsequent one gets its own offset, so N datasets
cost `2 × (N − 1)` parameters. That is the price, and for most multi-band structural work it is
the difference between an accurate model and a subtly wrong one.

The offset also has a wider prior range than you might expect in the workspace examples
(±1.0"); tighten it to what your reduction plausibly left behind, because a wide offset prior
gives the search room to trade position against structure.

## Branch — several exposures at one wavelength

The machinery does not care that the datasets are different filters. Several exposures in one
band — undithered HST frames fitted *before* drizzling, so that the drizzle's correlated noise
is never baked into the data you fit — use exactly the same construction with everything shared
except the offsets. `autogalaxy_workspace:scripts/multi_dataset/features/same_wavelength/modeling.py`.

Dithered frames are deliberately shifted by design, typically by a fraction of a pixel, so this
case and the offset branch above almost always travel together.

## Branch — CCD imaging together with visibilities

Optical imaging and sub-millimetre visibilities of the same galaxy are complementary rather than
redundant: the imaging constrains the smooth stellar light, the interferometer the compact
star-forming structure, and the two need not resemble each other at all. Combining them is the
same factor graph with a different analysis class on one factor
(`autogalaxy_workspace:scripts/multi_dataset/features/imaging_and_interferometer/modeling.py`):

```python
analysis_imaging = ag.AnalysisImaging(dataset=imaging, use_jax=True)

analysis_interferometer = ag.AnalysisInterferometer(
    dataset=interferometer, use_jax=True
)

analysis_factor_list = []

for analysis in [analysis_imaging, analysis_interferometer]:
    bulge = af.Model(ag.lp_linear.Sersic)
    disk = af.Model(ag.lp_linear.Exponential)

    galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)

    model_analysis = af.Collection(galaxies=af.Collection(galaxy=galaxy))

    analysis_factor_list.append(
        af.AnalysisFactor(prior_model=model_analysis, analysis=analysis)
    )

factor_graph = af.FactorGraphModel(*analysis_factor_list, use_jax=True)
```

Note what the workspace script is honest about, and repeat it to the user: composing the model
*inside* the loop, as above, means the two factors share **nothing**, and a joint fit of two
completely independent models is no better than two separate fits. The construction is worth
running only once you have decided which parameters genuinely couple the two views — commonly
the centre and the geometry, rarely the amplitudes — and shared those explicitly. The
interferometer side (real-space mask, transformer choice, dirty-image diagnostics) is
[`ag_build_interferometer_model`](./ag_build_interferometer_model.md).

## Branch — a pixelised component across bands

A pixelised reconstruction works inside the graph unchanged. The mesh and the pixelisation are
shared, and the natural thing to free per band is the regularisation coefficient, since the
signal-to-noise ratio and the amount of real small-scale structure differ from band to band
(`autogalaxy_workspace:scripts/multi_dataset/features/pixelization/modeling.py`):

```python
pixelization = af.Model(
    ag.Pixelization,
    mesh=af.Model(ag.mesh.RectangularBilinearAdaptDensity, shape=(30, 30)),
    regularization=ag.reg.Constant,
)

galaxy = af.Model(ag.Galaxy, redshift=0.5, pixelization=pixelization)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

for analysis in analysis_list:
    model_analysis = model.copy()
    model_analysis.galaxies.galaxy.pixelization.regularization.coefficient = (
        af.LogUniformPrior(lower_limit=1e-4, upper_limit=1e4)
    )

    analysis_factor_list.append(
        af.AnalysisFactor(prior_model=model_analysis, analysis=analysis)
    )
```

Watch the memory: every band's linear-algebra structures live in VRAM simultaneously. What a
pixelisation is and how regularisation works is
[`../wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md),
and the single-dataset procedure is `ag_pixelization`.

## Branch — one dataset at a time, deliberately

A simultaneous fit is not always the right answer.
`autogalaxy_workspace:scripts/multi_dataset/features/one_by_one/modeling.py` fits the best
dataset first, then chains its inferred model into each of the others. Three situations justify
it:

- **One dataset is much better than the rest.** A low-resolution band fitted simultaneously can
  drag a joint fit toward a compromise that suits neither; fitting the good band first and
  interpreting the poorer ones against it keeps the good constraint intact.
- **Total run time.** More searches, but each one is cheaper than a search over the joint
  likelihood, and often faster in sum.
- **Robustness.** A structure that shows up in a simultaneous fit and vanishes when the bands
  are fitted individually was probably not real. This is a cheap and underused check.

How much to fix and how much to free at each step is the judgement call, and the script walks
three variants: fix the bulge entirely and free only the disk; free everything but start from
the first result; or fix the whole galaxy and fit *only* the offset between the two datasets,
which is the cleanest way to measure an alignment residual. The prior-passing mechanics belong
to [`ag_chain_searches`](./ag_chain_searches.md) — read it before writing the second search,
because the difference between passing a `model` and passing an `instance` is the difference
between narrowing a prior and removing a dimension.

## Branch — reading the result, and the two traps in it

`search.fit` on a factor graph returns a list-like result — one entry per factor, in the order
the factors were built — rather than a single `Result`. Two things surprise people:

- **The `Samples` object is global.** It has the dimensionality of the whole graph and is
  *identical* in every entry. `result_list[2].samples` is not "band 2's posterior"; there is only
  one posterior, over the joint model. Per-band quantities come from
  `result_list[i].max_log_likelihood_instance` and `result_list[i].max_log_likelihood_fit`.
- **Ordering is yours to keep straight.** Nothing labels a factor with its band. Zip your
  waveband list against the results, as the script above does, rather than indexing by memory.

Plot each band's fit separately — `aplt.subplot_fit_imaging` writes a fixed `fit.png`, so give
each band its own directory:

```python
for waveband, result in zip(WAVEBAND_LIST, result_list):
    aplt.subplot_fit_imaging(
        fit=result.max_log_likelihood_fit,
        output_path=f"scripts/scratch/four_band/{waveband}/",
        output_format="png",
    )
```

The full functional plotting surface and which entry points accept `output_filename` is
[`../wiki/core/api/plotting.md`](../wiki/core/api/plotting.md) and
[`ag_plot_fit`](./ag_plot_fit.md).

## Branch — cost, and proving the script before you pay it

Every dataset adds its arrays to the likelihood and to VRAM. The factor graph carries the same
VRAM estimator the single-dataset analyses do
(`autogalaxy_workspace:scripts/multi_dataset/modeling.py` `__VRAM Use__`):

```python
factor_graph.print_vram_use(
    model=factor_graph.global_prior_model, batch_size=search.batch_size
)
```

It takes twenty or thirty seconds, so comment it out once you know your footprint. Batch size is
the lever in both directions: larger batches cut wall-clock time and raise VRAM.

Smoke test before committing hours, exactly as for a single dataset — the graph adds new ways to
be wrong (a mis-scoped override, a factor built from the wrong model copy) and level 2 catches
all of them in seconds:

```bash
PYAUTO_TEST_MODE=2 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/four_band_fit.py
```

Level 1 if you want the fit products written; the levels and the other short-circuit flags are
[`../wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md). Parameter values
from any test-mode run are meaningless — say so rather than quoting them.

## Combine

- [`ag_build_imaging_model`](./ag_build_imaging_model.md) — get one band fitting well before you
  join four. A joint fit is not a way to rescue a model that fails on its best dataset.
- [`ag_chain_searches`](./ag_chain_searches.md) — the one-by-one route, and prior passing.
- [`ag_build_interferometer_model`](./ag_build_interferometer_model.md) — the visibility side of
  a joint imaging-plus-interferometer fit.
- [`ag_load_results`](./ag_load_results.md) — pulling per-band amplitudes and colours out of the
  result list, and the aggregator when you have many galaxies each with many bands.
- [`ag_plot_fit`](./ag_plot_fit.md) — per-band residuals, which is where a wrongly-shared
  parameter shows itself.
- [`ag_configure_search`](./ag_configure_search.md) — `n_live`, `n_batch` and the resume
  semantics, all of which apply unchanged to the joint fit.
- `ag_pixelization` and `ag_basis_profiles` — the components most often shared across bands.

Population-level inference over *different* galaxies is a different construction on the same
graphical-model machinery;
[`../wiki/core/concepts/hierarchical_models.md`](../wiki/core/concepts/hierarchical_models.md)
covers it, and no skill owns it — that page says plainly that its composition is unvalidated,
so treat it as the shape of the API rather than a recipe.

When the joint fit is worth keeping, offer (default-yes) to record it in a dated
`wiki/project/YYYY-MM-DD-<slug>.md` entry: which bands, what was shared and why, what was freed,
and the output path — per [`_style.md`](./_style.md) property #5. The sharing decision is the
scientific content of a multi-band fit and is exactly the thing you will not remember in a
month.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Linear light profiles](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_2_modeling/tutorial_5_linear_profiles.ipynb):
  why solving amplitudes by linear inversion rather than sampling them is what makes per-band
  colours free of charge. There is no multi-wavelength chapter in the lecture series — this is
  the tutorial that teaches the idea the joint fit leans on hardest.
- **General reference** — [RTD: Features](https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_3_features.html):
  the multi-wavelength section of the feature tour, with pointers onward.
- **Experienced PyAutoGalaxy user** — [workspace: multi_dataset/start_here.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/multi_dataset/start_here.py):
  the minimal end-to-end joint fit, with the factor-graph and per-dataset-offset sections this
  skill mirrors.

## Agent procedural checklist

1. Establish how many datasets there are and what distinguishes them.
2. On real data, confirm the inspection gate has been satisfied for **every** dataset.
3. Settle the shared-versus-per-dataset decision with the user before writing the model; state
   the default (everything shared, amplitudes linear) if they have no view.
4. Build one analysis per dataset, wrap each in `af.AnalysisFactor` with its own `model.copy()`,
   and combine with `af.FactorGraphModel`.
5. `print(factor_graph.global_prior_model.info)` and read it — confirm the identified and freed
   priors are the ones intended.
6. Pass `factor_graph.global_prior_model` as the model and `factor_graph` as the analysis.
7. Where a parameter should vary smoothly with wavelength, offer the relation form before
   freeing it per band.
8. Free `grid_offset` for every dataset after the first unless the user is confident in the
   alignment.
9. Validate with `PYAUTO_TEST_MODE=2` before the production run; on a GPU also run
   `factor_graph.print_vram_use`.
10. Announce the output path immediately, and zip the results against the dataset labels when
    reading them back.
11. Offer the `wiki/project/` entry recording the sharing decision.
