---
name: ag_simulate_dataset
description: Simulate CCD imaging (or interferometer visibilities) of a galaxy with known truth — a grid and over-sampling, a PSF, an exposure time and background sky, one or more galaxies built from light profiles, then FITS output plus a `galaxies.json` truth record. Covers targeting a signal-to-noise ratio directly with the `lp_snr` profiles, simulating a whole sample in a loop for population or machine-learning work, adding a contaminating extra galaxy with its noise-scaling mask, and the `should_simulate` auto-simulation convention every workspace script uses. Use to rehearse the modelling loop before real data, to build training sets, to test a recovery, or when a user has no data yet. Not for loading or preparing real observations (`ag_prepare_imaging_data`), and not for fitting.
---

# Simulating a galaxy dataset with known truth

A simulated dataset is the only situation in galaxy modelling where you know the answer.
That makes it worth far more than a convenience: it is how you establish that your model
can recover a parameter at all, how you find out what signal-to-noise you need before you
propose for telescope time, how you separate "the fit is wrong" from "the data cannot
constrain this", and how you generate the thousands of labelled images a neural network
needs. It is also the fastest way to rehearse the whole loop — compose, search, inspect —
before real data is at stake.

Statistically, what you are building is a draw from the likelihood's own generative model:
take a noise-free galaxy image, convolve it with the PSF, scale to counts through an
exposure time, add a background sky, and draw Poisson noise. Because that is exactly the
forward model the likelihood inverts, a fit to simulated data tests the *inference* in
isolation — any bias you find is yours, not the data's. Simulated data is also **exempt from
the real-data inspection gate** (see
[`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md)) for the same reason: you already
know where every component is.

The canonical scripts are `autogalaxy_workspace:scripts/imaging/simulator.py` (bulge, disk
and a contaminating neighbour) and `autogalaxy_workspace:scripts/imaging/simulator_sersic.py`
(a single Sersic). What each light profile means physically is
[`../wiki/core/concepts/light_profiles.md`](../wiki/core/concepts/light_profiles.md); the
dataset objects are [`../wiki/core/api/datasets.md`](../wiki/core/api/datasets.md).

## Ask

- *"What are you simulating for — rehearsing the workflow, a recovery test, a training set,
  or a signal-to-noise feasibility study?"* This picks the branch, and the last two change
  the API you want (`lp_snr`, and the sample loop).
- *"One galaxy or several, and should a contaminating neighbour be included?"* Including one
  is worth doing deliberately: it is how you rehearse the noise-scaling step you will
  certainly need on real data.
- *"What instrument are you standing in for?"* — it sets `pixel_scales`, the PSF width and a
  plausible exposure time, and makes the simulation answer a question about *your* telescope
  rather than an abstract one.

## Branch — a single Sersic

The smallest useful simulation, and the one to start from. Adapted from
`autogalaxy_workspace:scripts/imaging/simulator_sersic.py`.

```python
"""
Simulator: Single Sersic
========================

Simulate CCD imaging of a galaxy whose light is a single elliptical Sersic profile, with
known truth parameters recorded alongside the data. The simulation applies the same forward
model a fit inverts — evaluate the profile on an over-sampled grid, convolve with the PSF,
scale through an exposure time, add a background sky and draw Poisson noise — so a fit to
the output tests the inference rather than the data.

__Contents__

- **Imports:** Import the required libraries.
- **Grid:** Build the coordinate grid and its adaptive over-sampling.
- **PSF and Simulator:** Define the optical blurring and the noise properties.
- **Galaxies:** Define the true galaxy whose parameters we intend to recover.
- **Output:** Write the dataset to FITS, plus a `galaxies.json` record of the truth.
"""

"""
__Imports__
"""
from pathlib import Path

import autogalaxy as ag
import autogalaxy.plot as aplt

DATASET_PATH = Path("dataset") / "imaging" / "simple_sersic"

"""
__Grid__

The `Grid2D` is the set of (y,x) arcsecond coordinates the galaxy's light is evaluated on,
and `pixel_scales` ties it to a detector — set it to the instrument you are standing in for.
Over-sampling then evaluates the profile on a finer sub-grid where its intensity gradient is
steep: a Sersic varies enormously across the central pixel, so a single evaluation at the
pixel centre under-counts the flux and produces a subtly wrong image. Simulations use higher
sub-sampling than fits (32x32 in the centre rather than 8x8) because the cost is paid once
rather than at every likelihood call
(`PyAutoArray:autoarray/operators/over_sampling/over_sample_util.py`).
"""
grid = ag.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.1)

over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=grid,
    sub_size_list=[32, 8, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)

grid = grid.apply_over_sampling(over_sample_size=over_sample_size)

"""
__PSF and Simulator__

Every real CCD image is blurred by the telescope optics, so a simulation without a PSF is not
imaging data. A Gaussian kernel is a reasonable stand-in when you do not have a real PSF
(FWHM = 2.35 * sigma). The `SimulatorImaging` object then supplies the rest of what makes
data noisy rather than ideal: `exposure_time` converts electrons per second to counts and so
sets the Poisson noise level, and `background_sky_level` adds the sky's contribution to the
noise budget (`PyAutoArray:autoarray/dataset/imaging/simulator.py`). Raising the exposure
time raises the signal-to-noise; the ratio of the two controls how much of the noise is
counting statistics versus sky.
"""
psf = ag.Convolver.from_gaussian(
    shape_native=(11, 11), sigma=0.1, pixel_scales=grid.pixel_scales
)

simulator = ag.SimulatorImaging(
    exposure_time=300.0,
    psf=psf,
    background_sky_level=0.1,
    add_poisson_noise_to_data=True,
)

"""
__Galaxies__

The truth. `sersic_index` sets the profile's concentration — n ~ 4 is a de Vaucouleurs-like
spheroid, n ~ 1 an exponential disk — and `effective_radius` is the radius containing half
the profile's light. For a *simulation* the axis-ratio and position-angle parameterisation is
the intuitive one, so `ag.convert.ell_comps_from` translates it into the `ell_comps` the
profile actually takes; a fit uses `ell_comps` directly, because a position angle's periodic
boundary is pathological for a non-linear search
(`PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py`).
"""
galaxy = ag.Galaxy(
    redshift=0.5,
    bulge=ag.lp.Sersic(
        centre=(0.0, 0.0),
        ell_comps=ag.convert.ell_comps_from(axis_ratio=0.9, angle=45.0),
        intensity=1.0,
        effective_radius=0.8,
        sersic_index=4.0,
    ),
)

galaxies = ag.Galaxies(galaxies=[galaxy])

dataset = simulator.via_galaxies_from(galaxies=galaxies, grid=grid)

print(f"peak signal-to-noise: {float(dataset.signal_to_noise_map.max()):.1f}")

"""
__Output__

The FITS files are written in exactly the layout `ag.Imaging.from_fits` expects, so the
simulated dataset is indistinguishable from real data to everything downstream. The
`galaxies.json` record is the part people skip and regret: it stores the true light profiles
so that months later you can still state what the fit was supposed to recover. Load it back
with `ag.from_json`.
"""
aplt.fits_imaging(
    dataset=dataset,
    data_path=DATASET_PATH / "data.fits",
    psf_path=DATASET_PATH / "psf.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    overwrite=True,
)

ag.output_to_json(obj=galaxies, file_path=DATASET_PATH / "galaxies.json")

aplt.subplot_imaging_dataset(
    dataset=dataset, output_path=DATASET_PATH, output_format="png"
)
aplt.subplot_galaxies(
    galaxies=galaxies, grid=grid, output_path=DATASET_PATH, output_format="png"
)

print(f"Saved to: {DATASET_PATH.resolve()}")
```

Quote that path back and offer to open it once. The `subplot_galaxies` figure is the useful
one for a simulation: it shows the noise-free truth beside the profile's components, which
is what you compare a fit against.

## Branch — bulge, disk, and a contaminating neighbour

The realistic default. Two components let you pose the question galaxy morphology usually
cares about — the bulge-to-total light ratio — and a faint offset neighbour lets you
rehearse the noise-scaling step. Adapted from
`autogalaxy_workspace:scripts/imaging/simulator.py`.

```python
extra_galaxy_centre = (2.2, 1.6)

over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=grid,
    sub_size_list=[32, 8, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0), extra_galaxy_centre],
)
grid = grid.apply_over_sampling(over_sample_size=over_sample_size)

galaxy = ag.Galaxy(
    redshift=0.5,
    bulge=ag.lp.Sersic(
        centre=(0.0, 0.0),
        ell_comps=ag.convert.ell_comps_from(axis_ratio=0.9, angle=45.0),
        intensity=1.0,
        effective_radius=0.6,
        sersic_index=3.0,
    ),
    disk=ag.lp.Exponential(
        centre=(0.0, 0.0),
        ell_comps=ag.convert.ell_comps_from(axis_ratio=0.7, angle=30.0),
        intensity=0.5,
        effective_radius=1.6,
    ),
)

extra_galaxy = ag.Galaxy(
    redshift=0.5,
    light=ag.lp.ExponentialSph(
        centre=extra_galaxy_centre, intensity=1.0, effective_radius=0.3
    ),
)

galaxies = ag.Galaxies(galaxies=[galaxy, extra_galaxy])
dataset = simulator.via_galaxies_from(galaxies=galaxies, grid=grid)
```

Three details carry weight. The bulge is compact with a high `sersic_index` and the disk is
extended with n fixed at 1 by construction — that contrast is what makes the decomposition
identifiable at all. The neighbour's centre appears in `centre_list` as well as in its own
profile, so it is over-sampled properly rather than being the one badly-evaluated object in
the frame. And the attribute names (`bulge`, `disk`, `light`) are arbitrary labels you choose
— name them for what they measure.

Write the neighbour's noise-scaling mask in the same script, so the modelling examples can
load it without a separate preparation step:

```python
mask_extra_galaxies = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    centre=extra_galaxy_centre,
    radius=3.0 * 0.3,  # ~3x the neighbour's effective radius
    invert=True,  # `True` inside the circle: the region whose noise is scaled.
)

aplt.fits_array(
    array=mask_extra_galaxies,
    file_path=DATASET_PATH / "mask_extra_galaxies.fits",
    overwrite=True,
)
```

Deriving the radius from the neighbour's own `effective_radius` keeps the two in sync if you
later change it. The strategies this mask feeds into are
[`../wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../wiki/core/concepts/extra_galaxies_and_noise_scaling.md).

## Branch — target a signal-to-noise ratio directly

Often the question is not "what intensity?" but "what if this galaxy were detected at S/N =
20?". Choosing an `intensity` that lands there is guesswork; the `lp_snr` profiles remove it
by solving for the intensity that achieves a requested ratio, using the simulator's
`exposure_time` and `background_sky_level` to do so. Adapted from
`autogalaxy_workspace:scripts/imaging/features/simulator_manual_signal_to_noise.py`.

```python
galaxy_0 = ag.Galaxy(
    redshift=0.5,
    bulge=ag.lp_snr.Sersic(
        signal_to_noise_ratio=20.0,
        centre=(0.0, -1.0),
        ell_comps=(0.25, 0.1),
        effective_radius=0.8,
        sersic_index=2.5,
    ),
)

galaxy_1 = ag.Galaxy(
    redshift=0.5,
    bulge=ag.lp_snr.Sersic(
        signal_to_noise_ratio=10.0,
        centre=(0.0, 1.0),
        ell_comps=(0.0, 0.1),
        effective_radius=0.6,
        sersic_index=3.0,
    ),
)

dataset = simulator.via_galaxies_from(
    galaxies=ag.Galaxies(galaxies=[galaxy_0, galaxy_1]), grid=grid
)
```

Note the profiles take **no** `intensity` — that is the parameter being solved for. The
trade-off is that `exposure_time` and `background_sky_level` no longer set the S/N, only the
*balance* between counting noise and sky noise. So they still matter for realism: doubling
the exposure time shifts the noise budget toward Poisson statistics even though the S/N is
pinned. Choose them to match your instrument if the noise character matters to the study.

This is also the profile family to reach for in a feasibility question — simulate the same
galaxy at S/N 10, 20 and 50, fit each, and see where the parameter you care about stops
being constrained. That is a far more honest answer than a single simulation at whatever
intensity happened to be typed.

## Branch — a sample, for population or machine-learning work

To generate many galaxies, draw each one's parameters from a distribution and loop. Adapted
from `autogalaxy_workspace:scripts/imaging/simulator_sample.py`, which draws directly from a
NumPy generator — deliberately, because these are *truths* for synthetic data, not a model
being fitted, so there is no reason to involve the model-composition API.

```python
import numpy as np

rng = np.random.default_rng()


def _clipped_ell_comp() -> float:
    return float(np.clip(rng.normal(0.0, 0.2), -1.0, 1.0))


def _random_galaxy() -> ag.Galaxy:
    bulge = ag.lp_snr.Sersic(
        centre=(0.0, 0.0),
        ell_comps=(_clipped_ell_comp(), _clipped_ell_comp()),
        effective_radius=float(rng.uniform(1.0, 5.0)),
        sersic_index=float(np.clip(rng.normal(4.0, 1.0), 0.8, 5.0)),
        signal_to_noise_ratio=float(rng.uniform(20.0, 60.0)),
    )
    return ag.Galaxy(redshift=0.5, bulge=bulge)


total_datasets = 3

for sample_index in range(total_datasets):

    sample_path = DATASET_PATH / f"dataset_{sample_index}"

    galaxies = ag.Galaxies(galaxies=[_random_galaxy()])
    dataset = simulator.via_galaxies_from(galaxies=galaxies, grid=grid)

    aplt.fits_imaging(
        dataset=dataset,
        data_path=sample_path / "data.fits",
        psf_path=sample_path / "psf.fits",
        noise_map_path=sample_path / "noise_map.fits",
        overwrite=True,
    )
    ag.output_to_json(obj=galaxies, file_path=sample_path / "galaxies.json")
```

The `lp_snr` bulge is what makes the loop usable: with a plain `intensity` drawn from a
distribution, a fraction of your sample would be invisible and another fraction saturated.
Pinning S/N per galaxy guarantees every image is detectable. Write a `galaxies.json` per
dataset — with a sample, the truth record stops being a nicety and becomes the labels.

For a one-line random galaxy without writing your own distributions,
`ag.model_util.random_galaxy_for_simulation_from()` returns one drawn from the library's own
choices, and `ag.model_util.SIMULATOR_RANDOM_GALAXY_SUMMARY` prints what those choices are —
read that summary before using it in anything you will publish, so the prior you inherited
is one you actually endorse.

## Branch — interferometer visibilities

For sub-mm and radio data (ALMA, JVLA, LOFAR) the observable is visibilities in the uv-plane,
not an image, and fitting them there avoids the correlated noise a dirty image carries.
Adapted from `autogalaxy_workspace:scripts/interferometer/simulator.py`.

```python
uv_wavelengths = ag.ndarray_via_fits_from(
    file_path=Path("dataset") / "interferometer" / "uv_wavelengths" / "sma.fits", hdu=0
)

simulator = ag.SimulatorInterferometer(
    uv_wavelengths=uv_wavelengths,
    exposure_time=300.0,
    noise_sigma=1000.0,
    transformer_class=ag.TransformerNUFFT,
)

real_space_grid = ag.Grid2D.uniform(shape_native=(800, 800), pixel_scales=0.05)

dataset = simulator.via_galaxies_from(galaxies=galaxies, grid=real_space_grid)

aplt.subplot_interferometer_dirty_images(
    dataset=dataset, output_path=DATASET_PATH, output_format="png"
)

aplt.fits_interferometer(
    dataset=dataset,
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    uv_wavelengths_path=DATASET_PATH / "uv_wavelengths.fits",
    overwrite=True,
)
```

Four differences from imaging are worth knowing. The baselines come from a real array's
`uv_wavelengths` — the workspace ships SMA (low resolution, very fast) and ALMA files;
swapping the file swaps the instrument. There is **no PSF and no over-sampling**: the image
is evaluated in real space and Fourier-transformed, and interferometers do not observe in a
way that makes over-sampling necessary. `noise_sigma` replaces the exposure-time-driven
Poisson model. And the thing you *look at* is the dirty image, which is a diagnostic — the
fit itself happens in the uv-plane. The physics is
[`../wiki/core/concepts/interferometer_theory.md`](../wiki/core/concepts/interferometer_theory.md).
Full interferometer modelling is a separate skill (`ag_build_interferometer_model`, not yet
written — see [`../PENDING.md`](../PENDING.md)).

## The auto-simulation convention

Every workspace script that fits a dataset first checks whether it exists and runs the
matching simulator if it does not, so an example can be run from a fresh clone with no
manual step:

```python
if ag.util.dataset.should_simulate(str(dataset_path)):
    import subprocess
    import sys

    subprocess.run([sys.executable, "scripts/imaging/simulator.py"], check=True)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py`. Adopt the same pattern in
scripts you write, and know the sharp edge: `should_simulate` tests **existence**, not
whether the dataset on disk matches the simulator that would produce it. Change the
simulator's parameters and re-run the fit and you will silently fit the *old* data. The same
applies to `PYAUTO_SMALL_DATASETS=1`, which caps grids and masks to a small size: a
full-resolution dataset already on disk will be reused and mismatch the capped grids. Delete
the dataset directory when you change either
([`../wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md)).

## JAX, for many simulations

For parameter sweeps, mock-data studies or batch figure generation, build the simulator with
`use_jax=True` — the simulation then runs on JAX arrays (and the GPU, when one is
configured):

```python
simulator_jax = ag.SimulatorImaging(
    exposure_time=300.0,
    psf=psf,
    background_sky_level=0.1,
    add_poisson_noise_to_data=True,
    use_jax=True,
)

dataset_jax = simulator_jax.via_galaxies_from(galaxies=galaxies, grid=grid)
```

`dataset_jax.data.array` is a `jax.Array`, and the plot and FITS helpers call
`numpy.asarray()` internally, so saving and plotting need no manual conversion.

Wrapping the whole simulation call in a jitted function — worth it across *many* calls —
additionally requires registering the galaxy classes as JAX pytrees before the first jitted
call, and the helper that does that registration is **not in the released stack yet** (it
lives on the libraries' development branches only). Until it ships in a release, use the
eager `use_jax=True` call above; the `__JAX Variant__` section of
`autogalaxy_workspace:scripts/imaging/simulator.py` carries the jitted recipe for a
source install. **For interferometer simulations the jitted path does not work either way** —
use the eager call; `autogalaxy_workspace:scripts/interferometer/simulator.py` documents why.

## Combine — where this hands off

- **Fit the dataset you just made** → [`ag_build_imaging_model`](./ag_build_imaging_model.md)
  to compose the model, then [`ag_configure_search`](./ag_configure_search.md) and the
  run-search skill (`ag_run_search`). Compose a model that *matches* the truth first: if it
  cannot recover parameters it was handed exactly, the problem is the inference, and you have
  learned that cheaply.
- **Compare a fit against the truth** → load `galaxies.json` with `ag.from_json` and put the
  true and inferred values side by side; the results-loading and fit-plotting skills
  (`ag_load_results`, `ag_plot_fit`) do the rest.
- **You actually have real data** → [`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md),
  which also owns the inspection gate this branch is exempt from.

Offer (default-yes) a dated `wiki/project/YYYY-MM-DD-<slug>.md` entry when the simulation is
part of a study — the truth parameters and the S/N you chose *are* the experimental design,
and a recovery test is meaningless later without them.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Grids and galaxies](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_1_introduction/tutorial_1_grids_and_galaxies.ipynb):
  how a light profile becomes an image on a grid, and what each Sersic parameter changes —
  the foundation under every simulation.
- **General reference** — [RTD: Start here overview](https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_1_start_here.html):
  the core API end to end, including the simulation section, in one page.
- **Experienced PyAutoGalaxy user** — [workspace: imaging/simulator.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/imaging/simulator.py):
  the full bulge-plus-disk simulator with the contaminant mask and the executed JAX variant.

## Agent procedural checklist

1. Ask what the simulation is *for*; it decides the branch and whether `lp_snr` is wanted.
2. Set `pixel_scales`, PSF width and exposure time from a real instrument, not defaults.
3. Over-sample with every bright centre in `centre_list` — including any neighbour.
4. Write FITS **and** `galaxies.json`; write the neighbour's `mask_extra_galaxies.fits` in
   the same script if one exists.
5. Plot the dataset and the noise-free galaxies subplot; print and **quote** the absolute
   path, offering to open it once.
6. Delete the dataset directory before re-running with changed parameters or with
   `PYAUTO_SMALL_DATASETS=1` — `should_simulate` only checks existence.
7. Hand off to `ag_build_imaging_model`, and offer the `wiki/project/` entry when the
   simulation is part of a study.
