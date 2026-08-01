---
title: Ellipse fitting — isophote measurement
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/ellipse/ellipse/ellipse.py
      - autogalaxy/ellipse/ellipse/ellipse_multipole.py
      - autogalaxy/ellipse/dataset_interp.py
      - autogalaxy/ellipse/fit_ellipse.py
      - autogalaxy/ellipse/model/analysis.py
      - autogalaxy/ellipse/model/result.py
      - autogalaxy/ellipse/model/visualizer.py
      - autogalaxy/ellipse/plot/fit_ellipse_plots.py
      - autogalaxy/aggregator/ellipse/
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/ellipse/modeling.py
      - scripts/ellipse/fit.py
      - scripts/ellipse/multipoles.py
      - scripts/ellipse/plot.py
      - scripts/ellipse/database.py
      - scripts/ellipse/simulator.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
  - project: autogalaxy_assistant
    paths:
      - config/priors/ellipse/ellipse.yaml
      - config/priors/ellipse/ellipse_multipole.yaml
    pinned_commit: ed72fabb33e14a9a701a4d280e8775dd3a20e98c
last_updated: 2026-08-01
content_sha256: 349e8f331c85e1a821c9eeb4fb97360a40e451f98b6031293f0817e89ebd6f60
---

# Ellipse fitting

Ellipse fitting is the **non-parametric** alternative to a light-profile decomposition. Instead of
assuming the galaxy is a Sersic and inferring its parameters, you fit an ellipse of fixed size at
each radius and let the data tell you its ellipticity and orientation. Repeat for a series of
growing radii and you have measured profiles of ellipticity and position angle as functions of
radius — the classical isophote analysis, with no assumption that any analytic law describes the
light.

That is a genuinely different measurement, and it answers different questions. Isophote twists
(position angle rotating with radius) and ellipticity gradients are direct evidence of a triaxial
structure or a bar; boxy or discy deviations quantified by an `m = 4` harmonic separate rotation-
from dispersion-supported early types. None of that is a parameter of a Sersic fit.

Concept page:
[`../concepts/ellipse_fitting_and_multipoles`](../concepts/ellipse_fitting_and_multipoles.md).

Note there is deliberately **no `start_here.py`** in the workspace's `ellipse/` package. Start at
`autogalaxy_workspace:scripts/ellipse/fit.py` for how the likelihood works, then
`autogalaxy_workspace:scripts/ellipse/modeling.py` for the fit.

## How the likelihood differs

This is the part that catches people, so it comes before the API.

In light-profile fitting a model **image** is subtracted from the data pixel by pixel, and the
residual map shows where the model failed. Ellipse fitting builds no model image. Instead:

1. An `ag.Ellipse` supplies a set of (y, x) coordinates spaced along its perimeter.
2. The data and noise-map are **interpolated** onto those coordinates.
3. The `model_data` *is* those interpolated data values.
4. The `residual_map` is each value minus the **mean** of those values.

So a good fit is one where the data values traced round the ellipse are all close to one another —
the ellipse is following an isophote. A bad fit crosses isophotes and the values scatter. The
`normalized_residual_map` and `chi_squared_map` then follow the usual definitions. Source:
`PyAutoGalaxy:autogalaxy/ellipse/fit_ellipse.py`; the walkthrough is
`autogalaxy_workspace:scripts/ellipse/fit.py`.

## Loading the data

An `ag.Imaging` object, loaded **without a PSF** — ellipse fitting never convolves anything, so
there is nothing for a PSF to do:

```python
dataset = ag.Imaging.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    pixel_scales=0.1,
)

mask_radius = 5.0

mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=mask_radius,
)

dataset = dataset.apply_mask(mask=mask)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/modeling.py`. Keep `mask_radius` in a variable:
it does double duty here, both restricting the fit and setting the largest ellipse you will fit
(the workspace uses `mask_radius * 0.9` as the outermost major axis). See
[`datasets`](./datasets.md) for the loading and masking API in general.

## `ag.Ellipse`

```python
ellipse = ag.Ellipse(centre=(0.0, 0.0), ell_comps=(0.0, 0.0), major_axis=1.0)
```

Three parameters: `centre`, `ell_comps`, `major_axis`. Useful members:

- `ellipse.points_from_major_axis_from(pixel_scale=...)` — the (y, x) coordinates along the
  perimeter. The number of points is chosen automatically from the data resolution and the
  ellipse's size, so a bigger ellipse samples proportionally more pixels; that is why
  `pixel_scale` is an input.
- `ellipse.axis_ratio`, `ellipse.angle`, `ellipse.minor_axis` — the derived geometry you actually
  report.

Source: `PyAutoGalaxy:autogalaxy/ellipse/ellipse/ellipse.py`.

## `ag.DatasetInterp` and `ag.FitEllipse`

`ag.DatasetInterp(dataset=dataset)` holds the interpolation weights and mappings in memory so they
are computed once rather than per ellipse. You rarely construct it yourself — `ag.FitEllipse` makes
one internally — but it is the object that explains where the model data comes from:

```python
interp = ag.DatasetInterp(dataset=dataset)

points = ellipse.points_from_major_axis_from(pixel_scale=dataset.pixel_scales[0])

data_interp = interp.data_interp(points)
noise_map_interp = interp.noise_map_interp(points)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/fit.py`. Source:
`PyAutoGalaxy:autogalaxy/ellipse/dataset_interp.py`.

The fit object itself:

```python
fit = ag.FitEllipse(dataset=dataset, ellipse=ellipse)
```

Signature: `FitEllipse(dataset, ellipse, multipole_list=None, use_jax=False)`. It exposes
`model_data`, `residual_map`, `normalized_residual_map`, `chi_squared_map`, `chi_squared`,
`log_likelihood` and `figure_of_merit`, matching the light-profile fit objects' names so that
downstream code and plotting work uniformly. `ag.FitEllipseSummed` combines several fits into one.
Source: `PyAutoGalaxy:autogalaxy/ellipse/fit_ellipse.py`.

## `ag.EllipseMultipole`

A pure ellipse cannot represent a boxy, discy or lopsided isophote. An `ag.EllipseMultipole` adds
an angular harmonic of order `m` to the ellipse's shape:

```python
multipole_order_4 = ag.EllipseMultipole(m=4, multipole_comps=(0.05, 0.05))

fit_multipole = ag.FitEllipse(
    dataset=dataset, ellipse=ellipse, multipole_list=[multipole_order_4]
)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/multipoles.py`. Two parameters: `m` and
`multipole_comps`. Several orders can be applied at once:

```python
multipole_order_1 = ag.EllipseMultipole(m=1, multipole_comps=(0.05, 0.05))
multipole_order_3 = ag.EllipseMultipole(m=3, multipole_comps=(0.05, 0.05))

fit_multipole = ag.FitEllipse(
    dataset=dataset,
    ellipse=ellipse,
    multipole_list=[multipole_order_1, multipole_order_3],
)
```

Physically: `m = 1` is a lopsided offset, `m = 3` a three-fold asymmetry, `m = 4` the boxy/discy
term most often quoted in the early-type literature.

`ag.EllipseMultipoleScaled(m=4, scaled_multipole_comps=(0.0, 0.0), major_axis=1.0)` is the variant
that holds its strength *relative* to an ellipse of unit major axis: the scaled components are
converted back to a true amplitude at each ellipse's own `major_axis`, so a whole series of
ellipses at different radii can share one scaled strength `k/a` instead of carrying an independent
amplitude each. Source:
`PyAutoGalaxy:autogalaxy/ellipse/ellipse/ellipse_multipole.py`.

## Fitting one ellipse

The model is always a `list` of ellipses inside `af.Collection(ellipses=[...])`, even when there is
only one, so that the same code fits many:

```python
import autofit as af

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
    nlive=50,
)

analysis = ag.AnalysisEllipse(dataset=dataset, use_jax=False)

result = search.fit(model=model, analysis=analysis)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/modeling.py`.

Three things are deliberate here:

- **`major_axis` is fixed**, not fitted. The whole point is to measure the isophote *at a given
  radius*, so the size is an input and the shape is what you infer. With `centre` and `ell_comps`
  free this is an N=4 fit.
- **`af.DynestyStatic`** rather than Nautilus. Testing found Dynesty with random-walk sampling the
  most accurate and efficient search for isophote fitting specifically. See
  [`searches`](./searches.md).
- **`use_jax=False`**. Ellipse fitting is not JAX-traceable, and every workspace ellipse example
  passes this explicitly. It is not an oversight; leaving the default in place is the error.

Default priors come from `autogalaxy_assistant:config/priors/ellipse/ellipse.yaml` and
`autogalaxy_assistant:config/priors/ellipse/ellipse_multipole.yaml` — see
[`configuration`](./configuration.md).

## Fitting a series of ellipses

The measurement you actually want is a *profile*, so the real workflow fits one ellipse per radius,
each seeded with the centre found by the first fit:

```python
import numpy as np

number_of_ellipses = 10

major_axis_list = np.linspace(0.3, mask_radius * 0.9, number_of_ellipses)

result_list = []

for i in range(len(major_axis_list)):

    ellipse = af.Model(ag.Ellipse)

    ellipse.centre.centre_0 = result.instance.ellipses[0].centre[0]
    ellipse.centre.centre_1 = result.instance.ellipses[0].centre[1]

    ellipse.ell_comps.ell_comps_0 = af.UniformPrior(lower_limit=-0.6, upper_limit=0.6)
    ellipse.ell_comps.ell_comps_1 = af.UniformPrior(lower_limit=-0.6, upper_limit=0.6)

    ellipse.major_axis = major_axis_list[i]

    model = af.Collection(ellipses=[ellipse])

    search = af.DynestyStatic(
        path_prefix=Path("ellipse"),
        name=f"fit_{i}",
        unique_tag=dataset_name,
        sample="rwalk",
        nlive=50,
        number_of_cores=4,
    )

    analysis = ag.AnalysisEllipse(dataset=dataset, use_jax=False)

    result = search.fit(model=model, analysis=analysis)

    result_list.append(result)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/modeling.py`. Fixing the centre from the first
fit is the standard choice: a common centre is what makes the resulting ellipticity and position
angle profiles comparable across radius.

To gather them into a single result folder, the workspace collects the fitted instances and runs a
one-draw `af.Drawer`:

```python
ellipses = [result.instance.ellipses[0] for result in result_list]

model = af.Collection(ellipses=ellipses)
model.dummy_0 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)

search = af.Drawer(
    path_prefix=Path("ellipse"),
    name="fit_all",
    unique_tag=dataset_name,
    total_draws=1,
)

result = search.fit(model=model, analysis=analysis)
```

The `dummy_0` prior exists because a model with no free parameters has nothing for a search to
draw; it is a one-parameter placeholder, not a physical quantity.

### With multipoles

The same loop, with the multipole components added to the model. `multipoles` is a second key in
the collection:

```python
multipole_3 = af.Model(ag.EllipseMultipole)
multipole_3.m = 3
multipole_3.multipole_comps.multipole_comps_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
multipole_3.multipole_comps.multipole_comps_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

multipole_4 = af.Model(ag.EllipseMultipole)
multipole_4.m = 4
multipole_4.multipole_comps.multipole_comps_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
multipole_4.multipole_comps.multipole_comps_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

multipole_list = [multipole_3, multipole_4]

model = af.Collection(ellipses=[ellipse], multipoles=multipole_list)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/multipoles.py`. `af.GaussianPrior(mean=0.0,
sigma=0.1)` centred on zero is the honest prior: it says "no deviation from an ellipse unless the
data demands one", so a non-zero inferred `m = 4` component is a detection rather than an artefact
of the prior.

## Reading the result

```python
instance = result.max_log_likelihood_instance

print(f"First Ellipse Centre: {instance.ellipses[0].centre}")
print(f"First Ellipse Elliptical Components: {instance.ellipses[0].ell_comps}")
print(f"First Ellipse Major Axis: {instance.ellipses[0].major_axis}")
print(f"First Ellipse Axis Ratio: {instance.ellipses[0].axis_ratio}")
print(f"First Ellipse Angle: {instance.ellipses[0].angle}")

for i, ellipse in enumerate(result.max_log_likelihood_instance.ellipses):
    print(f"Ellipse {i} Minor Axis: {ellipse.minor_axis}")
```

Adapted from `autogalaxy_workspace:scripts/ellipse/modeling.py`. `axis_ratio` and `angle` are
derived from `ell_comps`, so the search never samples an angle directly — which is exactly the
point of the `ell_comps` parameterisation. `result.info`, `result.samples` and the rest of the
result surface behave as in [`analysis_objects`](./analysis_objects.md).

The analysis also offers `analysis.fit_list_from(instance=...)`, which turns one model instance
into its list of `ag.FitEllipse` objects — the route from a posterior sample to a plottable fit.

## Plotting

```python
import autogalaxy.plot as aplt

fit = ag.FitEllipse(dataset=dataset, ellipse=ellipse)

aplt.subplot_fit_ellipse(fit_list=[fit])
```

Note the keyword is `fit_list=`, not `fit=`: the natural unit is a *set* of ellipses drawn over one
image.

```python
major_axis_list = [0.5, 1.0, 1.5, 2.0]

ellipse_list = [
    ag.Ellipse(centre=(0.0, 0.0), ell_comps=(0.3, 0.5), major_axis=major_axis)
    for major_axis in major_axis_list
]

fit_list = [ag.FitEllipse(dataset=dataset, ellipse=ellipse) for ellipse in ellipse_list]

aplt.subplot_fit_ellipse(fit_list=fit_list)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/plot.py`. `aplt.subplot_ellipse_errors(
fit_pdf_list=..., sigma=...)` plots the isophote parameter uncertainties from a list of
posterior-drawn fits, and `aplt.plot_array(array=dataset.data, title="Data")` covers the
single-panel cases. Full plotting API: [`plotting`](./plotting.md).

During a fit, `ag.AnalysisEllipse.Visualizer` writes these figures automatically into the run's
`image/` folder; which of them appear is controlled by the `fit_ellipse` entry in
`config/visualize/plots.yaml`.

## Many fits — the aggregator

An isophote analysis produces one fit per radius per galaxy, so it hits the aggregator sooner than
most workflows. Three galaxy-domain classes are ellipse-specific:

```python
ellipses_agg = ag.agg.EllipsesAgg(aggregator=agg)
ellipses_gen = ellipses_agg.max_log_likelihood_gen_from()

fit_agg = ag.agg.FitEllipseAgg(aggregator=agg)

multipoles_agg = ag.agg.MultipolesAgg(aggregator=agg)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/database.py`. Source:
`PyAutoGalaxy:autogalaxy/aggregator/ellipse/`. The full aggregator surface — queries, generators,
CSV/FITS/PNG export — is [`aggregator`](./aggregator.md).

## When to use this instead of a light profile

| Question | Approach |
|---|---|
| Effective radius, Sersic index, bulge-to-total ratio | light-profile fit — [`light_profile_catalog`](./light_profile_catalog.md) |
| Ellipticity and position angle **as functions of radius** | ellipse fitting |
| Isophote twist (evidence of triaxiality or a bar) | ellipse fitting |
| Boxy / discy deviation, quantified | ellipse fitting with an `m = 4` multipole, or `ag.lp.SersicMultipole` |
| A model you can extrapolate, simulate from, or integrate | light-profile fit |
| Structure no analytic law describes at all | a pixelisation — [`../concepts/inversions_and_pixelizations`](../concepts/inversions_and_pixelizations.md) |

The two are complements, not rivals: a common workflow measures the isophotes first to see what
structure is there, then chooses the parametric model that can represent it.

## See also

- [`../concepts/ellipse_fitting_and_multipoles`](../concepts/ellipse_fitting_and_multipoles.md) —
  the physics of isophote analysis.
- [`datasets`](./datasets.md) — loading and masking the imaging.
- [`analysis_objects`](./analysis_objects.md) — `ag.AnalysisEllipse` alongside the other analyses.
- [`searches`](./searches.md) — why `af.DynestyStatic` here.
- [`plotting`](./plotting.md) · [`aggregator`](./aggregator.md) · [`configuration`](./configuration.md).
