---
title: Interferometer fitting — visibilities, the uv-plane and dirty images
sources:
  - project: PyAutoArray
    paths:
      - autoarray/dataset/interferometer/dataset.py
      - autoarray/dataset/interferometer/simulator.py
      - autoarray/operators/transformer.py
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/interferometer/
      - autogalaxy/interferometer/model/analysis.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/interferometer/start_here.py
      - scripts/interferometer/modeling.py
      - scripts/interferometer/features/pixelization/modeling.py
      - scripts/interferometer/features/linear_light_profiles/modeling.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 8b874623d54019876858f6ca351df0359ae461d3fc6f43d3b132fd2e2284825c
---

# Interferometer fitting — visibilities, the uv-plane and dirty images

A radio or millimetre interferometer — ALMA, JVLA, NOEMA, SMA — does not photograph the sky.
Each pair of antennas measures one complex number, a **visibility**, which is a sample of the
Fourier transform of the sky brightness distribution at the spatial frequency set by that
baseline's projected separation. An observation is a list of such samples at scattered `(u, v)`
coordinates, in units of the observing wavelength.

PyAutoGalaxy fits those visibilities **directly**. Sources:
`PyAutoArray:autoarray/dataset/interferometer/dataset.py` and
`PyAutoArray:autoarray/operators/transformer.py`. Worked example:
`autogalaxy_workspace:scripts/interferometer/start_here.py`.

## Why not fit an image

You can always invert the visibilities to get a picture. But the `(u, v)` sampling is sparse
and irregular, so the inverse transform gives a **dirty image**: the true sky convolved with
the "dirty beam", the Fourier transform of the sampling pattern. That beam has extended,
oscillating sidelobes, so a single compact clump appears as a ring of positive and negative
artefacts spread across the field.

Two things follow:

- The noise in a dirty image is **strongly correlated between pixels**, in a pattern set by the
  array configuration. A pixel-by-pixel Gaussian likelihood on a dirty image is therefore
  wrong, and can bias structural parameters in ways that are hard to detect.
- Deconvolution algorithms (CLEAN and relatives) produce a plausible image but a non-linear,
  non-invertible transformation of the data, whose effective noise properties are not tractable.

In the visibility plane, by contrast, the measurement is exactly what the instrument recorded:
independent complex numbers with known RMS uncertainties. A Gaussian likelihood there is the
honest one. Dirty images remain the right tool for *looking* at the data — and PyAutoGalaxy
produces them (`dataset.dirty_image`, `aplt.subplot_interferometer_dirty_images`) — but not for
fitting.

## The workflow

The galaxy model is still built in real space; only the comparison happens in Fourier space.

1. Define a **real-space mask**, which sets the image-plane grid the model is evaluated on.
2. Evaluate the galaxy's surface brightness on that grid, exactly as for CCD imaging.
3. Fourier-transform the model image to the observed `(u, v)` coordinates.
4. Compare the model and measured visibilities with a Gaussian likelihood.

```python
import autogalaxy as ag

mask_radius = 3.5

real_space_mask = ag.Mask2D.circular(
    shape_native=(256, 256),
    pixel_scales=0.1,
    radius=mask_radius,
)

dataset = ag.Interferometer.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    uv_wavelengths_path=dataset_path / "uv_wavelengths.fits",
    real_space_mask=real_space_mask,
    transformer_class=ag.TransformerNUFFT,
)
```

`autogalaxy_workspace:scripts/interferometer/start_here.py`. Three FITS files instead of
imaging's three: complex visibilities, per-visibility complex RMS, and the `(u, v)` sampling.
There is no PSF — the sampling function plays that role, and it is in the data itself.

The **real-space mask** is the interferometer analogue of the imaging mask, and it is the main
scientific and computational lever. Its `shape_native` and `pixel_scales` set the resolution at
which the model is represented before transforming, and its radius sets the field being
modelled. Too small and you truncate real emission (and, worse, alias it); too large and every
likelihood evaluation transforms far more pixels than necessary. The same reasoning as
[`grids_and_masks`](./grids_and_masks.md) applies, with the extra wrinkle that here the mask
sets the *representation* of the model, not just which data enter the likelihood.

Everything else is the ordinary galaxy-modelling API: the same light profiles, the same MGE,
the same `af.Model` composition, and

```python
analysis = ag.AnalysisInterferometer(dataset=dataset, use_jax=True)
```

in place of `ag.AnalysisImaging`. `autogalaxy_workspace:scripts/interferometer/modeling.py`.

## Transformers

Real interferometers do not sample a rectangular Fourier grid, so a plain FFT is not enough.
Three transformers are available (`PyAutoArray:autoarray/operators/transformer.py`):

- **`ag.TransformerNUFFT`** — the default. A non-uniform FFT backed by
  [`nufftax`](https://github.com/GragasLab/nufftax), a pure-JAX NUFFT that jit-compiles and
  vmap-batches with the rest of the library. Recommended at any dataset size. It ships with the
  `[optional]` extras and requires Python ≥ 3.12; `pip install nufftax` if it is absent.
- **`ag.TransformerDFT`** — the exact discrete Fourier transform. Slower than the NUFFT once
  `n_vis` is large, but valuable as a reference for verifying a NUFFT result, and used by the
  pixelised reconstruction's sparse-operator path.
- **`ag.TransformerNUFFTPyNUFFT`** — a legacy `pynufft`-backed transformer, kept as a
  non-JAX fallback. It is not JAX-traceable, so it forfeits GPU acceleration and the
  gradient-based searches.

Because `nufftax` is JAX-native, light-profile interferometer fitting now runs at full GPU
speed for datasets with **arbitrarily many visibilities** — up to the tens or hundreds of
millions typical of high-resolution ALMA observations.
`autogalaxy_workspace:scripts/interferometer/start_here.py`. This is a genuine change in what
is practical: dataset size alone is no longer a reason to abandon a parametric fit.

## Pixelised reconstructions

A pixelisation is still the right choice when the galaxy's morphology is genuinely irregular
and no smooth profile or basis captures it — clumpy star formation, asymmetric structure. What
has changed is *why* you would choose it: it is now a decision about **morphology**, not about
dataset size. `autogalaxy_workspace:scripts/interferometer/features/pixelization/modeling.py`.

The linear algebra is the same as for imaging ([`inversions_and_pixelizations`](./inversions_and_pixelizations.md)),
with the transformer standing in for the PSF convolution. The sparse-operator workflow uses
`TransformerDFT`, and the same GPU-versus-CPU trade-off applies, driven by matrix sparsity.

Linear light profiles and MGE bases work identically here; see
`autogalaxy_workspace:scripts/interferometer/features/linear_light_profiles/modeling.py` and
[`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md).

## Looking at the data and the fit

```python
import autogalaxy.plot as aplt

aplt.subplot_interferometer_dirty_images(dataset=dataset)
aplt.plot_array(array=dataset.dirty_image, title="Dirty Image")

aplt.subplot_fit_dirty_images(fit=result.max_log_likelihood_fit)
```

The fit subplot shows the dirty image, the model's dirty image, residuals and chi-squared — all
formed by transforming *back* for display only. Interpret them with the dirty beam in mind: a
residual sidelobe pattern around a real source is expected, whereas a residual that survives
across many baselines is a genuine model failure.

## Simulating

```python
simulator = ag.SimulatorInterferometer(
    uv_wavelengths=dataset.uv_wavelengths,
    exposure_time=300.0,
    noise_sigma=1000.0,
    transformer_class=ag.TransformerNUFFT,
)

galaxies = ag.Galaxies([galaxy])
dataset = simulator.via_galaxies_from(galaxies=galaxies, grid=grid)
```

`autogalaxy_workspace:scripts/interferometer/start_here.py`. Note what is being simulated:
noise is added **to the visibilities** (`noise_sigma` is the RMS of complex Gaussian noise),
because that is where interferometer noise actually lives. Reusing the `uv_wavelengths` of a
real observation is the standard way to produce a realistic mock — the sampling function, not
the noise level alone, determines what structure is recoverable.

## Run time and memory

Interferometer fits are often memory-bound before they are sampler-bound: a visibility table
can be enormous and every likelihood evaluation performs a forward transform over all of it.
The levers, in order of effect:

- **Shrink the real-space mask** to the informative region — it reduces the number of pixels
  transformed on every call.
- **Average channels or baselines** where scientifically acceptable.
- **Choose the transformer deliberately** rather than accepting a default you have not checked.
- **Keep the model parametric** unless the morphology demands otherwise.

`ag.Interferometer.from_fits` carries a `raise_error_dft_visibilities_limit` guard that stops
you accidentally running an exact DFT over a visibility count it cannot handle — a warning
worth heeding rather than switching off.

## See also

- [`../api/datasets`](../api/datasets.md) — the `ag.Interferometer` dataset and its settings.
- [`grids_and_masks`](./grids_and_masks.md) — the real-space mask's imaging counterpart.
- [`inversions_and_pixelizations`](./inversions_and_pixelizations.md) — pixelised
  reconstruction from visibilities.
- [`multi_wavelength`](./multi_wavelength.md) — joint imaging plus interferometer fits.
- [`../stack/autoarray`](../stack/autoarray.md) — the transformer and dataset primitives.
