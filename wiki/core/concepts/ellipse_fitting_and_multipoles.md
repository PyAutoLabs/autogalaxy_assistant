---
title: Ellipse fitting and multipoles
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/ellipse/
      - autogalaxy/ellipse/fit_ellipse.py
      - autogalaxy/ellipse/dataset_interp.py
      - autogalaxy/ellipse/ellipse/
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/ellipse/fit.py
      - scripts/ellipse/modeling.py
      - scripts/ellipse/multipoles.py
      - scripts/ellipse/simulator.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 5ea82fa6f573d030694f5807f465344814471abba95e1a8545bb8fd79795a856
---

# Ellipse fitting and multipoles

Ellipse fitting is the **non-parametric** route to galaxy structure. Instead of assuming a
functional form for the surface brightness and inferring its parameters, you fit a sequence
of ellipses of increasing size to the image and read off how the ellipticity, position angle
and higher harmonics *change with radius*. It is the classical isophotal analysis of galaxy
morphology, and it answers a different question from a parametric fit.

Sources: `PyAutoGalaxy:autogalaxy/ellipse/`. Worked examples:
`autogalaxy_workspace:scripts/ellipse/fit.py` (how the likelihood works),
`.../modeling.py` (the search) and `.../multipoles.py` (harmonics). The API catalogue is
[`../api/ellipse`](../api/ellipse.md).

## What is being fitted

The idea is easiest to see from the likelihood, which is unusual and worth understanding
before you use it.

For a candidate ellipse, the data and noise-map values are **interpolated onto points spaced
along the ellipse** (`ag.DatasetInterp` holds the interpolation weights;
`ellipse.points_from_major_axis_from(pixel_scale=...)` chooses the number of points so that
it matches the number of image pixels the ellipse crosses — a bigger ellipse gets more
points). Then:

```
model_data = data interpolated onto the ellipse
residual_map = model_data - mean(model_data)
chi_squared_map = (residual_map / noise_map_interp) ** 2
log_likelihood = -2.0 * sum(chi_squared_map)
```

`autogalaxy_workspace:scripts/ellipse/fit.py`. Read that middle line carefully: the residual
is each interpolated value minus **the mean of the values on that ellipse**. There is no
model image and nothing is subtracted from the data. The quantity being minimised is the
*scatter of surface brightness around the ellipse* — so the best-fitting ellipse is the one
that traces a contour of constant brightness. That is exactly the definition of an isophote,
expressed as a likelihood.

Two consequences follow:

- **The PSF is not used.** Ellipse fitting does not forward-model the instrument, so
  `ag.Imaging.from_fits` is called without a `psf_path` in these examples. The measured
  isophotes are therefore the *observed* ones, seeing-broadened; interpreting them as
  intrinsic requires care, particularly at radii comparable to the PSF.
- **The likelihood omits the noise-normalisation term** that light-profile fitting includes.
  The term varies numerically with the interpolation, making it unstable, so it is dropped.
  Ellipse-fit likelihood values are consequently **not** comparable to light-profile fit
  likelihoods, and there is no Bayesian evidence to compare models with.

## An ellipse

```python
import autogalaxy as ag

ellipse = ag.Ellipse(centre=(0.0, 0.0), ell_comps=(0.0, 0.0), major_axis=1.0)

fit = ag.FitEllipse(dataset=dataset, ellipse=ellipse)
print(fit.log_likelihood)
```

Three parameters: `centre`, `ell_comps` and `major_axis`. The `ell_comps` convention is the
same as for light profiles and for the same reason (see
[`light_profiles`](./light_profiles.md)); human-readable equivalents are available as
`ellipse.axis_ratio`, `ellipse.angle`, `ellipse.minor_axis` and `ellipse.ellipticity`.

Diagnostics mirror light-profile fitting: `fit.data_interp`, `fit.noise_map_interp`,
`fit.model_data`, `fit.residual_map`, `fit.normalized_residual_map`, `fit.chi_squared_map`,
`fit.chi_squared`, `fit.log_likelihood`.

```python
import autogalaxy.plot as aplt

aplt.subplot_fit_ellipse(fit_list=[fit])
```

`subplot_fit_ellipse` takes a **list**, because the natural product of ellipse fitting is a
family of ellipses; it overlays the contours on the data and shows the 1D residuals as a
function of position angle. A good fit is one whose residuals are flat in angle — a
systematic sinusoid means the ellipse is misaligned or the isophote is not an ellipse at all
(which is where multipoles come in).

## Fitting a family of ellipses

Because each ellipse is fitted independently, the workflow is a loop, not one big model. The
workspace pattern is:

1. **Fit one small ellipse to determine the centre.** A single ellipse at `major_axis = 0.3`
   with a free `centre` and `ell_comps` — N = 4.
2. **Fix the centre and step outwards.** For each `major_axis` in a linear sequence up to
   ~90% of the mask radius, fit `ell_comps` alone (N = 2), with the centre taken from step 1.
3. **Combine.** Collect the maximum-likelihood ellipses into one final `af.Collection` and
   evaluate it once.

```python
import numpy as np
import autofit as af
import autogalaxy as ag

ellipse = af.Model(ag.Ellipse)

ellipse.centre.centre_0 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)
ellipse.centre.centre_1 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)
ellipse.ell_comps.ell_comps_0 = af.UniformPrior(lower_limit=-0.6, upper_limit=0.6)
ellipse.ell_comps.ell_comps_1 = af.UniformPrior(lower_limit=-0.6, upper_limit=0.6)
ellipse.major_axis = 0.3

model = af.Collection(ellipses=[ellipse])

search = af.DynestyStatic(
    path_prefix=Path("ellipse"),
    name="fit_start",
    unique_tag=dataset_name,
    sample="rwalk",
    n_live=50,
    iterations_per_quick_update=10000,
)

analysis = ag.AnalysisEllipse(dataset=dataset, use_jax=False)

result = search.fit(model=model, analysis=analysis)
```

`autogalaxy_workspace:scripts/ellipse/modeling.py`. Three deliberate choices:

- **The model key is `ellipses`, a list** — not `galaxies`. There are no galaxies and no
  light profiles in an ellipse model.
- **`major_axis` is fixed** at each step. It is the independent variable of the whole
  analysis: you are measuring shape *as a function of* radius, so letting it float would be
  measuring nothing.
- **`DynestyStatic` with `sample="rwalk"`, not `Nautilus`.** Extensive testing found random-walk
  Dynesty the most accurate and efficient search for this particular likelihood; `n_live=50`
  is ample for a 2–4 parameter model, and the likelihood is fast (~0.04 s).

**`use_jax=False` is required.** Ellipse fitting is not JAX-traceable — the interpolation is
not expressible in the traced pipeline — so it runs on NumPy. It is one of the few parts of
the library where the JAX default does not apply, and consequently it does not benefit from
GPU acceleration or the gradient-based searches.

The combining step uses `af.Drawer(total_draws=1)`, which simply evaluates the assembled
model once rather than searching. It needs a dummy free parameter
(`model.dummy_0 = af.UniformPrior(...)`) because a model with zero free parameters is not a
valid search input.

## Multipoles

A pure ellipse cannot describe an isophote that is **boxy**, **discy**, or lopsided — and
real galaxies routinely are. `ag.EllipseMultipole` perturbs the ellipse with an angular
Fourier harmonic of order `m`:

```python
multipole_order_4 = ag.EllipseMultipole(m=4, multipole_comps=(0.05, 0.05))

fit = ag.FitEllipse(
    dataset=dataset, ellipse=ellipse, multipole_list=[multipole_order_4]
)
```

`autogalaxy_workspace:scripts/ellipse/multipoles.py`. The physics of the orders:

- **`m = 1`** — a lopsided, one-sided distortion. Diagnostic of a recent interaction or of
  the disc being off-centre from the halo.
- **`m = 3`** — a three-fold distortion; asymmetric and again interaction-related.
- **`m = 4`** — the quadrupole: the classic **boxy / discy** deviation of an elliptical
  galaxy's isophotes, which correlates with formation history, rotation and kinematic class.
  This is the one measured most often.

They combine freely — pass a list — and each contributes two components
(`multipole_comps`), an amplitude and a phase in the ellipse's frame.

In a model fit the standard assumption is that the harmonic **amplitudes are shared across
all ellipses**, so each order costs N = 2 in total rather than 2 per radius:

```python
multipole_3 = af.Model(ag.EllipseMultipole)
multipole_3.m = 3
multipole_3.multipole_comps.multipole_comps_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
multipole_3.multipole_comps.multipole_comps_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

multipole_4 = af.Model(ag.EllipseMultipole)
multipole_4.m = 4
multipole_4.multipole_comps.multipole_comps_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
multipole_4.multipole_comps.multipole_comps_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

model = af.Collection(ellipses=[ellipse], multipoles=[[multipole_3, multipole_4]])
```

Note the nesting: `multipoles` is a list *per ellipse*, each entry itself a list of harmonics.
The `GaussianPrior(mean=0.0, sigma=0.1)` encodes the expectation that a galaxy is close to
elliptical and lets the data pull the amplitude away from zero if warranted — on data with no
real harmonic content the posterior returns to ~0, which is the correct behaviour and a
useful null test.

`autogalaxy_workspace:scripts/ellipse/multipoles.py` flags the caveat that shared amplitudes
are an *assumption*: there is published evidence that multipole strength varies radially. If
that variation is your science, fit per-radius amplitudes and accept the dimensionality.

Adding harmonics barely changes the likelihood evaluation time — perturbing an ellipse is
cheap — but it enlarges and correlates the parameter space, which is where the extra run time
goes.

## When to use ellipse fitting instead of a parametric fit

Reach for ellipse fitting when:

- You want **radial profiles of shape**: ellipticity, position angle and boxiness versus
  radius. An isophotal twist or a radially varying flattening is a *direct measurement* here,
  whereas a parametric fit only reveals it as a residual.
- You want a **model-independent** result. No functional form is assumed, so the answer does
  not inherit the biases of a Sersic.
- You need to compare with the large literature of isophotal analyses, which is expressed in
  exactly these quantities.

Reach for a parametric or basis fit instead when:

- You need **Sersic index, effective radius, total flux or a bulge-to-total ratio**. Ellipse
  fitting does not produce them.
- The **PSF matters** — compact galaxies, small radii, or any comparison of intrinsic sizes.
  Ellipse fitting does not deconvolve.
- You need a **model image to subtract**, or a Bayesian evidence to compare models.
- The galaxy is too **irregular** for isophotes to be meaningful at all: a merger, or a
  clumpy system with no monotonic brightness contours. Then reconstruct the light instead
  ([`inversions_and_pixelizations`](./inversions_and_pixelizations.md)).

The two are complementary rather than competing, and the usual best practice is to do both:
the isophote profiles tell you *what structure exists*, which tells you what a parametric
model needs to contain.

Contaminants must still be handled. Ellipse fitting is if anything more sensitive to a
neighbour than a parametric fit, because a single bright interloper on one side of an ellipse
inflates the scatter around it and drags the fitted shape. Apply an extra-galaxies mask before
fitting — `autogalaxy_workspace:scripts/ellipse/modeling.py` has a masked variant for exactly
this. See [`extra_galaxies_and_noise_scaling`](./extra_galaxies_and_noise_scaling.md).

## See also

- [`../api/ellipse`](../api/ellipse.md) — the full ellipse-fitting API.
- [`light_profiles`](./light_profiles.md) — the parametric alternative, and the
  `SersicMultipole` / `GaussianMultipole` profiles that *assume* rather than measure the same
  harmonics.
- [`non_linear_search`](./non_linear_search.md) — why Dynesty here rather than Nautilus.
- [`grids_and_masks`](./grids_and_masks.md) — the mask radius sets the outermost ellipse.
- [`../stack/autogalaxy`](../stack/autogalaxy.md) — where the ellipse module sits.
