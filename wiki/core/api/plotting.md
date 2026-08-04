---
title: Plotting — the functional aplt API
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/plot/__init__.py
      - autogalaxy/util/plot_utils.py
      - autogalaxy/imaging/plot/fit_imaging_plots.py
      - autogalaxy/interferometer/plot/fit_interferometer_plots.py
      - autogalaxy/ellipse/plot/fit_ellipse_plots.py
      - autogalaxy/galaxy/plot/galaxies_plots.py
      - autogalaxy/galaxy/plot/galaxy_plots.py
      - autogalaxy/galaxy/plot/adapt_plots.py
      - autogalaxy/profiles/plot/basis_plots.py
    pinned_commit: 13d3023cc312ce3e523598a024cb8430fe6f8ab8
  - project: PyAutoArray
    paths:
      - autoarray/dataset/plot/imaging_plots.py
      - autoarray/dataset/plot/interferometer_plots.py
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: PyAutoFit
    paths:
      - autofit/non_linear/plot/mle_plotters.py
      - autofit/non_linear/plot/nest_plotters.py
      - autofit/non_linear/plot/samples_plotters.py
      - autofit/non_linear/plot/plot_util.py
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/plot/start_here.py
      - scripts/guides/plot/plotters.py
      - scripts/guides/plot/visuals.py
      - scripts/guides/plot/searches.py
      - scripts/imaging/plot.py
      - scripts/interferometer/plot.py
      - scripts/ellipse/plot.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-04
content_sha256: c1ab38012f55f52d0f254184bc3bf1b11ef45b31b860b102ba95921c445c01ec
---

# Plotting

The plotting API is **functional only**. There is one import:

```python
import autogalaxy.plot as aplt
```

and a flat set of module-level functions behind it. `dir(aplt)` is the authoritative list, and the
tables below were enumerated from it.

**There are no plotter classes and no figure-configuration objects.** No `FitImagingPlotter`, no
`ImagingPlotter`, no `GalaxyPlotter`, no `MatPlot2D`, no `Include2D`, no `Output`. They were
removed, and reconstructing them from memory is the single most common stale-API error in this
library — older releases are heavily represented in model training data. If a call you remember is
not in `dir(aplt)`, it is not part of the current API.

The pattern is uniform: compute a quantity from a PyAutoGalaxy object via its own method, then pass
the result to a function.

```python
aplt.plot_array(array=galaxy.image_2d_from(grid=grid), title="Galaxy Image")
```

Adapted from `autogalaxy_workspace:scripts/guides/plot/start_here.py`. Because the plotting layer
takes plain arrays and grids, anything the library can compute you can plot — no dedicated plotter
per object is needed.

## The two fundamental functions

### `aplt.plot_array`

```python
aplt.plot_array(
    array=dataset.data,
    title="Data",
    output_path=Path("output") / "plot",
    output_filename="data",
    output_format="png",
)
```

Full signature (`PyAutoGalaxy:autogalaxy/util/plot_utils.py`):
`plot_array(array, title="", output_path=None, output_filename="array", output_format=None,
colormap="default", use_log10=False, vmin=None, vmax=None, symmetric=False, positions=None,
lines=None, line_colors=None, grid=None, cb_unit=None, ax=None)`.

### `aplt.plot_grid`

```python
aplt.plot_grid(grid=dataset.grid, title="Grid2D of Masked Dataset")
```

Signature: `plot_grid(grid, title="", output_path=None, output_filename="grid",
output_format=None, lines=None, ax=None)`.

## Subplot functions

Every one takes `output_path`, `output_format` and `title_prefix` directly. Most also take
`colormap` and `use_log10` — but the `_list` variants (`subplot_fit_imaging_list`,
`subplot_imaging_dataset_list`) do **not**, taking only
`(<the list>, output_path, output_filename, output_format, title_prefix)`. **They do not share
a naming kwarg** either, and passing the wrong one raises `TypeError`:

| How the file is named | Functions |
|---|---|
| `output_filename` | `subplot_imaging_dataset`, `subplot_imaging_dataset_list`, `subplot_fit_imaging_list`, `subplot_interferometer_dataset`, `subplot_interferometer_dirty_images` (plus `plot_array` and `plot_grid` above) |
| `auto_filename` (default `"galaxies"`) | `subplot_galaxies` |
| **fixed stem**, no naming kwarg | everything else |

The fixed stems, read off `_save_subplot(...)` in each function (`subplot_fit_imaging_list` is
the exception among the fit subplots — it names its own file):
`subplot_fit_imaging` and `subplot_fit_interferometer` → `fit`;
`subplot_fit_imaging_of_galaxy` → `of_galaxy_<galaxy_index>`;
`subplot_galaxy_images` → `galaxy_images`; `subplot_galaxy_light_profiles` → `image`;
`subplot_galaxy_mass_profiles` → the quantity it drew (`convergence`, `potential`,
`deflections_y`, `deflections_x` — one file per enabled flag);
`subplot_basis_image` → `basis_image`; `subplot_adapt_images` → `adapt_images`;
`subplot_fit_real_space` → `fit_real_space`; `subplot_fit_dirty_images` → `fit_dirty_images`;
`subplot_fit_ellipse` → `fit_ellipse`; `subplot_ellipse_errors` → `ellipse_errors`.

So for a fixed-stem subplot the **directory** is what distinguishes one context from another —
give each fit, or each variant of a figure, its own folder.

### Datasets

| Function | Plots |
|---|---|
| `aplt.subplot_imaging_dataset` | data, noise-map, PSF, S/N and over-sampling panels |
| `aplt.subplot_imaging_dataset_list` | the same for a list of datasets, side by side |
| `aplt.subplot_interferometer_dataset` | visibility-plane overview |
| `aplt.subplot_interferometer_dirty_images` | inverse-transformed real-space views of the data |

Sources: `PyAutoArray:autoarray/dataset/plot/imaging_plots.py` and
`PyAutoArray:autoarray/dataset/plot/interferometer_plots.py`.

### Galaxies and profiles

| Function | Plots |
|---|---|
| `aplt.subplot_galaxies` | the summed image of an `ag.Galaxies`, plus per-galaxy panels |
| `aplt.subplot_galaxy_images` | the individual galaxy images of an `ag.Galaxies` |
| `aplt.subplot_galaxy_light_profiles` | one galaxy, one panel per light profile — the bulge/disk/bar decomposition |
| `aplt.subplot_galaxy_mass_profiles` | one galaxy's convergence, potential and deflection components; toggled by the `convergence` / `potential` / `deflections_y` / `deflections_x` flags |
| `aplt.subplot_basis_image` | each profile of an `ag.lp_basis.Basis` — how an MGE or shapelet expansion divides the light |
| `aplt.subplot_adapt_images` | the adapt images that drive an adaptive mesh and regularisation |

Sources: `PyAutoGalaxy:autogalaxy/galaxy/plot/galaxies_plots.py`,
`PyAutoGalaxy:autogalaxy/galaxy/plot/galaxy_plots.py`,
`PyAutoGalaxy:autogalaxy/profiles/plot/basis_plots.py` and
`PyAutoGalaxy:autogalaxy/galaxy/plot/adapt_plots.py`.

### Fits

| Function | Plots |
|---|---|
| `aplt.subplot_fit_imaging` | data, model image, residuals, normalised residuals, chi-squared map |
| `aplt.subplot_fit_imaging_list` | an n×5 grid over several fits — one row per `FitImaging`, columns data / S-N / model image / normalised residuals / chi-squared. Takes `fit_list=`, not `fit=`, and is the one fit subplot that names its own file (`output_filename`, default `fit_combined`) |
| `aplt.subplot_fit_imaging_of_galaxy` | the fit restricted to one galaxy, chosen by `galaxy_index` |
| `aplt.subplot_fit_interferometer` | visibility-plane fit summary |
| `aplt.subplot_fit_dirty_images` | the fit's dirty data, model, residuals and chi-squared map |
| `aplt.subplot_fit_real_space` | the fit's real-space galaxy image, before transformation |
| `aplt.subplot_fit_ellipse` | isophote fits over the data — takes `fit_list=`, not `fit=` |
| `aplt.subplot_ellipse_errors` | isophote parameter errors from a `fit_pdf_list`, at a chosen `sigma` |

Sources: `PyAutoGalaxy:autogalaxy/imaging/plot/fit_imaging_plots.py`,
`PyAutoGalaxy:autogalaxy/interferometer/plot/fit_interferometer_plots.py` and
`PyAutoGalaxy:autogalaxy/ellipse/plot/fit_ellipse_plots.py`.

Individual fit quantities are plotted with `plot_array` rather than a dedicated function, because
they are just arrays:

```python
aplt.plot_array(array=fit.model_data, title="Model Image")
aplt.plot_array(array=fit.residual_map, title="Residual Map")
aplt.plot_array(array=fit.normalized_residual_map, title="Normalized Residual Map")
aplt.plot_array(array=fit.chi_squared_map, title="Chi-Squared Map")
```

Adapted from `autogalaxy_workspace:scripts/imaging/plot.py`. The interferometer equivalents are the
`dirty_` prefixed properties (`fit.dirty_image`, `fit.dirty_model_image`,
`fit.dirty_residual_map`, `fit.dirty_chi_squared_map`) —
`autogalaxy_workspace:scripts/interferometer/plot.py`.

### Search results

| Function | Plots |
|---|---|
| `aplt.corner_cornerpy` | corner plot of `result.samples` via `corner.py` |
| `aplt.corner_anesthetic` | corner plot via `anesthetic` (nested-sampling flavoured) |
| `aplt.subplot_parameters` | parameter values against iteration |
| `aplt.log_likelihood_vs_iteration` | likelihood trace; `use_log_y`, `use_last_50_percent` |

These four come from PyAutoFit and take `samples`, plus `path`, `filename` and `format` (rather
than the `output_*` names the array functions use). `aplt.output_figure(path, filename, format)` is
the shared writer. Sources: `PyAutoFit:autofit/non_linear/plot/samples_plotters.py`,
`PyAutoFit:autofit/non_linear/plot/nest_plotters.py`,
`PyAutoFit:autofit/non_linear/plot/mle_plotters.py` and
`PyAutoFit:autofit/non_linear/plot/plot_util.py`. Worked examples:
`autogalaxy_workspace:scripts/guides/plot/searches.py`.

Parameter labels in a corner plot are the short forms from `config/notation.yaml` (`n` for
`sersic_index`, and so on), with superscripts naming the model component — see
[`configuration`](./configuration.md).

## Customisation

Keyword arguments, not wrapper objects:

| Keyword | Effect |
|---|---|
| `title` | figure title (and, by default, the output filename) |
| `colormap` | any matplotlib colormap name — `"jet"`, `"hot"`, `"gray"` |
| `use_log10` | log10 colour scale; a galaxy's light spans orders of magnitude, so this is often the readable view |
| `vmin` / `vmax` | fix the colour limits, so two figures can be compared on one scale |
| `symmetric` | symmetric limits about zero — the right choice for a residual map |
| `cb_unit` | colorbar unit label |
| `ax` | draw into an existing matplotlib axis instead of a new figure |

Adapted from `autogalaxy_workspace:scripts/guides/plot/start_here.py`.

## Overlays

Overlays are keyword arguments too (`autogalaxy_workspace:scripts/guides/plot/visuals.py`):

```python
import numpy as np

light_profile_centres = galaxies.extract_attribute(
    cls=ag.LightProfile, attr_name="centre"
)

aplt.plot_array(
    array=galaxies.image_2d_from(grid=grid),
    positions=[np.array(light_profile_centres)],
    title="Image with Light Profile Centres",
)
```

- **`positions=`** — a list of `(N, 2)` arrays of scatter points: light-profile centres, the
  coordinate origin, extra-galaxy centres.
- **`grid=`** — a coordinate grid drawn over the figure.
- **`lines=`** / **`line_colors=`** — polylines.

`ag.Grid2DIrregular(values=[(0.0, 0.0)])` is the other accepted form for a single position
(`autogalaxy_workspace:scripts/guides/plot/start_here.py`).

## Output to disk

With no `output_path`, a figure is displayed. Pass `output_path` (a directory) and
`output_format` and it is written as `{output_path}/{title}.{output_format}`; pass
`output_filename` to name it explicitly — **on the functions that accept it**, which is
`plot_array`, `plot_grid` and the five subplots tabulated under "Subplot functions" above. Every
other subplot writes a fixed stem, so name the *directory* instead. `output_format` also accepts
a **list**, which writes the same figure in each format at once:

```python
aplt.plot_array(
    array=data,
    title="Image",
    output_path=Path("output") / "plot",
    output_filename="example",
    output_format=["png", "pdf"],
)
```

Adapted from `autogalaxy_workspace:scripts/guides/plot/start_here.py`. In this workspace,
throwaway figures belong in the gitignored `scripts/scratch/<context>/`; then `print(...)` the
absolute path so it lands in stdout — see [`../../../skills/_style.md`](../../../skills/_style.md)
"Plot output and path announcement".

## Writing FITS

| Function | Writes |
|---|---|
| `aplt.fits_array(array, file_path, overwrite, ext_name)` | a single array |
| `aplt.fits_imaging(dataset, file_path=..., data_path=..., psf_path=..., noise_map_path=..., overwrite=...)` | an imaging dataset — one multi-HDU file via `file_path`, or separate files via the per-component paths |
| `aplt.fits_interferometer(dataset, file_path=..., data_path=..., noise_map_path=..., uv_wavelengths_path=..., overwrite=...)` | an interferometer dataset |

Adapted from `autogalaxy_workspace:scripts/imaging/start_here.py` (which uses `fits_imaging` to
write a simulated dataset and `fits_array` to save a mask drawn in the GUI) and
`autogalaxy_workspace:scripts/interferometer/plot.py`.

## Config defaults

Anything you do not pass explicitly comes from `config/visualize/`:

- `config/visualize/general.yaml` — `colormap`, `ticks -> number_of_ticks_2d`,
  `colorbar -> labelsize` / `labelsize_subplot`, `contour -> total_contours`, `units -> cb_unit`,
  `subplot_shape_to_figsize_factor`, and the matplotlib backend.
- `config/visualize/plots.yaml` — which figures a model-fit outputs **automatically**.
- `config/visualize/plots_search.yaml` — which search figures it outputs.

Editing these changes the default appearance project-wide without touching code (restart the
Python session or Jupyter kernel afterwards). Details in [`configuration`](./configuration.md);
the workspace's own account is the `__Config Defaults__` section of
`autogalaxy_workspace:scripts/guides/plot/start_here.py`.

## Automatic visualisation during a fit

You do not call any of these functions to watch a fit converge. Each analysis carries a
`Visualizer` that writes the standard figures into the fit's `image/` folder at every update, using
the best model found so far — see [`analysis_objects`](./analysis_objects.md) and the
`__Visualizer__` section at the end of each `plot.py` in the workspace's dataset packages.

## See also

- [`datasets`](./datasets.md) — inspecting data before you fit it.
- [`analysis_objects`](./analysis_objects.md) — the `Visualizer` and the fit objects these
  functions consume.
- [`ellipse`](./ellipse.md) — the isophote-specific figures.
- [`aggregator`](./aggregator.md) — assembling figures across many completed fits.
- [`configuration`](./configuration.md) — the `visualize/` and `notation.yaml` defaults.
- [`../../../skills/_style.md`](../../../skills/_style.md) — the workspace convention for where
  figures go and how to announce them.
