---
name: ag_build_interferometer_model
description: Model a galaxy observed with a radio or millimetre interferometer (ALMA, JVLA, NOEMA, SMA) by fitting its complex visibilities directly in the uv-plane. Covers loading an `ag.Interferometer` from three FITS files against a real-space mask, choosing the transformer by visibility count and the `raise_error_dft_visibilities_limit` guard that stops a slow exact DFT, why there is no PSF and no over-sampling, composing the model and the `ag.AnalysisInterferometer`, reading dirty images as diagnostics rather than data, the fit and real-space subplots and the filenames they write, the sparse NUFFT operator precomputation for very large visibility tables, and preparing data from a CASA measurement set. Use for visibility-plane data. Not for CCD imaging (`ag_build_imaging_model`), not for a joint imaging-plus-visibilities fit (`ag_multi_dataset`), and not for simulating visibilities (`ag_simulate_dataset`).
---

# Modelling a galaxy in the uv-plane

An interferometer does not photograph the sky. Each pair of antennas measures one complex
number — a **visibility** — which samples the Fourier transform of the sky brightness
distribution at the spatial frequency set by that baseline's projected separation. An
observation is a list of such samples at scattered `(u, v)` coordinates, measured in units of
the observing wavelength, and that list is the data.

You could invert it to get a picture, and PyAutoGalaxy will make you one. But the `(u, v)`
sampling is sparse and irregular, so the inverse transform gives a **dirty image**: the true sky
convolved with the Fourier transform of the sampling pattern. That beam has extended oscillating
sidelobes, so one compact clump appears as a ring of positive and negative artefacts spread
across the field, and the noise between pixels is strongly correlated in a pattern set by the
array configuration. A per-pixel Gaussian likelihood on such an image is simply the wrong
likelihood, and it biases structural parameters in ways that are hard to notice. Deconvolution
(CLEAN and relatives) makes a plausible picture at the cost of a non-linear, non-invertible
transformation whose effective noise properties are not tractable.

In the visibility plane the measurement is exactly what the instrument recorded: independent
complex numbers with known RMS uncertainties. A Gaussian likelihood there is the honest one. So
the galaxy model is still built in real space — the same light profiles, the same `af.Model`
composition, the same MGE — and only the *comparison* moves to Fourier space: evaluate the
surface brightness on a real-space grid, transform it to the observed `(u, v)` coordinates,
compare with the measured visibilities.

The physics and the transformer theory are
[`../wiki/core/concepts/interferometer_theory.md`](../wiki/core/concepts/interferometer_theory.md);
the dataset object and its settings are
[`../wiki/core/api/datasets.md`](../wiki/core/api/datasets.md). The canonical scripts are
`autogalaxy_workspace:scripts/interferometer/start_here.py` and
`autogalaxy_workspace:scripts/interferometer/modeling.py`, and the likelihood is walked term by
term in `autogalaxy_workspace:scripts/interferometer/likelihood_function.py`.

## Ask

- *"How many visibilities?"* The single most consequential number. It decides the transformer,
  whether a pixelised reconstruction needs the sparse-operator precomputation, and whether this
  runs on a laptop.
- *"How big is the emission on the sky, in arcseconds?"* This sets the real-space mask, which is
  the main scientific and computational lever here — more so than the imaging mask, because it
  sets the *representation* of the model rather than only which data enter the likelihood.
- *"A best-fit model quickly, or a posterior you can quote?"* `af.MultiStartProdigy` for the
  former, `af.Nautilus` for the latter; the two workspace scripts differ in exactly this and
  nothing else.
- *"Where did the data come from?"* If the answer is "a CASA measurement set", the export step
  comes first — see the data-preparation branch.

## Before you start — the environment

The default transformer is a JAX-native NUFFT backed by
[`nufftax`](https://github.com/GragasLab/nufftax), which ships with the `[optional]` extras and
requires Python ≥ 3.12. Check it before writing a script, because the workspace's own examples
exit early when it is missing (`autogalaxy_workspace:scripts/interferometer/start_here.py`
`__NUFFT Backend Check__`):

```python
import importlib.util

print("nufftax available:", importlib.util.find_spec("nufftax") is not None)
```

If it is absent, `pip install nufftax` — or `pip install autogalaxy[optional]`. Repairing the
environment is [`ag_setup_environment`](./ag_setup_environment.md).

## Branch — the fit

The deliverable is one script. Adapted from
`autogalaxy_workspace:scripts/interferometer/modeling.py` (the Nautilus configuration, the VRAM
check and the real-space mask) and `autogalaxy_workspace:scripts/interferometer/start_here.py`
(the load and the result).

```python
"""
Galaxy Structure: Interferometer Modeling
========================================

Fit the morphology of a galaxy observed with a millimetre interferometer by modelling its
complex visibilities directly in the uv-plane: define the real-space grid the model is
evaluated on, load the visibilities, noise-map and (u, v) sampling, compose a linear Sersic
bulge and Exponential disk, and sample the posterior with Nautilus so the effective radius and
Sersic index come with errors that do not depend on a deconvolution.

__Contents__

- **Imports:** JAX environment first, then the standard trio.
- **Real Space Mask:** The real-space grid the model is represented on.
- **Dataset:** Load visibilities, noise-map and uv-wavelengths, and pick a transformer.
- **Model:** Compose the galaxy's light profiles.
- **Search:** Configure Nautilus.
- **Analysis:** Bind the model to the visibilities.
- **Model-Fit:** Run the fit and announce the output folder.
- **Result:** Read the best-fit model and its dirty-image diagnostics.
"""
from autogalaxy import jax_wrapper  # Sets the JAX environment before other imports

from pathlib import Path

import autofit as af
import autogalaxy as ag
import autogalaxy.plot as aplt

"""
__Real Space Mask__

The real-space mask is the interferometer analogue of the imaging mask, and it does more work.
`shape_native` and `pixel_scales` set the resolution at which the galaxy is represented *before*
it is transformed, and the radius sets the field being modelled. Too small and you truncate real
emission and alias it back into the fit; too large and every likelihood evaluation transforms
far more pixels than the data can constrain. Match the pixel scale to a few pixels per
synthesised beam and the radius to the emission you can see in the dirty image
(`PyAutoArray:autoarray/mask/mask_2d.py`).
"""
MASK_RADIUS = 3.5

real_space_mask = ag.Mask2D.circular(
    shape_native=(256, 256),
    pixel_scales=0.1,
    radius=MASK_RADIUS,
)

"""
__Dataset__

Three FITS files, not imaging's three: the complex visibilities (shape `(n_vis,)`), the
per-visibility complex RMS, and the `(u, v)` sampling with shape `(n_vis, 2)`. There is **no
PSF** — the sampling function plays that role and it is already in the data — and consequently
nothing to deconvolve at load time.

`transformer_class` chooses how the model image is mapped to the observed `(u, v)` coordinates.
`ag.TransformerNUFFT` is the default and the right answer at essentially any dataset size
(`PyAutoArray:autoarray/dataset/interferometer/dataset.py`,
`PyAutoArray:autoarray/operators/transformer.py`).
"""
DATASET_PATH = Path("dataset") / "interferometer" / "<your_galaxy>"

dataset = ag.Interferometer.from_fits(
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    uv_wavelengths_path=DATASET_PATH / "uv_wavelengths.fits",
    real_space_mask=real_space_mask,
    transformer_class=ag.TransformerNUFFT,
)

print(f"n_vis = {dataset.data.shape[0]}")

aplt.subplot_interferometer_dirty_images(
    dataset=dataset,
    output_path="scripts/scratch/<your_galaxy>/",
    output_filename="dirty_images",
    output_format="png",
)

"""
__Model__

Identical to an imaging model — that is the point. A linear `Sersic` bulge and a linear
`Exponential` disk with their centres paired, so the two components describe one galaxy rather
than drifting apart. `lp_linear` solves each profile's `intensity` by linear inversion instead
of sampling it, which removes one dimension per component
(`PyAutoGalaxy:autogalaxy/profiles/light/linear/sersic.py`).

There is **no over-sampling section**, and its absence is deliberate: an interferometer does not
observe in a way that makes sub-pixel integration of the light profile meaningful, so every
interferometer calculation runs without it
(`autogalaxy_workspace:scripts/interferometer/modeling.py` `__Over Sampling__`).
"""
bulge = af.Model(ag.lp_linear.Sersic)
disk = af.Model(ag.lp_linear.Exponential)
bulge.centre = disk.centre

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

print(model.info)

"""
__Search__

`Nautilus` returns the full posterior — errors and covariances, the thing you can quote
(`PyAutoFit:autofit/non_linear/search/nest/nautilus/search.py`). The folder's `start_here.py`
instead uses `af.MultiStartProdigy`, a multi-start gradient optimizer which is far faster and
returns a single best-fit model with no errors at all; use that to check the model and the data
make sense, then this when the numbers go in a paper.
"""
search = af.Nautilus(
    path_prefix=Path("interferometer"),
    name="sersic_exp",
    unique_tag="<your_galaxy>",
    n_live=100,
    n_batch=50,
    iterations_per_quick_update=10000,
    live_visual_update=False,
)

"""
__Analysis__

`ag.AnalysisInterferometer` defines the `log_likelihood_function` the search calls: evaluate the
galaxy image on the real-space grid, transform it to the `(u, v)` points, and compare against the
measured visibilities with a Gaussian likelihood over the real and imaginary parts
(`PyAutoGalaxy:autogalaxy/interferometer/model/analysis.py`).
"""
analysis = ag.AnalysisInterferometer(dataset=dataset, use_jax=True)

analysis.print_vram_use(model=model, batch_size=search.batch_size)

"""
__Model-Fit__

Results are written to the output folder on the fly, from the best model found so far.
"""
print(f"Output folder: {search.paths.output_path.resolve()}")

result = search.fit(model=model, analysis=analysis)

"""
__Result__

`fit.png` in the output folder is the visibility-space fit; `dirty_images` are the real-space
diagnostics. Both are written automatically, and both are reproducible here at whatever scaling
the science needs.
"""
print(result.info)

PLOT_DIR = Path("scripts") / "scratch" / "<your_galaxy>"

aplt.subplot_fit_interferometer(
    fit=result.max_log_likelihood_fit,
    output_path=str(PLOT_DIR / "fit"),
    output_format="png",
)

aplt.subplot_fit_dirty_images(
    fit=result.max_log_likelihood_fit,
    output_path=str(PLOT_DIR / "fit_dirty"),
    output_format="png",
)

aplt.subplot_fit_real_space(
    fit=result.max_log_likelihood_fit,
    output_path=str(PLOT_DIR / "fit_real_space"),
    output_format="png",
)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

The output-folder anatomy — `files/`, `image/` (which here holds `dirty_images.fits` alongside
`fit.fits`), `model.info`, `model.results`, `search.summary` and the `<unique_hash>` resume
behaviour — is `__Output Folder Layout__` in
[`autogalaxy_workspace/scripts/interferometer/modeling.py`](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/interferometer/modeling.py).
Link it rather than copying the tree. Driving the fit, watching it, and the resume trap are
[`ag_run_search`](./ag_run_search.md).

## Branch — choosing the transformer

Three transformers exist (`PyAutoArray:autoarray/operators/transformer.py`), and the choice is
not cosmetic.

- **`ag.TransformerNUFFT`** — the default, and the default in `ag.Interferometer.from_fits`
  itself. A non-uniform FFT backed by `nufftax`, a pure-JAX implementation that jit-compiles and
  vmap-batches with the rest of the library. Recommended at any dataset size. Because it is
  JAX-native, light-profile fits now run at full GPU speed for visibility counts in the tens or
  hundreds of millions — the scale of a high-resolution ALMA observation.
- **`ag.TransformerDFT`** — the exact discrete Fourier transform. Slower once `n_vis` is large,
  because it is genuinely `O(n_vis × n_pixels)`, but it is the reference implementation. It is
  worth running once on a small dataset to check a NUFFT result: on a 190-visibility SMA
  sampling with a 64 × 64 real-space grid the two agree in log likelihood to roughly one part in
  10⁹, so a disagreement bigger than that means something about the NUFFT setup is wrong rather
  than the transform being approximate. It is also what the pixelised reconstruction's
  sparse-operator path uses.
- **`ag.TransformerNUFFTPyNUFFT`** — a legacy `pynufft`-backed transformer, kept as a non-JAX
  fallback. It is not JAX-traceable, so it forfeits GPU acceleration *and* the gradient-based
  searches, which need the likelihood's derivatives.

**There is a guard, and it is there for a reason.** `ag.Interferometer` (and `from_fits`) raises
`raise_error_dft_visibilities_limit=True` by default, and it will refuse to build a dataset with
more than **10,000 visibilities** while `transformer_class=ag.TransformerDFT`. The DFT at that
scale is not slow-but-tolerable, it is unusable. The escape hatch exists —
`raise_error_dft_visibilities_limit=False` — and is legitimate when you are deliberately
profiling the exact path, but the honest reading of that error is "you meant to use the NUFFT".

The reason dataset size no longer forces a modelling decision is worth stating plainly to the
user: it used to be that a large visibility table pushed you toward a pixelised reconstruction
for performance reasons. It does not any more
(`autogalaxy_workspace:scripts/interferometer/start_here.py` `__Number of Visibilities__`).
Choose a pixelisation because the *morphology* demands it, never because the file is big.

## Branch — dirty images are diagnostics, not data

The thing you look at is not the thing you fit, and keeping that straight is most of the skill
of interpreting an interferometer fit.

```python
aplt.subplot_interferometer_dataset(dataset=dataset, output_path=..., output_format="png")
aplt.subplot_interferometer_dirty_images(dataset=dataset, output_path=..., output_format="png")

aplt.plot_array(array=dataset.dirty_image, title="Dirty Image", output_path=...,
                output_filename="dirty_image", output_format="png")
```

`autogalaxy_workspace:scripts/interferometer/plot.py`. `subplot_interferometer_dataset` shows the
visibility-space quantities and the uv coverage; the dirty-image subplot transforms *back* for
display only. On the fit side there are three:

| Call | Shows | Writes into `output_path` |
|---|---|---|
| `aplt.subplot_fit_interferometer` | the visibility-space fit — data, model visibilities, residuals, chi-squared | `fit.png` |
| `aplt.subplot_fit_dirty_images` | the same fit transformed back to real space | `fit_dirty_images.png` |
| `aplt.subplot_fit_real_space` | the model's real-space image and the reconstruction, with no transform applied | `fit_real_space.png` |

All three write a **fixed filename stem** and do not accept `output_filename`, so a separate
directory per figure is how you keep two fits apart — the same rule as the imaging subplots
([`../wiki/core/api/plotting.md`](../wiki/core/api/plotting.md)). `plot_array`,
`subplot_interferometer_dataset` and `subplot_interferometer_dirty_images` *do* accept
`output_filename`; passing it to one of the fit subplots raises `TypeError`.

Reading the residuals needs the dirty beam in mind. The individual real-space maps are available
on the fit object — `fit.dirty_image`, `fit.dirty_model_image`, `fit.dirty_residual_map`,
`fit.dirty_normalized_residual_map`, `fit.dirty_chi_squared_map`
(`PyAutoGalaxy:autogalaxy/interferometer/fit_interferometer.py`) — and a ringing pattern of
positive and negative residual around a real source is the *expected* signature of an imperfectly
subtracted beam, not a model failure. What is a model failure is a residual with structure that
survives across baselines, or a normalised residual map with coherent large-scale sign. Judge the
fit in visibility space first (`subplot_fit_interferometer`) and use the dirty maps to see *where*
on the sky the misfit lives. The general residual-inspection discipline is
[`ag_plot_fit`](./ag_plot_fit.md).

## Branch — a pixelised reconstruction, and very large visibility tables

A pixelisation remains the right choice when the morphology is genuinely irregular — clumpy star
formation, strong asymmetry — and no smooth profile or basis captures it. The linear algebra is
the same as for imaging with the transformer standing in for the PSF convolution
([`../wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md)),
and the composition procedure is `ag_pixelization`.
`autogalaxy_workspace:scripts/interferometer/features/pixelization/modeling.py` is the
interferometer variant.

What is specific to visibilities is the **sparse NUFFT operator**. Pixelised reconstruction needs
dense linear algebra that would be prohibitive over a large visibility table, so the dataset can
precompute an operator matrix that exploits the sparsity of the reconstruction
(`PyAutoArray:autoarray/inversion/inversion/interferometer/inversion_interferometer_util.py`).
Building it costs anything from milliseconds to hours depending on visibility count, real-space
mask size, and CPU versus GPU — and without it that cost is paid before *every* fit. So compute
it once and cache it, which is exactly what
`autogalaxy_workspace:scripts/interferometer/features/pixelization/many_visibilities_preparation.py`
does:

```python
import numpy as np

dataset = dataset.apply_sparse_operator(
    use_jax=True,
    chunk_k=2048,        # visibilities processed at a time; raise until memory complains
    show_progress=True,  # a progress bar, which matters when this takes an hour
    show_memory=True,
)

nufft_precision_operator = dataset.psf_precision_operator_from(
    use_jax=True, chunk_k=2048, show_progress=True, show_memory=True
)

np.save(
    file=DATASET_PATH / f"nufft_precision_operator_{MASK_RADIUS}.npy",
    arr=nufft_precision_operator,
    allow_pickle=False,
)
```

Reload it with `np.load(..., allow_pickle=False)` and hand it back through
`apply_sparse_operator(nufft_precision_operator=...)`. Two practical notes: the cached file is
tied to the real-space mask it was built with, which is why the mask radius belongs in the
filename; and on a modern GPU a million-visibility operator takes under a minute, so on that
hardware computing it inline is fine and the caching is a laptop-and-CPU concern.

That preparation script also carries a commented-out profiling block that fabricates a synthetic
visibility table at a chosen size, which is the honest way to find out how long *your* dataset
will take before committing to it.

## Branch — preparing your own data

The three FITS files and what must be true of them — units, the `(n_vis, 2)` shape of
`uv_wavelengths` in wavelengths rather than metres, the pixel-scale choice for the real-space
mask, and the optional light-centre and extra-galaxy centre files — are
`autogalaxy_workspace:scripts/interferometer/data_preparation.py`. Read it before loading real
data; the pixel-scale and uv-unit mistakes are both silent.

Coming from a CASA measurement set, the export path is
`autogalaxy_workspace:scripts/interferometer/casa_reduction.py` — and that script **says of
itself that it is incomplete and in development**, so treat it as a set of hints rather than a
recipe. What it does establish reliably is the shape contract: an ALMA `.ms` stores visibilities
as `(2, n_spw, n_c, n_v, 2)` with the leading axis the two polarisations; `split` peels off
spectral windows and averages channels; and the `uv_wavelengths` you export must be in
wavelengths, not metres. Do not invent the rest of that workflow — if a user needs a step the
script does not cover, say the script is incomplete and point them at the project's support
channel rather than guessing at CASA semantics.

Extra galaxies whose emission blends with the target are handled the same way as for imaging, and
`autogalaxy_workspace:scripts/interferometer/features/extra_galaxies/modeling.py` is the
visibility version; the levers themselves are `ag_light_model_extras`.

## Branch — cost, and proving the script first

Two numbers dominate run time: the visibility count, which sets the transform cost per
evaluation, and the real-space pixel count, which sets it too. The levers, in order of effect:

- **Shrink the real-space mask** to the informative region. This is the biggest one and the one
  most often left at a default.
- **Average channels or baselines** where the science allows.
- **Keep the model parametric** unless the morphology genuinely demands a pixelisation.
- **Choose the transformer deliberately** rather than inheriting a default you have not checked.

On a GPU, check VRAM before a long run — `analysis.print_vram_use(model=model,
batch_size=search.batch_size)`, twenty or thirty seconds
(`autogalaxy_workspace:scripts/interferometer/modeling.py` `__VRAM Use__`). A parametric fit to a
small visibility set is a few hundred megabytes; a pixelised reconstruction on a large one can
run past ten gigabytes.

And smoke-test before the real run:

```bash
PYAUTO_TEST_MODE=2 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/interferometer_fit.py
```

Level 2 calls the likelihood exactly once, which is the fastest proof that the mask, the
transformer and the model all agree with each other. Level 1 if you want the fit products
written. The levels and the writable-cache variables are
[`../wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md). If a NumPy stack
trace would be easier to read than a JAX one, `use_jax=False` or `PYAUTO_DISABLE_JAX=1` — see
[`ag_debug_fit_failure`](./ag_debug_fit_failure.md).

## Combine

- [`ag_simulate_dataset`](./ag_simulate_dataset.md) — simulate visibilities with known truth
  from a real array's `uv_wavelengths` and fit those first. This is the cleanest way to separate
  a model problem from a data problem, and note that `ag.SimulatorInterferometer` defaults to
  `TransformerDFT` where the dataset loader defaults to the NUFFT, so set it explicitly when you
  simulate at scale.
- [`ag_multi_dataset`](./ag_multi_dataset.md) — fit visibilities jointly with CCD imaging of the
  same galaxy, which is a factor graph with `ag.AnalysisInterferometer` on one factor.
- [`ag_configure_search`](./ag_configure_search.md) — `af.MultiStartProdigy` for a fast MAP
  check, `af.Nautilus` for the posterior, and the `unique_tag` resume semantics.
- [`ag_run_search`](./ag_run_search.md) — driving the fit, the output folder, and the stale-resume
  trap.
- [`ag_plot_fit`](./ag_plot_fit.md) — figure scaling, log10 stretch and fixed colour limits, all
  of which apply to the dirty maps.
- [`ag_load_results`](./ag_load_results.md) — getting the posterior and derived quantities back.
- `ag_pixelization` and `ag_basis_profiles` — the components you would reach for when a Sersic
  cannot describe the morphology.

When the fit is worth keeping, offer (default-yes) to record it in a dated
`wiki/project/YYYY-MM-DD-<slug>.md` entry: the array and visibility count, the real-space mask
and transformer chosen and why, what was inferred, and the output path — per
[`_style.md`](./_style.md) property #5. The mask and transformer choices are the two decisions a
reader of the fit will want justified.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Fitting](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_1_introduction/tutorial_3_fitting.ipynb):
  how a model image becomes a log likelihood via residuals, noise and chi-squared. The lecture
  series has no interferometer chapter, so this teaches the likelihood in its imaging form —
  everything transfers except that the comparison happens after a Fourier transform.
- **General reference** — [RTD: Features](https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_3_features.html):
  the interferometry section of the feature tour, with pointers onward.
- **Experienced PyAutoGalaxy user** — [workspace: interferometer/start_here.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/interferometer/start_here.py):
  the minimal end-to-end uv-plane fit, with the transformer and NUFFT-backend sections this
  skill mirrors.

## Agent procedural checklist

1. Confirm `nufftax` is importable before writing a script that defaults to the NUFFT.
2. Ask for the visibility count and the on-sky extent of the emission — they set the transformer
   and the real-space mask.
3. Set `shape_native`, `pixel_scales` and `radius` of the real-space mask deliberately, and say
   what each one buys; never leave them at a copied default on real data.
4. Load with `ag.Interferometer.from_fits` and an explicit `transformer_class`; if the user asks
   for `TransformerDFT` above 10,000 visibilities, explain the guard rather than disabling it.
5. Compose the model exactly as for imaging, and do **not** add an over-sampling section.
6. Plot the dirty images before fitting, quote the absolute path, and offer to open it.
7. Validate with `PYAUTO_TEST_MODE=2`; on a GPU run `analysis.print_vram_use` before a long fit.
8. Announce the output path at launch and name `model.results` and `image/fit.png` first.
9. Judge the fit in visibility space first, then use the dirty maps to locate the misfit; say
   plainly that beam sidelobes in a residual map are expected.
10. For a pixelised fit on a large table, cache the sparse operator and name the file after the
    mask radius it was built with.
11. Offer the `wiki/project/` entry recording the mask and transformer choices.
