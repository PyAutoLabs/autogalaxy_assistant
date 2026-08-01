---
title: Configuration — the config/ tree
sources:
  - project: PyAutoNerves
    paths:
      - autonerves/conf.py
      - autonerves/directory_config.py
      - autonerves/workspace.py
    pinned_commit: e82c17fd6c8966f6b3a2f6ffbcb655db7035fdb1
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/config/
      - autogalaxy/config/priors/
      - autogalaxy/config/visualize/
      - autogalaxy/__init__.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: PyAutoFit
    paths:
      - autofit/config/
      - autofit/config/priors/
      - autofit/config/non_linear/
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: PyAutoArray
    paths:
      - autoarray/config/
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: autogalaxy_assistant
    paths:
      - config/README.md
      - config/general.yaml
      - config/notation.yaml
      - config/output.yaml
      - config/latent.yaml
      - config/logging.yaml
      - config/non_linear/GridSearch.yaml
      - config/priors/README.md
      - config/priors/light/standard/sersic.yaml
      - config/priors/ellipse/ellipse.yaml
      - config/visualize/general.yaml
      - config/visualize/plots.yaml
      - config/visualize/plots_search.yaml
    pinned_commit: ed72fabb33e14a9a701a4d280e8775dd3a20e98c
last_updated: 2026-08-01
content_sha256: bdc7d14e2ec2fc6d73b703baa17299f0bb00f69a4dcdb3410fe68f14c564a8d8
---

# Configuration

Almost every default in the stack — the prior on a Sersic's `effective_radius`, the colormap of a
figure, how often a search writes output, which figures a fit produces — comes from a YAML file,
not from Python. PyAutoNerves finds and merges those files; the libraries query the result.

**This repository ships a live `config/` tree at its root**, derived from
`autogalaxy_workspace`'s. When you run a script from this repo's root directory, that tree is the
highest-priority config, so editing a file in it changes behaviour immediately and repo-wide. That
is the intended place to record project defaults — not the library YAMLs inside site-packages.

## How the layering works

`conf.instance` holds an ordered list of `config/` directories and **the first match wins**. The
default instance is built from the current working directory:

```python
current_directory = Path(os.getcwd())

default = Config(
    current_directory / "config", output_path=current_directory / "output/"
)
```

Source: `PyAutoNerves:autonerves/conf.py`. Each library then registers its own defaults *behind*
that entry — `autogalaxy/__init__.py`, `autofit/__init__.py` and `autoarray/__init__.py` each call
`conf.instance.register(__file__)`, which pushes `<pkg>/config/` in with `keep_first=True` so the
working directory keeps priority (`PyAutoGalaxy:autogalaxy/__init__.py`).

So the resolution order is:

1. **`<cwd>/config/`** — this repo's `config/` when you run from the repo root. Highest priority.
2. **`<pkg>/config/`** for each library — `autogalaxy`, `autofit`, `autoarray` — as fallbacks.

Two practical consequences:

- **Run from the repo root.** The config path is resolved from `os.getcwd()` at import time, so
  running a script from a subdirectory silently drops this repo's overrides and you get library
  defaults instead. Output goes to `<cwd>/output/` for the same reason.
- **To add another directory at runtime**, use `conf.instance.push(new_path, output_path=None,
  keep_first=False)`. It raises if the path does not exist or contains no `.yaml` / `.yml` /
  `.json` / `.ini` file, so a typo fails loudly rather than silently reverting to defaults. This is
  what the Colab and notebook setup helpers do.

More on the loader: [`../stack/autonerves`](../stack/autonerves.md).

## What each library ships

The file set differs per package — not every package has every YAML:

| Package | Ships |
|---|---|
| `PyAutoArray:autoarray/config/` | `general.yaml`, `logging.yaml`, `visualize/` |
| `PyAutoFit:autofit/config/` | `general.yaml`, `logging.yaml`, `notation.yaml`, `output.yaml`, `non_linear/`, `priors/`, `visualize/` |
| `PyAutoGalaxy:autogalaxy/config/` | `general.yaml`, `latent.yaml`, `notation.yaml`, `output.yaml`, `priors/`, `visualize/` |

Note `PyAutoGalaxy:autogalaxy/config/` has **no** `non_linear/` and no `logging.yaml` — search
defaults and logging come from `PyAutoFit:autofit/config/`, and the galaxy library adds priors,
notation, output and visualisation on top.

## This repository's `config/`

91 files at the repo root. The tree:

```
config/
├── README.md
├── general.yaml
├── latent.yaml
├── logging.yaml
├── notation.yaml
├── output.yaml
├── non_linear/
│   └── GridSearch.yaml
├── priors/
│   ├── basis.yaml, cosmology.yaml, dataset_model.yaml, point_sources.yaml
│   ├── ellipse/       (ellipse.yaml, ellipse_multipole.yaml)
│   ├── galaxy/        (redshift.yaml)
│   ├── light/         (standard/, linear/, linear_operated/, operated/, shapelets/)
│   ├── mass/          (total/, dark/, stellar/, sheets/, point/)
│   ├── mesh/          (delaunay, rectangular_uniform, rectangular_adapt_*)
│   └── regularization/
└── visualize/
    ├── general.yaml
    ├── plots.yaml
    └── plots_search.yaml
```

Every folder carries its own `README.md` explaining what it controls
(`autogalaxy_assistant:config/README.md`, `autogalaxy_assistant:config/priors/README.md`,
`autogalaxy_assistant:config/priors/ellipse/README.md`,
`autogalaxy_assistant:config/visualize/README.md`,
`autogalaxy_assistant:config/non_linear/README.md`) — read those first, this page is the map.

## Priors

A prior YAML is one file per source module, one block per class, one entry per parameter. From
`autogalaxy_assistant:config/priors/light/standard/sersic.yaml`:

```yaml
Sersic:
  effective_radius:
    type: Uniform
    lower_limit: 0.0
    upper_limit: 30.0
    width_modifier:
      type: Relative
      value: 1.0
    limits:
      lower: 0.0
      upper: inf
  sersic_index:
    type: Uniform
    lower_limit: 0.8
    upper_limit: 5.0
    width_modifier:
      type: Absolute
      value: 1.5
    limits:
      lower: 0.8
      upper: 5.0
```

Three keys per parameter:

- **`type`** — the prior class: `Uniform`, `Gaussian`, `TruncatedGaussian`, `LogUniform`, each with
  its own fields (`lower_limit` / `upper_limit`, or `mean` / `sigma`). This is what
  `af.Model(ag.lp.Sersic)` picks up. Note the real defaults are not naive: `intensity` is
  `LogUniform` over six decades because brightness spans orders of magnitude, `centre_0` /
  `centre_1` are `Gaussian(mean=0.0, sigma=0.3)` because the data-preparation convention centres
  the galaxy at the origin, and `ell_comps` are `TruncatedGaussian` clipped to ±1 because that is
  their valid range.
- **`width_modifier`** — how wide the passed prior becomes when one search's result seeds the next.
  `Absolute` adds a fixed width, `Relative` a fraction of the inferred value. This is the knob that
  governs search chaining (`autogalaxy_workspace:scripts/guides/modeling/chaining.py`).
- **`limits`** — hard physical bounds the passed `GaussianPrior` may not cross. `sersic_index` is
  capped at `[0.8, 5.0]`, so chaining can never propose an unphysical index.

`PyAutoFit:autofit/config/priors/` holds the meta-templates the per-class files are shaped from.

**Where the folders map to.** `priors/light/` and `priors/mass/` mirror the source layout
described in [`light_profile_catalog`](./light_profile_catalog.md) and
[`mass_profile_catalog`](./mass_profile_catalog.md) — `standard/`, `linear/`, `operated/`,
`linear_operated/` and a separate `shapelets/` folder for the shapelet bases. `priors/ellipse/`
holds `Ellipse` and `EllipseMultipole` (see [`ellipse`](./ellipse.md)); `priors/galaxy/redshift.yaml`
the `ag.Galaxy` redshift; `priors/mesh/` and `priors/regularization/` the pixelisation components;
`priors/dataset_model.yaml` the `ag.DatasetModel` nuisance parameters; `priors/cosmology.yaml` and
`priors/basis.yaml` the cosmology and basis-expansion defaults.

**Two ways to override.** Permanently and repo-wide, edit the YAML in this repo's `config/priors/`.
Per fit, set the prior on the model instance instead:

```python
sersic = af.Model(ag.lp.Sersic)
sersic.intensity = af.UniformPrior(lower_limit=0.01, upper_limit=10.0)
```

Prefer the second for anything specific to one dataset; the first is for a convention you want every
fit in the project to inherit. See [`analysis_objects`](./analysis_objects.md).

To add priors for a class of your own, copy the structure of an existing file — one YAML per
module, one block per class.

## `general.yaml`

The biggest file, and the one worth reading once end to end
(`autogalaxy_assistant:config/general.yaml`). The sections that come up most:

| Section | Controls |
|---|---|
| `updates` | `iterations_per_quick_update`, `iterations_per_full_update`, `quick_update_background`, `live_visual_update` — the cadence every search inherits when you do not pass it explicitly (see [`searches`](./searches.md)) |
| `hpc` | `hpc_mode` plus its own `updates` overrides; both display flags are deliberately off, because HPC nodes are headless |
| `inversion` | `check_reconstruction`, `use_positive_only_solver`, `use_edge_zeroed_pixels`, `use_border_relocator`, `no_regularization_add_to_curvature_diag_value`, `reconstruction_vmax_factor` — the defaults `ag.Settings(...)` overrides per fit |
| `output` | `info_whitespace_length` (the alignment of `model.info` / `result.info`), `model_results_decimal_places`, `samples_to_csv`, `log_level`, `log_to_file`, `force_visualize_overwrite`, `remove_files` |
| `grid` | `max_evaluation_grid_size` — caps the adaptive grid used for derived quantities |
| `psf` | `use_fft_default` — FFT convolution by default, faster except for very small kernels |
| `numba`, `parallel`, `profiling`, `structures`, `test` | runtime and diagnostic switches |
| `version` | `minimum_library_version` — the **compatibility floor**, the oldest library release whose API these scripts need, plus `workspace_version_check` |

That `version` block is checked at import by `PyAutoNerves:autonerves/workspace.py`, which warns
when the installed library and this config disagree. Bump `minimum_library_version` deliberately —
only when a script starts needing new API — and never per release. This is a different mechanism
from the assistant's own API baseline (`wiki/core/api_audit_baseline.json`), which pins the
*documented* API surface rather than a compatibility floor.

If a `model.info` printout wraps awkwardly on your screen, `info_whitespace_length` under `output`
is the fix — and the Jupyter kernel needs a restart for it to take effect.

## `visualize/`

Three files (`autogalaxy_assistant:config/visualize/`):

- **`general.yaml`** — appearance: the default `colormap`, the matplotlib backend,
  `ticks -> number_of_ticks_2d`, `colorbar -> labelsize` / `labelsize_subplot`,
  `contour -> total_contours`, `units -> cb_unit`, `subplot_shape_to_figsize_factor`. Anything you
  do not pass to an `aplt` function comes from here.
- **`plots.yaml`** — **which figures a model-fit outputs automatically**, as `true` / `false`
  switches grouped by object: `dataset`, `fit`, `galaxies`, `inversion`, `adapt`,
  `fit_interferometer`, `fit_ellipse`. Two top-level keys govern all of them: `subplot_format`
  (e.g. `[png]`, or `[png, pdf]`) and `fits_are_zoomed`, which crops output FITS to the unmasked
  region to save disk. This is how you turn a figure on or off for every fit without touching code.
- **`plots_search.yaml`** — the same for search figures, grouped by search family (`nest`, `mcmc`,
  `mle`): `corner_anesthetic` for nested samplers, `corner_cornerpy` for the others.

The old `mat_wrap_1d/` and `mat_wrap_2d/` folders belonged to the removed object-oriented plotting
system and no longer exist. Full plotting API: [`plotting`](./plotting.md).

## `notation.yaml`, `output.yaml`, `latent.yaml`, `logging.yaml`

- **`notation.yaml`** — the short labels and LaTeX strings parameters get in figures and tables:
  `sersic_index` renders as `n`, and superscripts come from the name you gave the component in the
  model. Change these to match your paper's conventions
  (`autogalaxy_assistant:config/notation.yaml`).
- **`output.yaml`** — what a fit writes into its output folder, and under what filenames
  (`autogalaxy_assistant:config/output.yaml`).
- **`latent.yaml`** — which latent variables (quantities derived from the model rather than sampled)
  are computed and stored per fit (`autogalaxy_assistant:config/latent.yaml`).
- **`logging.yaml`** — logger levels and handlers; the place to silence a noisy dependency
  (`autogalaxy_assistant:config/logging.yaml`).

## `non_linear/`

Per-search defaults ship with **PyAutoFit** (`PyAutoFit:autofit/config/non_linear/`), so this repo's
`config/non_linear/` holds only workspace-level overrides — currently
`autogalaxy_assistant:config/non_linear/GridSearch.yaml`, which sets the default
`number_of_cores` and the `step_size` (in unit-prior values) of a grid search. See
[`searches`](./searches.md).

## Common tasks

| Task | Where |
|---|---|
| Tighten a default prior for every fit | `config/priors/<family>/<module>.yaml` |
| Tighten a prior for one fit | on the `af.Model` in code |
| Control how chained priors widen | `width_modifier` in the same prior YAML |
| Change the default colormap or tick count | `config/visualize/general.yaml` |
| Stop a figure being output on every fit | `config/visualize/plots.yaml` |
| Change how often a search writes output | `updates:` in `config/general.yaml` |
| Change inversion solver defaults | `inversion:` in `config/general.yaml`, or `ag.Settings(...)` per fit |
| Rename a parameter's plot label | `config/notation.yaml` |
| Quieten logging | `config/logging.yaml`, or `output -> log_level` in `config/general.yaml` |
| Declare the API floor these scripts need | `version:` in `config/general.yaml` |

## See also

- [`../stack/autonerves`](../stack/autonerves.md) — the loader and its serialisation siblings.
- [`analysis_objects`](./analysis_objects.md) — `ag.Settings` and per-fit prior overrides.
- [`searches`](./searches.md) — the update cadence and grid-search defaults.
- [`plotting`](./plotting.md) — the functions the `visualize/` YAMLs configure.
- [`light_profile_catalog`](./light_profile_catalog.md) ·
  [`mass_profile_catalog`](./mass_profile_catalog.md) · [`ellipse`](./ellipse.md) — the classes
  whose priors live under `config/priors/`.
