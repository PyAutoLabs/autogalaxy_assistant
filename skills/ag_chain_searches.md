---
name: ag_chain_searches
description: Break one hard fit into a sequence of easier non-linear searches, using each result to initialize the next. Covers when chaining beats a single search and when it does not, passing a whole profile or galaxy with `result.model` (which preserves the original priors) versus narrowing them with `result.model_centred` and its absolute, relative and bounded variants, the `TruncatedGaussianPrior` those produce and where its sigma comes from in the `priors` config `width_modifier`, fixing a component with `result.instance` to remove its dimensions, and the output-path convention that keeps a chain's searches together. Use when a model is too complex for one search, when an early search should use cheap settings and a later one accurate ones, or when several galaxies must be added one at a time. Not for choosing a single search (`ag_configure_search`), not for driving one fit (`ag_run_search`), and not for combining several datasets (`ag_multi_dataset`).
---

# Chaining searches

Every other modelling skill in this workspace composes one model and hands it to one search.
Chaining is the alternative shape: split the problem into a sequence of searches, and use what
each one learned to tell the next where to look.

The reason is statistical, not cosmetic. A non-linear search has to map a parameter space it knows
nothing about, and the cost of doing that grows sharply with dimensionality while the risk of
settling in a local maximum grows with multi-modality. A galaxy model with a bulge, a disk, a sky
level and two blended neighbours has both problems at once. Fit the bulge alone and the space is
small, unimodal and mapped in minutes; then the disk only has to be added to a galaxy whose size
and centre are already known. Each search in a chain solves a problem that is easy *because* of
the one before it.

Three distinct benefits, and they are worth separating because they justify chaining in different
situations:

- **Lower dimensionality per search.** Earlier searches fit simpler models with a parameter space
  that can be sampled properly, which reduces the chance of an incorrect local maximum in the
  final one.
- **Cheap settings early, accurate settings late.** An early search only needs to find the high-
  likelihood region, so it can use a fast optimizer or a small `n_live`. Only the final search
  needs settings good enough to quantify errors.
- **Cheap approximations early.** An early search can use a smaller mask, coarser over-sampling
  or a simplified component, and revert to the accurate-but-expensive settings at the end. The
  approximation costs some fidelity in the early result, which is fine when that result is only
  being used to place a prior.

This skill has **one** grounding script: `autogalaxy_workspace:scripts/guides/modeling/chaining.py`.
It is deliberately an API overview rather than a library of pipelines, and this skill is scoped to
match it — the mechanics of prior passing, done honestly, rather than a catalogue of recipes that
do not exist upstream. Chapter 3 of the HowToGalaxy lecture series is where the pedagogy lives.
Read [`../wiki/core/concepts/non_linear_search.md`](../wiki/core/concepts/non_linear_search.md) for
how run time scales with the model, which is the quantity chaining exists to manage.

## Ask

- *"What makes this fit hard — too many parameters, or a search that keeps landing somewhere
  wrong?"* Both are chaining's territory, but they suggest different splits: dimensionality
  suggests adding components one at a time, multi-modality suggests fixing the thing the search
  keeps getting wrong.
- *"What would you fit first if you had to pick one component?"* Usually the brightest and
  simplest. If the user cannot name one, chaining may not be the right tool — see the branch on
  when not to chain.
- *"Is a single search actually failing, or just slow?"* A slow-but-correct search is often better
  served by a faster sampler or JAX than by a chain, because a chain adds a whole class of
  failure: a wrong early result confidently narrowing a later prior.

## Branch — the two-search chain

The deliverable is one script containing the whole chain, so it can be re-run end to end. Adapted
from `autogalaxy_workspace:scripts/guides/modeling/chaining.py`.

```python
"""
Galaxy Structure: Chained Searches
=================================

Fit a galaxy's bulge alone, then add a disk with the bulge's parameters initialized from the
first fit. Splitting the fit this way lets each search sample a parameter space it can actually
map, and makes the two-component decomposition a refinement of a known galaxy rather than a
fourteen-dimensional search from broad priors.

__Contents__

- **Imports:** JAX environment first, then the standard trio.
- **Dataset:** Load, mask and over-sample the imaging once, for every search.
- **Paths:** One output prefix shared by every search in the chain.
- **Model (Search 1):** A single linear Sersic bulge.
- **Model-Fit (Search 1):** Fit it, cheaply.
- **Model Chaining:** Pass the bulge into search 2 and add a disk.
- **Model-Fit (Search 2):** Fit the two-component model with accurate settings.
- **Result:** Read the final model back.
"""
from autogalaxy import jax_wrapper  # Sets the JAX environment before other imports

from pathlib import Path

import autofit as af
import autogalaxy as ag
import autogalaxy.plot as aplt

"""
__Dataset__

Loaded, masked and over-sampled once. Every search in the chain shares one `analysis`, which is
what makes their likelihoods comparable — if search 2 used a different mask, its log likelihood
would not be on the same scale as search 1's, and the priors passed between them would refer to a
different dataset.
"""
DATASET_PATH = Path("dataset") / "imaging" / "<your_galaxy>"

dataset = ag.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    psf_path=DATASET_PATH / "psf.fits",
    pixel_scales=0.1,
)

mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=3.0,
)

dataset = dataset.apply_mask(mask=mask)

over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[8, 4, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)

dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

analysis = ag.AnalysisImaging(dataset=dataset, use_jax=True)

"""
__Paths__

One `path_prefix` for the whole chain, with each search distinguished only by `name`. This keeps
every stage of one chain in one directory tree, which matters when you come back to a fit and
need to see what search 1 actually inferred before trusting search 2.
"""
path_prefix = Path("imaging") / "chaining" / "<your_galaxy>"

"""
__Model (Search 1)__

The bulge alone. A linear `Sersic` solves its own `intensity`, so this is a compact space the
search can map quickly (`PyAutoGalaxy:autogalaxy/profiles/light/linear/sersic.py`).
"""
bulge = af.Model(ag.lp_linear.Sersic)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)

model_1 = af.Collection(galaxies=af.Collection(galaxy=galaxy))

print(model_1.info)

"""
__Model-Fit (Search 1)__

Cheap settings on purpose: this search only has to find the high-likelihood region, not measure
errors. Inspect its result before relying on it — a chain built on a bad first search propagates
that error into every subsequent prior, with more confidence at every step.
"""
search_1 = af.Nautilus(
    path_prefix=path_prefix,
    name="search[1]__bulge",
    unique_tag="<your_galaxy>",
    n_live=100,
)

result_1 = search_1.fit(model=model_1, analysis=analysis)

print(result_1.info)

"""
__Model Chaining__

`result_1.model_centred` returns the search-1 model with every free parameter replaced by a
`TruncatedGaussianPrior` centred on that parameter's median from search 1
(`PyAutoFit:autofit/non_linear/result.py`,
`PyAutoFit:autofit/mapper/prior/truncated_gaussian.py`). Search 2 therefore starts sampling in
the region search 1 found, rather than from broad priors.

Note the attribute: `result_1.model` passes the component through with its **original** priors
unchanged, which is useful when you want the structure of a previous model but not its
constraints. `model_centred` is the one that narrows.
"""
bulge = result_1.model_centred.galaxies.galaxy.bulge
disk = af.Model(ag.lp_linear.Exponential)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)

model_2 = af.Collection(galaxies=af.Collection(galaxy=galaxy))

print(model_2.info)

"""
__Model-Fit (Search 2)__

The accurate search. Read search 2's `model.info` in the output folder to confirm the priors
arrived as intended before trusting the result.
"""
search_2 = af.Nautilus(
    path_prefix=path_prefix,
    name="search[2]__bulge_disk",
    unique_tag="<your_galaxy>",
    n_live=150,
)

result_2 = search_2.fit(model=model_2, analysis=analysis)

"""
__Result__
"""
print(result_2.info)

PLOT_DIR = Path("scripts") / "scratch" / "<your_galaxy>" / "chained"

aplt.subplot_fit_imaging(
    fit=result_2.max_log_likelihood_fit,
    output_path=str(PLOT_DIR),
    output_format="png",
)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

Whole components pass, not just single parameters: `result_1.model_centred.galaxies.galaxy.bulge`
carries every one of the bulge's parameters across in one expression, provided the component's
*type* has not changed. A single parameter passes the same way —
`galaxy.bulge.effective_radius = result_1.model_centred.galaxies.galaxy.bulge.effective_radius` —
which is how you narrow some parameters and leave others broad.

## Branch — `model`, `model_centred`, and `instance`

This is the part to get right, and the distinction is sharper than the workspace script's prose
suggests. Three attributes on a `Result`, three different things:

**`result.model`** — the same model with the **same priors it had before**. On the released stack
this attribute preserves the priors rather than narrowing them
(`PyAutoFit:autofit/non_linear/result.py`), so a component passed this way brings its structure
across but no information from the fit. That is occasionally exactly what you want — reuse the
composition, refit from scratch — but it is *not* prior passing, and reading the workspace
script's older description of it as producing narrowed Gaussians will mislead you. Check what you
actually got:

```python
print(type(model_2.galaxies.galaxy.bulge.sersic_index).__name__)
```

**`result.model_centred`** — the narrowing one. Every free parameter becomes a
`TruncatedGaussianPrior` whose `mean` is that parameter's median from the previous search and whose
`sigma` comes from the parameter's `width_modifier` in the `priors` config. Three further variants
let you override that width:

| Attribute | Prior produced | `sigma` |
|---|---|---|
| `result.model_centred` | `TruncatedGaussianPrior` | from the parameter's config `width_modifier` |
| `result.model_centred_absolute(a=0.1)` | `TruncatedGaussianPrior` | exactly `a`, for every parameter |
| `result.model_centred_relative(r=0.2)` | `TruncatedGaussianPrior` | `r × mean`, per parameter |
| `result.model_centred_max_lh_bounded(b=0.3)` | `UniformPrior` | bounds at `mean ± b` |

**`result.instance`** — the maximum-likelihood *values*, as fixed numbers. A component passed this
way has no free parameters at all, so search 2's dimensionality drops by that component's
parameter count. This is the lever for "fit the bulge, freeze it, then fit the disk against a
fixed bulge", and it is much stronger medicine than a narrow prior: the later search cannot
revisit the frozen component even if the added component would have changed it.

```python
galaxy = af.Model(
    ag.Galaxy,
    redshift=0.5,
    bulge=result_1.instance.galaxies.galaxy.bulge,  # fixed, contributes 0 parameters
    disk=af.Model(ag.lp_linear.Exponential),
)
```

The common three-stage pattern uses all of it: fit the bulge; fix it and fit the disk; then free
both from the second result's narrowed priors for a final search where everything moves together.
Freezing permanently is a real bias risk, because a bulge fitted without a disk absorbs some of
the disk's light — so the third stage is not optional if the decomposition is the result you are
quoting.

## Branch — where `sigma` comes from, and its two traps

`model_centred` reads each parameter's width from the `width_modifier` field of its entry in the
`priors` config (`autogalaxy_assistant:config/priors/`, mapped in
[`../wiki/core/api/configuration.md`](../wiki/core/api/configuration.md)). Two forms:

- **Absolute** — `sigma` is the config value directly. For a linear `Sersic`, `sersic_index`
  carries `Absolute: 1.5`, each `centre` component `Absolute: 0.05`, and each `ell_comps`
  component `Absolute: 0.2`.
- **Relative** — `sigma` is that fraction of the inferred value. `effective_radius` carries
  `Relative: 1.0`.

The reasoning behind which is which is worth understanding, because it tells you when to override.
A relative width on a centre makes no sense: a galaxy centred near `(0.0, 0.0)` would get a sigma
near zero and the next search could not move it at all. An absolute width on an `intensity` makes
no sense either, because intensity depends on units, exposure and brightness, so no single number
generalises. Hence absolute centres and relative radii.

Two traps follow directly, and both are worth stating to a user before they hit them:

**Relative widths break on parameters that can be negative or zero.**
`model_centred_relative(r=...)` applies one relative width to *every* parameter, including
`ell_comps`, whose median is legitimately near zero and often negative. That yields a negative
`sigma` and raises rather than silently misbehaving — which is the good outcome, but it does mean
the blanket relative form is unusable on a general light-profile model. Use `model_centred`
(per-parameter config widths), or `model_centred_absolute` where a single absolute width is
defensible for the parameters you are passing.

**The bounded variant does not inherit the parameter's physical limits.**
`model_centred_max_lh_bounded(b=...)` builds a `UniformPrior` at `mean ± b` regardless of the
parameter's configured limits, so a `sersic_index` inferred near its ceiling of 5.0 can come back
with an upper limit above 5.0. Set the bound with the parameter's range in mind, or clamp the
prior yourself afterwards.

The width you want is a genuine trade-off with no default that is right everywhere: wide enough
that a better nearby solution can still be found, narrow enough that the search is not doing
search-1's work over again. The shipped `width_modifier` values are a considered balance rather
than a physical truth, and overriding them for one parameter you understand well is normal.

## Branch — when chaining is the wrong tool

Chaining adds a failure mode that a single search does not have: **a wrong early result narrows a
later prior around the wrong place, and the later search never looks anywhere else.** The final
posterior then looks tight and well-behaved and is simply wrong. Three situations where a single
search is better:

- **The single search works and is merely slow.** Reach for a faster sampler, a linear light
  profile, JAX or a GPU first ([`ag_configure_search`](./ag_configure_search.md),
  [`ag_run_search`](./ag_run_search.md)). Complexity you do not need is complexity that can be
  wrong.
- **The early model is not a subset of the late one.** Prior passing assumes the parameter means
  something similar in both searches. Passing a `Sersic`'s parameters into an `Exponential`, or a
  parametric component's into a pixelised one, is either an error or meaningless.
- **The parameter you fixed early is the one you are measuring.** If a bulge fitted without a disk
  is the number going in the paper, do not chain to a frozen bulge — chain to a narrowed one and
  let the final search move it.

Always inspect the intermediate result rather than trusting the chain. `result_1.info`, and
`model.info` inside search 2's output folder, are the two things to read before believing the
final number.

## Branch — the practical mechanics

**One analysis, reused.** Build the `ag.AnalysisImaging` once, before search 1, and pass the same
object to every search — unless you are deliberately changing the data between stages (a smaller
mask early, the full one late), in which case say so explicitly, because the log likelihoods are
then not comparable across stages.

**Naming.** One `path_prefix` for the chain, and `name="search[1]__<what>"` per stage. The bracket
convention is the workspace's and it sorts correctly; the `__<what>` suffix is what makes an
output tree readable a month later.

**`unique_tag`.** Keep it identical across the chain's searches, since it identifies the *dataset*.
Each stage still lands in its own folder because `name` differs. And the identifier trap from
[`ag_configure_search`](./ag_configure_search.md) applies to every stage: it does not hash your
data's pixel values, so if you swap datasets without changing `unique_tag`, every search in the
chain silently returns the previous galaxy's result.

**Smoke test the whole chain, not one search.** A chain's characteristic bug is a mis-typed
attribute path in the passing expression, and that only fires at the second search:

```bash
PYAUTO_TEST_MODE=1 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/chained_fit.py
```

Level 1 rather than level 2 here: level 1 runs a real (tiny) search at each stage, so a `Result`
exists with samples for the next stage to pass from. Level 2 bypasses the sampler and leaves the
chain nothing meaningful to narrow around. The levels are
[`../wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md), and the priors a
test-mode chain produces are wiring evidence only — never quote them.

## Combine

- [`ag_configure_search`](./ag_configure_search.md) — cheap settings for early searches and
  accurate ones for the last; also the `unique_tag` semantics every stage inherits.
- [`ag_run_search`](./ag_run_search.md) — driving each stage and reading its output folder.
- [`ag_build_imaging_model`](./ag_build_imaging_model.md) — composing the models the chain steps
  between, including prior customisation by hand when you want to override a passed width.
- [`ag_multi_galaxy_and_cluster`](./ag_multi_galaxy_and_cluster.md) — adding galaxies one at a
  time is the most common real use of chaining.
- [`ag_multi_dataset`](./ag_multi_dataset.md) — its one-by-one branch is a chain across datasets
  rather than across model complexity.
- [`ag_debug_fit_failure`](./ag_debug_fit_failure.md) — when a single search lands somewhere
  unphysical, which is the diagnosis that most often leads here.
- `ag_pixelization` — a smooth-profile fit chained into a pixelised one is a natural pairing,
  because the pixelisation wants a decent light model to start from.

When a chain is worth keeping, offer (default-yes) to record it in a dated
`wiki/project/YYYY-MM-DD-<slug>.md` entry: why the fit was split, what each stage fitted, what was
passed as a narrowed prior versus fixed as an instance, and the shared output prefix — per
[`_style.md`](./_style.md) property #5. The split and the passing decisions are the reasoning a
reader will want, and they are invisible in the final `model.results`.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Search chaining](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_3_search_chaining/tutorial_1_search_chaining.ipynb):
  the first tutorial of the chaining chapter, which builds the idea from a fit that fails without
  it; `tutorial_2_prior_passing` then walks the prior mechanics and `tutorial_3_x2_galaxies`
  applies the chain to two galaxies.
- **General reference** — [RTD: Configs](https://pyautogalaxy.readthedocs.io/en/latest/general/configs.html):
  how the config files are laid out and looked up — the `priors` tree is where each parameter's
  `width_modifier` lives, and hence where a passed prior's `sigma` comes from.
- **Experienced PyAutoGalaxy user** — [workspace: guides/modeling/chaining.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/guides/modeling/chaining.py):
  the API overview this skill is grounded in, with its own long discussion of absolute versus
  relative widths.

## Agent procedural checklist

1. Ask whether the single search is failing or merely slow; recommend a faster search before a
   chain when it is only slow.
2. Choose the split with the user and say what each stage buys — dimensionality, settings, or a
   cheap approximation.
3. Build the dataset and one `ag.AnalysisImaging` before search 1 and reuse it, or state
   explicitly why a stage uses different data.
4. Write the whole chain into one script under one `path_prefix`, with `search[N]__<what>` names.
5. Use `result.model_centred` (or a `model_centred_*` variant) to narrow, `result.instance` to
   fix, and `result.model` only when you deliberately want the original priors back.
6. Verify what you built: print the passed prior's type, and read `model.info` in the later
   search's output folder.
7. Do not use `model_centred_relative` on a model containing `ell_comps` or a centre — it raises
   on a negative median.
8. Inspect `result_1.info` before trusting anything downstream of it.
9. If a component is frozen mid-chain, plan the final stage that frees it again before quoting its
   parameters.
10. Validate the whole chain with `PYAUTO_TEST_MODE=1` (not 2 — the chain needs samples to pass).
11. Offer the `wiki/project/` entry recording the split and the passing decisions.
