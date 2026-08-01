---
title: Hierarchical and graphical models over galaxy samples
sources:
  - project: PyAutoFit
    paths:
      - autofit/graphical/
      - autofit/graphical/declarative/factor/hierarchical.py
      - autofit/graphical/declarative/factor/analysis.py
      - autofit/graphical/declarative/collection.py
      - autofit/graphical/expectation_propagation/
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: autogalaxy_workspace
    paths:
      - scripts/multi_dataset/start_here.py
      - scripts/multi_dataset/modeling.py
      - scripts/guides/results/aggregator/queries.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: d8a9ef07484c5a5da3e722145297413baad159728e053161611c668f2eee4539
---

# Hierarchical and graphical models over galaxy samples

Fitting one galaxy gives a posterior on that galaxy. Fitting a *sample* of galaxies with a model
that links them gives a posterior on the **population** — the mean Sersic index of early types
at some stellar mass, the intrinsic scatter in a size–mass relation, the distribution of
boxiness across a morphological class. The linking machinery is PyAutoFit's graphical-model
framework: one factor per galaxy, plus shared or parent-distribution nodes.

Source: `PyAutoFit:autofit/graphical/`.

> **Grounding note.** The `autogalaxy_workspace` has no dedicated hierarchical-model example
> today; `autogalaxy_workspace:scripts/multi_dataset/modeling.py` notes only that the factor
> graph it builds "supports advanced hierarchical and probabilistic modeling for large,
> multi-dataset analyses". This page is therefore **conceptual**, with every `af.*` symbol
> verified against the installed PyAutoFit but the *galaxy-structure* composition left to you.
> Treat the code below as the shape of the API, not as a script lifted from a validated example,
> and check `model.info` at every step. The repo-root [`PENDING.md`](../../../PENDING.md) is
> where a grounded worked example would be tracked.

## What "hierarchical" means

In a hierarchical model each galaxy keeps its own local parameters, but some of those parameters
are treated as **draws from a shared parent distribution** whose own parameters are inferred from
the whole sample at once.

The statistical payoff is **shrinkage**: a noisy individual measurement borrows strength from the
ensemble. A galaxy whose Sersic index is only weakly constrained by its own data is pulled toward
the population mean, by an amount set by the relative width of its likelihood and the parent
distribution — without being *forced* to equal it, as fixing the parameter would.

The scientific payoff is different and often larger: the parent distribution's **width** is a
measurement in its own right. Fitting galaxies independently and then taking the sample standard
deviation of the results overestimates the intrinsic scatter, because it adds the measurement
errors in quadrature. A hierarchical fit separates intrinsic scatter from measurement error by
construction, which is exactly the quantity a population study usually wants.

Galaxy-structure examples of a hierarchically shared quantity:

- a population mean and intrinsic scatter for the Sersic index of a morphological class;
- the slope and scatter of a size–luminosity or size–stellar-mass relation;
- the distribution of `m = 4` boxiness amplitudes across a sample of ellipticals;
- a shared bulge-to-total ratio distribution across an environment-selected sample.

## When it is worth it

It is not free, and for a small sample it is often not worth it.

Prefer a hierarchical fit when the sample is large, the individual measurements are noisy, and
the population-level quantity (particularly a scatter) is the science. Prefer independent fits
plus a careful downstream analysis when the sample is small, each galaxy is well constrained, or
you want per-galaxy results that are demonstrably uncontaminated by an assumed population prior —
because that is the cost: a hierarchical result depends on the parametric form you chose for the
parent distribution, and a badly chosen one (a Gaussian imposed on a bimodal population, say)
will bias every individual galaxy toward a mode that does not exist. Fit the galaxies
independently first and *look* at the distribution before choosing a parent form.

## Composing the graph

The composition builds on the ordinary multi-dataset pattern
([`multi_wavelength`](./multi_wavelength.md)), with the difference that each factor now carries a
*different galaxy*, not a different view of one:

```python
import autofit as af

analysis_factor_list = []

for model_galaxy, analysis in zip(model_galaxy_list, analysis_list):
    analysis_factor_list.append(
        af.AnalysisFactor(prior_model=model_galaxy, analysis=analysis)
    )

factor_graph = af.FactorGraphModel(*analysis_factor_list)

result_list = search.fit(model=factor_graph.global_prior_model, analysis=factor_graph)
```

`af.AnalysisFactor` and `af.FactorGraphModel` are the same objects the multi-dataset fits use
(`PyAutoFit:autofit/graphical/declarative/`), which is the point: a graphical model is not a
separate API but the general case of which multi-dataset fitting is a special case.

Two ways to link parameters across factors:

- **Identify them.** Reuse the *same* prior object in more than one factor's model and the graph
  treats it as one parameter shared by all of them. This is a hard tie — every galaxy takes the
  identical value — appropriate for something genuinely common (an instrument-level nuisance),
  not for a population property.
- **Draw them from a parent distribution.** `af.HierarchicalFactor` associates a set of
  per-galaxy parameters with a distribution whose own parameters are themselves inferred:

```python
import autofit as af

hierarchical_factor = af.HierarchicalFactor(
    af.GaussianPrior,
    mean=af.GaussianPrior(mean=4.0, sigma=2.0),
    sigma=af.GaussianPrior(mean=1.0, sigma=0.5),
)

for model_galaxy in model_galaxy_list:
    hierarchical_factor.add_drawn_variable(model_galaxy.bulge.sersic_index)

factor_graph = af.FactorGraphModel(*analysis_factor_list, hierarchical_factor)
```

`PyAutoFit:autofit/graphical/declarative/factor/hierarchical.py`. The first argument is the
**distribution class** (a `Prior` subclass, so `af.GaussianPrior`, `af.LogUniformPrior`, …) and
the keyword arguments are its own parameters, which may be priors — giving the hyperparameters
their own posteriors. `add_drawn_variable(prior)` then registers one per-galaxy parameter as a
draw from it. A `HierarchicalFactor` is passed to `af.FactorGraphModel` alongside the analysis
factors, because it too is a factor in the graph.

Two API notes. The method is **`add_drawn_variable`**; older documentation, including a docstring
in the source itself, shows `add_sampled_variable`, which does not exist on the installed class —
verify against `dir(af.HierarchicalFactor)` if in doubt. And a `HierarchicalFactor` internally
generates one factor per drawn variable rather than a single high-dimensional one, which is what
keeps the optimisation tractable as the sample grows.

Choose the parent distribution for what the parameter *is*: a `GaussianPrior` parent for a
quantity that can take any sign (a multipole amplitude, a colour gradient), a log-space parent
for a positive scale quantity like an effective radius, where a Gaussian would put prior mass on
impossible values.

## Joint sampling versus expectation propagation

Two regimes for actually fitting the graph.

**Joint sampling** puts every local and global parameter into one search. Conceptually simple,
and the right choice while the total dimensionality is manageable. But it grows linearly with the
sample: 50 galaxies with 6 parameters each plus 2 hyperparameters is a 302-dimensional search,
which is beyond what nested sampling handles well.

**Expectation propagation (EP)** factorises the problem instead. Each galaxy is fitted
individually and the factors exchange *messages* about the shared hyperparameters, iterating
until the global posterior stabilises. Cost then scales with the number of galaxies rather than
with the dimension of a monolithic search, which is what makes hundreds or thousands of galaxies
feasible. The framework lives in `PyAutoFit:autofit/graphical/expectation_propagation/`; it is
driven through `factor_graph.optimise(optimiser=...)` with an optimiser such as
`af.LaplaceOptimiser`, and `af.EPHistory` records the iteration history you diagnose from. The
formal treatment is Bishop-style variational inference;
`PyAutoFit:autofit/graphical/README.md` ties each step to its equations.

Practical guidance: use a joint fit if it fits, because it has fewer moving parts. Move to EP
when it does not. When you do, cross-check EP against a joint fit on a **reduced** sample where
both are affordable — if they disagree there, the EP configuration is wrong, not the science.
Watch for the shared-parameter posterior stabilising across iterations and for messages between
factors remaining consistent.

## Feeding it

A hierarchical model consumes many per-galaxy fits, so the aggregator is the natural front end:
it yields `Samples`, `Model` and dataset objects one fit at a time, and its query tools select
the sub-sample you want to model jointly
(`autogalaxy_workspace:scripts/guides/results/aggregator/queries.py`). See
[`../api/aggregator`](../api/aggregator.md) and
[`samples_and_posteriors`](./samples_and_posteriors.md).

One warning that matters more here than anywhere else: if the per-galaxy parameter you intend to
share is a **solved** quantity — a linear profile's `intensity`, a basis amplitude, a mesh flux —
it is not a sampled parameter and cannot be handed to a `HierarchicalFactor` directly. Share a
sampled parameter instead (a shape parameter), or reformulate so that the population quantity is
built from sampled ones. See
[`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md).

## See also

- [`multi_wavelength`](./multi_wavelength.md) — the same factor-graph API for many views of one
  galaxy; read it first.
- [`../api/aggregator`](../api/aggregator.md) — assembling the per-galaxy fits.
- [`samples_and_posteriors`](./samples_and_posteriors.md) — per-galaxy posteriors and derived
  quantities.
- [`non_linear_search`](./non_linear_search.md) — the searches a graph is fitted with.
- [`../stack/autofit`](../stack/autofit.md) — the graphical-model layer in context.
- [`../../../PENDING.md`](../../../PENDING.md) — where a grounded worked example is tracked.
