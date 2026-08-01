---
title: PyAutoFit (autofit)
sources:
  - project: PyAutoFit
    paths:
      - autofit/mapper/
      - autofit/non_linear/
      - autofit/aggregator/
      - autofit/database/
      - autofit/config/
      - pyproject.toml
      - README.md
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
last_updated: 2026-08-01
content_sha256: 61e26d39226e27ffbd64d814f18476c0fc5595d960e53539b7f82cb1d1998e58
---

# PyAutoFit — model composition + non-linear search

Project: [`PyAutoFit`](https://github.com/PyAutoLabs/PyAutoFit). Import: `autofit`,
aliased to `af` everywhere.

PyAutoFit is the *probabilistic modelling and inference* layer. PyAutoGalaxy uses it for
everything that isn't galaxy-specific: composing a parametric model out of profiles and
galaxies, running a non-linear search to fit it, and reading the resulting posterior.

PyAutoFit is **not galaxy-aware**. The model could just as easily describe a chemical
reaction network or a regression. PyAutoGalaxy supplies the galaxy-specific likelihood
via its `AnalysisImaging` / `AnalysisInterferometer` / `AnalysisEllipse` classes;
PyAutoFit handles the inference around it.

## Model composition

The two headline classes:

- **`af.Model`** — a single class wrapped in a model-aware shell. `af.Model(ag.lp.Sersic)`
  is "a Sersic profile whose parameters are free during the fit". Each parameter gets a
  default prior from the YAML config; you can override per-instance with
  `model.effective_radius = af.UniformPrior(lower_limit=0.0, upper_limit=10.0)`.
- **`af.Collection`** — an ordered collection of models. `af.Collection(galaxy=galaxy,
  extra_galaxy=extra_galaxy)` groups them with names you can address.

A galaxy-structure model is typically:

```python
galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=af.Model(ag.lp.Sersic))
model = af.Collection(galaxies=af.Collection(galaxy=galaxy))
```

Source: `PyAutoFit:autofit/mapper/prior_model/prior_model.py` and
`PyAutoFit:autofit/mapper/prior_model/collection.py`.

## Non-linear searches

PyAutoFit ships a catalogue of samplers and optimisers, all callable via the same
`search.fit(model=..., analysis=...)` interface. Headline picks:

- **`af.Nautilus`** — nested sampling; the robust default when you want a full posterior.
  Handles multimodality well.
- **`af.DynestyStatic` / `af.DynestyDynamic`** — alternative nested samplers.
- **`af.Emcee`** / **`af.Zeus`** — ensemble MCMC and ensemble slice sampling, for
  characterising a posterior you already know is unimodal.
- **`af.MultiStartProdigy` / `af.MultiStartAdam` / `af.MultiStartLion` /
  `af.MultiStartADABelief`** — JAX-native gradient MAP searches run from many starting
  points; these are the fast default in the galaxy workspace's `start_here` scripts when
  JAX is installed.
- **`af.LBFGS`** / **`af.BFGS`** / **`af.Drawer`** — gradient descent / random draws
  (initialisation and debugging).
- **`af.BlackJAXNUTS`** — Hamiltonian Monte Carlo via blackjax (optional dependency).

Sources: `PyAutoFit:autofit/non_linear/search/`.

## Samples and aggregator

After a fit, PyAutoFit produces a `Samples` object holding every accepted sample, and
writes a CSV + JSON manifest to disk. The aggregator
(`PyAutoFit:autofit/aggregator/`) iterates over many fits without loading them all into
memory at once — useful when you've run hundreds of fits and want summary statistics.
PyAutoGalaxy layers galaxy-aware loading on top via `ag.agg`.

For bulk querying of large numbers of fits, the SQLAlchemy-backed database in
`autofit/database/` exists.

## Configuration

`autofit/config/` ships `general.yaml`, `logging.yaml`, `notation.yaml`, `output.yaml`,
plus search defaults under `non_linear/`, default prior YAMLs under `priors/`, and plot
settings under `visualize/`. The prior YAMLs are how the model system knows that the
`effective_radius` parameter of `ag.lp.Sersic` defaults to a uniform prior between 0.0
and 30.0 (`PyAutoGalaxy:autogalaxy/config/priors/light/standard/sersic.yaml`) — or
whatever the workspace config says instead.

## Dependencies

`autonerves`, `array_api_compat`, plus a deep scientific stack — `anesthetic`, `corner`,
`dynesty`, `emcee`, `h5py`, `SQLAlchemy`, `scipy`, `networkx`, `pyvis`, `psutil`,
`xxhash`, `threadpoolctl`. Optional extras: `astropy`, `getdist`, `nautilus-sampler`,
`zeus-mcmc`, `blackjax`, and `optax` (via `autofit[jax]`, needed by the `MultiStart*`
gradient searches).

The heavier samplers are optional on purpose; install them when you need them.

## See also

- [`stack/autogalaxy`](./autogalaxy.md) — the `Analysis` classes that supply the
  log-likelihood PyAutoFit maximises.
- [`stack/autonerves`](./autonerves.md) — the loader behind the prior YAMLs.
- [`stack/overview`](./overview.md) — where autofit sits in the dependency chain.
