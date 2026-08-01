---
name: ag_ellipse_fitting
description: Measure a galaxy's morphology non-parametrically by fitting isophotes — `ag.Ellipse` fitted to the data through `ag.FitEllipse` and `ag.AnalysisEllipse`, one ellipse at a time at fixed `major_axis`, producing radial profiles of axis ratio and position angle instead of a light-profile model. Covers how the likelihood differs (data interpolated onto the ellipse, residual = flux minus its own mean, no PSF and no model image), why Dynesty rather than Nautilus and why `use_jax=False` is required, the fit-the-centre-then-step-outwards workflow with the centre pinned from the first fit, `ag.EllipseMultipole` for m=1 lopsidedness / m=3 tripole / m=4 boxy-versus-discy deviations, combining every ellipse with `af.Drawer`, `aplt.subplot_fit_ellipse`, and reading many fits back with `ag.agg.EllipsesAgg` / `MultipolesAgg` / `FitEllipseAgg`. Use when the science is the isophote shape itself, or when no parametric model fits and you need a model-independent measurement. Not for light-profile modelling (`ag_build_imaging_model`, `ag_basis_profiles`), not for pixelized reconstruction (`ag_pixelization`), and note there is no `start_here.py` in the workspace's `ellipse/` package — `modeling.py` is the entry point.
---

# Measuring isophotes with ellipse fitting

Every other fitting skill in this workspace builds a model image and subtracts it from the data.
Ellipse fitting does not. It puts an ellipse on the sky, samples the data around it, and asks a
much simpler question: **are these flux values all the same?** An isophote is by definition a
contour of constant surface brightness, so an ellipse that traces one will find the same flux all
the way round. One that does not is either the wrong shape, the wrong orientation, or centred in
the wrong place.

Fit a ladder of ellipses at increasing `major_axis` and what comes out is not a model but a set of
*profiles*: axis ratio against radius, position angle against radius, and — with multipoles — the
deviation from an ellipse against radius. Those are the classical measurements of galaxy
structure. An isophotal **twist** (position angle rotating with radius) indicates a triaxial
system or a bar; ellipticity rising outwards distinguishes a disk emerging from a bulge; and the
m=4 multipole amplitude is the boxy/discy parameter that separates the two families of
early-type galaxies. None of these are things a Sersic profile can tell you, because a Sersic
asserts a single axis ratio and a single position angle at every radius by construction.

The trade against a parametric fit is explicit. You gain a model-independent measurement, with no
functional form to be wrong about and nothing to deconvolve. You lose a total luminosity, a
size that extrapolates beyond the data, and any ability to decompose the light into components.
The two are complements: run an ellipse fit to *see* the structure, then use what you learn to
choose the parametric model — a measured twist, for instance, is the direct argument for a
two-basis MGE ([`ag_basis_profiles`](./ag_basis_profiles.md)).

The concept page is
[`../wiki/core/concepts/ellipse_fitting_and_multipoles.md`](../wiki/core/concepts/ellipse_fitting_and_multipoles.md);
the API surface is [`../wiki/core/api/ellipse.md`](../wiki/core/api/ellipse.md). The grounding
scripts are `autogalaxy_workspace:scripts/ellipse/fit.py` (the likelihood, worked by hand),
`autogalaxy_workspace:scripts/ellipse/modeling.py` (the search-based workflow — **this is the
entry point; the `ellipse/` package has no `start_here.py`**),
`autogalaxy_workspace:scripts/ellipse/multipoles.py` and
`autogalaxy_workspace:scripts/ellipse/database.py`.

## How the likelihood differs — read this before fitting anything

Three properties of ellipse fitting surprise people, and all three follow from there being no
model image.

**No PSF.** The dataset is loaded without one. Nothing is convolved, so nothing needs
deconvolving — you are measuring the observed isophotes, seeing included. That is a real
limitation for structure near the resolution limit and a real simplification everywhere else.

**The residual is flux minus its own mean.** There is no model to subtract, so "residual" means
each interpolated flux value minus the mean of all the values on that ellipse. A good fit is one
where they agree; the goodness-of-fit measures scatter around the ellipse, not agreement with a
prediction.

**No noise-normalisation term.** The usual log-likelihood carries a term from the noise map's
determinant. Here it is omitted, because interpolating the noise map onto the ellipse makes that
term numerically unstable. The consequence: **ellipse log-likelihoods are not comparable to
light-profile log-likelihoods**, and not comparable between ellipses of different `major_axis`
(different numbers of sampled points). Use them to compare shapes at one radius, not across radii.

Worth doing once, by hand, because the objects then make sense:

```python
"""
Ellipse Fitting: The Likelihood By Hand
=======================================

Reproduce `ag.FitEllipse`'s likelihood arithmetic explicitly, to make concrete what "the data
interpolated onto an ellipse" means and why the residual is defined against the mean rather than
against a model.

__Contents__

- **Imports:** Import the required libraries.
- **Dataset:** Load imaging without a PSF and mask it.
- **Interpolation:** Sample the data and noise map onto the ellipse's coordinates.
- **Likelihood:** Build the residual, chi-squared and log likelihood, and check against FitEllipse.
"""

"""
__Imports__
"""
from pathlib import Path

import numpy as np

import autofit as af
import autogalaxy as ag
import autogalaxy.plot as aplt

DATASET_PATH = Path("dataset") / "imaging" / "my_galaxy"
PIXEL_SCALES = 0.1
MASK_RADIUS = 5.0

"""
__Dataset__

No `psf_path`: ellipse fitting never convolves, so the PSF is not loaded
(`PyAutoArray:autoarray/dataset/imaging/dataset.py`). The mask radius does double duty here — it
excludes the noisy edges *and* sets how far out the ellipses can reach, so it is the single most
consequential number in the script. Keep it in a variable.
"""
dataset = ag.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    pixel_scales=PIXEL_SCALES,
)

mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=MASK_RADIUS,
)
dataset = dataset.apply_mask(mask=mask)

"""
__Interpolation__

`ag.DatasetInterp` holds the interpolation weights and mappings once, so sampling many ellipses
is cheap (`PyAutoGalaxy:autogalaxy/ellipse/dataset_interp.py`). You do not normally construct it
yourself — `ag.FitEllipse` does it internally — but seeing it makes the mechanism obvious.

`points_from_major_axis_from` returns (y, x) coordinates equally spaced along the ellipse, and it
needs `pixel_scale` because the *number* of points is chosen to match the number of data pixels
the ellipse crosses. A bigger ellipse therefore gets more points automatically, which is why the
likelihood is not comparable between radii.
"""
interp = ag.DatasetInterp(dataset=dataset)

ellipse = ag.Ellipse(centre=(0.0, 0.0), ell_comps=(0.0, 0.0), major_axis=1.0)

points = ellipse.points_from_major_axis_from(pixel_scale=dataset.pixel_scales[0])

data_interp = interp.data_interp(points)
noise_map_interp = interp.noise_map_interp(points)

print(f"{len(points)} points sampled around a {ellipse.major_axis}\" ellipse")

"""
__Likelihood__

The model data *is* the interpolated data — there is nothing else. The residual is each value
minus the mean of them all, which is the formal statement of "does this ellipse trace a contour
of constant brightness". Chi-squared and normalised residuals then follow the usual definitions
with the interpolated noise, and the log likelihood is -0.5 * chi-squared with no
noise-normalisation term (`PyAutoGalaxy:autogalaxy/ellipse/fit_ellipse.py`).
"""
model_data = data_interp
residual_map = data_interp - np.mean(data_interp)
normalized_residual_map = residual_map / noise_map_interp
chi_squared_map = (residual_map / noise_map_interp) ** 2.0

log_likelihood = -0.5 * np.sum(chi_squared_map)

print(f"log likelihood by hand      = {float(log_likelihood):.4f}")

fit = ag.FitEllipse(dataset=dataset, ellipse=ellipse)

print(f"FitEllipse.log_likelihood   = {float(fit.log_likelihood):.4f}")
print(f"ratio to chi_squared        = {float(fit.log_likelihood / fit.chi_squared):.4f}")
```

The two agree exactly. Note the factor: `log_likelihood` is **−0.5 × `chi_squared`**, verified
against the released library — the workspace's own prose in `ellipse/fit.py` and `ellipse/plot.py`
says −2.0, which is wrong by a factor of four. It does not change any inference (a constant
multiple of the log likelihood rescales but does not move the maximum), but it does change any
number you quote, so use −0.5.

`ag.FitEllipse(dataset, ellipse, multipole_list=None, use_jax=False)` exposes all of it as
attributes — `data_interp`, `noise_map_interp`, `model_data`, `residual_map`,
`normalized_residual_map`, `chi_squared_map`, `chi_squared`, `log_likelihood` — so in practice you
construct the fit and read what you need.

## `ag.Ellipse`, and one API trap

`ag.Ellipse(centre=(0.0, 0.0), ell_comps=(0.0, 0.0), major_axis=1.0)` — three arguments, and the
ellipticity uses `ell_comps` rather than an axis-ratio/angle pair for the same reason every
profile does: a position angle is periodic, and a periodic parameter creates a boundary
pathology a non-linear search handles badly.

You will want the axis ratio and position angle back out, and here is the trap: **`axis_ratio` and
`angle` are methods, not properties.** `minor_axis` is a property. Verified on the released stack:

```python
ellipse = ag.Ellipse(
    centre=(0.0, 0.0),
    ell_comps=ag.convert.ell_comps_from(axis_ratio=0.5, angle=45.0),
    major_axis=1.0,
)

print(ellipse.minor_axis)      # property  -> 0.5
print(ellipse.axis_ratio())    # CALL it   -> 0.5
print(ellipse.angle())         # CALL it   -> 45.0
```

Forgetting the parentheses does not raise — it prints `<bound method ...>`, so a results table
built without them is silently full of method reprs rather than numbers. The workspace's
`ellipse/modeling.py` result section makes exactly this mistake in its own `print` statements;
`ag.convert.ell_comps_from(axis_ratio=..., angle=...)` is the inverse, for constructing an ellipse
from the values you would rather think in.

## Ask

- *"What are you measuring — a twist, an ellipticity profile, or boxiness?"* All three come from
  the same ladder of fits, but boxiness needs multipoles, and that changes the model.
- *"How far out do you need to go?"* This sets the mask radius, which sets the ellipse ladder.
  Going further than the data supports produces ellipses fitting noise, which show up as wild
  swings in axis ratio at large radius.
- *"Is the centre known?"* The workflow below fits it once at small radius and then pins it. If
  the galaxy is lopsided you may want it free at every radius — but expect a much noisier profile,
  and consider an m=1 multipole instead, which is the physical way to say "lopsided".
- *"Are there contaminants inside the mask?"* An ellipse crossing a neighbour will average its
  flux in and be pulled off the isophote. Mask them
  ([`ag_light_model_extras`](./ag_light_model_extras.md)); `ellipse/modeling.py` repeats its whole
  ladder with an extra-galaxies mask applied for exactly this reason.

## Branch — the search: Dynesty, and no JAX

Two settings that differ from every other fitting skill here, and both are deliberate.

```python
"""
__Search__

Dynesty rather than Nautilus. Extensive testing has shown Dynesty with `sample="rwalk"` gives the
most accurate and efficient results for ellipse fitting specifically — a small, low-dimensional
parameter space with a likelihood surface unlike a light-profile fit's
(`PyAutoFit:autofit/non_linear/search/nest/dynesty/`). `n_live=50` is ample for N=4; the default
of 200 is more than these models need.

`iterations_per_quick_update=10000` is high because these fits are fast: writing results and
visualisation to disk would otherwise dominate the run time.
"""
search = af.DynestyStatic(
    path_prefix=Path("ellipse"),
    name="fit_start",
    unique_tag="my_galaxy",
    sample="rwalk",
    n_live=50,
    iterations_per_quick_update=10000,
)

"""
__Analysis__

`use_jax=False` is **required**: ellipse fitting does not support JAX acceleration. The default is
`True`, so this argument is not optional — omitting it is a real error, not a performance choice
(`PyAutoGalaxy:autogalaxy/ellipse/model/analysis.py`).
"""
analysis = ag.AnalysisEllipse(dataset=dataset, use_jax=False)
```

The cost is low. A likelihood evaluation is ~0.04 s on a typical dataset, rising to 0.5–1.0 s at
high resolution — so an ellipse ladder is a laptop-scale job, not an HPC one, which is part of why
it is such a good first look at a galaxy. Search selection generally is
[`ag_configure_search`](./ag_configure_search.md) and
[`../wiki/core/api/searches.md`](../wiki/core/api/searches.md).

## Branch — fit the centre, then step outwards

This is the workflow. It is two stages because the centre is a global property of the galaxy while
the shape is a function of radius, and fitting them together at every radius wastes parameters and
produces a noisier profile.

**Stage one: one small ellipse, centre free.**

```python
"""
__Model — the centre ellipse__

A single ellipse at a small fixed `major_axis`, with its centre and ellipticity free: N=4. The
`major_axis` is *fixed*, not fitted — the whole method works by choosing a radius and asking what
shape best traces the isophote there, so a free size would have nothing to constrain it.

The model uses a list even for one ellipse, because that is the shape the analysis expects and it
generalises to many (`PyAutoFit:autofit/mapper/prior_model/collection.py`).

Priors: the centre within 0.1" of the image centre, which is true if the data was cut out around
the galaxy; `ell_comps` over [-0.6, 0.6], which spans essentially every realistic ellipticity.
"""
ellipse = af.Model(ag.Ellipse)

ellipse.centre.centre_0 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)
ellipse.centre.centre_1 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)

ellipse.ell_comps.ell_comps_0 = af.UniformPrior(lower_limit=-0.6, upper_limit=0.6)
ellipse.ell_comps.ell_comps_1 = af.UniformPrior(lower_limit=-0.6, upper_limit=0.6)

ellipse.major_axis = 0.3

model = af.Collection(ellipses=[ellipse])

print(model.info)

result = search.fit(model=model, analysis=analysis)

centre = result.instance.ellipses[0].centre
print(f"centre = ({centre[0]:.4f}, {centre[1]:.4f})")
```

If the galaxy is not near (0.0", 0.0") the defaults will fight you. Either re-cut the data around
it ([`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md)) or widen those centre priors.

**Stage two: a ladder, centre pinned.**

```python
"""
__Multiple Ellipses__

Ten ellipses from 0.3" out to 90% of the mask radius, each with the centre *fixed* to the value
from stage one and its own `ell_comps` free. That drops each model from N=4 to N=2, and it is what
makes the resulting profiles clean: the axis ratio and position angle at each radius are then
measured independently of any centring uncertainty.

Each radius is a separate `search.fit` with its own `name`, so each gets its own output folder and
resumes independently — a ladder that dies halfway restarts where it stopped.

Stopping at 0.9 * mask_radius rather than at the mask edge keeps every ellipse fully inside the
unmasked region; an ellipse that runs off the mask samples nothing there and returns a shape
driven by which part of it survived.
"""
import numpy as np

number_of_ellipses = 10
major_axis_list = np.linspace(0.3, MASK_RADIUS * 0.9, number_of_ellipses)

result_list = []

for i, major_axis in enumerate(major_axis_list):

    ellipse = af.Model(ag.Ellipse)

    ellipse.centre.centre_0 = centre[0]
    ellipse.centre.centre_1 = centre[1]

    ellipse.ell_comps.ell_comps_0 = af.UniformPrior(lower_limit=-0.6, upper_limit=0.6)
    ellipse.ell_comps.ell_comps_1 = af.UniformPrior(lower_limit=-0.6, upper_limit=0.6)

    ellipse.major_axis = major_axis

    model = af.Collection(ellipses=[ellipse])

    search = af.DynestyStatic(
        path_prefix=Path("ellipse"),
        name=f"fit_{i}",
        unique_tag="my_galaxy",
        sample="rwalk",
        n_live=50,
        number_of_cores=4,
        iterations_per_quick_update=10000,
    )

    result_list.append(search.fit(model=model, analysis=analysis))

"""
__Profiles__

The radial profiles are the result. Remember the parentheses on `axis_ratio()` and `angle()`.
"""
for result in result_list:
    e = result.instance.ellipses[0]
    print(f"a = {e.major_axis:.2f}\"   q = {e.axis_ratio():.3f}   PA = {e.angle():.1f} deg")
```

Read the PA column down the page: monotonic drift is an isophotal twist, and a jump of ~90° is
usually the major and minor axes swapping when the isophote is nearly round — not a physical
twist. Read the q column: rising outwards is a disk emerging from a bulge.

**Stage three: one combined fit, for the record.** Every ellipse in a single model, evaluated once,
so the whole ladder lives in one output folder and one aggregator entry:

```python
"""
__Final Fit__

`af.Drawer` with `total_draws=1` does not search — it evaluates the model once and writes it out.
The ellipses are the *instances* from the ladder, so nothing is re-fitted; this exists to produce
one combined result and one combined visualisation
(`PyAutoFit:autofit/non_linear/search/mle/drawer/search.py`).

`model.dummy_0` is required: a model with no free parameters at all cannot be constructed, so one
unused parameter is added to satisfy that. It carries no meaning — do not report it.
"""
ellipses = [result.instance.ellipses[0] for result in result_list]

model = af.Collection(ellipses=ellipses)
model.dummy_0 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)

search = af.Drawer(
    path_prefix=Path("ellipse"),
    name="fit_all",
    unique_tag="my_galaxy",
    total_draws=1,
)

result = search.fit(model=model, analysis=analysis)
```

The whole three-stage workflow is `autogalaxy_workspace:scripts/ellipse/modeling.py`.

## Branch — multipoles: the deviation from an ellipse

An ellipse cannot be boxy, discy, lopsided or three-fold symmetric. Real galaxies are all four.
`ag.EllipseMultipole` perturbs the ellipse's radius with an angular harmonic of order `m` and two
amplitude components, and the physics is entirely in `m`:

| `m` | Perturbation | What it measures |
|---|---|---|
| 1 | monopole displacement | **lopsidedness** — an asymmetry between opposite sides, from a recent interaction or a warp |
| 3 | tripole | **three-fold** asymmetry, a genuine departure from point symmetry |
| 4 | quadrupole | **boxy versus discy** — the classical parameter separating the two early-type families |

The m=4 amplitude is the one with the deepest literature behind it: boxy ellipticals are typically
more luminous, slow-rotating and radio-loud, discy ones the reverse, so its sign carries real
physical information about formation history. m=2 is absent from this list because an m=2
perturbation *is* an ellipse — it is already in `ell_comps`.

Directly, on a concrete fit:

```python
"""
__Multipoles__

Each `EllipseMultipole` takes an order `m` and two `multipole_comps`, and any number of them can
perturb one ellipse at once — the white contour on a plot stops being an ellipse and becomes the
perturbed shape (`PyAutoGalaxy:autogalaxy/ellipse/ellipse/ellipse_multipole.py`).
"""
multipole_order_1 = ag.EllipseMultipole(m=1, multipole_comps=(0.05, 0.05))
multipole_order_3 = ag.EllipseMultipole(m=3, multipole_comps=(0.05, 0.05))
multipole_order_4 = ag.EllipseMultipole(m=4, multipole_comps=(0.05, 0.05))

fit = ag.FitEllipse(
    dataset=dataset,
    ellipse=ellipse_instance,
    multipole_list=[multipole_order_1, multipole_order_3, multipole_order_4],
)
```

As model components, multipoles are a **separate top-level collection** from the ellipses, nested
one level deeper — `multipoles=[[multipole_3, multipole_4]]`, a list per ellipse of the multipoles
perturbing it:

```python
"""
__Model — ellipse plus multipoles__

Two multipoles on one ellipse: N=6 (the ellipse's 2 free `ell_comps` with the centre pinned, plus
2 components each for m=3 and m=4). `m` itself is *fixed* — it is the harmonic order, not
something to infer.

`GaussianPrior(mean=0.0, sigma=0.1)` centred on zero is the right prior: zero is "a perfect
ellipse", so the prior expresses "probably close to elliptical, but let the data say otherwise",
and a posterior clearly displaced from zero is then a detection.
"""
multipole_3 = af.Model(ag.EllipseMultipole)
multipole_3.m = 3
multipole_3.multipole_comps.multipole_comps_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
multipole_3.multipole_comps.multipole_comps_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

multipole_4 = af.Model(ag.EllipseMultipole)
multipole_4.m = 4
multipole_4.multipole_comps.multipole_comps_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
multipole_4.multipole_comps.multipole_comps_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

model = af.Collection(ellipses=[ellipse], multipoles=[[multipole_3, multipole_4]])

print(model.info)

result = search.fit(model=model, analysis=analysis)

print(result.instance.multipoles[0][0].multipole_comps)  # m=3
print(result.instance.multipoles[0][1].multipole_comps)  # m=4
```

Adapted from `autogalaxy_workspace:scripts/ellipse/multipoles.py`. Note the index shape:
`instance.multipoles[<ellipse index>][<multipole index>]`.

Two judgement calls. The workspace's ladder shares **one** set of multipole amplitudes across all
ellipses — two free parameters per order for the whole galaxy rather than per radius — which is a
common assumption and keeps the model tractable. There is literature showing multipoles vary
radially, and fitting them per radius is a straightforward extension of the ladder loop; it costs
two parameters per order per radius and needs the signal to support it. And multipoles increase
parameter-space degeneracy noticeably: the amplitudes trade against `ell_comps`, so expect wider
errors and check the corner plot rather than the point estimate. On data with no real multipole
signal the amplitudes go to values close to zero, which is the control worth running first.

## Branch — plotting and reading many fits back

Ellipse fitting has its own subplot, because its quantities are 1D arrays around a contour rather
than 2D images:

```python
"""
__Plot__

`aplt.subplot_fit_ellipse` takes a *list* of fits and plots the data with every ellipse's contour
overlaid, alongside the 1D residuals as a function of position angle — the second panel is the
diagnostic, because a good fit is flat there and a bad one shows a clear sinusoid whose period
tells you which harmonic is missing (`PyAutoGalaxy:autogalaxy/ellipse/plot/`).

It takes `output_path` / `output_format` but **not** `output_filename`, so give each figure its own
directory ([`../wiki/core/api/plotting.md`](../wiki/core/api/plotting.md) tabulates the split).
"""
PLOT_DIR = Path("scripts/scratch/my_galaxy/ellipse/")

fit_list = [
    ag.FitEllipse(dataset=dataset, ellipse=result.instance.ellipses[0])
    for result in result_list
]

aplt.subplot_fit_ellipse(
    fit_list=fit_list, output_path=str(PLOT_DIR), output_format="png"
)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

A two-period sinusoid in the residual panel means the ellipticity is wrong; a four-period one
means you need an m=4 multipole. That is the fastest read on whether multipoles are worth adding.
`aplt.plot_array(array=dataset.data, ...)` for the data alone, and during a fit the
`VisualizerEllipse` attached to `ag.AnalysisEllipse` writes these figures to the output folder
automatically — controlled by the `fit_ellipse` entry in `config/visualize/plots.yaml`, so you can
switch figures on and off without touching code
(`autogalaxy_workspace:scripts/ellipse/plot.py`).

A ladder produces ten-plus separate fits, and reading them back one folder at a time is
unpleasant. The aggregator has dedicated objects, and there are three because the model has three
kinds of component. From `autogalaxy_workspace:scripts/ellipse/database.py`:

```python
"""
__Aggregator__

`add_directory` scrapes an output tree into a queryable SQLite database. `EllipsesAgg` then yields
the maximum-likelihood ellipses of every fit in it via generators, so a ladder of any length stays
memory-light (`PyAutoGalaxy:autogalaxy/aggregator/ellipse/`).

Each generator yields a *list* — one entry per analysis in the fit — so the `[0]` below takes the
single analysis. Multipoles live in their own aggregator because they are their own model
component; `FitEllipseAgg` rebuilds whole `FitEllipse` objects and picks up any multipoles
automatically.
"""
DATABASE = Path("output") / "ellipse.sqlite"
if DATABASE.exists():
    DATABASE.unlink()

agg = af.Aggregator.from_database(filename=DATABASE.name, completed_only=False)
agg.add_directory(directory=Path("output") / "ellipse")

ellipses_agg = ag.agg.EllipsesAgg(aggregator=agg)

for ellipses_lists_list in ellipses_agg.max_log_likelihood_gen_from():
    for e in ellipses_lists_list[0]:
        print(f"a = {e.major_axis:.2f}\"  q = {e.axis_ratio():.3f}  PA = {e.angle():.1f}")

multipoles_agg = ag.agg.MultipolesAgg(aggregator=agg)

for multipoles_lists_list in multipoles_agg.max_log_likelihood_gen_from():
    for multipole_list in multipoles_lists_list[0]:
        print([m.m for m in multipole_list])
```

`ag.agg.FitEllipseAgg` additionally offers `randomly_drawn_via_pdf_gen_from(total_samples=...)`,
which draws fits from the posterior rather than taking the maximum — that is how you put error
bars on a shape profile rather than quoting point estimates, and it is the right way to answer
"is this twist significant?". Aggregator patterns generally are
[`ag_load_results`](./ag_load_results.md) and
[`../wiki/core/api/aggregator.md`](../wiki/core/api/aggregator.md).

## Combine — where this hands off

- **Prepare the data and settle the mask** → [`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md).
  The mask radius bounds the ellipse ladder, so it matters more here than anywhere.
- **Mask contaminating neighbours first** → [`ag_light_model_extras`](./ag_light_model_extras.md).
  An ellipse crossing a companion averages its flux in and is pulled off the isophote; the
  workspace's `modeling.py` re-runs its whole ladder with such a mask applied.
- **Turn a measured twist into a parametric model** → [`ag_basis_profiles`](./ag_basis_profiles.md).
  An MGE with `gaussian_per_basis=2` is the parametric model that *can* represent what the ellipse
  fit measured, and this is the cleanest reason to run both.
- **Turn a measured decomposition into components** →
  [`ag_build_imaging_model`](./ag_build_imaging_model.md). An ellipticity profile rising outwards
  is the argument for a bulge-plus-disk fit, and the ellipse fit gives you the priors.
- **Configure the search** → [`ag_configure_search`](./ag_configure_search.md), remembering that
  the choices here (Dynesty, `sample="rwalk"`, `use_jax=False`) are ellipse-specific.
- **Run and watch the output folder** → [`ag_run_search`](./ag_run_search.md).
- **Read many fits back** → [`ag_load_results`](./ag_load_results.md).
- **A fit returns a wild axis ratio, or the PA jumps by 90°** →
  [`ag_debug_fit_failure`](./ag_debug_fit_failure.md). The ellipse-specific causes are an ellipse
  running off the mask, a contaminant crossed by the contour, a nearly-round isophote making the
  axes ambiguous, and `use_jax` left at its `True` default.
- **Irregular structure no contour can trace** → [`ag_pixelization`](./ag_pixelization.md).
  Ellipse fitting assumes the isophotes *are* closed contours around one centre; clumpy star
  formation breaks that assumption outright.

Offer (default-yes) a dated `wiki/project/YYYY-MM-DD-<slug>.md` entry recording the mask radius,
the `major_axis` ladder, the fitted centre, whether multipoles were included and at which orders,
and the q and PA profiles. Those profiles *are* the measurement, and unlike a parametric fit there
is no single `model.results` file that holds them.

## Further reading

- **General reference** — [RTD: Features overview](https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_3_features.html):
  ellipse fitting in the context of the other capabilities beyond a single smooth profile, with
  links onward.
- **Experienced PyAutoGalaxy user** — [workspace: ellipse/modeling.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/ellipse/modeling.py):
  the full three-stage workflow — centre fit, ladder, combined `Drawer` fit — and the repeat with
  an extra-galaxies mask. This is the `ellipse/` package's entry point; there is no `start_here.py`
  there. [multipoles.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/ellipse/multipoles.py)
  is the multipole extension.

(No HowToGalaxy chapter covers ellipse fitting — the lecture series teaches light-profile
modelling. For a newcomer, the concept page
[`../wiki/core/concepts/ellipse_fitting_and_multipoles.md`](../wiki/core/concepts/ellipse_fitting_and_multipoles.md)
is the place to start instead.)

## Agent procedural checklist

1. Set the mask radius consciously and keep it in a variable — it bounds the ellipse ladder, and
   ellipses are stopped at `0.9 * mask_radius`.
2. Load the dataset **without** a PSF; ellipse fitting never convolves.
3. Use `af.DynestyStatic(sample="rwalk", n_live=50)` and `ag.AnalysisEllipse(..., use_jax=False)` —
   `use_jax` defaults to `True` and must be overridden.
4. Fix `major_axis` on every ellipse; it is the radius you chose, never a fitted parameter.
5. Fit one small ellipse with the centre free, then pin that centre for the whole ladder (N=4 → 2).
6. Call `axis_ratio()` and `angle()` with parentheses — they are methods, and forgetting them
   silently yields method reprs in your table.
7. Report the log likelihood as −0.5 × chi-squared, and never compare ellipse likelihoods across
   radii or against a light-profile fit.
8. Add multipoles only with zero-centred Gaussian priors; fix `m`; index results as
   `instance.multipoles[ellipse][multipole]`.
9. Read the 1D residual panel of `aplt.subplot_fit_ellipse` for period structure before adding a
   harmonic; quote the plot's absolute path and offer to open it.
10. Combine the ladder with `af.Drawer(total_draws=1)` plus a `dummy_0` parameter, read profiles
    back with `ag.agg.EllipsesAgg` / `MultipolesAgg`, and offer the `wiki/project/` entry holding
    the q and PA profiles.
