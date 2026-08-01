---
title: Analysis objects and model composition
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/analysis/analysis/analysis.py
      - autogalaxy/analysis/analysis/dataset.py
      - autogalaxy/analysis/result.py
      - autogalaxy/imaging/model/analysis.py
      - autogalaxy/imaging/model/result.py
      - autogalaxy/imaging/model/visualizer.py
      - autogalaxy/interferometer/model/analysis.py
      - autogalaxy/ellipse/model/analysis.py
      - autogalaxy/galaxy/galaxy.py
      - autogalaxy/galaxy/galaxies.py
      - autogalaxy/analysis/adapt_images/
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: PyAutoArray
    paths:
      - autoarray/settings.py
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: PyAutoFit
    paths:
      - autofit/graphical/declarative/factor/analysis.py
      - autofit/graphical/declarative/collection.py
      - autofit/graphical/declarative/abstract.py
      - autofit/non_linear/combined_result.py
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: autogalaxy_workspace
    paths:
      - scripts/imaging/modeling.py
      - scripts/imaging/likelihood_function.py
      - scripts/imaging/plot.py
      - scripts/ellipse/modeling.py
      - scripts/guides/modeling/cookbook.py
      - scripts/multi_dataset/start_here.py
      - scripts/imaging/features/sky_background/modeling.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: ee92fe5c4da627ac7590e3d52d02ca7a007be06176cbbf2995e3d17edd6a9141
---

# Analysis objects and model composition

A fit has exactly two halves. The **model** says what could be true — which light profiles, on
which galaxies, with what priors. The **analysis** holds a dataset and knows how to score a
proposed model against it. A search (see [`searches`](./searches.md)) shuttles between them:

```python
result = search.fit(model=model, analysis=analysis)
```

Everything below is either how you build the left-hand argument or how you build the right-hand
one.

## Composing a model

Model composition comes from PyAutoFit: `af.Model` wraps a class whose parameters become free,
and `af.Collection` groups models into a named tree you can address later.

```python
import autofit as af
import autogalaxy as ag

bulge = af.Model(ag.lp_linear.Sersic)
disk = af.Model(ag.lp_linear.Exponential)
bulge.centre = disk.centre

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

print(model.info)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py` — an N=11 bulge-plus-disk model,
where `bulge.centre = disk.centre` says the two components are concentric and so removes two
parameters rather than fitting them twice.

Four things to know:

- **Attribute names are yours.** `bulge`, `disk`, `bar`, `clump` — the name you pass to
  `af.Model(ag.Galaxy, ...)` is the key you address afterwards, e.g.
  `model.galaxies.galaxy.bulge.sersic_index`. `ag.Galaxy` takes `redshift` and then arbitrary
  keyword arguments, which is why any name works
  (`PyAutoGalaxy:autogalaxy/galaxy/galaxy.py`).
- **The concise form.** Passing a profile *class* rather than an `af.Model` promotes it
  automatically: `af.Model(ag.Galaxy, redshift=0.5, bulge=ag.lp_linear.Sersic,
  disk=ag.lp_linear.Exponential)` is equivalent to the long form above
  (`autogalaxy_workspace:scripts/guides/modeling/cookbook.py`).
- **The `galaxies` collection is a convention the analysis relies on.** Several galaxies go in
  side by side — `af.Collection(galaxies=af.Collection(galaxy_0=..., galaxy_1=...))` — and their
  light is summed on the sky (`PyAutoGalaxy:autogalaxy/galaxy/galaxies.py`).
- **`print(model.info)`** is the cheapest sanity check there is: it prints every free parameter
  with its prior, so a model subtly larger or more constrained than you intended shows up before
  you spend hours on a search.

Priors are overridden on the model instance:

```python
bulge = af.Model(ag.lp_linear.Sersic)
bulge.centre.centre_0 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)
bulge.centre.centre_1 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)
bulge.sersic_index = af.TruncatedGaussianPrior(
    mean=4.0, sigma=1.0, lower_limit=0.8, upper_limit=5.0
)
```

Adapted from `autogalaxy_workspace:scripts/guides/modeling/cookbook.py`. The *defaults* those
overrides replace come from the YAMLs described in [`configuration`](./configuration.md). The
cookbook also covers pairing and fixing parameters, JSON round-tripping via
`af.Model.from_json(...)`, and the many-profile (MGE / shapelet) composition helpers.

### `ag.DatasetModel` — nuisance parameters of the data

Some free parameters belong to the *dataset*, not the galaxy: a residual background sky level, a
sub-pixel astrometric offset between bands, a small rotation. These live in
`ag.DatasetModel(background_sky_level=0.0, grid_offset=(0.0, 0.0), grid_rotation_angle=0.0)`,
added to the model alongside `galaxies`:

```python
dataset_model = af.Model(ag.DatasetModel)
dataset_model.background_sky_level = af.UniformPrior(lower_limit=0.0, upper_limit=5.0)

model = af.Collection(
    galaxies=af.Collection(galaxy=galaxy), dataset_model=dataset_model
)
```

Adapted from `autogalaxy_workspace:scripts/imaging/features/sky_background/modeling.py`. Fitting
the sky rather than assuming it is zero matters for exactly the measurement galaxy structure
cares most about — the faint outer envelope that sets `effective_radius` and `sersic_index`.
Concept page:
[`../concepts/sky_background_and_operated_profiles`](../concepts/sky_background_and_operated_profiles.md).

## The three analyses

| Analysis | Dataset | Source |
|---|---|---|
| `ag.AnalysisImaging` | `ag.Imaging` | `PyAutoGalaxy:autogalaxy/imaging/model/analysis.py` |
| `ag.AnalysisInterferometer` | `ag.Interferometer` | `PyAutoGalaxy:autogalaxy/interferometer/model/analysis.py` |
| `ag.AnalysisEllipse` | `ag.Imaging` (no PSF) | `PyAutoGalaxy:autogalaxy/ellipse/model/analysis.py` |

All three share a base class in `PyAutoGalaxy:autogalaxy/analysis/analysis/dataset.py`, and all
three are handed to `search.fit(model=..., analysis=...)`.

### `ag.AnalysisImaging`

```python
analysis = ag.AnalysisImaging(dataset=dataset, use_jax=True)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py`. The full argument list is
`AnalysisImaging(dataset, adapt_images=None, cosmology=None, settings=None, title_prefix=None,
use_jax=True)`:

- **`use_jax`** — defaults to `True`, and is what makes the gradient searches possible at all:
  the likelihood and its derivatives are traced by JAX and evaluated in batches, on a GPU if one
  is present. Pass `use_jax=False` (or set `PYAUTO_DISABLE_JAX=1`) when debugging — NumPy
  tracebacks are far easier to read than JAX ones.
- **`settings`** — `ag.Settings(...)` carries the inversion and linear-solver knobs:
  `use_mixed_precision`, `use_positive_only_solver`, `use_edge_zeroed_pixels`,
  `use_border_relocator`, `no_regularization_add_to_curvature_diag_value`, `nnls_solver_tol`,
  `nnls_max_iter`, `log_det_method` (`PyAutoArray:autoarray/settings.py`). Every one has a
  config default — see [`configuration`](./configuration.md) — so you only pass `settings` to
  override.
- **`cosmology`** — e.g. `ag.cosmo.Planck15()`; needed when the model or a derived quantity
  converts between angular and physical units. See
  [`../concepts/cosmology_and_units`](../concepts/cosmology_and_units.md).
- **`adapt_images`** — images from an earlier fit that drive an adaptive mesh and
  brightness-weighted regularisation in a pixelised reconstruction
  (`PyAutoGalaxy:autogalaxy/analysis/adapt_images/`).
- **`title_prefix`** — prepended to the titles of the figures this analysis outputs.

**Before a GPU run, check VRAM.** JAX must hold the whole batched likelihood in GPU memory:

```python
analysis.print_vram_use(model=model, batch_size=search.batch_size)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py`, which quotes ~0.027 GB for an
MGE model on a low-resolution dataset and > 1 GB (occasionally > 10 GB) for a pixelised
reconstruction at high resolution. The call takes 20–30 seconds; that is much cheaper than
discovering the limit as an out-of-memory error mid-compile.

### `ag.AnalysisInterferometer`

```python
analysis = ag.AnalysisInterferometer(dataset=dataset, use_jax=True)
```

The same argument surface as `AnalysisImaging`. The real-space mask and the visibility
transformer are properties of the *dataset*, chosen when you load it — see
[`datasets`](./datasets.md).

### `ag.AnalysisEllipse`

```python
analysis = ag.AnalysisEllipse(dataset=dataset, use_jax=False)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/modeling.py`. A deliberately smaller surface —
`AnalysisEllipse(dataset, title_prefix=None, use_jax=True)` — because isophote fitting takes no
cosmology, no inversion settings and no adapt images. **Pass `use_jax=False`**: ellipse fitting
is not JAX-traceable, and every workspace ellipse example says so explicitly. Its extra method
`analysis.fit_list_from(instance=...)` returns the list of `ag.FitEllipse` objects for one model
instance. Full page: [`ellipse`](./ellipse.md).

## Fitting several datasets — the factor graph

To fit one galaxy to several datasets at once (multi-band imaging, joint imaging plus
interferometer, multi-epoch), you build **one analysis per dataset**, pair each with a model
inside an `af.AnalysisFactor`, and combine the factors into an `af.FactorGraphModel`. The graph's
log-likelihood is the sum of the per-factor log-likelihoods, and the graph decides which priors
are shared across datasets and which are free per dataset.

```python
import autofit as af

analysis_factor_list = []

for dataset in dataset_list:

    analysis = ag.AnalysisImaging(dataset=dataset, use_jax=True)

    model_analysis = model.copy()

    analysis_factor = af.AnalysisFactor(prior_model=model_analysis, analysis=analysis)

    analysis_factor_list.append(analysis_factor)

factor_graph = af.FactorGraphModel(*analysis_factor_list, use_jax=True)

result_list = search.fit(model=factor_graph.global_prior_model, analysis=factor_graph)
```

Adapted from `autogalaxy_workspace:scripts/multi_dataset/start_here.py`.

- **`af.AnalysisFactor(prior_model, analysis, optimiser=None, name=None)`** — pairs one analysis
  with the model whose log-likelihood it evaluates
  (`PyAutoFit:autofit/graphical/declarative/factor/analysis.py`).
- **`af.FactorGraphModel(*model_factors, name=None, include_prior_factors=True, use_jax=False)`** —
  collects the factors; its `global_prior_model` property is the `Collection` you hand to the
  search (`PyAutoFit:autofit/graphical/declarative/collection.py`,
  `PyAutoFit:autofit/graphical/declarative/abstract.py`).
- **`search.fit(...)`** then returns a `CombinedResult` — iterable and indexable, one `Result` per
  factor, in order (`PyAutoFit:autofit/non_linear/combined_result.py`).

**Shared versus per-dataset parameters.** With a bare `model.copy()` per factor and no prior
overrides, every prior is *identified* across factors: the graph deduplicates them, so the global
model has exactly the dimensionality of the single-dataset model — everything shared. To free a
parameter per dataset, override that prior on the `model.copy()` **before** wrapping it in its
factor. The canonical case is an astrometric offset between bands:

```python
model_analysis.dataset_model.grid_offset.grid_offset_0 = af.UniformPrior(
    lower_limit=-0.1, upper_limit=0.1
)
model_analysis.dataset_model.grid_offset.grid_offset_1 = af.UniformPrior(
    lower_limit=-0.1, upper_limit=0.1
)
```

Adapted from `autogalaxy_workspace:scripts/multi_dataset/start_here.py`. A per-band `intensity`
is the other common one — the physics being that morphology is shared across wavelength while
brightness is not. Design discussion:
[`../concepts/multi_wavelength`](../concepts/multi_wavelength.md).

There is deliberately no way to add two analyses together. The `+` overload that once summed
log-likelihoods was removed; the factor graph above is the only supported way to combine
datasets.

## What the result gives you

`search.fit(...)` returns a `Result` whose exact class depends on the analysis
(`PyAutoGalaxy:autogalaxy/analysis/result.py`,
`PyAutoGalaxy:autogalaxy/imaging/model/result.py`). The members you reach for most:

| Member | What it is |
|---|---|
| `result.info` | the human-readable fit summary — parameters, errors, log likelihood |
| `result.samples` | the full `Samples` object; posterior, errors, covariances |
| `result.samples_summary` | pre-computed summary; much faster than re-deriving from `samples` |
| `result.max_log_likelihood_instance` | the best-fit model as concrete objects |
| `result.max_log_likelihood_galaxies` | the best-fit `ag.Galaxies` |
| `result.max_log_likelihood_fit` | the best-fit `ag.FitImaging` — model image, residuals, chi-squared map |
| `result.model` | the *prior* model that was fitted |
| `result.instance` | the median-PDF instance |
| `result.dataset`, `result.mask`, `result.grids` | what was fitted, as loaded |
| `result.unmasked_model_image`, `result.unmasked_model_image_of_galaxies` | model images beyond the mask |
| `result.model_image_galaxy_dict`, `result.subtracted_image_galaxy_dict` | per-galaxy model and residual images |

Concept page: [`../concepts/samples_and_posteriors`](../concepts/samples_and_posteriors.md). For
many fits at once, see [`aggregator`](./aggregator.md).

## Evaluating the likelihood by hand

You rarely call the likelihood yourself — the search does. But for debugging a prior range or a
suspicious model it is the most direct probe there is:

```python
instance = model.instance_from_prior_medians()
log_likelihood = analysis.log_likelihood_function(instance=instance)
```

`log_likelihood_function(instance)` is the single contract between model and data, and a
step-by-step walk through what happens inside it lives in
`autogalaxy_workspace:scripts/imaging/likelihood_function.py`.

## Visualisation during a fit

Each analysis carries a `Visualizer` (`ag.AnalysisImaging.Visualizer`,
`ag.AnalysisEllipse.Visualizer`, …) that PyAutoFit invokes at update intervals and again at the
end, writing figures into the fit's `image/` folder using the best model found so far. You do
not call the plot functions yourself to watch a fit converge. Which figures appear is set by
`config/visualize/plots.yaml`; the cadence is set by the search's
`iterations_per_quick_update` / `iterations_per_full_update`. Sources:
`PyAutoGalaxy:autogalaxy/imaging/model/visualizer.py` and, for the prose walkthrough, the
`__Visualizer__` section of `autogalaxy_workspace:scripts/imaging/plot.py`.

## Writing your own analysis

When no built-in analysis fits your data, subclass `af.Analysis`, store the dataset in
`__init__`, and implement `log_likelihood_function(instance)` — the instance is your model at one
parameter vector, with every galaxy and profile already realised as a concrete object.
Everything else (searches, priors, samples, the aggregator) keeps working unchanged, because that
method is PyAutoFit's only contract between a model and data. The three built-in analyses in
`PyAutoGalaxy:autogalaxy/imaging/model/analysis.py`,
`PyAutoGalaxy:autogalaxy/interferometer/model/analysis.py` and
`PyAutoGalaxy:autogalaxy/ellipse/model/analysis.py` are the reference implementations;
PyAutoFit's analysis cookbook
(https://pyautofit.readthedocs.io/en/latest/cookbooks/analysis.html) is the concise API
reference.

## See also

- [`datasets`](./datasets.md) — what each analysis ingests.
- [`searches`](./searches.md) — the other half of `search.fit(...)`.
- [`ellipse`](./ellipse.md) — the isophote-fitting analysis in full.
- [`light_profile_catalog`](./light_profile_catalog.md) — what goes inside `af.Model`.
- [`configuration`](./configuration.md) — where default priors and `Settings` defaults come from.
- [`../stack/autofit`](../stack/autofit.md) — the model and search machinery itself.
