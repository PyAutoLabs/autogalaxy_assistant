---
name: ag_build_imaging_model
description: Compose the galaxy model for a CCD imaging fit — an `af.Model` / `af.Collection` tree of light profiles on one or more galaxies, plus the `ag.AnalysisImaging` that scores it against a loaded dataset. Covers a single Sersic, a bulge-plus-disk decomposition, why `ag.lp_linear` profiles are the default, a Multi-Gaussian Expansion for irregular morphology, prior customisation, pairing / fixing / assertions, `ag.DatasetModel` for a residual sky or astrometric offset, modelling contaminating extra galaxies with fixed centres, and checking the model with `print(model.info)` and a single likelihood evaluation before spending a search on it. Use once a dataset is loaded and masked. Requires the real-data inspection gate to have been satisfied first (`ag_prepare_imaging_data`). Not for choosing or configuring the search (`ag_configure_search`), not for running the fit, and not for visibility-plane data.
---

# Composing an imaging galaxy model

The model is your statement of what this galaxy *could* be: how many components, with what
functional forms, which parameters free and which fixed, and what prior on each. It is the
half of the fit you are responsible for — the search only explores what you wrote down. A
model too simple leaves structure in the residuals and biases every parameter that has to
absorb it; a model too complex has a parameter space the search cannot map, and returns wide
errors or a local maximum. Getting this right is most of galaxy morphology.

A fit has exactly two halves: the **model** says what could be true, and the **analysis**
holds a dataset and knows how to score a proposal against it. A search shuttles between them:

```python
result = search.fit(model=model, analysis=analysis)
```

Everything in this skill builds one of those two arguments. The canonical script is
`autogalaxy_workspace:scripts/imaging/modeling.py`; the API page is
[`../wiki/core/api/analysis_objects.md`](../wiki/core/api/analysis_objects.md), and the
systematic composition reference is
`autogalaxy_workspace:scripts/guides/modeling/cookbook.py`.

## Before you compose — the gate

If the dataset is **real observational data**, confirm the inspection gate has been
satisfied: that the user has seen `dataset.png`, and that both (a) contaminating extra
galaxies / foreground stars / artefacts and (b) the mask extent were settled from that look.
If either is still open, stop and do it in
[`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md) first — composing a model over data
with an unaddressed contaminant, or a mask left at a silent default, produces a confident
wrong answer rather than an obvious failure. Simulated data is exempt.

## Ask

- *"One galaxy, or several whose light blends?"* The only structural choice. This skill
  assumes a single target with optional contaminating neighbours; two or more co-dominant
  galaxies is a different skill (`ag_multi_galaxy_and_cluster`, not yet written — see
  [`../PENDING.md`](../PENDING.md)).
- *"A single Sersic to start, or straight to a bulge-plus-disk decomposition?"* Single Sersic
  first is almost always the right answer, even when you want the decomposition: it converges
  fast, tells you the galaxy's overall size and concentration, and gives you something to
  compare the two-component fit against.
- *"Is the morphology smooth, or irregular — spiral arms, asymmetry, a merger?"* Smooth means
  Sersic-family profiles. Irregular means a Multi-Gaussian Expansion, and beyond that a
  pixelised reconstruction (`ag_pixelization`, not yet written).
- *"What redshift?"* Even a ballpark value is enough; it is needed only for physical-unit
  conversions, not for the fit itself.
- *"Has the sky background been subtracted, and do you trust that subtraction?"* If the faint
  outer envelope is what you care about, the answer decides whether you need a
  `ag.DatasetModel`.

## Branch — a single Sersic

The minimum viable model, and the right first fit for almost any galaxy.

```python
"""
Galaxy Structure: Single Sersic
===============================

Compose and check a one-component galaxy model for CCD imaging: an elliptical Sersic profile
whose effective radius and Sersic index measure the galaxy's size and central concentration.
This is the first fit to run on any galaxy — it converges quickly, and its inferred size and
concentration are the reference every more complex model is judged against.

__Contents__

- **Imports:** Import the required libraries.
- **Dataset:** Load the masked, over-sampled imaging dataset produced during preparation.
- **Model:** Compose the galaxy's light as a single linear Sersic profile.
- **Check:** Print the model and evaluate the likelihood once before committing to a search.
"""

"""
__Imports__
"""
from pathlib import Path

import autofit as af
import autogalaxy as ag

DATASET_PATH = Path("dataset") / "imaging" / "my_galaxy"
PIXEL_SCALES = 0.1
MASK_RADIUS = 2.5

"""
__Dataset__

The dataset arrives already prepared: loaded from FITS, contaminant noise scaled, masked to
the radius chosen by inspecting the data, and over-sampled adaptively in the centre where the
profile's intensity gradient is steep. All four decisions belong to data preparation rather
than to the model, and all four change the answer, so they are reproduced here rather than
hidden (`PyAutoArray:autoarray/dataset/imaging/dataset.py`).
"""
dataset = ag.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    psf_path=DATASET_PATH / "psf.fits",
    pixel_scales=PIXEL_SCALES,
)

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

"""
__Model__

A single elliptical Sersic. Its `sersic_index` is free, so the fit itself decides whether this
galaxy is a de Vaucouleurs-like spheroid (n ~ 4) or an exponential disk (n ~ 1) rather than
you asserting it, and `effective_radius` is the radius containing half the profile's light.
The profile is elliptical via `ell_comps` rather than an axis-ratio and position-angle pair,
which avoids the periodic-boundary pathology a position angle creates for a non-linear search
(`PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py`).

We use `ag.lp_linear` rather than `ag.lp`: a linear light profile has its `intensity` solved
analytically by a linear inversion inside each likelihood evaluation instead of being sampled
as a free parameter. The profile is identical; one dimension simply leaves the search's
parameter space, which improves speed, accuracy and reliability at no cost. Every workspace
modeling example uses them by default
(`PyAutoGalaxy:autogalaxy/profiles/light/linear/sersic.py`).

`af.Model` wraps the class so its parameters become free; `af.Collection` groups models into
the named tree the analysis expects — the `galaxies` collection is a convention the analysis
relies on, not a stylistic choice (`PyAutoFit:autofit/mapper/prior_model/collection.py`).
"""
bulge = af.Model(ag.lp_linear.Sersic)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

"""
__Check__

`model.info` prints every free parameter with its prior, and it is the cheapest sanity check
available: a model subtly larger, smaller or more constrained than intended shows up here
rather than after hours of searching. Evaluating the likelihood once at the prior medians is
the second cheap check — it proves the model, dataset and analysis are mutually compatible
and that a finite likelihood comes back, without paying for inference.

`ag.AnalysisImaging` holds the dataset and defines the `log_likelihood_function` the search
calls. `use_jax=True` is the default and is what makes the gradient-based searches possible
at all; pass `use_jax=False` when debugging, because NumPy tracebacks are far easier to read
than JAX ones (`PyAutoGalaxy:autogalaxy/imaging/model/analysis.py`).
"""
print(model.info)
print(f"Total free parameters = {model.total_free_parameters}")

analysis = ag.AnalysisImaging(dataset=dataset, use_jax=True)

log_likelihood = analysis.log_likelihood_function(
    instance=model.instance_from_prior_medians()
)

print(f"log likelihood at prior medians: {float(log_likelihood):.2f}")
```

That composes to **N = 6** free parameters: centre (2), `ell_comps` (2), `effective_radius`,
`sersic_index` — with `intensity` solved rather than sampled. Six parameters is a parameter
space any search handles comfortably.

What each profile represents and when to reach for which is
[`../wiki/core/concepts/light_profiles.md`](../wiki/core/concepts/light_profiles.md); the
`ell_comps` convention has its own section there. The catalogue of every available profile,
by module, is
[`../wiki/core/api/light_profile_catalog.md`](../wiki/core/api/light_profile_catalog.md).

## Branch — bulge plus disk

The decomposition galaxy morphology usually wants, because the ratio of the two components'
inferred luminosities is the bulge-to-total light ratio. Adapted from
`autogalaxy_workspace:scripts/imaging/modeling.py`.

```python
bulge = af.Model(ag.lp_linear.Sersic)
disk = af.Model(ag.lp_linear.Exponential)

bulge.centre = disk.centre

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

print(model.info)
```

N = 9. The physics is in the asymmetry between the two components: the bulge's
`sersic_index` is free so it can find a concentrated spheroid, while the `Exponential` disk
has n fixed at 1 by construction. That contrast is what makes the decomposition identifiable
at all — two free Sersics on the same galaxy are largely degenerate, and the fit will happily
trade light between them.

`bulge.centre = disk.centre` is the load-bearing line. It asserts the two components are
concentric, which is physically reasonable for most galaxies and removes two parameters
rather than fitting the same centre twice. Drop it only if you have a specific reason to
believe the components are offset — a lopsided or interacting system — and expect a harder
search when you do.

The attribute names are entirely yours. `bulge`, `disk`, `bar`, `clump`, `bulge_0` — whatever
you pass to `af.Model(ag.Galaxy, ...)` is the key you address afterwards
(`model.galaxies.galaxy.bulge.sersic_index`), because `ag.Galaxy` takes `redshift` and then
arbitrary keyword arguments (`PyAutoGalaxy:autogalaxy/galaxy/galaxy.py`). Name them for what
they measure.

There is a concise form when you do not need to touch the components first — passing a
profile *class* rather than an `af.Model` promotes it automatically
(`autogalaxy_workspace:scripts/guides/modeling/cookbook.py`):

```python
galaxy = af.Model(
    ag.Galaxy,
    redshift=0.5,
    bulge=ag.lp_linear.Sersic,
    disk=ag.lp_linear.Exponential,
    bar=ag.lp_linear.Sersic,
)
```

How several profiles and galaxies compose into what is actually fitted is
[`../wiki/core/concepts/galaxies.md`](../wiki/core/concepts/galaxies.md).

## Branch — a Multi-Gaussian Expansion, for morphology a Sersic cannot fit

When the galaxy is irregular, asymmetric or has structure a smooth profile leaves in the
residuals, decompose its light into tens of Gaussians instead. Because they are *linear*
profiles, all of their intensities are solved by the inversion, so a 20-Gaussian basis costs
the search almost nothing in dimensionality — it is far more flexible than a Sersic at a
*lower* parameter count.

The composition is long and technical, so the library ships a helper:

```python
bulge = ag.model_util.mge_model_from(
    mask_radius=MASK_RADIUS,
    total_gaussians=20,
    centre_prior_is_uniform=True,
)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

print(model.info)
```

Adapted from `autogalaxy_workspace:scripts/imaging/start_here.py`, where the MGE is the
*recommended default* model — it balances speed, flexibility and accuracy well enough to fit
the vast majority of galaxies. N = 4: a shared centre and shared `ell_comps` across the
basis, with every `sigma` fixed on a logarithmic ladder from below the pixel scale to beyond
the galaxy's extent, and every intensity solved. `mask_radius` is what sets the outer end of
that ladder, so pass the radius you actually masked at.

Other arguments worth knowing: `centre_fixed=(y, x)` pins the centre entirely (used for
contaminating neighbours, below), `gaussian_per_basis` splits the ladder into several bases
with independent ellipticities for a twisting galaxy, and `use_spherical=True` drops the
ellipticity. The physics of why fewer free parameters wins here is
[`../wiki/core/concepts/linear_light_profiles_and_mge.md`](../wiki/core/concepts/linear_light_profiles_and_mge.md);
the orthonormal-basis alternative is
[`../wiki/core/concepts/shapelets.md`](../wiki/core/concepts/shapelets.md). Both get their own
skill in a later phase (`ag_basis_profiles`).

## Branch — priors, pairing, fixing, assertions

Every parameter has a default prior from the configuration YAMLs
([`../wiki/core/api/configuration.md`](../wiki/core/api/configuration.md)). Override one when
you know something the default cannot. Adapted from
`autogalaxy_workspace:scripts/guides/modeling/cookbook.py`.

```python
bulge = af.Model(ag.lp_linear.Sersic)

bulge.centre.centre_0 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)
bulge.centre.centre_1 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)
bulge.sersic_index = af.TruncatedGaussianPrior(
    mean=4.0, sigma=1.0, lower_limit=0.8, upper_limit=5.0
)
```

The centre priors say "this galaxy is within 0.1" of the image centre", which is true if the
data was cut out around it and is worth asserting because it removes a large volume of
parameter space the search would otherwise wander through. The `sersic_index` prior says
"this is an early-type" — and that is a genuine statistical commitment, not a convenience:
it changes the posterior and therefore the errors you quote. If you want to *guide* a search
without moving what you infer, the start-point API in
[`ag_configure_search`](./ag_configure_search.md) is the right tool instead.

Three other levers reduce complexity without adding a prior:

```python
bulge = af.Model(ag.lp_linear.Sersic)
disk = af.Model(ag.lp_linear.Exponential)

bulge.centre = disk.centre  # pair: one centre, not two (N -= 2)
bulge.sersic_index = 4.0  # fix: a de Vaucouleurs bulge (N -= 1)
bulge.effective_radius = disk.effective_radius - 0.5  # offset: a relation, not a parameter

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)
model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

model.add_assertion(
    model.galaxies.galaxy.bulge.effective_radius
    < model.galaxies.galaxy.disk.effective_radius
)
```

Assertions are added **after** the components are collected, and they are the cleanest way to
rule out the unphysical solution a decomposition is prone to: a "bulge" that is larger than
its disk, which is the search relabelling the two components rather than fitting them. A
model can also be round-tripped through JSON with `model.dict()` and
`af.Model.from_json(file=...)`, which is how you hand a model to a collaborator or edit one
by hand.

## Branch — nuisance parameters of the data, not the galaxy

Some free parameters belong to the dataset: a residual background sky, a sub-pixel
astrometric offset, a small rotation. These live in `ag.DatasetModel` and sit alongside
`galaxies` rather than inside it. Adapted from
`autogalaxy_workspace:scripts/imaging/features/sky_background/modeling.py`.

```python
dataset_model = af.Model(ag.DatasetModel)
dataset_model.background_sky_level = af.UniformPrior(lower_limit=0.0, upper_limit=5.0)

model = af.Collection(
    galaxies=af.Collection(galaxy=galaxy), dataset_model=dataset_model
)
```

You **must** set the sky prior by hand — unlike a light profile's priors, the right range
depends entirely on your data's units and depth, so no default can be correct. This costs one
parameter and matters for exactly the measurement galaxy structure cares most about: the
faint outer envelope that sets `effective_radius` and `sersic_index`. It is worth including
even on data you believe is sky-subtracted, precisely to check that belief. The other fields
are `grid_offset=(y, x)` and `grid_rotation_angle`, which earn their keep in multi-band work
where bands are not perfectly registered. Concept page:
[`../wiki/core/concepts/sky_background_and_operated_profiles.md`](../wiki/core/concepts/sky_background_and_operated_profiles.md).

## Branch — modelling contaminating extra galaxies

When a neighbour's light genuinely overlaps the target's, neither masking nor noise scaling
can separate them without removing signal you need — so model it. The convention is that its
centre is **fixed** to a value measured from the data, leaving its other parameters free.
Adapted from `autogalaxy_workspace:scripts/imaging/features/extra_galaxies/modeling.py`.

```python
extra_galaxies_centres = ag.from_json(
    file_path=DATASET_PATH / "extra_galaxies_centres.json"
)

extra_galaxies_list = []

for extra_galaxy_centre in extra_galaxies_centres:

    extra_galaxy = af.Model(
        ag.Galaxy, redshift=0.5, bulge=ag.lp_linear.SersicSph
    )
    extra_galaxy.bulge.centre = extra_galaxy_centre

    extra_galaxies_list.append(extra_galaxy)

model = af.Collection(
    galaxies=af.Collection(galaxy=galaxy),
    extra_galaxies=af.Collection(extra_galaxies_list),
)
```

The centres come from the JSON written during data preparation. A spherical `SersicSph` costs
about two free parameters per neighbour once its intensity is solved — cheap enough that a
handful of companions is affordable. For irregular or asymmetric companions, swap the
spherical Sersic for an MGE with a pinned centre,
`ag.model_util.mge_model_from(mask_radius=MASK_RADIUS, total_gaussians=10,
centre_fixed=tuple(extra_galaxy_centre))`, which costs the same in the linear limit while
being far more flexible. Note that `extra_galaxies` is its own top-level collection, not a
member of `galaxies`. When to model versus mask versus scale is
[`../wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../wiki/core/concepts/extra_galaxies_and_noise_scaling.md).

## Wrap with an analysis, and check it before you search

```python
analysis = ag.AnalysisImaging(dataset=dataset, use_jax=True)
```

Source: `PyAutoGalaxy:autogalaxy/imaging/model/analysis.py`. The full surface is
`AnalysisImaging(dataset, adapt_images=None, cosmology=None, settings=None,
title_prefix=None, use_jax=True)`. Pass `cosmology=ag.cosmo.Planck15()` when a derived
quantity needs angular-to-physical conversion; `settings=ag.Settings(...)` only to override
an inversion or linear-solver default; `adapt_images` only for an adaptive pixelised
reconstruction.

Two checks before you hand this to a search, both cheap and both catching a different class
of mistake:

```python
print(model.info)

analysis.print_vram_use(model=model, batch_size=search.batch_size)
```

`model.info` catches a *model* mistake — a parameter you thought was fixed, a prior wider
than intended, a component you added twice. `print_vram_use` catches a *resource* mistake:
JAX must hold the whole batched likelihood in GPU memory, and this reports the estimate in
20-30 seconds rather than letting you discover the limit as an out-of-memory error mid-compile
(`autogalaxy_workspace:scripts/imaging/modeling.py` quotes ~0.027 GB for an MGE on a
low-resolution dataset, and more than 1 GB — occasionally more than 10 GB — for a pixelised
reconstruction at high resolution). Add the single likelihood evaluation from the first branch
when you have changed anything structural; a finite number back means the three pieces fit
together.

## Combine — where this hands off

- **Pick and configure the search** → [`ag_configure_search`](./ag_configure_search.md).
  `MultiStartProdigy` for a fast check that this model and dataset are sensible, `Nautilus`
  when you need errors you can quote.
- **Run the fit** → the run-search skill (`ag_run_search`), which owns
  `search.fit(model=model, analysis=analysis)` and the output folder.
- **The search fails, stalls or returns something unphysical** → the fit-debugging skill
  (`ag_debug_fit_failure`). Nine times in ten the fix is here rather than in the search: a
  model too complex for the data, an unpaired centre, a missing assertion, or a contaminant
  that should have been handled during preparation.
- **A smooth profile leaves structure in the residuals** → the basis-profile and pixelisation
  skills (`ag_basis_profiles`, `ag_pixelization`) in a later phase; the MGE branch above is
  the first step in that direction and often enough on its own.
- **Several datasets of the same galaxy** → the multi-dataset skill (`ag_multi_dataset`).
  Datasets are combined through a factor graph — one `af.AnalysisFactor` per dataset, folded
  into an `af.FactorGraphModel`; see
  [`../wiki/core/concepts/multi_wavelength.md`](../wiki/core/concepts/multi_wavelength.md).

Offer (default-yes) a dated `wiki/project/YYYY-MM-DD-<slug>.md` entry: the components you
chose, the parameters you fixed or paired, and *why*, are the modelling assumptions a referee
will ask about.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Realism and complexity](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_2_modeling/tutorial_3_realism_and_complexity.ipynb):
  the trade-off at the heart of this skill — what happens when a model is too simple for the
  data, and what happens when it is too complex for the search.
- **General reference** — [RTD: Model cookbook](https://pyautogalaxy.readthedocs.io/en/latest/general/model_cookbook.html):
  the systematic reference for `af.Model` and `af.Collection` — multiple components, multiple
  galaxies, prior customisation, pairing, and many-profile bases.
- **Experienced PyAutoGalaxy user** — [workspace: imaging/modeling.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/imaging/modeling.py):
  the canonical bulge-plus-disk fit end to end, including the VRAM check, run-time estimation
  and the annotated output-folder layout.

## Agent procedural checklist

1. On real data, confirm the inspection gate was satisfied; if not, return to
   `ag_prepare_imaging_data`.
2. Ask: one galaxy or several; single Sersic or a decomposition; smooth or irregular.
3. Prefer `ag.lp_linear` over `ag.lp` — the intensity is solved, not sampled.
4. Start with a single Sersic even when the goal is a decomposition; keep it as the reference.
5. Pair concentric centres, fix what physics fixes, and add assertions that rule out the
   relabelling solution.
6. `print(model.info)` and check `total_free_parameters` against what you intended.
7. Build `ag.AnalysisImaging`, run one likelihood evaluation, and `print_vram_use` before a
   GPU run.
8. Save the script to `scripts/`, hand off to `ag_configure_search`, and offer the
   `wiki/project/` entry recording the modelling assumptions.
