---
name: ag_multi_galaxy_and_cluster
description: Model several galaxies whose light blends on the sky — an interacting or projected pair, a compact multiple, or a cluster field with a brightest cluster galaxy plus tens-to-hundreds of catalogued members. Covers the regime ladder and how to place a system on it, the list-based composition that gives every co-dominant galaxy its own free light model, why an MGE suits a blend, the catalogue-driven member tier loaded with `ag.galaxy_table_from_csv` whose intensities are tied to one shared free normalization so population size costs no dimensions, promoting bright members out of the tier, and per-galaxy decomposed photometry from `subplot_fit_imaging_of_galaxy`. Use when two or more galaxies are co-equal subjects of the fit. Not for one target with faint contaminating neighbours (`ag_light_model_extras`), not for several datasets of one galaxy (`ag_multi_dataset`), and not for a single galaxy (`ag_build_imaging_model`).
---

# Blended pairs and cluster fields

Every galaxy-light model has to answer one question before anything else: how many galaxies in
this image are *subjects* of the fit, rather than things to be removed from it? PyAutoGalaxy
organises the answer as a ladder of three regimes, and choosing the wrong rung is the most
expensive mistake available in this part of the library.

- **One galaxy.** It dominates the frame; anything else is a contaminant to mask out or model
  with a restricted, centre-fixed profile. This is [`ag_build_imaging_model`](./ag_build_imaging_model.md)
  and `ag_light_model_extras`.
- **Several blended galaxies.** Two or more of comparable brightness whose light overlaps —
  an interacting pair, a close projected pair, a compact multiple. Each gets its own **free**
  light model and they are fitted together, because where their light overlaps you cannot measure
  one without the other. `autogalaxy_workspace:scripts/multi_galaxy/start_here.py`.
- **A cluster field.** A brightest cluster galaxy (BCG) plus tens to hundreds of member galaxies.
  Giving each member a free model is neither possible nor desirable, so the population is driven
  by a **catalogue** and the model's dimensionality stops growing with it.
  `autogalaxy_workspace:scripts/cluster/start_here.py`.

**The subject throughout is galaxy light.** The cluster workflow here models the surface
brightness of the BCG and its member population — that is its entire purpose. Nothing on this
ladder infers a mass distribution from the positions of background objects, and no member is
represented as an unresolved point of emission: every galaxy on every rung is a surface-brightness
profile evaluated on a real-space grid, exactly as a single galaxy is.

Why it is worth doing: the assembly of BCG and intracluster light; member luminosity functions
measured from photometry that is *not* contaminated by the BCG's envelope; per-galaxy fluxes for
an interacting pair whose isophotes overlap; and a clean light model for any downstream analysis
that needs the galaxies' emission subtracted before it can see anything fainter.

Read [`../wiki/core/concepts/galaxies.md`](../wiki/core/concepts/galaxies.md) for how several
galaxies compose into what gets fitted, and
[`../wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../wiki/core/concepts/extra_galaxies_and_noise_scaling.md)
for the boundary between a co-equal galaxy and a contaminant.

## Ask

- *"How many galaxies, and are they comparably bright?"* Comparable brightness and overlapping
  light means the blended-pair rung. One dominant galaxy with faint companions means the
  single-galaxy rung with extra galaxies — a different and much cheaper model.
- *"Do you have a catalogue?"* A photometry catalogue of centres and luminosities is what makes
  the cluster rung tractable. Without one, a field of many galaxies has no tier to pin the faint
  members and you are back to promoting each one by hand.
- *"Do you have the centres?"* Every rung above the first needs them, and they are what breaks
  the labelling degeneracy between components in a blend.
- *"What is the deliverable — total photometry per galaxy, structural parameters for each, or a
  member-subtracted BCG?"* The answer decides how much freedom each galaxy needs, and whether a
  shared shape across a member tier is acceptable.

On real data the inspection gate in [`../AGENTS.md`](../AGENTS.md) is doing more work here than
usual: the *number of subjects* and the mask extent are both decided from looking at the image,
and the mask must enclose every galaxy the model contains, not just the brightest.
[`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md) owns that procedure.

## Branch — a blended pair or multiple

The deliverable is one script. Adapted from
`autogalaxy_workspace:scripts/multi_galaxy/start_here.py` and
`autogalaxy_workspace:scripts/multi_galaxy/modeling.py`.

```python
"""
Galaxy Structure: A Blended Pair
===============================

Decompose the overlapping light of two galaxies of comparable brightness: mask the whole system,
give each galaxy its own free Multi-Gaussian Expansion initialized on its observed centre, fit
both simultaneously, and read each galaxy's flux out of the decomposition uncontaminated by its
neighbour.

__Contents__

- **Imports:** JAX environment first, then the standard trio.
- **Dataset:** Load the imaging.
- **Galaxy Centres:** Read the centres that initialize each galaxy's priors.
- **Mask:** One mask enclosing every galaxy, over-sampled at each centre.
- **Model:** One free MGE per galaxy, composed in a loop.
- **Search:** Configure the search.
- **Model-Fit:** Fit both galaxies together and announce the output folder.
- **Result:** Per-galaxy decomposition and photometry.
"""
from autogalaxy import jax_wrapper  # Sets the JAX environment before other imports

from pathlib import Path

import autofit as af
import autogalaxy as ag
import autogalaxy.plot as aplt

"""
__Dataset__
"""
DATASET_PATH = Path("dataset") / "imaging" / "<your_pair>"

dataset = ag.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    psf_path=DATASET_PATH / "psf.fits",
    pixel_scales=0.1,
)

"""
__Galaxy Centres__

The centres are read from a small JSON file of `(y, x)` arcsecond pairs, one per galaxy
(`ag.from_json`, `PyAutoNerves:autonerves/dictable.py`). They are not free data — they are what
initializes each galaxy's centre prior, and in a blend that is load-bearing: two identical
components with identical broad priors are exchangeable, and the search will happily put both on
the brighter galaxy. Anchoring each on its observed position breaks that degeneracy.
"""
galaxy_centres = ag.from_json(file_path=DATASET_PATH / "galaxy_centres.json")

"""
__Mask__

One mask enclosing **every** galaxy. The fit's job is to decompose the blend, so a mask drawn
around one galaxy would remove exactly the overlap region the decomposition depends on.
Over-sample at each galaxy's centre, not just at the origin.
"""
MASK_RADIUS = 3.0

mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=MASK_RADIUS,
)

dataset = dataset.apply_mask(mask=mask)

over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[4, 2, 2],
    radial_list=[0.3, 0.6],
    centre_list=list(galaxy_centres),
)

dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

"""
__Model__

One galaxy per centre, each with its own free Multi-Gaussian Expansion, built in a loop and
keyed `galaxy_0`, `galaxy_1`, … The composition scales to any number of blended galaxies without
changing shape (`ag.model_util.mge_model_from`,
`PyAutoGalaxy:autogalaxy/analysis/model_util.py`).

An MGE is the right basis for a blend for two reasons. Its Gaussians share the galaxy's centre
and ellipticity, so each galaxy contributes only a handful of non-linear parameters despite being
flexible enough for an irregular or interacting morphology — and in a blend the two galaxies'
parameters are partially degenerate wherever their light overlaps, so keeping the count down
matters more than usual. And its Gaussians are *linear* light profiles: their intensities are
solved exactly by linear inversion at every likelihood evaluation, so the flux ratio between the
two galaxies — the single most degenerate quantity in a blend — is solved rather than explored
stochastically ([`../wiki/core/concepts/linear_light_profiles_and_mge.md`](../wiki/core/concepts/linear_light_profiles_and_mge.md)).
"""
galaxy_dict = {}

for i, centre in enumerate(galaxy_centres):
    bulge = ag.model_util.mge_model_from(
        mask_radius=MASK_RADIUS,
        total_gaussians=20,
        centre_prior_is_uniform=True,
        centre=(centre[0], centre[1]),
    )

    galaxy_dict[f"galaxy_{i}"] = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)

model = af.Collection(galaxies=af.Collection(**galaxy_dict))

print(model.info)

"""
__Search__

`Nautilus` for a posterior you can quote. The folder's `start_here.py` uses
`af.MultiStartProdigy` instead — a multi-start gradient optimizer that launches many independent
descents in parallel and returns the best. That population of starts matters here specifically:
several co-dominant galaxies make the parameter space strongly multi-modal, and a single starting
point lands in a local maximum often enough to be untrustworthy
(`PyAutoFit:autofit/non_linear/search/nest/nautilus/search.py`).
"""
search = af.Nautilus(
    path_prefix=Path("multi_galaxy"),
    name="pair",
    unique_tag="<your_pair>",
    n_live=150,
    n_batch=50,
    iterations_per_quick_update=1000,
)

analysis = ag.AnalysisImaging(dataset=dataset, use_jax=True)

"""
__Model-Fit__
"""
print(f"Output folder: {search.paths.output_path.resolve()}")

result = search.fit(model=model, analysis=analysis)

"""
__Result__

`subplot_fit_imaging_of_galaxy` is the deliverable of a blended fit: for each galaxy it shows
that galaxy's modeled light and the data with the *other* galaxies subtracted. Each call writes
`of_galaxy_<index>.png` into `output_path`, so give each galaxy its own directory.

With the blend decomposed, per-galaxy photometry is direct — each galaxy's model image contains
only its own light, so summing it gives a flux uncontaminated by its neighbour.
"""
print(result.info)

PLOT_DIR = Path("scripts") / "scratch" / "<your_pair>"

aplt.subplot_fit_imaging(
    fit=result.max_log_likelihood_fit,
    output_path=str(PLOT_DIR / "fit"),
    output_format="png",
)

for i in range(len(galaxy_centres)):
    aplt.subplot_fit_imaging_of_galaxy(
        fit=result.max_log_likelihood_fit,
        galaxy_index=i,
        output_path=str(PLOT_DIR / f"galaxy_{i}"),
        output_format="png",
    )

for i, galaxy in enumerate(result.max_log_likelihood_galaxies):
    image = galaxy.image_2d_from(grid=dataset.grids.lp)
    print(f"galaxy_{i}: total model flux = {float(image.array.sum()):.3f}")

print(f"Saved to: {PLOT_DIR.resolve()}")
```

Everything else about the fit is unchanged from the single-galaxy case: the same
`ag.AnalysisImaging`, the same searches, the same output folder. Only the model composition moved.
Every imaging feature applies per galaxy unchanged too — linear profiles, MGE variants, a sky
background, shapelets.

## Branch — a cluster field

The cluster rung changes *how the model is composed*, and the change is the interesting part.

The BCG (and any other dominant galaxy) is modelled individually, exactly as a single galaxy
would be. The member population is driven by a catalogue: a CSV of `y, x, luminosity`, one row
per member, whose photometry pins the faint members so that only a **shared normalization** is
free. Adding a member is a row append that adds **zero** free parameters.

```python
scaling_table = ag.galaxy_table_from_csv(
    file_path=DATASET_PATH / "scaling_galaxies.csv"
)

member_centres = scaling_table.centres.in_list
member_luminosities = scaling_table.luminosities

bcg_centres = ag.from_json(file_path=DATASET_PATH / "bcg_centres.json")
```

`ag.galaxy_table_from_csv` (`PyAutoGalaxy:autogalaxy/galaxy/galaxy_table.py`) returns a
`GalaxyTable` whose `.centres` is a `Grid2DIrregular` — hence `.in_list` to get plain tuples —
and whose `.luminosities` are the catalogue values in whatever consistent units your photometry
uses. Only their *ratios* matter, because the absolute scale is absorbed by the single fitted
normalization, so magnitudes converted to relative fluxes work as well as calibrated ones.

The mask has to be generous — the members span the frame — and every galaxy inside it must be in
the model, or its light lands in the residuals and biases the BCG's outer isophotes:

```python
MASK_RADIUS = 11.0

mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=MASK_RADIUS,
)

dataset = dataset.apply_mask(mask=mask)

over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[4, 2, 2],
    radial_list=[0.3, 0.6],
    centre_list=list(bcg_centres) + list(member_centres),
)

dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)
```

Then the two-tier composition, from `autogalaxy_workspace:scripts/cluster/start_here.py`:

```python
# Tier 1 — the BCG, a free MGE like any single galaxy.

bulge = ag.model_util.mge_model_from(
    mask_radius=3.0,
    total_gaussians=20,
    centre_prior_is_uniform=True,
    centre=(bcg_centres[0][0], bcg_centres[0][1]),
)

galaxy_dict = {"bcg": af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)}

# Tier 2 — the catalogue members, sharing ONE free normalization.

intensity_scale = af.UniformPrior(lower_limit=0.0, upper_limit=10.0)

for i, (centre, luminosity) in enumerate(zip(member_centres, member_luminosities)):
    bulge = af.Model(ag.lp.SersicSph)
    bulge.centre = tuple(centre)                            # fixed to the catalogue
    bulge.intensity = intensity_scale * float(luminosity)    # tied to the catalogue
    bulge.effective_radius = 0.6                             # fixed shape
    bulge.sersic_index = 3.0

    galaxy_dict[f"member_{i}"] = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)

model = af.Collection(galaxies=af.Collection(**galaxy_dict))

print(model.info)
```

The mechanism is one line: `bulge.intensity = intensity_scale * float(luminosity)`. Multiplying a
prior by a number builds a derived prior
(`PyAutoFit:autofit/mapper/prior/arithmetic/arithmetic.py`), so `intensity_scale` is the sampled
parameter and every member's intensity is determined by it —
`intensity_i = intensity_scale × luminosity_i`. The whole tier therefore costs exactly **one**
free parameter, whether it holds six members or two hundred. `print(model.info)` shows each
member's intensity as tied rather than as a prior, which is how you confirm you built a tier and
not a hundred independent galaxies.

The scaling relation is the scientific assumption: it says the members' surface brightnesses
follow their catalogue luminosities up to one common factor. That is a statement about the member
population being a reasonably homogeneous family, and it is the reason the model is tractable at
all. Recovering `intensity_scale ≈ 1` when the catalogue luminosities *are* the true intensities
is the sanity check the workspace's simulated example is built around
(`autogalaxy_workspace:scripts/cluster/modeling.py` `__Result + Truth Comparison__`).

### Refining the tier

`autogalaxy_workspace:scripts/cluster/modeling.py` shows the two natural refinements, in
increasing cost.

**Promote the shape to shared parameters.** Rather than fixing `effective_radius` and
`sersic_index`, let the whole tier share two free ones. The tier then costs three parameters
instead of one — still independent of population size:

```python
intensity_scale = af.UniformPrior(lower_limit=0.0, upper_limit=10.0)
tier_effective_radius = af.UniformPrior(lower_limit=0.1, upper_limit=2.0)
tier_sersic_index = af.UniformPrior(lower_limit=0.5, upper_limit=5.0)

for i in range(len(member_centres)):
    bulge = af.Model(ag.lp.SersicSph)
    bulge.centre = tuple(member_centres[i])
    bulge.intensity = intensity_scale * float(member_luminosities[i])
    bulge.effective_radius = tier_effective_radius
    bulge.sersic_index = tier_sersic_index

    galaxy_dict[f"member_{i}"] = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)
```

**Promote individual members out of the tier.** Give the brightest members their own free models.
This costs their full per-galaxy parameter count each, so promote sparingly — brightest first,
and only while the data still constrains them:

```python
N_PROMOTE = 2

for i in range(N_PROMOTE):
    bulge = af.Model(ag.lp.SersicSph)
    bulge.centre = tuple(member_centres[i])
    bulge.intensity = af.UniformPrior(lower_limit=0.0, upper_limit=2.0)
    bulge.effective_radius = af.UniformPrior(lower_limit=0.1, upper_limit=3.0)
    bulge.sersic_index = af.UniformPrior(lower_limit=0.5, upper_limit=5.0)

    galaxy_dict[f"member_{i}"] = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)

# ... remaining rows go into the shared tier as above, starting from N_PROMOTE.
```

The workspace's shipped CSV happens to be sorted brightest-first, so rows 0 and 1 are the two
brightest. Your own catalogue almost certainly is not — sort by luminosity, or select rows
explicitly, rather than assuming.

The BCG's decomposed light is what the whole exercise is for:

```python
aplt.subplot_fit_imaging_of_galaxy(
    fit=result.max_log_likelihood_fit,
    galaxy_index=0,
    output_path="scripts/scratch/<your_cluster>/bcg/",
    output_format="png",
)
```

Galaxy index 0 is the BCG because it was inserted into `galaxy_dict` first; the ordering is the
insertion order of that dictionary, so keep it deliberate.

## Branch — blended galaxies *and* faint contaminants together

The two tiers are not exclusive, and a real field usually needs both. A blended pair often sits in
a frame with fainter companions that are not subjects of the fit but do overlap the mask:

- **Co-equal galaxies** go under `galaxies=af.Collection(galaxy_0=..., galaxy_1=...)` with full
  free light models.
- **Contaminants** go under `extra_galaxies=af.Collection(...)` with a restricted light model
  whose **centre is fixed**, or are removed from the likelihood by noise scaling.

```python
extra_galaxies_centres = ag.Grid2DIrregular(
    ag.from_json(file_path=DATASET_PATH / "extra_galaxies_centres.json")
)

extra_galaxies_list = []

for extra_galaxy_centre in extra_galaxies_centres:
    extra_galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=ag.lp_linear.SersicSph)
    extra_galaxy.bulge.centre = extra_galaxy_centre
    extra_galaxies_list.append(extra_galaxy)

model = af.Collection(
    galaxies=af.Collection(**galaxy_dict),
    extra_galaxies=af.Collection(extra_galaxies_list),
)
```

`autogalaxy_workspace:scripts/multi_galaxy/features/extra_galaxies/modeling.py`. Fixing the
centres matters *more* in a blended field than in a single-galaxy one, and the script says why: a
free-centre contaminant can wander, and here there is more than one bright thing for it to wander
onto. It may drift toward one of the co-equal galaxies and start absorbing light that the
decomposition is supposed to be measuring — quietly corrupting the one result the fit exists to
produce.

Noise scaling is the alternative lever: `dataset.apply_noise_scaling(mask=mask_extra_galaxies)`
with a `mask_extra_galaxies.fits` inflates the noise over the contaminated pixels so they stop
constraining anything. The trade-off between modelling, masking and scaling is
[`../wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../wiki/core/concepts/extra_galaxies_and_noise_scaling.md),
and the single-galaxy procedure with the centre-marking GUI is `ag_light_model_extras`.

Note the ordering consequence: `extra_galaxies` are appended after `galaxies`, so with two
co-equal galaxies and two contaminants the `galaxy_index` values are 0 and 1 for the pair and 2
and 3 for the extras.

## Branch — the failure modes, and how to see them

Three things go wrong on these rungs, and none of them raises an exception.

**Component swapping.** Two galaxies with identical models and broad centre priors are
exchangeable, so a search can put both on one galaxy and leave the other unmodelled — or swap
them between runs so results are not comparable. The fix is the one already in the recipe: anchor
each galaxy's centre prior on its observed position. If it still happens, tighten those priors.

**A galaxy inside the mask that is not in the model.** Its light has nowhere to go but the
residuals, and the nearest modelled galaxy absorbs what it can — biasing that galaxy's outer
profile and hence its effective radius and total flux. Check the residual map for a coherent
positive blob at a position you did not model.

**A tier that is really a wrong assumption.** If the member population is not a homogeneous
family, one shared normalization cannot fit it, and the symptom is systematic residuals that
correlate with member luminosity — bright members under-subtracted and faint ones over-subtracted,
or vice versa. That is the signal to promote the shape to shared free parameters, or to promote
the brightest members individually.

All three are read off residual maps rather than parameter values, which makes
[`ag_plot_fit`](./ag_plot_fit.md) the tool and
[`ag_debug_fit_failure`](./ag_debug_fit_failure.md) the taxonomy.

## Branch — cost, and proving it before you pay

Model dimensionality is the thing to watch, and it is why the two rungs are composed differently:
each promoted galaxy costs its full parameter count, while the catalogue tier costs one (or three)
regardless of size. Count before you fit — `print(model.info)` and the `prior_count` — and be
suspicious of any total beyond a few tens of parameters.

Smoke test first, always:

```bash
PYAUTO_TEST_MODE=2 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/cluster_fit.py
```

Level 2 evaluates the likelihood exactly once, which proves the catalogue loaded, the tying
worked, and every galaxy is on the grid. Level 1 if you want the fit products written. The levels
are [`../wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md). Never quote a
structural parameter or an `intensity_scale` from a test-mode run — the sampler was truncated and
the numbers are prior medians.

On a GPU, `analysis.print_vram_use(model=model, batch_size=search.batch_size)` before a long run.
A large member tier adds many fixed-shape profiles which JIT-compile into the same batched
likelihood, so population size moves the cost far less than the number of *free* parameters does.

## Combine

- [`ag_build_imaging_model`](./ag_build_imaging_model.md) — get one galaxy fitting well first. A
  blended fit will not rescue a model that fails on an isolated galaxy.
- `ag_light_model_extras` — the contaminant tier in full, including the centre-marking GUI and the
  noise-scaling route.
- `ag_basis_profiles` — the MGE that every rung here leans on, and the shapelet alternative.
- `ag_pixelization` — when one of the blended galaxies is genuinely irregular and no basis fits.
- [`ag_chain_searches`](./ag_chain_searches.md) — fit the brightest galaxy first, fix it, then add
  the rest. Often the most reliable route through a crowded field.
- [`ag_multi_dataset`](./ag_multi_dataset.md) — the same composition across several bands, where
  each galaxy's colour becomes measurable.
- [`ag_load_results`](./ag_load_results.md) — per-galaxy parameters with errors, and the
  aggregator for many fields.
- [`ag_simulate_dataset`](./ag_simulate_dataset.md) — build a blend with known truth and fit it,
  which is the only way to know whether your decomposition is recoverable at your signal-to-noise
  ratio.

When the fit is worth keeping, offer (default-yes) to record it in a dated
`wiki/project/YYYY-MM-DD-<slug>.md` entry: which rung you placed the system on and why, the
catalogue used and what was tied to it, what was promoted, and the output path — per
[`_style.md`](./_style.md) property #5. The rung choice and the promotion decisions are the
scientific content of the fit.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Multi-galaxy fits](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_4_scaling_up_galaxies/tutorial_2_multi_galaxy.ipynb):
  fitting two galaxies in one image from first principles, including why chaining searches is
  often easier than fitting both at once.
- **General reference** — [RTD: New user guide](https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_2_new_user_guide.html):
  the decision tree that routes by scale of system — single galaxy, blended pair, cluster field —
  which is this skill's ladder in the upstream docs' own words.
- **Experienced PyAutoGalaxy user** — [workspace: cluster/start_here.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/cluster/start_here.py):
  the two-tier catalogue composition this skill mirrors; its sibling
  [multi_galaxy/start_here.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/multi_galaxy/start_here.py)
  is the blended-pair version.

## Agent procedural checklist

1. Place the system on the ladder explicitly, and say which rung and why, before composing
   anything.
2. On real data, confirm the inspection gate has been satisfied — including that the mask
   encloses every galaxy the model will contain.
3. Get the centres (and, for a cluster, the catalogue) before writing the model; do not invent
   positions.
4. Compose in a loop keyed `galaxy_0`, `galaxy_1`, … for co-equal galaxies; use the two-tier
   BCG-plus-catalogue form for a cluster.
5. Anchor every co-equal galaxy's centre prior on its observed position.
6. Over-sample at every galaxy's centre, not just the origin.
7. `print(model.info)` and confirm the tier is tied rather than free, and the total dimensionality
   is what you intended.
8. Validate with `PYAUTO_TEST_MODE=2`; on a GPU also run `analysis.print_vram_use`.
9. Announce the output path at launch; plot `subplot_fit_imaging_of_galaxy` per galaxy into its
   own directory and quote the path.
10. Check the residual map for an unmodelled galaxy and for luminosity-correlated tier residuals
    before believing any parameter.
11. Offer the `wiki/project/` entry recording the rung and the promotion decisions.
