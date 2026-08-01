---
title: The PyAuto* stack at a glance
sources:
  - project: PyAutoNerves
    paths: [pyproject.toml]
    pinned_commit: e82c17fd6c8966f6b3a2f6ffbcb655db7035fdb1
  - project: PyAutoArray
    paths: [pyproject.toml]
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: PyAutoFit
    paths: [pyproject.toml]
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: PyAutoGalaxy
    paths: [pyproject.toml]
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
last_updated: 2026-08-01
content_sha256: 788bfa6fbedb78a418f4610fe3b37d36e27301e23547aa1a18249dde3eefbaf4
---

# The PyAuto\* stack at a glance

Four libraries, one chain. Each builds on the one below it; PyAutoGalaxy is the
user-facing library you write code against, and the layers below surface only when you
need to understand something specific.

```
autonerves     configuration: layered YAML loader, prior + class registry, JSON/FITS I/O
   ↓
autoarray      data: arrays, grids, masks, geometry, datasets, inversions
   ↓
autofit        modelling: af.Model / af.Collection, non-linear searches, samples
   ↓
autogalaxy     galaxies: light profiles, galaxies, ellipse fitting, analysis objects
```

## Who does what

- **autonerves** ([page](./autonerves.md)) — reads `<pkg>/config/*.yaml` files for
  default priors, plotting defaults, output paths, and provides the JSON/FITS
  serialisation helpers. Every other library uses it.
- **autoarray** ([page](./autoarray.md)) — defines `Array2D`, `Grid2D`, `Mask2D`,
  `Imaging`, `Interferometer`, plus the geometry / over-sampling / inversion machinery
  the galaxy analyses rely on.
- **autofit** ([page](./autofit.md)) — model composition via `af.Model` /
  `af.Collection`, a catalogue of non-linear searches, a `Samples` API for the
  posterior, and an aggregator for bulk results.
- **autogalaxy** ([page](./autogalaxy.md)) — the structure of a galaxy: a catalogue of
  light profiles (Sersic, Exponential, Gaussian, Moffat, Shapelets…), basis expansions
  (MGE), `Galaxy` / `Galaxies`, ellipse fitting, pixelised reconstruction, and the
  `AnalysisImaging` / `AnalysisInterferometer` / `AnalysisEllipse` likelihoods.

## Imports you see everywhere

```python
import autofit as af
import autogalaxy as ag
import autogalaxy.plot as aplt
```

The aliases are conventional — every workspace script uses them, and so do the skills
here. PyAutoGalaxy re-exports the data structures it needs from autoarray, so
`ag.Grid2D`, `ag.Mask2D` and `ag.Imaging` are the same classes autoarray defines: you
almost never import `autoarray` yourself.

## Cross-package dependencies

| Package | Depends on |
|---|---|
| autonerves | (none from this stack) |
| autoarray | autonerves |
| autofit | autonerves, array_api_compat |
| autogalaxy | autofit, autoarray |

Installing PyAutoGalaxy via pip pulls in the three below it automatically.

## When to look at which page

- *"What is a `Mask2D`, and what does slim vs. native mean?"* →
  [autoarray](./autoarray.md).
- *"Where does the default prior for a Sersic parameter come from?"* →
  [autonerves](./autonerves.md) for the loader, [autofit](./autofit.md) for how the
  model reads it.
- *"Which non-linear searches can I use?"* → [autofit](./autofit.md).
- *"What light profiles ship out of the box?"* → [autogalaxy](./autogalaxy.md).
- *"How do I fit isophotal ellipses instead of a parametric profile?"* →
  [autogalaxy](./autogalaxy.md).

## See also

- [`stack` pages](./autogalaxy.md) — one page per library, linked above.
- [Core wiki index](../index.md) — what else this sub-wiki covers.
