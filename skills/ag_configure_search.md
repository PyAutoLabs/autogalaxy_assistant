---
name: ag_configure_search
description: Choose and configure the non-linear search that fits a galaxy model to data — `af.Nautilus` for a full posterior with errors you can quote, `af.MultiStartProdigy` for a fast maximum-a-posteriori check, `af.DynestyStatic` for isophote/ellipse fitting and as a cross-check, and the MCMC / quasi-Newton / diagnostic alternatives. Covers `n_live` and `n_batch`, `n_starts` and `n_steps`, the `iterations_per_quick_update` output cadence, the start-point initialiser API, grid searches, and — critically — the `unique_tag` / unique-identifier and resume semantics, since the identifier is a hash of the model and search but **not** of the data, so re-using a tag across datasets silently resumes the wrong fit. Use once a model and analysis exist. Not for composing the model (`ag_build_imaging_model`), not for executing the fit or reading its output folder (`ag_run_search`), and not for diagnosing a fit that already failed.
---

# Choosing and configuring the search

A search is the algorithm that explores your model's parameter space, calling
`analysis.log_likelihood_function(instance)` over and over and deciding where to look next.
Every search in PyAutoFit takes the same two arguments, so swapping one for another is a
one-line change:

```python
result = search.fit(model=model, analysis=analysis)
```

The choice matters for one reason above all others: **some searches return a posterior and
some return a point.** A nested sampler maps the probability density of every parameter, its
errors, and the covariances between them — so it can tell you whether an inferred effective
radius of 1.6" is 1.6 ± 0.01 or 1.6 ± 0.5, and whether it trades off against the Sersic index.
A gradient optimiser hands you a single best-fit model and *nothing else*: no errors, no
covariances. Both are useful, for different questions, and confusing them is the most
consequential mistake available here.

The runnable tour of the whole menu is
`autogalaxy_workspace:scripts/guides/modeling/searches.py`; the catalogue with every argument
is [`../wiki/core/api/searches.md`](../wiki/core/api/searches.md), and what each family
actually does is
[`../wiki/core/concepts/non_linear_search.md`](../wiki/core/concepts/non_linear_search.md).

## Ask

- *"Do you need error bars, or do you just want to know whether this model fits at all?"*
  This is the whole decision. Errors → `Nautilus`. A quick check → `MultiStartProdigy`.
- *"How many free parameters does the model have?"* — `print(model.info)` if you don't know.
  It sets `n_live`, and it is the main driver of run time.
- *"Is this dataset one of several you will fit with the same model?"* — if yes, the
  `unique_tag` section below is not optional reading; it is where results silently collide.
- *"Is JAX available, and a GPU?"* — `MultiStartProdigy` requires a JAX-traceable analysis
  (`use_jax=True`) and is not available without it.

## Branch — `af.Nautilus`, the default

The search every workspace `modeling.py` example uses, and the one to reach for when the
answer will be quoted in a paper. Extensive testing across galaxy modelling found it the most
accurate and efficient search available. Adapted from
`autogalaxy_workspace:scripts/imaging/modeling.py`.

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

Source: `PyAutoFit:autofit/non_linear/search/nest/nautilus/`; optional dependency
`nautilus-sampler`. Reference: Lange (2023), arXiv:2306.16923.

**`n_live` is the accuracy / run-time dial**, and essentially the only setting you need to
think about. More live points map the posterior more reliably but cost more likelihood
evaluations; fewer are faster but risk converging on a local maximum. 200 is sufficient for
the vast majority of galaxy models, and more parameters want more — a bulge-plus-disk model
at N = 9 is comfortable at 200, while a model past ~30 free parameters is worth running at
400. Dropping to 100 on a simple model to save time is a legitimate move (`modeling.py` does
exactly that) but it is a deliberate accuracy trade, so say so when you make it.

**`n_batch` is where the GPU speed-up comes from**, and it is worth understanding because
Nautilus is *gradient-free* — it never differentiates the likelihood, so unlike the optimisers
below it does not use JAX's derivatives at all. What it does do is propose points in batches,
and when the analysis is JAX-traceable PyAutoFit evaluates the whole batch through one
`jax.vmap(jax.jit(...))` call, fitting all `n_batch` models simultaneously. It is therefore
also the main control on VRAM: a bigger batch holds more models in memory at once. Pair it
with `analysis.print_vram_use(model=model, batch_size=search.batch_size)` before a GPU run
(see [`ag_build_imaging_model`](./ag_build_imaging_model.md)).

For parallel CPU runs, `number_of_cores` scales well: roughly linearly below 8 cores and
about `0.5 * number_of_cores` above, continuing past 50 cores — which is why supercomputing
facilities make even large models tractable.

## Branch — `af.MultiStartProdigy`, when you want an answer now

The search every workspace `start_here.py` example uses. Far faster than Nautilus, and
returns a single best-fit model with **no errors at all**. Adapted from
`autogalaxy_workspace:scripts/imaging/start_here.py`.

```python
search = af.MultiStartProdigy(
    path_prefix=Path("imaging"),
    name="start_here",
    unique_tag=dataset_name,
    n_starts=48,
    n_steps=300,
    iterations_per_quick_update=50,
    live_visual_update=False,
)
```

Source: `PyAutoFit:autofit/non_linear/search/mle/multi_start_gradient/`; optional dependencies
`jax` and `optax`.

The design is what makes gradient descent usable on this problem at all. Galaxy-model
parameter spaces are multi-modal, so a *single*-start optimiser routinely descends confidently
into a local maximum — which is exactly the weakness of `LBFGS` below.
`MultiStartProdigy` launches `n_starts` independent descents from broad starting points spread
across the parameter space, runs them **all in parallel** through `jax.vmap`, and returns the
best. That wide population is what reliably finds the global maximum-likelihood basin; it is
the approach introduced for galaxy modelling by GIGA-Lens (Gu, Huang et al. 2022,
arXiv:2202.07663). Prodigy adds a *learning-rate free* update rule (Mishchenko & Defazio 2024,
arXiv:2306.06101): it estimates its own step size as it runs, so there is no `learning_rate`
for you to tune — which is precisely why it is the recommended member of the family over
`MultiStartAdam`, `MultiStartADABelief` and `MultiStartLion`, all of which want one chosen.

Three things to hold onto:

- **It requires `use_jax=True`.** It is gradient-based, so a NumPy analysis cannot supply what
  it needs. It is therefore unavailable for `ag.AnalysisEllipse`, which is not JAX-traceable.
- **`n_steps` is a ceiling, not a target.** The search stops early once the best fit stops
  improving, so expect a handful of quick updates rather than `n_steps / 50` of them.
- **There is no posterior.** If the fit reports `effective_radius = 1.6"`, this search cannot
  tell you the uncertainty, and no amount of extra starts will change that.

The workflow the workspace recommends, and the one to recommend to the user: run
`MultiStartProdigy` first to confirm cheaply that the model and data are sensible, then run
`Nautilus` on the same model when you need numbers you can quote.

## Branch — `af.DynestyStatic`, for isophotes and as a cross-check

The nested-sampling alternative, and the search the workspace's **ellipse** examples use,
because testing showed it the most reliable for isophote fitting specifically.

```python
search = af.DynestyStatic(
    path_prefix=Path("ellipse"),
    name="fit_start",
    unique_tag=dataset_name,
    sample="rwalk",
    nlive=50,
    iterations_per_quick_update=2500,
)
```

Source: `PyAutoFit:autofit/non_linear/search/nest/dynesty/`. Reference: Speagle (2020),
arXiv:1904.02180.

Note `nlive`, not `n_live` — the argument names follow each upstream sampler's own convention,
which is a real source of typos when switching. Dynesty's sampler options pass straight
through (`sample`, `walks`, `bound`, `bootstrap`, `enlarge`, `update_interval`, `facc`,
`slices`, `fmove`, `max_move`), and `af.DynestyDynamic` reallocates live points as it runs —
toward the tails for a better evidence estimate, toward the bulk for better parameters —
taking `nlive_init`, `dlogz_init` and the other `_init` variants instead.

Two reasons to reach for it. **Isophote fitting**: use it whenever the analysis is
`ag.AnalysisEllipse`, where the gradient optimisers are unavailable anyway. **Independent
cross-check**: a posterior that reproduces under a different nested sampler is far more
convincing than one that does not, and this is the cheapest such check available. Ellipse
fitting has its own page,
[`../wiki/core/api/ellipse.md`](../wiki/core/api/ellipse.md), and its own skill,
[`ag_ellipse_fitting`](./ag_ellipse_fitting.md).

## Branch — the rest of the catalogue

Reach for these only when you know why. All are tabulated with full argument lists in
[`../wiki/core/api/searches.md`](../wiki/core/api/searches.md) and demonstrated in
`autogalaxy_workspace:scripts/guides/modeling/searches.py`.

| Search | When |
|---|---|
| `af.Zeus` | Ensemble MCMC **slice** sampler; the best-performing MCMC in the workspace's tests, though still behind Nautilus. Good for characterising a posterior around a mode you already found. |
| `af.Emcee` | The familiar affine-invariant ensemble sampler. Same role as Zeus, generally a little worse on these parameter spaces. |
| `af.LBFGS` / `af.BFGS` | Single-start quasi-Newton descent via SciPy. Fast in principle, but galaxy-model parameter spaces are usually too complex to use it without careful initialisation — `MultiStartProdigy` exists to fix exactly that. |
| `af.Drawer` | Not a search: draws models from the prior and evaluates them. A diagnostic for "are my priors sane and does my likelihood run at all?", and the workspace's one-draw container for collecting many completed fits into a single output folder (`total_draws=1`). |

MCMC and MLE searches monitor convergence differently from nested samplers — both `Emcee` and
`Zeus` accept an `af.AutoCorrelationsSettings(check_for_convergence=True, check_size=100,
required_length=50, change_threshold=0.01)` and will terminate early when the chains satisfy
it.

## Branch — the output cadence

Every search writes results to disk **as it runs**, using the highest-likelihood model found
so far, and `iterations_per_quick_update` sets how often. This is not free, and the two
canonical values look contradictory until you notice the unit differs:

- `Nautilus(iterations_per_quick_update=10000)` — the unit is a likelihood evaluation, and on
  a fast fit writing output every few hundred would dominate the run time.
- `MultiStartProdigy(iterations_per_quick_update=50)` — the unit is a *gradient step*, a far
  coarser thing, so 50 gives a useful handful of updates.

If the log keeps announcing that it is outputting results, raise the number. The heavier
`iterations_per_full_update` controls the full pass — all visuals plus `model.results` and
`search.summary`. Defaults for both live in `autogalaxy_assistant:config/general.yaml` under
`updates:` (set to effectively infinite there, so the per-search value governs), and the
config layer is [`../wiki/core/api/configuration.md`](../wiki/core/api/configuration.md).

`live_visual_update=False` is the default and the right choice on a headless or cluster run.
Set it `True` to also push each quick update to a live surface — a matplotlib window that
refreshes from a script, or an in-place refresh of the Jupyter cell. The disk write happens
either way.

## The unique identifier, `unique_tag`, and resuming — read this one

Output lands at `output/<path_prefix>/<name>/<unique_identifier>/`, where the identifier is a
32-character hash. Re-running an identical configuration **resumes** the existing fit rather
than starting over, which is a genuinely useful feature — and the sharp edge of this whole
skill, because of what goes into the hash and what does not.

**The identifier is a hash of the model and the search. It is not a hash of the data.**

That is not a subtlety; it is a trap with a silent failure mode. Fit galaxy A, then change
only the FITS paths and fit galaxy B with the same model and the same search: the identifier
is identical, PyAutoFit finds a completed fit at that path, and reports "Fit Already
Completed". You get galaxy A's result back, labelled as galaxy B, with no error raised.

The fix is one argument, and it is why every workspace example passes it:

```python
search = af.Nautilus(
    path_prefix=Path("imaging"),
    name="modeling",
    unique_tag=dataset_name,  # <-- the discriminator the data itself does not supply
    n_live=200,
)
```

**Pass your dataset name as `unique_tag`, always.** Then the two galaxies hash differently and
land in different folders. And the corollary that catches people a second time: if the *data*
changes but its name does not — you re-reduced it, fixed the noise-map, changed the mask,
re-ran the simulator with different truth — **bump the `unique_tag`** (or delete the output
folder). Otherwise you resume a fit to data that no longer exists.

Changing the model or the search *does* change the identifier, so you never need to manage
that case by hand: a bulge-plus-disk fit cannot collide with a single-Sersic fit, and an
`n_live=200` run cannot collide with an `n_live=400` one. It is only the data axis that is
invisible to the hash.

Verify rather than trust when it matters. Comparing the identifier across two configurations
before launching a long run costs nothing:

```python
search.paths.model = model
search.paths.search = search

print(search.paths.identifier)
```

Two runs printing the same string will share an output folder, whatever you believe about
them. The annotated tour of what lands in that folder — `files/`, `image/`, `model.info`,
`model.results`, `search.summary` — is the `__Output Folder Layout__` section of
`autogalaxy_workspace:scripts/imaging/modeling.py`, and the run-search skill
(`ag_run_search`) owns reading it.

## Branch — a start point, for MCMC and MLE only

MCMC and optimiser searches have a *location* in parameter space, so you can say where they
begin. Nested samplers draw from the prior and cannot use this API. Adapted from
`autogalaxy_workspace:scripts/guides/modeling/searches.py`, where an early-type galaxy is
started near n = 4.

```python
initializer = af.InitializerParamBounds(
    {
        model.galaxies.galaxy.bulge.centre_0: (-0.01, 0.01),
        model.galaxies.galaxy.bulge.centre_1: (-0.01, 0.01),
        model.galaxies.galaxy.bulge.effective_radius: (0.9, 1.1),
        model.galaxies.galaxy.bulge.sersic_index: (3.9, 4.1),
    }
)

search = af.Emcee(
    path_prefix=Path("imaging"),
    name="start_point",
    unique_tag=dataset_name,
    nwalkers=50,
    nsteps=500,
    initializer=initializer,
)
```

Parameters you do not name are drawn from their priors. `af.InitializerBall(lower_limit=0.49,
upper_limit=0.51)` is the other common choice — a tight ball in unit-prior space around the
prior centres, and the recommended initialisation for both MCMC samplers.

The statistical point here is worth stating explicitly, because there is a tempting shortcut
that is not equivalent. You *could* achieve a similar effect by tightening priors instead —
a narrow `af.TruncatedGaussianPrior` on `sersic_index`, say. But priors change the posterior,
and therefore change the errors you quote and the model you infer. The start-point API moves
where the search *looks* without moving what you *infer*. Prefer it whenever your knowledge is
about where the answer probably is rather than about what the answer must be.

## Branch — mapping a parameter on a grid

To scan a parameter on a fixed grid rather than marginalising over it — a light centre, a
fixed `sersic_index`, anything you want mapped — wrap a search:

```python
grid_search = af.SearchGridSearch(
    search=search, number_of_steps=4, number_of_cores=1, result_output_interval=100
)
```

One child fit runs per grid cell and an `af.GridSearchResult` comes back. Source:
`PyAutoFit:autofit/non_linear/grid/`. This is the one search whose defaults *do* live in a
YAML — `autogalaxy_assistant:config/non_linear/GridSearch.yaml` sets `number_of_cores` and
`step_size` in unit-prior values, and it is the only file in that folder because per-search
defaults ship inside PyAutoFit itself
(`autogalaxy_assistant:config/non_linear/README.md`).

## A different lever: chaining instead of a better search

When a model is too complex for any single search, the answer is usually not a bigger
`n_live` — it is to fit a simpler model first and pass its posterior forward as the priors of
the complex one. Fit a single Sersic, then chain into a bulge-plus-disk or pixelised fit,
which starts from a region of parameter space that is already good.
`autogalaxy_workspace:scripts/guides/modeling/chaining.py` is the walkthrough, the
`width_modifier` entries in the prior YAMLs control how wide the passed priors become, and it
gets its own skill in a later phase (`ag_chain_searches`).

## Picking one at a glance

| Goal | Pick |
|---|---|
| Quick check that model + data are sensible | `MultiStartProdigy(n_starts=48, n_steps=300)` |
| Results you will quote, model under ~30 free parameters | `Nautilus(n_live=200)` |
| Production run, complex or multi-modal model | `Nautilus(n_live=400)`, higher `n_batch` if VRAM allows |
| Bayesian evidence comparison between models | `Nautilus` or `DynestyStatic` |
| Ellipse / isophote fitting | `DynestyStatic(sample="rwalk", nlive=50)` |
| Independent cross-check of a posterior | `DynestyStatic` or `Zeus` |
| Posterior refinement around a known mode | `Zeus` or `Emcee` with an `initializer` |
| Map a parameter on a fixed grid | `af.SearchGridSearch` |
| Check the priors are sane and the likelihood runs | `af.Drawer` |

## Combine — where this hands off

- **Run the fit** → the run-search skill (`ag_run_search`), which owns
  `search.fit(model=model, analysis=analysis)`, announcing the output folder at launch, and
  what to open first while it runs.
- **The model isn't right yet** → [`ag_build_imaging_model`](./ag_build_imaging_model.md).
  Changing the search rarely rescues a badly-specified model, and a search that will not
  converge is more often a model problem than a sampler problem.
- **It ran and failed, stalled, or returned something unphysical** → the fit-debugging skill
  (`ag_debug_fit_failure`), which is also where "Fit Already Completed" on data you thought was
  new gets diagnosed.
- **Read the posterior that comes back** → the results-loading and fit-plotting skills
  (`ag_load_results`, `ag_plot_fit`); the `Samples` API and how errors are computed is
  [`../wiki/core/concepts/samples_and_posteriors.md`](../wiki/core/concepts/samples_and_posteriors.md).

Offer (default-yes) a dated `wiki/project/YYYY-MM-DD-<slug>.md` entry recording the search and
its settings — `n_live` in particular, since it is an accuracy claim about the posterior you
are about to publish.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: The non-linear search](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_2_modeling/tutorial_1_non_linear_search.ipynb):
  what a non-linear search actually is — parameter spaces, likelihoods, priors — and the
  statistical foundation under every setting on this page. The
  [optional chapter](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_optional/tutorial_searches.ipynb)
  tours the sampler zoo.
- **General reference** — [RTD: Configs](https://pyautogalaxy.readthedocs.io/en/latest/general/configs.html):
  how the configuration files customise searches, visualisation and output, and where each is
  looked up.
- **Experienced PyAutoGalaxy user** — [workspace: guides/modeling/searches.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/guides/modeling/searches.py):
  every available search instantiated with its settings spelled out, plus the start-point API.

## Agent procedural checklist

1. Ask the one question that decides it: errors needed, or a fast check?
2. `Nautilus(n_live=200)` by default; `MultiStartProdigy` for speed (needs `use_jax=True`);
   `DynestyStatic` for isophotes or a cross-check.
3. Set `n_live` from the model's free-parameter count, and say when you trade it down.
4. **Always pass `unique_tag=dataset_name`** — and bump it when the data changes but the name
   does not.
5. Print `search.paths.identifier` before a long run whenever a collision is plausible.
6. Set `iterations_per_quick_update` to the search's unit — thousands for Nautilus, tens for a
   gradient optimiser. Keep `live_visual_update=False` on headless runs.
7. Run `analysis.print_vram_use(model=model, batch_size=search.batch_size)` before a GPU run.
8. Hand off to `ag_run_search`, and offer the `wiki/project/` entry recording the settings.
