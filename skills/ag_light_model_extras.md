---
name: ag_light_model_extras
description: Add the three model components that sit beside a galaxy's own light profiles — contaminating extra galaxies, a residual background sky via `ag.DatasetModel`, and operated (already-PSF-convolved) light profiles for compact nuclear emission. Covers when to mask a neighbour, scale its noise or model it and why the choice changes the answer; loading fixed centres from JSON with `ag.Grid2DIrregular`; `SersicSph` versus a pinned-centre MGE for a companion; why `af.Model(ag.DatasetModel)` starts with zero free parameters and silently fixes the sky at 0.0 unless you assign a prior; `grid_offset` and `grid_rotation_angle` for band registration; and `ag.lp_operated` / `ag.lp_linear_operated` for an AGN or nuclear starburst whose emission already shows the PSF. Worked against the bundled real dataset `dataset/imaging/cosj100020+015344`, which has both an un-subtracted sky pedestal and a faint neighbour 2.6" from the centre. Use once a galaxy model exists and the data has contaminants, an uncertain sky, or a point-like nucleus. Not for the galaxy's own morphology (`ag_build_imaging_model`, `ag_basis_profiles`), not for pixelized reconstruction (`ag_pixelization`), and not for two or more co-dominant galaxies.
---

# The parts of the model that are not the galaxy

Three things routinely bias a galaxy-structure measurement, and none of them are the galaxy: a
neighbour whose light overlaps it, a background sky that was not perfectly subtracted, and a
compact nuclear source that a smooth profile cannot represent. All three are handled as extra
model components, and all three matter for the same reason — they contaminate the **faint outer
light**, which is precisely what sets `effective_radius` and `sersic_index`. Get them wrong and
the fit does not fail; it returns confident, wrong numbers.

Statistically these are nuisance parameters. You do not care about the sky level or the
neighbour's size, but you care very much that their uncertainty propagates into the errors you
quote. A model that fixes the sky at zero because the reduction "should have" removed it asserts
zero uncertainty on something genuinely uncertain, and every parameter that has to absorb the
residual inherits a bias with no error bar to show it. Including a nuisance parameter you expect
to be small is how you *check* that belief rather than assume it.

The three components sit in different places in the model tree, and that geography is worth
knowing before any code:

| Component | Where it goes | Typical cost |
|---|---|---|
| extra galaxies | its own top-level `extra_galaxies` collection, **not** inside `galaxies` | ~2 free parameters each |
| background sky, astrometric offset | `dataset_model=af.Model(ag.DatasetModel)`, beside `galaxies` | 1–3 |
| operated profile | an ordinary component *on* the galaxy | 3–4 |

## The worked case — the bundled dataset

This skill uses `dataset/imaging/cosj100020+015344`, the real four-band JWST/NIRCam cutout that
ships with this repo, because it has two of the three problems for real:

- **The sky is not subtracted.** `calwebb_image3`'s skymatch step matches the exposures'
  backgrounds to each other but does not remove them, so `data.fits` carries the real JWST sky as
  a positive pedestal — 4.5× the median noise at F115W, rising to 19× at F444W. A light-profile
  fit that ignores this absorbs the pedestal into the profile wings and returns an inflated
  effective radius and Sersic index. The measured value per band is in each `info.json` as
  `background_sky_level` (0.1246 MJy/sr at F277W).
- **There is a real neighbour inside any useful mask.** A faint source sits **2.6" from the
  centre**, holding about 0.3% of the galaxy's flux. A brighter one 8.0" out is excluded by any
  mask under ~4", but the 2.6" source is not — it has to be masked or modelled every session.
  **No `mask_extra_galaxies.fits` ships with the dataset**, so this is a live decision, not a
  solved one.

Both caveats, the `info.json` schema and the model-PSF warning are in
[`../wiki/core/operations/dataset.md`](../wiki/core/operations/dataset.md), with the full
provenance in the dataset's own `README.md`. The real-data inspection gate in
[`../AGENTS.md`](../AGENTS.md) applies to this dataset in full: plot it, show the user
`dataset.png`, and settle the neighbour and the mask extent from that look before composing
anything. If you have not done that, go to
[`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md) first.

```python
"""
__Dataset__

The bundled cutout, F277W — the reference band, with the highest signal-to-noise (peak S/N 180)
and uniform exposure coverage across the frame. `info.json` carries every measured quantity,
including the pixel scale and the sky pedestal, so read it rather than hard-coding numbers
(`PyAutoArray:autoarray/dataset/imaging/dataset.py`).

Note that `dataset.psf` is a `Convolver`, not an array — the kernel itself is
`dataset.psf.kernel`. And treat the PSF as the dominant systematic here: it is an STPSF *model*
kernel, slightly sharper than an empirical one, so expect a fitted size to compensate slightly
large.
"""
import json
from pathlib import Path

import autofit as af
import autogalaxy as ag
import autogalaxy.plot as aplt

DATASET_PATH = (
    Path("dataset") / "imaging" / "cosj100020+015344" / "wavebands" / "F277W"
)
MASK_RADIUS = 3.5
REDSHIFT = 0.3422  # spectroscopic, from zCOSMOS-Bright DR3 — cited in the dataset README

info = json.loads((DATASET_PATH / "info.json").read_text())

dataset = ag.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    psf_path=DATASET_PATH / "psf.fits",
    pixel_scales=info["pixel_scale"],
)

mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=MASK_RADIUS,
)
dataset = dataset.apply_mask(mask=mask)
```

A mask of 3.5" keeps the fit inside the uniformly covered region and excludes the 8.0"
neighbour, while reaching the galaxy's outer isophotes. It does **not** exclude the 2.6" source —
that is what the rest of this skill is about.

## Ask

- *"Do you trust the sky subtraction?"* If the science is the faint outer envelope — an effective
  radius, a Sersic index, a bulge-to-total ratio — the honest answer is usually "not enough to
  fix it at zero". One parameter buys you the check.
- *"Is the neighbour's light genuinely blended with the target's, or merely nearby?"* Merely
  nearby, and outside where the target's light matters → shrink the mask. Blended → scale its
  noise or model it. The three strategies are not equivalent and the choice is scientific.
- *"Are you using a pixelization?"* If so, the masking option is off the table — removing pixels
  punches holes in the mesh. Scale or model
  ([`ag_pixelization`](./ag_pixelization.md)).
- *"Is there a compact nuclear source?"* A sharp central peak that a Sersic cannot reach without
  driving `sersic_index` to its limit is usually an AGN or nuclear starburst. Two ways to model
  it — an operated profile or a compact MGE — and they behave differently.
- *"Several bands, and are they registered?"* Sub-pixel misregistration between bands is what
  `grid_offset` exists for.

## Branch — the background sky

One parameter, and the single highest-value addition to a fit that cares about outer light.

```python
"""
__Model__

The galaxy's light plus the dataset's sky. `ag.DatasetModel` is not a galaxy and does not live in
the `galaxies` collection — it describes the *data*, and sits beside `galaxies` as its own
top-level component (`PyAutoArray:autoarray/dataset/dataset_model.py`).

**You must set the prior on `background_sky_level` by hand.** Unlike a light profile's priors,
the right range depends entirely on the data's units and depth, so no default could be correct —
and `af.Model(ag.DatasetModel)` therefore starts with **zero** free parameters, holding every
constructor argument at its default. Omit the assignment below and the sky is silently *fixed*
at 0.0, which is the failure this branch exists to prevent. Confirm with
`print(dataset_model.total_free_parameters)`.

Here the measured pedestal is 0.1246 MJy/sr, so a uniform prior from 0.0 to 0.4 comfortably
brackets it without letting the sky wander into the galaxy's flux.
"""
bulge = af.Model(ag.lp_linear.Sersic)
galaxy = af.Model(ag.Galaxy, redshift=REDSHIFT, bulge=bulge)

dataset_model = af.Model(ag.DatasetModel)
dataset_model.background_sky_level = af.UniformPrior(
    lower_limit=0.0, upper_limit=0.4
)

model = af.Collection(
    galaxies=af.Collection(galaxy=galaxy), dataset_model=dataset_model
)

print(f"DatasetModel free parameters = {dataset_model.total_free_parameters}")
print(model.info)
```

N = 7: the linear Sersic's six plus the sky. Adapted from
`autogalaxy_workspace:scripts/imaging/features/sky_background/modeling.py`, whose dataset is
simulated with a known pedestal of 5.0 electrons per second and recovers it — a useful control if
you want to convince yourself the mechanism works before trusting it on real data.

Two traps worth stating explicitly, both verified:

- `af.Model(ag.DatasetModel).total_free_parameters` is **0**. There is no warning; the fit runs
  and reports a perfect sky subtraction you never tested.
- `background_sky_level` is **not a class attribute**. It is a constructor parameter, so reading it
  off the `ag.DatasetModel` class itself raises `AttributeError`, and the only way to free it is to
  assign a prior on an `af.Model` of that class, as above.

After the fit, the inferred value is on the result's instance:

```python
print(result.instance.dataset_model.background_sky_level)
```

Compare it against `info["background_sky_level"]`. Agreement is a real validation of the whole
fit; a large disagreement means the sky and the profile wings are trading, which is the
degeneracy this parameter exists to expose. The physics of why that degeneracy is so strong for
low-surface-brightness features is
[`../wiki/core/concepts/sky_background_and_operated_profiles.md`](../wiki/core/concepts/sky_background_and_operated_profiles.md).

The alternative is to subtract `info["background_sky_level"]` from the data before fitting. That
is legitimate and cheaper, but it asserts the measurement is exact — you lose the error
propagation, which is the main thing modelling it buys.

### The other two `DatasetModel` fields

`ag.DatasetModel(background_sky_level=0.0, grid_offset=(0.0, 0.0), grid_rotation_angle=0.0)` —
the full surface, verified. The other two describe the data's *astrometry* rather than its
background, and earn their keep in multi-band work where the bands are not perfectly registered:

```python
dataset_model = af.Model(ag.DatasetModel)
dataset_model.grid_offset.grid_offset_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
dataset_model.grid_offset.grid_offset_1 = af.GaussianPrior(mean=0.0, sigma=0.1)
dataset_model.grid_rotation_angle = af.UniformPrior(lower_limit=-5.0, upper_limit=5.0)
```

Three parameters. Only free these when you have a reason: a sub-pixel offset between bands, or a
known small rotation. On a single band with the galaxy already centred, they add dimensions for
nothing. The bundled dataset's four bands agree on the centre to 0.08", which is a real offset at
0.03"/pixel — so this is exactly the case where a joint multi-band fit wants `grid_offset` free
(the multi-dataset skill, `ag_multi_dataset`, owns that).

## Branch — extra galaxies: three strategies, one decision

A neighbour inside the mask leaves you three options, and they are ordered by cost and by how
much of the target's light they preserve:

1. **Shrink the mask.** Free. Correct when the neighbour lies outside the radius where your
   target's light matters. On the bundled dataset this handles the 8.0" source completely.
   It cannot handle the 2.6" one without truncating the galaxy's own outer isophotes — which
   biases exactly the parameters you are measuring.
2. **Scale its noise.** One extra file, no parameters. Keeps the pixels in the fit but zeroes
   their data and inflates their noise so they contribute nothing to the likelihood. This is the
   right default when the neighbour is faint and its light does not deeply overlap the target's,
   and it is **mandatory** if you are using a pixelization.
3. **Model it.** Two parameters per neighbour. The only option that recovers the target's light
   *underneath* the neighbour, so the only correct one when the two genuinely blend.

### Scaling the noise

```python
"""
__Noise Scaling__

The mask is loaded with `invert=True` because in a `mask_extra_galaxies.fits` file `True` means
"scale this pixel" — the opposite of a modelling mask's convention. Getting it backwards scales
the galaxy instead of the neighbour, so always look at the signal-to-noise panel afterwards: the
scaled pixels should be visibly blank. Scale first, then apply the modelling mask
(`PyAutoArray:autoarray/dataset/imaging/dataset.py`).

No such mask ships with the bundled dataset — draw one over the 2.6" source with
`autogalaxy_workspace:scripts/imaging/data_preparation/gui/mask_extra_galaxies.py`.
"""
mask_extra_galaxies = ag.Mask2D.from_fits(
    file_path=DATASET_PATH / "mask_extra_galaxies.fits",
    pixel_scales=info["pixel_scale"],
    invert=True,
)

dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)
dataset = dataset.apply_mask(mask=mask)

aplt.subplot_imaging_dataset(
    dataset=dataset,
    output_path="scripts/scratch/cosj100020/",
    output_filename="noise_scaled",
    output_format="png",
)
```

The scaled pixels reach a noise value of order 1e8 — that is what "contributes negligibly" means
in practice, and it is unmistakable on the subplot. Adapted from
`autogalaxy_workspace:scripts/imaging/features/extra_galaxies/modeling.py`.

### Modelling it

The convention is that a neighbour's **centre is fixed** to a value measured from the data,
leaving its other parameters free. This is not laziness: a companion with a free centre is a
model too complex to fit reliably, and the classic failure is one component wandering off to
absorb part of the target instead.

```python
"""
__Extra Galaxies__

Centres come from a JSON written during data preparation, wrapped in `ag.Grid2DIrregular` so they
behave as a coordinate list (`PyAutoArray:autoarray/structures/grids/irregular_2d.py`). Each
neighbour becomes its own `ag.Galaxy` with a spherical linear Sersic whose centre is pinned —
`SersicSph` rather than `Sersic` because a faint companion rarely justifies two ellipticity
parameters, and its `intensity` is solved by the inversion. That leaves `effective_radius` and
`sersic_index`: **two free parameters per neighbour**, cheap enough for a handful of companions.

`extra_galaxies` is its own top-level collection, **not** a member of `galaxies` — the analysis
relies on that placement (`PyAutoFit:autofit/mapper/prior_model/collection.py`).
"""
extra_galaxies_centres = ag.Grid2DIrregular(
    ag.from_json(file_path=DATASET_PATH / "extra_galaxies_centres.json")
)

extra_galaxies_list = []

for extra_galaxy_centre in extra_galaxies_centres:

    extra_galaxy = af.Model(
        ag.Galaxy, redshift=REDSHIFT, bulge=ag.lp_linear.SersicSph
    )
    extra_galaxy.bulge.centre = extra_galaxy_centre

    extra_galaxies_list.append(extra_galaxy)

model = af.Collection(
    galaxies=af.Collection(galaxy=galaxy),
    extra_galaxies=af.Collection(extra_galaxies_list),
    dataset_model=dataset_model,
)

print(model.info)
```

For an irregular or asymmetric companion, swap the spherical Sersic for an MGE with a pinned
centre. It costs the **same** two free parameters in the linear limit while being far more
flexible — verified, and the reason the workspace recommends it once the number of companions
grows beyond a handful:

```python
extra_galaxies_list = []

for extra_galaxy_centre in extra_galaxies_centres:

    mge_bulge = ag.model_util.mge_model_from(
        mask_radius=MASK_RADIUS,
        total_gaussians=10,
        centre_fixed=tuple(extra_galaxy_centre),
    )
    extra_galaxies_list.append(
        af.Model(ag.Galaxy, redshift=REDSHIFT, bulge=mge_bulge)
    )
```

Both options come straight from
`autogalaxy_workspace:scripts/imaging/features/extra_galaxies/modeling.py`, which presents them
as equally supported alternatives — Option A and Option B in its own prose. The MGE route is
[`ag_basis_profiles`](./ag_basis_profiles.md).

### Two things people forget

**Enlarge the mask.** If you are modelling a neighbour, its light has to be *in* the fit. The
workspace example uses a 6.0" mask against the 3.0" of its sibling scripts for exactly this
reason. Modelling a companion whose pixels you masked out fits nothing and costs two parameters.

**Over-sample at every centre.** The adaptive over-sampling helper takes a `centre_list`, and it
needs each neighbour's centre as well as the target's — otherwise the companion's steep central
gradient is evaluated on a coarse grid and its light is systematically mis-computed:

```python
over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[4, 2, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)] + extra_galaxies_centres.in_list,
)
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)
```

When to pick which strategy, in full:
[`../wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../wiki/core/concepts/extra_galaxies_and_noise_scaling.md).

One thing this feature deliberately does **not** have: a scaling-relation tier tying many faint
companions' properties to their luminosities through a few shared parameters. For a light-only
fit that is degenerate by construction — linear light profiles already solve `intensity`, so
scaling intensity by another shared free parameter adds nothing. The workspace's
`features/extra_galaxies/README.md` has the full argument. If several galaxies are genuinely
co-dominant rather than contaminating, that is a different model altogether — the
multi-galaxy and cluster skill (`ag_multi_galaxy_and_cluster`).

## Branch — operated light profiles, for emission that already shows the PSF

Compact central emission — an AGN, an unresolved nuclear starburst — is genuinely hard to model
the ordinary way. The model image of a near-point source is convolved with the PSF, and the
result is acutely sensitive to which pixel (and which sub-pixel) the emission lands in. The
likelihood surface acquires structure on the scale of a pixel, which is exactly the kind of
surface a sampler cannot map.

An **operated** profile sidesteps the problem by assuming the profile is *already* PSF-convolved.
The convolution step is skipped, and the profile is fitted directly to the emission as observed —
PSF features included. That is both faster (no convolution) and far better behaved.

```python
"""
__Model__

A linear Sersic bulge plus a linear operated `Gaussian` for the nucleus, with their centres
paired because a nuclear source sits at the galaxy's centre by definition
(`PyAutoGalaxy:autogalaxy/profiles/light/linear_operated/gaussian.py`).

**Set the `sigma` prior by hand.** The default is a `UniformPrior` from 0.0 to 5.0, which is far
too wide: an operated Gaussian's width should be comparable to the PSF, so a fraction of an
arcsecond. Use what you know about your PSF — for this dataset the shipped F277W kernel has a
half-light radius of 0.074", so a prior up to ~0.5" is generous already.

`ag.lp_linear_operated` rather than `ag.lp_operated` for the same reason as everywhere else: the
`intensity` is solved rather than sampled, which matters more here than usual because operated
profiles are the hardest components in this workspace to sample robustly.
"""
psf_component = af.Model(ag.lp_linear_operated.Gaussian)
psf_component.sigma = af.UniformPrior(lower_limit=0.0, upper_limit=0.5)

bulge = af.Model(ag.lp_linear.Sersic)
bulge.centre = psf_component.centre

galaxy = af.Model(
    ag.Galaxy, redshift=REDSHIFT, bulge=bulge, point=psf_component
)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

print(model.info)
```

N = 9 — the bulge's six, plus the nucleus's `ell_comps` (2) and `sigma`, with the centre shared
and both intensities solved. The non-linear `ag.lp_operated.Gaussian` variant gives N = 10, since
its `intensity` is sampled. Adapted from
`autogalaxy_workspace:scripts/imaging/features/operated_light_profile/modeling.py`, which shows
both and recommends the linear one.

`ag.lp_operated` and `ag.lp_linear_operated` each offer `Gaussian`, `Moffat` and `Sersic`.
`Gaussian` is the usual choice for a nucleus; `Moffat` if your PSF has strong wings. And the
mechanism is not limited to point sources — an operated profile is simply one that bypasses
convolution, so it fits any component you have reason to treat as already-convolved.

There is a **competing approach**: a compact MGE, ten Gaussians on a `sigma` ladder capped at
twice the pixel scale, which is `ag.model_util.mge_point_model_from` in
[`ag_basis_profiles`](./ag_basis_profiles.md). Four free parameters, and it does not need a
`sigma` prior tuned by hand. The trade: the operated profile is one interpretable width you can
quote, the compact MGE is more flexible and better behaved if the nuclear emission is not quite
Gaussian. Both are documented side by side in
[`../wiki/core/concepts/sky_background_and_operated_profiles.md`](../wiki/core/concepts/sky_background_and_operated_profiles.md).
Ask if you want to fit both and compare.

Note there is no `fit.py` example for operated profiles in the workspace — to do a single direct
fit, follow any other `imaging/fit.py` and swap the profile classes. Nothing else changes.

## Branch — all three at once, on the real data

They compose without interacting, which is the point of the model tree's geography:

```python
"""
__Model__

The full model for the bundled cutout: the target's linear Sersic bulge with a linear operated
nuclear Gaussian, the 2.6" neighbour as a pinned-centre spherical Sersic, and the un-subtracted
sky as a `DatasetModel`. Three components in three different places in the tree — the galaxy's
own light inside `galaxies`, the companion in `extra_galaxies`, the sky in `dataset_model`.
"""
model = af.Collection(
    galaxies=af.Collection(galaxy=galaxy),
    extra_galaxies=af.Collection(extra_galaxies_list),
    dataset_model=dataset_model,
)

print(model.info)
print(f"Total free parameters = {model.total_free_parameters}")

analysis = ag.AnalysisImaging(dataset=dataset, use_jax=True)

log_likelihood = analysis.log_likelihood_function(
    instance=model.instance_from_prior_medians()
)
print(f"log likelihood at prior medians: {float(log_likelihood):.2f}")
```

Twelve free parameters for the full model on this dataset, which any search handles comfortably.
Build it up rather than composing it in one go: fit the bulge alone, then add the sky, then the
neighbour, then the nucleus, and watch what each addition does to the residuals and to
`effective_radius`. That sequence is the evidence for the model, and it is what a referee will
ask you to show.

Run times are effectively unchanged by any of these. The sky is a constant added to the data;
`SersicSph` and an operated `Gaussian` are cheap to evaluate, and the operated one is *faster*
than an ordinary profile because it skips convolution. The cost is dimensionality, not
arithmetic.

## Combine — where this hands off

- **Inspect the data and settle the mask** → [`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md).
  On real data this is a gate, not a suggestion — and it is where `mask_extra_galaxies.fits` and
  `extra_galaxies_centres.json` get made.
- **Compose the galaxy's own light** → [`ag_build_imaging_model`](./ag_build_imaging_model.md).
- **A basis for the target or for an irregular companion** →
  [`ag_basis_profiles`](./ag_basis_profiles.md), which also holds the compact-MGE alternative to
  an operated profile.
- **Pixelized reconstruction** → [`ag_pixelization`](./ag_pixelization.md). Noise scaling is
  mandatory there; masking is not an option.
- **Configure and run** → [`ag_configure_search`](./ag_configure_search.md) and
  [`ag_run_search`](./ag_run_search.md).
- **The sky runs to its prior boundary, or a companion absorbs the target** →
  [`ag_debug_fit_failure`](./ag_debug_fit_failure.md). A sky pinned at its upper limit means the
  prior is too narrow or the profile wings are being starved; a companion at an implausible size
  usually means its centre was not fixed, or the mask cut off its light.
- **Several bands, with registration offsets** → the multi-dataset skill (`ag_multi_dataset`),
  where `grid_offset` is fitted per band through the factor graph. The bundled dataset's four
  bands are the worked case.
- **Two or more co-dominant galaxies rather than a target plus contaminants** → the multi-galaxy
  and cluster skill (`ag_multi_galaxy_and_cluster`).
- **Add components progressively across chained searches** → the search-chaining skill
  (`ag_chain_searches`).

Offer (default-yes) a dated `wiki/project/YYYY-MM-DD-<slug>.md` entry recording which strategy
you used for each contaminant and **why**, the sky prior and the value recovered against the
measured one, and how `effective_radius` moved as each component was added. Those are the
modelling assumptions the result depends on, and none of them are visible in the output folder.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Two galaxies](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_3_search_chaining/tutorial_3_x2_galaxies.ipynb):
  what happens to a fit when a second galaxy's light is in the frame, and how the model grows to
  account for it.
- **General reference** — [RTD: Features overview](https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_3_features.html):
  the tour of the capabilities beyond a single smooth profile, including the sky background and
  operated light profiles with links onward.
- **Experienced PyAutoGalaxy user** — [workspace: imaging/features/extra_galaxies/modeling.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/imaging/features/extra_galaxies/modeling.py):
  masking, noise scaling and modelling in one script, with the `SersicSph` and MGE options side
  by side.

## Agent procedural checklist

1. On real data, confirm the inspection gate was satisfied — plot the data, show the user the
   path, and settle contaminants and mask extent — before composing anything.
2. On the bundled dataset, state the two live caveats: the un-subtracted sky and the 2.6"
   neighbour with no mask shipped.
3. For the sky, assign a prior on `af.Model(ag.DatasetModel).background_sky_level` and **verify
   `total_free_parameters` is not 0** before running.
4. Scale the prior to the data's units and depth — read `info["background_sky_level"]` rather
   than guessing; after the fit, compare the inferred value against it.
5. For a neighbour, choose consciously between shrinking the mask, scaling noise and modelling —
   and say why. With a pixelization, masking is off the table.
6. Fix every extra galaxy's centre; enlarge the mask to include its light; add its centre to the
   over-sampling `centre_list`.
7. Load the `invert=True` scaling mask, then look at the signal-to-noise panel to confirm the
   right pixels were scaled.
8. For a nucleus, prefer `ag.lp_linear_operated` and set the `sigma` prior from the PSF's
   measured width — never leave it at the 0–5" default.
9. Build the model up one component at a time and record how `effective_radius` responds.
10. Save the script to `scripts/`, quote every plot's absolute path and offer to open it, then
    offer the `wiki/project/` entry recording each contaminant decision.
