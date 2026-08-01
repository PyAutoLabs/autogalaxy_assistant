---
title: The non-linear search
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/search/abstract_search.py
      - autofit/non_linear/search/nest/
      - autofit/non_linear/search/mcmc/
      - autofit/non_linear/search/mle/
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/modeling/searches.py
      - scripts/guides/modeling/chaining.py
      - scripts/imaging/start_here.py
      - scripts/imaging/modeling.py
      - scripts/ellipse/modeling.py
      - scripts/guides/results/start_here.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 05120accc325720145ce1d7fbf2decebb9f93bb5df5ff617fe842ebb7a1c5010
---

# The non-linear search

A model gives you a family of possible galaxies; an `Analysis` gives you a log-likelihood
for any one of them. The **non-linear search** is the algorithm that explores the parameter
space between them. You pick one, configure it, and hand it the model and analysis:

```python
result = search.fit(model=model, analysis=analysis)
```

Sources: `PyAutoFit:autofit/non_linear/search/`. The full catalogue with per-search settings
is [`../api/searches`](../api/searches.md); the survey script it is grounded in is
`autogalaxy_workspace:scripts/guides/modeling/searches.py`.

## Two searches cover almost everything

The workspace is deliberately opinionated: two searches account for essentially all galaxy
modelling, and everything else is a cross-check or a specialist tool.

### Nautilus — when you need a result you can quote

`af.Nautilus` is a nested sampler and the default of every `modeling.py` example. It does not
return a best-fit point; it maps the **full posterior** — a probability density for every
parameter, error bars on each, and the covariances between them. If a fit infers
`effective_radius = 1.6″`, only a posterior tells you whether that is `1.6 ± 0.01` or
`1.6 ± 0.5`, and whether it is trading off against `sersic_index`.

```python
import autofit as af

search = af.Nautilus(
    path_prefix=Path("imaging"),
    name="modeling",
    unique_tag=dataset_name,
    n_live=100,       # accuracy vs run time; raise for more complex models
    n_batch=50,       # models evaluated per GPU call; bounds VRAM
    iterations_per_quick_update=10000,
)
```

- **`n_live`** is the main accuracy knob. More live points map parameter space more
  faithfully and cost more time; fewer risk converging on a local maximum. Higher-dimensional
  models need more. The linear-profile and MGE examples *reduce* it to 75 precisely because
  those models have simpler parameter spaces (see
  [`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md)).
- **Nautilus is gradient-free** — it never differentiates the likelihood — but it still
  exploits JAX on a GPU, because it proposes points in **batches** and PyAutoFit evaluates
  each batch through a `jax.vmap(jax.jit(...))`-wrapped likelihood in a single call. `n_batch`
  is therefore both a throughput and a VRAM control.

### MultiStartProdigy — when you need an answer fast

`af.MultiStartProdigy` is the JAX multi-start gradient optimizer used by every
`start_here.py`. It launches `n_starts` independent optimisations from broad starting points
and descends them **all in parallel** via `jax.vmap`, returning the best.

```python
search = af.MultiStartProdigy(
    path_prefix=Path("imaging"),
    name="start_here",
    unique_tag=dataset_name,
    n_starts=48,
    n_steps=300,
    iterations_per_quick_update=50,
)
```

The multi-start design is the whole point. Galaxy-model parameter spaces are multi-modal, and
a single-start gradient descent regularly gets stuck; running a wide population of starts is
what makes gradient descent reliable here — the approach introduced for galaxy modelling by
GIGA-Lens (Gu, Huang et al. 2022, [arXiv:2202.07663](https://arxiv.org/abs/2202.07663)).
Prodigy itself is a **learning-rate-free** update rule (Mishchenko & Defazio 2024,
[arXiv:2306.06101](https://arxiv.org/abs/2306.06101)) that estimates its own step size, so
there is nothing to tune. Related members of the family: `af.MultiStartAdam` (the GIGA-Lens
original, needs a `learning_rate`), `af.MultiStartADABelief`, `af.MultiStartLion`.

**It returns no posterior.** It is a maximum a posteriori estimator: one best-fit model, no
error bars, no covariances. For most science that is not enough.

The workflow the workspace recommends follows directly: **`MultiStartProdigy` to check
quickly that your model and data are sensible, then `Nautilus` when you need numbers you can
publish.** `autogalaxy_workspace:scripts/imaging/start_here.py`.

Because it is gradient-based it requires a JAX-traceable analysis (`use_jax=True`), which
rules it out for ellipse fitting (see
[`ellipse_fitting_and_multipoles`](./ellipse_fitting_and_multipoles.md)).

## The rest of the catalogue

`autogalaxy_workspace:scripts/guides/modeling/searches.py` documents each of these; reach for
them when you know why.

**Nested sampling** — `af.DynestyStatic`, `af.DynestyDynamic`. Dynesty with random-walk
sampling (`sample="rwalk"`) was the default before Nautilus and remains a good independent
cross-check. It is also the **recommended search for ellipse fitting**, where testing found
it the most accurate and efficient.

**MCMC** — `af.Emcee` (affine-invariant ensemble) and `af.Zeus` (ensemble slice sampler).
Zeus is the better of the two for this problem class in the workspace's testing, though
neither matches Nautilus. Both characterise a posterior well *around a mode you have already
found* and are poor at finding modes from scratch. Both support convergence checking via
`af.AutoCorrelationsSettings`.

**Optimisation** — `af.LBFGS`, a single-start quasi-Newton method. Fast in principle;
in practice galaxy parameter spaces are too complex for it without careful initialisation,
which is exactly the weakness `MultiStartProdigy` was built to fix.

**`af.Drawer`** — draws models from the priors rather than searching. Used to evaluate an
assembled model once (the ellipse-fitting workflow's final combining step) and for debugging
that priors produce sensible galaxies.

### Choosing

| Situation | Search |
|---|---|
| First look at a new dataset | `af.MultiStartProdigy` |
| Errors you will quote in a paper | `af.Nautilus` |
| Complex or high-dimensional model | `af.Nautilus`, higher `n_live` |
| Independent cross-check of a Nautilus result | `af.DynestyStatic` |
| Ellipse / isophote fitting | `af.DynestyStatic(sample="rwalk")` |
| Refining a posterior around a known mode | `af.Zeus` |
| Evaluating a fixed model once | `af.Drawer` |

## Settings every search shares

- **`path_prefix`**, **`name`**, **`unique_tag`** — together with a hash of the model, these
  determine the output directory. `unique_tag` is conventionally the dataset name so that the
  same model fitted to different data lands in different folders.
- **`iterations_per_quick_update`** — how often the current best fit is visualised and written
  to disk. Too low and output dominates the run time; too high and you cannot watch progress.
  The unit depends on the search (Nautilus: likelihood evaluations; `MultiStartProdigy`:
  gradient steps, hence the much smaller value of 50).
- **`live_visual_update`** — additionally push the quick-update image to a live matplotlib
  window (script) or a self-updating notebook cell. Leave it `False` on a headless machine.
- **`number_of_cores`** — parallel likelihood evaluation on CPU, used by the non-JAX searches.

## Priors and start points

Priors come from configuration by default (`ag.lp.*` entries in
`PyAutoGalaxy:autogalaxy/config/priors/`; see [`../api/configuration`](../api/configuration.md))
and are overridden per parameter on the model:

```python
bulge.effective_radius = af.UniformPrior(lower_limit=0.5, upper_limit=1.5)
bulge.sersic_index = af.UniformPrior(lower_limit=0.5, upper_limit=6.0)
```

MCMC and optimisation searches additionally accept a **start point**, which sets where the
walkers begin without changing the priors:

```python
initializer = af.InitializerParamBounds(
    {
        model.galaxies.galaxy.bulge.centre_0: (-0.01, 0.01),
        model.galaxies.galaxy.bulge.effective_radius: (0.9, 1.1),
        model.galaxies.galaxy.bulge.sersic_index: (3.9, 4.1),
    }
)

search = af.Emcee(path_prefix=..., name=..., nwalkers=50, nsteps=500, initializer=initializer)
```

`autogalaxy_workspace:scripts/guides/modeling/searches.py`. Nested samplers cannot use it —
they draw from the prior by construction — so the equivalent there is to tighten the priors
themselves. That distinction matters scientifically: **narrowing a prior changes the
posterior**, and hence the inferred parameters and their errors, whereas a start point does
not. Use tight priors to encode real knowledge, not to steer a search.

## Search chaining

A search can be initialised from the posterior of a previous one. The attribute that does the
narrowing is **`result.model_centred`**: it returns a new model whose priors are
`TruncatedGaussianPrior`s centred on the previous median-PDF values, with widths taken from each
parameter's `width_modifier` in the priors configuration:

```python
bulge = result_1.model_centred.galaxies.galaxy.bulge
disk = result_1.model_centred.galaxies.galaxy.disk

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)
model_2 = af.Collection(galaxies=af.Collection(galaxy=galaxy))
```

Three variants override that width: `model_centred_absolute(a=)` (one absolute `sigma` for every
parameter), `model_centred_relative(r=)` (`sigma = r × mean`) and
`model_centred_max_lh_bounded(b=)` (a `UniformPrior` at `mean ± b`).

**`result.model` does not narrow anything.** On the released stack it returns the fitted model
with its **original priors unchanged** — `samples_summary.model.mapper_via_defaults_from()` maps
every prior to itself (`PyAutoFit:autofit/non_linear/result.py`) — so a component passed that way
brings its composition across but no information from the fit. Reach for it only when that is
what you want; the prose in
`autogalaxy_workspace:scripts/guides/modeling/chaining.py` still describes `result.model` as
producing narrowed Gaussians and is out of date on this point.
[`../../../skills/ag_chain_searches.md`](../../../skills/ag_chain_searches.md) is the procedural
recipe and carries the full three-way split.

Whole profiles or whole galaxies can be passed either way. The third alternative,
`result_1.instance...`, passes the maximum-likelihood values as **fixed** numbers, removing them
from the search — useful for fixing a light model in an intermediate stage and freeing it again
later.

Chaining is what makes hard fits tractable: start with a simple parametric model, then chain
into a pixelisation or a many-component basis with the simple fit's posterior as the starting
priors. It is chapter 3 of the HowToGalaxy lectures, and the recommended route into a
pixelised fit ([`inversions_and_pixelizations`](./inversions_and_pixelizations.md)). Always
check `model.info` of the chained search to confirm the priors arrived as intended.

## The output folder

`search.fit(...)` writes to `output/<path_prefix>/<name>/<unique_tag>/<unique_hash>/`
**on the fly**, using the best model found so far — so it is worth opening the moment the
search starts, not when it finishes:

```
files/                    JSON + CSV, loadable Python objects
    galaxies.json         max log likelihood galaxies (loads as a list)
    model.json            the fitted af.Collection
    samples.csv           every accepted sample
    samples_summary.json  max log likelihood values + errors
    covariance.csv        parameter covariance matrix
    cosmology.json        the cosmology used
image/                    FITS + PNG products
    dataset.fits, fit.fits, model_galaxy_images.fits
    dataset.png, fit.png
model.info                human-readable model + priors
model.results             human-readable fit summary
search.summary            search run summary
```

`autogalaxy_workspace:scripts/guides/results/start_here.py`. Open `model.results` and
`image/fit.png` first. The `<unique_hash>` is derived from the model, search and dataset, so
re-running an identical configuration **resumes** rather than restarts — which also means that
if you change the data without changing the model or the `unique_tag`, you can silently resume
someone else's fit. Change the `unique_tag` when the data changes.

Loading any of it back is [`samples_and_posteriors`](./samples_and_posteriors.md) and
[`../api/aggregator`](../api/aggregator.md).

## Run-time estimation

Total run time is (likelihood evaluation time) × (number of evaluations). The first is
measurable: ~0.01 s for standard light profiles on a typical dataset, ~0.05 s with linear
profiles, ~0.4 s for a shapelet basis, ~0.5 s for a 60-Gaussian MGE, and minutes-scale per
fit for a pixelisation. The second is model-dependent; the workspace's conservative rule of
thumb is **~10 000 evaluations per free parameter** as an upper bound, with most models
converging in far fewer.

This is why dimensionality matters more than per-evaluation speed: an MGE with a slower
likelihood but 6 free parameters routinely beats a Sersic decomposition with a faster
likelihood and 13. On a GPU, also check VRAM before a long pixelised run
(`analysis.print_vram_use(model=model, batch_size=search.batch_size)`).

## See also

- [`../api/searches`](../api/searches.md) — every search and its settings.
- [`samples_and_posteriors`](./samples_and_posteriors.md) — what the search produces.
- [`../api/analysis_objects`](../api/analysis_objects.md) — the likelihood side of
  `search.fit`.
- [`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md) — why a smaller
  parameter space beats a faster likelihood.
- [`multi_wavelength`](./multi_wavelength.md) — fitting several datasets with one search.
- [`../stack/autofit`](../stack/autofit.md) — the library that owns all of this.
