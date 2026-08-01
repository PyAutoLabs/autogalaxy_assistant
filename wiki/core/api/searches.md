---
title: Non-linear search catalogue
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/search/abstract_search.py
      - autofit/non_linear/search/nest/nautilus/
      - autofit/non_linear/search/nest/dynesty/
      - autofit/non_linear/search/mcmc/emcee/
      - autofit/non_linear/search/mcmc/zeus/
      - autofit/non_linear/search/mle/bfgs/
      - autofit/non_linear/search/mle/drawer/
      - autofit/non_linear/search/mle/multi_start_gradient/
      - autofit/non_linear/initializer.py
      - autofit/non_linear/grid/
      - autofit/config/non_linear/
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/modeling/searches.py
      - scripts/guides/modeling/customize.py
      - scripts/guides/modeling/chaining.py
      - scripts/imaging/start_here.py
      - scripts/imaging/modeling.py
      - scripts/ellipse/modeling.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
  - project: autogalaxy_assistant
    paths:
      - config/non_linear/GridSearch.yaml
      - config/general.yaml
    pinned_commit: ed72fabb33e14a9a701a4d280e8775dd3a20e98c
last_updated: 2026-08-01
content_sha256: ce9e29263a3ee8643317388d2375ef4866a7fb561a0964b5f5a1211b07311dc9
---

# Non-linear search catalogue

A search is the algorithm that explores the model's parameter space, calling
`analysis.log_likelihood_function(instance)` over and over. Every search in this page comes from
PyAutoFit and takes the same two arguments:

```python
result = search.fit(model=model, analysis=analysis)
```

**Two searches account for essentially all galaxy modelling**, and the workspace is explicit
about which is which:

| Search | What it returns | Where the workspace uses it |
|---|---|---|
| `af.Nautilus` | the **full posterior** — errors and covariances | every `modeling.py` example |
| `af.MultiStartProdigy` | a **single best-fit model**, no errors, much faster | every `start_here.py` example |

Use `MultiStartProdigy` to check quickly that a model and dataset are sensible; use `Nautilus`
when you need a number you can quote. Everything else below is a cross-check or a special case.
The runnable tour of the whole menu is
`autogalaxy_workspace:scripts/guides/modeling/searches.py`; conceptual background is
[`../concepts/non_linear_search`](../concepts/non_linear_search.md).

## Nested sampling

### `af.Nautilus` — the default

```python
search = af.Nautilus(
    path_prefix=Path("imaging"),
    name="modeling",
    unique_tag=dataset_name,
    n_live=200,
    n_batch=50,
    iterations_per_quick_update=10000,
)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py`. Source:
`PyAutoFit:autofit/non_linear/search/nest/nautilus/`; optional dependency `nautilus-sampler`.
Reference: Lange (2023), arXiv:2306.16923.

- **`n_live`** — the accuracy / run-time dial. 200 is enough for the vast majority of galaxy
  models; `modeling.py` drops to 100 on a simple model to save time, and complex models want more.
  More parameters ⇒ more live points.
- **`n_batch`** — Nautilus proposes points in batches. When the analysis is JAX-traceable
  (`use_jax=True`), PyAutoFit evaluates the whole batch through one
  `jax.vmap(jax.jit(...))` call, so all `n_batch` models are fitted simultaneously — this is where
  the GPU speed-up comes from for a nested sampler. It is also the main control on VRAM: a bigger
  batch holds more models in memory at once. Pair it with `analysis.print_vram_use(...)` (see
  [`analysis_objects`](./analysis_objects.md)).
- Nautilus is **gradient-free** — it never differentiates the likelihood. It benefits from JAX
  through batched evaluation, not through gradients.

### `af.DynestyStatic` / `af.DynestyDynamic`

The nested-sampling cross-check, and the search the workspace's **ellipse** examples use, because
testing showed it is the most reliable for isophote fitting.

```python
search = af.DynestyStatic(
    path_prefix=Path("ellipse"),
    name="fit_start",
    unique_tag=dataset_name,
    sample="rwalk",
    nlive=50,
)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/modeling.py` and
`autogalaxy_workspace:scripts/guides/modeling/searches.py`. Source:
`PyAutoFit:autofit/non_linear/search/nest/dynesty/`. Reference: Speagle (2020), arXiv:1904.02180.

- `DynestyStatic` takes `nlive`, `dlogz`, `maxiter`, `logl_max`; `DynestyDynamic` takes
  `nlive_init`, `dlogz_init`, `logl_max_init`, `maxcall_init`, `maxiter_init`.
- Dynesty's own sampler options pass straight through: `sample` (`"rwalk"`, `"slice"`, …),
  `walks`, `bound`, `bootstrap`, `enlarge`, `update_interval`, `facc`, `slices`, `fmove`,
  `max_move`. `guides/modeling/searches.py` sets all of them explicitly if you want a template.
- Static keeps the live-point count fixed; dynamic reallocates live points where they help most
  (tails for the evidence, the bulk for parameters).

## Gradient optimisers (JAX)

These are maximum a posteriori (**MAP**) optimisers: they return one best-fit model and **no
uncertainties at all**. If a fit reports `effective_radius = 1.6"`, an optimiser cannot tell you
whether that is ±0.01 or ±0.5.

### `af.MultiStartProdigy` — the recommended optimiser

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

Adapted from `autogalaxy_workspace:scripts/imaging/start_here.py`. Source:
`PyAutoFit:autofit/non_linear/search/mle/multi_start_gradient/`; optional dependencies `jax` and
`optax`.

The design matters, because it is what makes gradient descent usable here at all. Galaxy-model
parameter spaces are multi-modal, so a *single*-start optimiser routinely descends into a local
maximum. `MultiStartProdigy` launches `n_starts` independent descents from broad starting points,
runs them **all in parallel** through `jax.vmap`, and returns the best — the multi-start approach
introduced for galaxy modelling by GIGA-Lens (Gu, Huang et al. 2022, arXiv:2202.07663).
Prodigy is additionally *learning-rate free* (Mishchenko & Defazio 2024, arXiv:2306.06101): it
estimates its own step size, so there is no `learning_rate` to tune.

Parameters: `n_starts`, `n_steps`, `learning_rate` (unused by Prodigy), `batch_size`,
`max_consecutive_nan`, `start_lower_limit`, `start_upper_limit`, `resurrect`, `convergence`
(an `af.MultiStartGradientConvergence`), `iterations_per_log`.

`n_steps` is a ceiling, not a target: the search stops early once the best fit stops improving, so
expect a handful of quick updates rather than `n_steps / iterations_per_quick_update` of them.

Requires a JAX-traceable analysis (`use_jax=True`) — so **not** `ag.AnalysisEllipse`, which does
not support JAX.

### The rest of the family

| Search | Difference |
|---|---|
| `af.MultiStartAdam` | the GIGA-Lens original; robust, but you must choose a `learning_rate` |
| `af.MultiStartADABelief` | an Adam variant; drop-in at the same `learning_rate` |
| `af.MultiStartLion` | sign-based; prefers a `learning_rate` roughly 10× smaller |

All four share `MultiStartProdigy`'s parameter list.

## MCMC

Best for characterising a posterior around a mode you have already found, not for finding the mode
in the first place. Both accept an `initializer` (see "Start point" below).

### `af.Emcee`

Affine-invariant ensemble sampler; the familiar choice in astronomy.

```python
search = af.Emcee(
    path_prefix=Path("imaging", "searches"),
    name="Emcee",
    unique_tag="example",
    nwalkers=30,
    nsteps=500,
    initializer=af.InitializerBall(lower_limit=0.49, upper_limit=0.51),
)
```

Adapted from `autogalaxy_workspace:scripts/guides/modeling/searches.py`. Source:
`PyAutoFit:autofit/non_linear/search/mcmc/emcee/`. Reference: Foreman-Mackey et al. (2013),
arXiv:1202.3665.

The wrapper monitors chain auto-correlations and can terminate early on convergence; pass an
`af.AutoCorrelationsSettings(check_for_convergence=True, check_size=..., required_length=...,
change_threshold=...)` object to `auto_correlation_settings` to control it.

### `af.Zeus`

Ensemble **slice** sampler — handles correlated posteriors better than Emcee at similar cost per
step, and is the best-performing MCMC method in the workspace's own tests (still behind Nautilus).

```python
search = af.Zeus(
    path_prefix=Path("imaging", "searches"),
    name="Zeus",
    nwalkers=30,
    nsteps=20,
    initializer=af.InitializerBall(lower_limit=0.49, upper_limit=0.51),
)
```

Extra knobs: `tune`, `tolerance`, `patience`, `mu`, `light_mode`, `maxsteps`, `maxiter`,
`maxcall`, `vectorize`, `shuffle_ensemble`, `check_walkers`. Source:
`PyAutoFit:autofit/non_linear/search/mcmc/zeus/`; optional dependency `zeus-mcmc`. Reference:
Karamanis, Beutler & Peacock (2021), arXiv:2105.03468.

## Classical optimisers and diagnostics

### `af.LBFGS` / `af.BFGS`

Quasi-Newton descent to the maximum-likelihood point via SciPy. Single-start, so — as
`guides/modeling/searches.py` puts it — galaxy-model parameter spaces are usually too complex for
these to be used without careful initialisation. `MultiStartProdigy` exists precisely to fix that.

```python
search = af.LBFGS(path_prefix=Path("imaging", "searches"), name="LBFGS")
```

SciPy pass-throughs: `tol`, `disp`, `eps`, `ftol`, `gtol`, `iprint`, `maxcor`, `maxfun`,
`maxiter`, `maxls`. Source: `PyAutoFit:autofit/non_linear/search/mle/bfgs/`.

### `af.Drawer`

Draws models from the prior and evaluates them. Not a search — a diagnostic that answers "are my
priors sane, and does my likelihood run at all?". The workspace also uses it as a **one-draw
container** for combining many completed fits into a single output folder:

```python
search = af.Drawer(
    path_prefix=Path("ellipse"),
    name="fit_all",
    unique_tag=dataset_name,
    total_draws=1,
)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/modeling.py`, which uses exactly this to write
out all ten fitted isophotes as one result. Note the parameter is `total_draws`. Source:
`PyAutoFit:autofit/non_linear/search/mle/drawer/`.

## Shared arguments

Every search takes these, from the common base class
(`PyAutoFit:autofit/non_linear/search/abstract_search.py`):

| Argument | Meaning |
|---|---|
| `name` | identifier; combines with the model hash to form the output folder's unique id |
| `path_prefix` | folder prefix under `output/` |
| `unique_tag` | extra discriminator — **pass your dataset name here**, so the same model on different data lands in different folders |
| `initializer` | where an MCMC/MLE search starts (see below) |
| `iterations_per_quick_update` | iterations between quick updates: the max-likelihood model and its `fit.png` |
| `iterations_per_full_update` | iterations between full updates: all visuals plus `model.results` / `search.summary` |
| `live_visual_update` | default `False`; `True` also pushes each quick update to a live surface — a matplotlib window from a script, an in-place refresh in Jupyter/Colab. Keep it `False` on headless or HPC runs; the disk write happens either way |
| `number_of_cores` | parallel likelihood evaluations (CPU) |
| `silence` | suppress console output |

**On the update cadence.** The quick update is not free — `modeling.py` sets
`iterations_per_quick_update=10000` on a fast fit precisely so that writing output does not
dominate the run time, while `start_here.py` uses 50 because a gradient step is a much coarser
unit than a likelihood call. If the log keeps saying it is outputting results, raise the number.
Config fallbacks live in `autogalaxy_assistant:config/general.yaml` under `updates:`, with an HPC
override block under `hpc:` — see [`configuration`](./configuration.md).

### The unique identifier and resuming

The output path ends in a hash derived from the model, the search and the dataset. Re-running an
identical configuration **resumes** the existing fit rather than starting over; change the model
or the search and a new folder appears. This is why `unique_tag=dataset_name` matters: without it,
two datasets fitted with the same model and search would collide. The annotated tour of the output
tree is the `__Output Folder Layout__` section of
`autogalaxy_workspace:scripts/imaging/modeling.py`.

## Start point — for MCMC and MLE only

MCMC and optimiser searches have a *location* in parameter space, so you can say where they begin.
Nested samplers draw from the prior and cannot use this API.

```python
initializer = af.InitializerParamBounds(
    {
        model.galaxies.galaxy.bulge.centre_0: (-0.01, 0.01),
        model.galaxies.galaxy.bulge.centre_1: (-0.01, 0.01),
        model.galaxies.galaxy.bulge.effective_radius: (0.9, 1.1),
        model.galaxies.galaxy.bulge.sersic_index: (3.9, 4.1),
    }
)

search = af.Emcee(path_prefix=Path("imaging"), name="start_point", initializer=initializer)
```

Adapted from `autogalaxy_workspace:scripts/guides/modeling/searches.py` — an early-type galaxy
started near `n = 4`. `af.InitializerBall(lower_limit=..., upper_limit=...)` is the other common
choice, a ball in unit-prior space around the prior centres. Parameters you do not name are drawn
from their priors.

The statistical point the workspace makes here is worth repeating: you *could* get the same effect
by tightening priors, but priors change the posterior and therefore the errors you quote. The
start-point API moves where the search looks without moving what you infer.

## Grid searches

To scan a parameter on a fixed grid — a light centre, a fixed `sersic_index`, anything you want
mapped rather than marginalised — wrap a search in `af.SearchGridSearch(search, number_of_steps=4,
number_of_cores=1, result_output_interval=100)`, which runs one child fit per grid cell and
returns an `af.GridSearchResult`. Defaults for the workspace's grid searches live in
`autogalaxy_assistant:config/non_linear/GridSearch.yaml` (`number_of_cores`, and `step_size` in
unit-prior values). Source: `PyAutoFit:autofit/non_linear/grid/`.

## Chaining searches

A different lever from choosing a better search: run a cheap search first, then use its posterior
as the priors of a more complex one. This is how you fit a model too complex for a single search —
fit a single Sersic, then pass the result forward to a bulge-plus-disk or pixelised fit.
`autogalaxy_workspace:scripts/guides/modeling/chaining.py` is the walkthrough, and the
`width_modifier` entries in the prior YAMLs are what control how wide the passed priors become
(see [`configuration`](./configuration.md)).

## Picking a search at a glance

| Goal | Pick |
|---|---|
| Quick check that model + data are sensible | `MultiStartProdigy(n_starts=48, n_steps=300)` |
| Results you will quote, model under ~30 free parameters | `Nautilus(n_live=200)` |
| Production run, complex or multi-modal model | `Nautilus(n_live=400)`, higher `n_batch` if VRAM allows |
| Bayesian evidence comparison between models | `Nautilus` or `DynestyStatic` |
| Ellipse / isophote fitting | `DynestyStatic(sample="rwalk", nlive=50)` |
| Independent cross-check of a Nautilus posterior | `DynestyStatic` or `Zeus` |
| Posterior refinement around a known mode | `Zeus` or `Emcee` with an `initializer` |
| Map a parameter on a fixed grid | `af.SearchGridSearch` |
| Check the priors are sane | `af.Drawer` |

## See also

- [`../concepts/non_linear_search`](../concepts/non_linear_search.md) — what each family actually
  does.
- [`../concepts/samples_and_posteriors`](../concepts/samples_and_posteriors.md) — reading what
  comes back.
- [`analysis_objects`](./analysis_objects.md) — the other half of `search.fit(...)`.
- [`configuration`](./configuration.md) — the `updates:` cadence and per-search config defaults.
- [`plotting`](./plotting.md) — corner plots and search diagnostics from `result.samples`.
- [`../stack/autofit`](../stack/autofit.md) — where all of these classes live.
