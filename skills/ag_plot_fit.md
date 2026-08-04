---
name: ag_plot_fit
description: Visualise a dataset, a galaxy, or a fit with the functional `aplt` plotting API — dataset and fit subplots, individual model-image / residual / normalised-residual / chi-squared panels, per-galaxy breakdowns, log10 stretch and fixed colour limits, overlays, writing figures to disk and writing FITS. Also carries the residual-inspection discipline: what a good chi-squared map looks like, what each characteristic residual pattern is telling you about the model, and how to compare two fits honestly. Use when the user wants to look at data before fitting it, look at a finished fit, produce a figure for a paper or a talk, or decide whether a fit is acceptable. Not for composing or running the fit (`ag_build_imaging_model`, `ag_run_search`), not for pulling numbers and posteriors out of a result (`ag_load_results`), and not for the diagnostic workflow when a fit has clearly failed (`ag_debug_fit_failure`).
---

# Looking at the data, the galaxy, and the fit

Plotting is not decoration here — it is the main instrument of judgement. A galaxy model is
accepted or rejected on whether its residuals look like noise, and no summary statistic
replaces that look. A chi-squared of 1.05 per pixel with a coherent ring of residuals at one
arcsecond is a *worse* result than a chi-squared of 1.3 scattered randomly, because the first
one is telling you the model is structurally wrong while the second is telling you the noise
estimate is slightly off.

The plotting surface is **functional only**. One import, then module-level functions:

```python
import autogalaxy.plot as aplt
```

Quantities are computed from PyAutoGalaxy objects by their own methods, and the resulting
array or grid is passed to a function
(`autogalaxy_workspace:scripts/guides/plot/start_here.py`). Because the layer takes plain
arrays, anything the library can compute you can plot, and there is no per-object plotting
class to learn.

There are **no plotter classes and no figure-configuration objects** — the object-oriented
plotters and the matplotlib-wrapper objects that older releases shipped were removed. Those
older releases are heavily represented in language-model training data, which makes
reconstructing them from memory the single most common stale-API error in this library. If a
call you remember is not in `dir(aplt)`, it is not part of the current API: check before you
emit it. [`wiki/core/api/plotting.md`](../wiki/core/api/plotting.md) is the authoritative
enumeration of what does exist, with a "when to use which" note on each entry.

## Ask

- *"Are we looking at the data, a galaxy model, or a fit?"* Three different branches below.
  Data before fitting is the inspection gate; a galaxy on its own is usually a sanity check on
  a model you just composed; a fit is the judgement call.
- *"On screen, or to a file?"* With no `output_path`, a figure is displayed. From a terminal
  that flashes and vanishes, so default to writing files.
- *"Quick look, or a figure for a paper?"* A quick look is one subplot. A paper figure means
  fixed colour limits, a log10 stretch, a chosen colormap and probably several formats.

## Branch — the dataset, before you fit it

One call gives the whole dataset: data, noise-map, PSF, signal-to-noise map and the
over-sampling panels.

```python
from pathlib import Path

import autogalaxy as ag
import autogalaxy.plot as aplt

DATASET_PATH = Path("dataset") / "imaging" / "<your_galaxy>"
PLOT_DIR = Path("scripts") / "scratch" / "<your_galaxy>"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

dataset = ag.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    psf_path=DATASET_PATH / "psf.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    pixel_scales=0.1,
)

aplt.subplot_imaging_dataset(
    dataset=dataset,
    output_path=PLOT_DIR,
    output_filename="dataset",
    output_format="png",
)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

Adapted from `autogalaxy_workspace:scripts/imaging/plot.py` `__Dataset Subplot__`. Individual
components are attributes, plotted with the fundamental array function:

```python
aplt.plot_array(array=dataset.data, title="Data")
aplt.plot_array(array=dataset.noise_map, title="Noise Map")
aplt.plot_array(array=dataset.psf.kernel, title="PSF")
aplt.plot_array(array=dataset.signal_to_noise_map, title="Signal-to-Noise Map")
```

What to look for in this figure is the substance of
[`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md) — neighbouring galaxies, foreground
stars, reduction artefacts, and where the galaxy's emission meets the sky, which is what sets
the mask radius. Re-plot after `apply_mask` and after `apply_over_sampling`: the subplot's
lower panels update to show the over-sampling scheme, so you can see the scheme you asked for
rather than trusting it (`autogalaxy_workspace:scripts/imaging/modeling.py`
`__Over Sampling__`). Masks and over-sampling as concepts are
[`wiki/core/concepts/grids_and_masks.md`](../wiki/core/concepts/grids_and_masks.md); the
dataset object itself is [`wiki/core/api/datasets.md`](../wiki/core/api/datasets.md).

## Branch — a galaxy or a light profile on its own

Useful before any data is involved: does the model you just composed actually look like the
galaxy you have in mind? Every object exposes `image_2d_from(grid=grid)`, and the array goes
straight to `plot_array`
(`autogalaxy_workspace:scripts/guides/plot/plotters.py`):

```python
grid = ag.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.05)

bulge = ag.lp.Sersic(
    centre=(0.0, 0.0),
    ell_comps=ag.convert.ell_comps_from(axis_ratio=0.9, angle=45.0),
    intensity=4.0,
    effective_radius=0.6,
    sersic_index=3.0,
)
disk = ag.lp.Exponential(
    centre=(0.0, 0.0),
    ell_comps=ag.convert.ell_comps_from(axis_ratio=0.7, angle=30.0),
    intensity=2.0,
    effective_radius=1.6,
)

galaxy = ag.Galaxy(redshift=0.5, bulge=bulge, disk=disk)

aplt.plot_array(array=bulge.image_2d_from(grid=grid), title="Bulge Image")
aplt.plot_array(array=galaxy.image_2d_from(grid=grid), title="Galaxy Image", use_log10=True)
```

A galaxy's image is the sum of its light profiles' images, so the bulge/disk decomposition is
visible by plotting each component beside the total. `aplt.subplot_galaxy_light_profiles`
does that as one figure; `aplt.subplot_galaxies` shows the summed image plus a panel per
galaxy, and takes `auto_filename` to name its file. The physics of what the effective radius
and Sersic index actually measure is
[`wiki/core/concepts/light_profiles.md`](../wiki/core/concepts/light_profiles.md), and how
several profiles and galaxies compose is
[`wiki/core/concepts/galaxies.md`](../wiki/core/concepts/galaxies.md).

**Linear light profiles cannot be plotted directly.** An `ag.lp_linear.*` profile has no
`intensity` until the linear inversion solves for it, so the galaxy-level subplots reject
them. Get the solved profiles from a fit — `fit.galaxies_linear_light_profiles_to_light_profiles`
— and plot those instead (`autogalaxy_workspace:scripts/guides/results/start_here.py`
`__Linear Light Profiles__`). Background:
[`wiki/core/concepts/linear_light_profiles_and_mge.md`](../wiki/core/concepts/linear_light_profiles_and_mge.md).

## Branch — the fit, and how to read the residuals

A `FitImaging` compares a model galaxy against the data, PSF convolution included. Build one
from a dataset and galaxies, or take the best-fit one straight off a result:

```python
fit = ag.FitImaging(dataset=dataset, galaxies=galaxies)

# or, from a completed search:
fit = result.max_log_likelihood_fit
```

The summary figure is six panels — data, signal-to-noise map, model image, residual map,
normalised residual map and chi-squared map:

```python
aplt.subplot_fit_imaging(
    fit=fit,
    output_path=PLOT_DIR,
    output_format="png",
)
```

Adapted from `autogalaxy_workspace:scripts/imaging/plot.py` `__Fit Subplot__`.

**Most fit subplots do not take `output_filename`.** They write a fixed stem into
`output_path`: `subplot_fit_imaging` writes `fit.png`, and
`subplot_fit_imaging_of_galaxy` writes `of_galaxy_<index>.png`
(`PyAutoGalaxy:autogalaxy/imaging/plot/fit_imaging_plots.py`). So the *directory* is what
distinguishes one context from another — give each fit, or each variant of a figure, its own
folder under `scripts/scratch/`. The one exception is `subplot_fit_imaging_list` below, which
does take `output_filename`. `plot_array`, `plot_grid` and `subplot_imaging_dataset` do
take `output_filename`; `subplot_galaxies` takes `auto_filename`
(`PyAutoGalaxy:autogalaxy/galaxy/plot/galaxies_plots.py`). Check the signature rather than
assuming a uniform interface.

To compare several fits side by side — the same galaxy under competing models, or one model
across a set of datasets — `subplot_fit_imaging_list` draws one row per fit rather than making
you place several `fit.png` files next to each other:

```python
aplt.subplot_fit_imaging_list(
    fit_list=[fit_sersic, fit_bulge_disk, fit_mge],
    output_path=PLOT_DIR,
    output_filename="model_comparison",
    output_format="png",
)
```

Note it takes `fit_list=`, not `fit=`. Its rows are data | signal-to-noise | model image |
normalised residuals | chi-squared — five columns, not the six of the single-fit subplot, and
it drops `colormap` / `use_log10` (`PyAutoGalaxy:autogalaxy/imaging/plot/fit_imaging_plots.py`).
Read the normalised-residual column across rows: the model that flattens it is the one to keep,
and the discipline below applies unchanged.

Individual quantities are attributes, so they go through `plot_array` — which is also how you
get per-panel control the subplot does not offer:

```python
aplt.plot_array(array=fit.model_data, title="Model Image")
aplt.plot_array(array=fit.residual_map, title="Residual Map")
aplt.plot_array(array=fit.normalized_residual_map, title="Normalized Residual Map", symmetric=True)
aplt.plot_array(array=fit.chi_squared_map, title="Chi-Squared Map")
```

Adapted from `autogalaxy_workspace:scripts/imaging/plot.py` `__Fit Figures__`. `symmetric=True`
puts zero at the centre of a diverging colour scale, which is the right choice for a residual
map — otherwise a colormap keyed to the extremes hides the sign of the structure you are
looking for.

### The inspection discipline

Three maps, three different questions:

- **`residual_map`** = data − model, in data units. Answers *how much* flux is unaccounted
  for, and where. Useful for judging whether a mismatch matters physically.
- **`normalized_residual_map`** = residual / noise. Answers *how significant* the mismatch is.
  This is the map to read first, because it is the only one calibrated against the noise.
  Values scattered within roughly ±3 are consistent with noise; coherent structure well
  outside that is a model failure, however small it looks in flux.
- **`chi_squared_map`** = normalised residual squared. Answers *where the likelihood is being
  paid*, since `fit.chi_squared` is its sum
  (`autogalaxy_workspace:scripts/imaging/likelihood_function.py` `__Chi Squared__`). Squaring
  discards the sign, so read it alongside the normalised residuals rather than instead of
  them.

Read the pattern, not just the magnitude. The characteristic ones:

| Pattern in the normalised residuals | Usually means |
|---|---|
| Structure concentrated at the very centre | Over-sampling too coarse, or a genuinely cored/nuclear component the model lacks |
| A symmetric ring at one radius | The radial profile is wrong — one Sersic where a bulge plus disk is needed, or a fixed Sersic index |
| Four-lobed pattern, alternating sign | The ellipticity or position angle is wrong, or the isophotes twist with radius |
| A compact blob away from the centre | A neighbouring galaxy, a foreground star, or a reduction artefact left in the fit |
| Clumpy structure with no symmetry | Real asymmetric morphology no smooth profile can absorb |
| Uniformly slightly too large everywhere | The noise-map is underestimated, or a sky background is unmodelled |

Each row routes somewhere. Ellipticity and isophote twists are
[`wiki/core/concepts/ellipse_fitting_and_multipoles.md`](../wiki/core/concepts/ellipse_fitting_and_multipoles.md);
neighbours are
[`wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../wiki/core/concepts/extra_galaxies_and_noise_scaling.md);
irreducible clumpiness is
[`wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md);
an unmodelled background is
[`wiki/core/concepts/sky_background_and_operated_profiles.md`](../wiki/core/concepts/sky_background_and_operated_profiles.md).
Turning any of those diagnoses into a plan is
[`ag_debug_fit_failure`](./ag_debug_fit_failure.md).

For a blended pair or a galaxy with a modelled neighbour, the per-galaxy view is what shows
whether the decomposition is real or just two profiles trading flux:

```python
aplt.plot_array(array=fit.model_images_of_galaxies_list[0], title="Galaxy 0 Model Image")
aplt.subplot_fit_imaging_of_galaxy(fit=fit, galaxy_index=0, output_path=PLOT_DIR, output_format="png")
```

Adapted from `autogalaxy_workspace:scripts/imaging/plot.py` `__Galaxy Images__` and
`__Galaxy Subplots__`. The per-galaxy subplot shows the data with the *other* galaxies
subtracted, alongside that galaxy's model image and residuals.

## Branch — making the figure say what you mean

Customisation is keyword arguments, never a wrapper object
(`autogalaxy_workspace:scripts/guides/plot/start_here.py` `__Customization__`):

```python
aplt.plot_array(array=dataset.data, title="Jet", colormap="jet")
aplt.plot_array(array=galaxy.image_2d_from(grid=grid), title="Log10", use_log10=True)
aplt.plot_array(array=dataset.data, title="Fixed Scale", vmin=0.0, vmax=1.0)
```

Three of these carry scientific weight:

- **`use_log10=True`** — a galaxy's surface brightness spans orders of magnitude, so a linear
  stretch shows the bright core and nothing else. The log10 view is where faint extended
  emission, tidal features and a disk under a bright bulge become visible. It is available on
  the subplots too, and is often the more honest default for a galaxy.
- **`vmin` / `vmax`** — fixed limits are what make two figures comparable. Comparing two fits
  on auto-scaled colour bars is not a comparison.
- **`symmetric=True`** — for anything that can be negative, which is every residual map.

Overlays are keyword arguments as well
(`autogalaxy_workspace:scripts/guides/plot/visuals.py`): `positions=` scatters points such as
light-profile centres, `grid=` draws a coordinate grid, `lines=` / `line_colors=` draw
polylines. Two accepted forms for positions:

```python
import numpy as np

light_profile_centres = galaxies.extract_attribute(cls=ag.LightProfile, attr_name="centre")

aplt.plot_array(
    array=galaxies.image_2d_from(grid=grid),
    positions=[np.array(light_profile_centres)],
    title="Image with Light Profile Centres",
)

aplt.plot_array(
    array=galaxy.image_2d_from(grid=grid),
    positions=ag.Grid2DIrregular(values=[(0.0, 0.0)]),
    title="Image with Centre",
)
```

1D radial profiles are plain matplotlib on a radially projected grid, not an `aplt` function —
including the shaded error region drawn from a set of profiles sampled from the posterior
(`autogalaxy_workspace:scripts/guides/plot/plotters.py` `__One Dimensional Plots__` and
`__Probability Density Function (PDF) Plots__`, which uses
`ag.util.error.profile_1d_median_and_error_region_via_quantile`).

Anything not passed explicitly comes from `config/visualize/general.yaml` — the default
colormap, tick counts, colorbar label sizes, contour levels, the unit label. Editing that file
changes the look project-wide without touching code, after a session or kernel restart. See
[`wiki/core/api/configuration.md`](../wiki/core/api/configuration.md).

## Branch — writing to disk, and announcing it

With `output_path` set (a directory) plus `output_format`, the figure is written rather than
displayed. Without `output_filename` the file is named from the title; `output_format` also
accepts a list, which writes several formats in one call — a PNG to look at and a PDF for the
paper (`autogalaxy_workspace:scripts/guides/plot/start_here.py` `__Output__`):

```python
aplt.plot_array(
    array=dataset.data,
    title="Image",
    output_path=PLOT_DIR,
    output_filename="data",
    output_format=["png", "pdf"],
)
```

Three rules from [`_style.md`](./_style.md) "Plot output and path announcement", and they are
not optional:

1. Throwaway figures go to the gitignored `scripts/scratch/<context>/`, where `<context>` is
   usually the dataset name. Never `output/` — that belongs to the fit runtime.
2. `print(f"Saved to: {PLOT_DIR.resolve()}")` at the end of the recipe, so the absolute
   location lands in stdout.
3. After running, **quote that absolute path back to the user and offer to open it** —
   `xdg-open` on Linux, `open` on macOS, `explorer.exe` or `wslview` from WSL. One offer per
   plot run. "Plot saved" on its own is not useful to someone who cannot see your filesystem.

To write data rather than an image, the `fits_*` functions are separate
(`autogalaxy_workspace:scripts/imaging/plot.py` `__Outputting to FITS__`):

```python
aplt.fits_imaging(dataset=dataset, file_path=PLOT_DIR / "dataset.fits", overwrite=True)
aplt.fits_array(array=mask, file_path=DATASET_PATH / "mask.fits", overwrite=True)
```

`file_path` writes one multi-HDU file with named extensions; the per-component
`data_path` / `psf_path` / `noise_map_path` arguments write separate files instead.

## Branch — the figures a fit produces on its own

You do not need any of the above to watch a fit converge. Each analysis carries a `Visualizer`
that PyAutoFit invokes at every update interval and again at the end, writing the standard
dataset, fit and per-galaxy figures into the fit's `image/` folder using the best model found
so far (`autogalaxy_workspace:scripts/imaging/plot.py` `__Visualizer__`;
`PyAutoGalaxy:autogalaxy/imaging/model/visualizer.py`). Which figures appear is set by
`config/visualize/plots.yaml` — `dataset -> subplot_dataset`, `fit -> subplot_fit`,
`fit -> subplot_of_galaxies` — so switching a figure on or off for every fit is a YAML edit,
not a code change. The cadence is the search's `iterations_per_quick_update`
([`ag_run_search`](./ag_run_search.md)).

Reach for this skill when you want something the automatic figures do not give you: a
different stretch, a crop, fixed limits across two fits, a specific panel at publication
size, or a per-galaxy breakdown that `plots.yaml` has switched off.

Posterior figures — corner plots and likelihood traces — come from PyAutoFit and take
`samples` plus `path` / `filename` / `format` rather than the `output_*` names, e.g.
`aplt.corner_cornerpy(samples=result.samples)`. They belong to
[`ag_load_results`](./ag_load_results.md); the surface is tabulated in
[`wiki/core/api/plotting.md`](../wiki/core/api/plotting.md) "Search results".

## Combine

- [`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md) — the inspection the dataset
  subplot exists to serve, and the mask that follows from it.
- [`ag_debug_fit_failure`](./ag_debug_fit_failure.md) — you have read the residuals and they
  are wrong; this is the triage.
- [`ag_load_results`](./ag_load_results.md) — the numbers behind the figures, and figures
  across many fits at once.
- [`ag_run_search`](./ag_run_search.md) — the fit that produced the `image/` folder, and the
  cadence at which it refreshes.
- [`ag_simulate_dataset`](./ag_simulate_dataset.md) — plot a simulated fit where you know the
  truth, to calibrate what an acceptable residual map looks like for your data quality.

When a figure is going into a paper or a talk, offer (default-yes) the dated
`wiki/project/YYYY-MM-DD-<slug>.md` entry recording what it shows and which fit it came from
— per [`_style.md`](./_style.md) property #5.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Fitting](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_1_introduction/tutorial_3_fitting.ipynb):
  builds up residuals, normalised residuals and the chi-squared map from first principles, so
  the six panels of a fit subplot stop being opaque.
- **General reference** — [RTD: Plot API reference](https://pyautogalaxy.readthedocs.io/en/latest/api/plot.html):
  the generated reference for the visualisation library.
- **Experienced PyAutoGalaxy user** — [workspace: guides/plot/start_here.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/guides/plot/start_here.py):
  the plotting API in one runnable script — customisation, output, config defaults, overlays
  and subplots.

## Agent procedural checklist

1. Establish what is being plotted: dataset, galaxy/profile, or fit.
2. Ground every call against [`wiki/core/api/plotting.md`](../wiki/core/api/plotting.md) or
   `dir(aplt)`. Never write a plotter class or a figure-configuration object.
3. Check the signature for `output_filename` before passing it — the fit and galaxy subplots
   do not accept it and write a fixed stem instead.
4. Write the recipe into a script; send figures to `scripts/scratch/<context>/`.
5. `print` the resolved plot directory at the end of the script.
6. For a fit, read the **normalised residual** map first, then the chi-squared map; report the
   pattern, not only the number.
7. Use `symmetric=True` on residuals, `use_log10=True` for galaxy light, and fixed
   `vmin`/`vmax` whenever two figures will be compared.
8. Quote the absolute path back and offer to open it — once per plot run.
9. Route any diagnosed model failure to the debug skill rather than tweaking the figure until
   it looks acceptable.
10. Offer the `wiki/project/` entry for a figure that will be published.
