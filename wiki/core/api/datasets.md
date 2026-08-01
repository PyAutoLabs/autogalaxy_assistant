---
title: Datasets — Imaging and Interferometer
sources:
  - project: PyAutoArray
    paths:
      - autoarray/dataset/abstract/dataset.py
      - autoarray/dataset/imaging/dataset.py
      - autoarray/dataset/interferometer/dataset.py
      - autoarray/mask/mask_2d.py
      - autoarray/operators/convolver.py
      - autoarray/operators/over_sampling/over_sample_util.py
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/imaging/simulator.py
      - autogalaxy/interferometer/simulator.py
      - autogalaxy/ellipse/dataset_interp.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/imaging/start_here.py
      - scripts/imaging/modeling.py
      - scripts/imaging/data_preparation/start_here.py
      - scripts/interferometer/start_here.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 588526e9facb90fe46fc488fbece00c62fc2a5640fa9cf01ff0ebf92243fafd8
---

# Datasets

Two dataset flavours cover everything PyAutoGalaxy fits: **CCD imaging** (`ag.Imaging`) and
**visibility-plane interferometer data** (`ag.Interferometer`). Each pairs with a matching
`Analysis*` object (see [`analysis_objects`](./analysis_objects.md)) and a matching set of
`aplt` subplot functions (see [`plotting`](./plotting.md)).

Whichever you load, the same three-step arc applies before you fit: **load → deal with
contaminants → mask and over-sample**. Every step is a science decision, not boilerplate.
Masking too tightly truncates the outer isophotes and biases `effective_radius` and
`sersic_index` directly; leaving a neighbouring galaxy's light in the frame biases every
parameter of the model at once.

## `ag.Imaging`

CCD imaging: an image, a per-pixel RMS noise-map, and a PSF.

```python
from pathlib import Path
import autogalaxy as ag

dataset_path = Path("dataset") / "imaging" / "simple"

dataset = ag.Imaging.from_fits(
    data_path=dataset_path / "data.fits",
    psf_path=dataset_path / "psf.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    pixel_scales=0.1,
)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py`. `pixel_scales` converts
pixels to arcseconds and must match your instrument — it is the single most consequential
number in the call, because every radius the fit reports is expressed in it.

Constructor arguments worth knowing (source:
`PyAutoArray:autoarray/dataset/imaging/dataset.py`):

| Argument | What it does |
|---|---|
| `data_path`, `noise_map_path`, `psf_path` | FITS inputs; `psf_path` is optional (ellipse fitting does not use a PSF) |
| `data_hdu`, `noise_map_hdu`, `psf_hdu` | HDU index in each file, default `0` |
| `pixel_scales` | arcsec/pixel, scalar or `(y, x)` tuple |
| `over_sample_size_lp`, `over_sample_size_pixelization` | initial uniform over-sampling factors (default `4`) |
| `convolve_over_sample_size_lp` | PSF-convolution over-sampling; `modeling.py` sets `1` and notes "increase for PSF oversampling" |
| `noise_covariance_matrix` | correlated-noise matrix, when the reduction produced one |
| `check_noise_map` | raises on non-positive noise values rather than failing later |
| `psf_pixel_scales` | when the PSF was drizzled to a different scale than the image |

### Contaminant handling — `apply_noise_scaling`

Nearby galaxies, foreground stars and reduction artefacts blend into the field. PyAutoGalaxy
does not remove those pixels; it keeps them in the fit and zeroes their data while inflating
their noise, so they contribute negligibly to the likelihood. Removing pixels outright would
punch discontinuities into a pixelised reconstruction.

```python
mask_extra_galaxies = ag.Mask2D.from_fits(
    file_path=dataset_path / "mask_extra_galaxies.fits",
    pixel_scales=dataset.pixel_scales,
    invert=True,  # `True` means a pixel is scaled.
)

dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py`. The signature is
`apply_noise_scaling(mask, noise_value=1e8, signal_to_noise_value=None, should_zero_data=True)`.
Concept page: [`../concepts/extra_galaxies_and_noise_scaling`](../concepts/extra_galaxies_and_noise_scaling.md).

### Masking — `apply_mask`

```python
mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=3.0,
)

dataset = dataset.apply_mask(mask=mask)
```

`ag.Mask2D` also offers `circular_annular`, `elliptical`, `elliptical_annular`,
`circular_radius`, `all_false`, `from_pixel_coordinates` and `from_fits`
(`PyAutoArray:autoarray/mask/mask_2d.py`). Pick the radius from a look at the data, not from
a default — the mask must reach out to where the galaxy's emission meets the sky.
Concept page: [`../concepts/grids_and_masks`](../concepts/grids_and_masks.md).

### Over-sampling — `apply_over_sampling`

A Sersic profile with a steep inner slope varies enormously across a single central pixel, so
the pixel's value has to be integrated on a sub-grid rather than sampled at its centre. The
workspace's standard idiom is an adaptive scheme: fine sub-grids in the centre, coarser
outside.

```python
over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[8, 4, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)

dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py`; the helper lives in
`PyAutoArray:autoarray/operators/over_sampling/over_sample_util.py`. `sub_size_list` gives the
sub-grid factor inside each radial annulus of `radial_list` (and beyond the last one), so
`[8, 4, 2]` with `[0.3, 0.6]` means 8×8 inside 0.3", 4×4 out to 0.6", 2×2 beyond. Simulations
push the central factor much higher (`[32, 8, 2]` in
`autogalaxy_workspace:scripts/imaging/start_here.py`) because there is no noise to hide the
integration error. `apply_over_sampling` takes `over_sample_size_lp` (light-profile
evaluation) and `over_sample_size_pixelization` separately; the full treatment is
`autogalaxy_workspace:scripts/guides/advanced/over_sampling.py`.

### Attributes

- `dataset.data` — `Array2D` of image values.
- `dataset.noise_map` — `Array2D` of per-pixel RMS.
- `dataset.psf` — a `Convolver` (build one directly with `ag.Convolver.from_fits(...)` or
  `ag.Convolver.from_gaussian(...)`); `dataset.psf.kernel` is the array itself.
- `dataset.signal_to_noise_map`, `dataset.signal_to_noise_max`.
- `dataset.grid` — masked `Grid2D` of (y, x) arcsecond coordinates.
- `dataset.mask`, `dataset.shape_native`, `dataset.shape_slim`, `dataset.pixel_scales`.

## `ag.Interferometer`

Visibility-plane data: complex visibilities, their noise-map, and the (u, v) baseline
coordinates. The model is evaluated in real space inside a **real-space mask** and then
transformed to visibilities, so the mask is a constructor argument rather than something you
apply afterwards.

```python
real_space_mask = ag.Mask2D.circular(
    shape_native=(256, 256),
    pixel_scales=0.1,
    radius=3.5,
)

dataset = ag.Interferometer.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    uv_wavelengths_path=dataset_path / "uv_wavelengths.fits",
    real_space_mask=real_space_mask,
    transformer_class=ag.TransformerNUFFT,
)
```

Adapted from `autogalaxy_workspace:scripts/interferometer/start_here.py`. Source:
`PyAutoArray:autoarray/dataset/interferometer/dataset.py`.

**Transformers.** `ag.TransformerNUFFT` is the JAX-native non-uniform FFT and the recommended
default at any visibility count. `ag.TransformerDFT` is an exact discrete transform — slower
for large `n_vis`, but useful as a verification reference. `ag.TransformerNUFFTPyNUFFT` is the
legacy backend, available when explicitly requested.

Attributes:

- `dataset.data` — complex visibilities; `dataset.amplitudes`, `dataset.phases`.
- `dataset.noise_map` — RMS per visibility.
- `dataset.uv_wavelengths`, `dataset.uv_distances`.
- `dataset.real_space_mask`, `dataset.transformer`, `dataset.grid`.
- `dataset.dirty_image`, `dataset.dirty_noise_map`, `dataset.dirty_signal_to_noise_map` —
  inverse-transformed real-space views, for **visualisation only**; the likelihood is
  evaluated in the visibility plane.

Concept page: [`../concepts/interferometer_theory`](../concepts/interferometer_theory.md).

## Simulating a dataset

Both flavours have a simulator that turns a `Galaxies` object into data with the instrumental
signature and noise of a real observation — the fastest way to sanity-check a model before you
point it at real data.

```python
grid = ag.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.1)

psf = ag.Convolver.from_gaussian(
    shape_native=(11, 11), sigma=0.1, pixel_scales=grid.pixel_scales
)

simulator = ag.SimulatorImaging(
    exposure_time=300.0,
    psf=psf,
    background_sky_level=0.1,
    add_poisson_noise_to_data=True,
)

dataset = simulator.via_galaxies_from(galaxies=ag.Galaxies([galaxy]), grid=grid)
```

Adapted from `autogalaxy_workspace:scripts/imaging/start_here.py`. Source:
`PyAutoGalaxy:autogalaxy/imaging/simulator.py`. `ag.SimulatorInterferometer(uv_wavelengths=...,
exposure_time=..., transformer_class=...)` is the visibility-plane counterpart
(`PyAutoGalaxy:autogalaxy/interferometer/simulator.py`).

Write a simulated (or masked, or noise-scaled) dataset back to FITS with
`aplt.fits_imaging(...)` / `aplt.fits_interferometer(...)` — see
[`plotting`](./plotting.md).

## Preparing your own data

`autogalaxy_workspace:scripts/imaging/data_preparation/start_here.py` is the checklist your
FITS files must satisfy. In short: the image and noise-map share units and shape; the noise-map
is RMS, not variance; the PSF is odd-sized, normalised and centred; the galaxy sits near
(0.0", 0.0") because that is where the default priors put it. Load each ingredient on its own
with `ag.Array2D.from_fits(...)` / `ag.Convolver.from_fits(...)` and plot it before assembling
an `ag.Imaging`.

The optional extras in the same package — a custom mask, a marked light centre, extra-galaxy
centres, a `mask_extra_galaxies.fits`, and an `info.json` of auxiliary metadata — are produced
by the GUI tools in `autogalaxy_workspace:scripts/imaging/data_preparation/gui/` and the manual
examples alongside them.

## Picking a dataset type

| Observation | Dataset |
|---|---|
| HST / JWST / Euclid CCD imaging | `ag.Imaging` |
| Ground-based CCD imaging | `ag.Imaging` |
| ALMA / JVLA / SMA visibilities | `ag.Interferometer` |
| Multi-band CCD imaging | one `ag.Imaging` per band, combined with a factor graph — see [`analysis_objects`](./analysis_objects.md) |
| Isophote / ellipse fitting | `ag.Imaging` loaded **without** a PSF — see [`ellipse`](./ellipse.md) |

## See also

- [`../concepts/grids_and_masks`](../concepts/grids_and_masks.md) — the geometry every dataset
  is built on.
- [`analysis_objects`](./analysis_objects.md) — the paired `Analysis*` classes.
- [`plotting`](./plotting.md) — inspecting a dataset before you fit it.
- [`../concepts/multi_wavelength`](../concepts/multi_wavelength.md) — fitting several bands at
  once.
- [`../stack/autoarray`](../stack/autoarray.md) — where the dataset, mask and grid classes live.
