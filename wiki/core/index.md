---
title: Core wiki — PyAuto* reference
sources: []
last_updated: 2026-08-01
content_sha256: 211c1db15cf6cd3f6997ded834a0c43ca61c1e19ad4e3377f865a0a08a334fff
---

# Core wiki — PyAuto\* reference

The reference layer for everything an agent needs to know about the PyAuto\* stack when
helping a user model galaxy structure. Skills in [`../../skills/`](../../skills/) link in
here for the *what* / *which* / *why*.

## Stack

- [The stack at a glance](./stack/overview.md) — dependency chain, who imports whom.
- [PyAutoNerves](./stack/autonerves.md) — layered YAML config loader, JSON/FITS I/O.
- [PyAutoArray](./stack/autoarray.md) — arrays, grids, masks, datasets, inversions.
- [PyAutoFit](./stack/autofit.md) — model composition, non-linear search, samples.
- [PyAutoGalaxy](./stack/autogalaxy.md) — light profiles, galaxies, ellipse fitting,
  pixelised reconstruction, analysis objects.

## Coming in later phases

This sub-wiki is being built out in stages, and the stack pages above are all that exist
today. Still to come:

- **`concepts/`** — light profiles, grids and masks, basis expansions and MGE, ellipse
  fitting, inversions, non-linear search, samples and posteriors, cosmology and units.
- **`api/`** — task-oriented catalogues: every search, every light profile, every mass
  profile, datasets, plotting entry points, analysis objects, the aggregator.
- **`operations/`** — installation, dataset layout, sandbox / restricted environments,
  HPC.
- **`external/`** — routing into HowToGalaxy, the RTD docs and the
  `autogalaxy_workspace` script catalogue.

Nothing links to those directories yet, deliberately: a dangling link in a reference
wiki is worse than an honest gap. The repo-root `PENDING.md` is the authoritative list of
what is still missing and what grounds each page when it is written. Until a page lands,
ground an answer in the installed source (or the `autogalaxy_workspace` scripts) and say
that you did.
