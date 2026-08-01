---
name: ag_prepare_imaging_data
description: Load a user's own CCD imaging of a galaxy from FITS into an `ag.Imaging` dataset and get it ready to fit — pixel scale, flux units, the RMS noise-map, the PSF, the mask extent, contaminating extra galaxies and foreground stars, over-sampling, and the optional `info.json` / centre sidecars. **This skill owns the real-data inspection gate**: the plot-and-settle procedure that must run before any model is composed or fitted on real observational data. Use whenever the user brings their own data (HST, JWST, Euclid, ground-based), whenever a dataset needs checking against PyAutoGalaxy's standards, or whenever a mask or contaminant decision is open. Not for simulating data (`ag_simulate_dataset`), not for composing the model itself (`ag_build_imaging_model`), and not for visibility-plane data.
---

# Preparing your own imaging data

Everything downstream inherits the decisions made here. A noise-map that is a variance
rather than an RMS makes every likelihood wrong by a constant power; a mask that truncates
the outer isophotes biases the effective radius and Sersic index directly; an unmodelled
neighbour inside the mask pulls the fit toward a galaxy that isn't there. None of those
three announce themselves — the search converges, the residuals look plausible, and the
number you publish is wrong. That is why this step is a gate rather than a formality.

Scientifically, the job is to hand the likelihood three things it can trust: an **image**
in electrons per second, a **per-pixel RMS noise-map** in the same units, and a **PSF** to
forward-convolve the model with. Statistically, the job is to define the *support* of the
likelihood — which pixels are in the sum — and to make sure every pixel inside it is
described by the model you are about to fit. The standards themselves come from
`autogalaxy_workspace:scripts/imaging/data_preparation/start_here.py`; the API catalogue
is [`../wiki/core/api/datasets.md`](../wiki/core/api/datasets.md).

## The real-data gate — non-negotiable

**Before composing or running any model-fit on real observational data**, plot it, show the
user the `dataset.png` path, and settle two things from that same look:

**(a) Extra galaxies, foreground stars and artefacts.** These are the single largest source
of fit bias. Decide, explicitly, which of the three strategies below applies to each one.

**(b) The mask extent** — the radius and shape that captures the galaxy's emission out to
where it meets the sky, without dragging in noise or contaminants. **Never leave the mask
radius as a silent default on real data.** A mask that cuts inside the outer isophotes
biases `effective_radius` and `sersic_index`, so this is a science-critical choice, not a
tidy-up.

**If you cannot plot it yourself** — no code execution, for example a GitHub-connector chat
— **the gate is not waived**: ask the user to plot and inspect the data, and to confirm both
(a) contaminants and (b) the mask extent, before you compose the fit. These are the
questions every real-data run must ask, on every harness.

**Simulated data is exempt** — you know the truth, including where every component is, so
there is nothing to discover by looking. Everything else in this skill still applies to
simulated data as documentation of what a real run would need.

The gate is satisfied by looking, not by asserting. The first branch below is how you look.

## Ask

- *"What instrument and filter, and what is the pixel scale?"* — you cannot proceed without
  it, and it is the one number nothing in the data can tell you.
- *"Is the noise-map an RMS standard deviation per pixel, or a variance / weight map / HST
  WHT map?"* — if they are not certain, treat it as unknown and convert; the likelihood
  assumes RMS.
- *"Are there neighbouring galaxies, foreground stars or reduction artefacts near the
  target?"* — the (a) half of the gate.
- *"How far out do you care about the light — just the bright body, or the faint outer
  envelope?"* — this is the (b) half of the gate phrased as a science question, which is
  how it should be decided.

## Branch — look at it first

Load the three ingredients and plot them. Nothing else happens until this figure has been
seen.

```python
"""
Data Inspection: <Galaxy Name> (<Instrument>)
=============================================

Load a galaxy's CCD imaging from FITS and inspect it before any model is composed. This
script exists to satisfy the real-data inspection gate: the image, noise-map, PSF and
signal-to-noise map are plotted so that two science-critical decisions can be made from
evidence rather than defaults — which contaminating objects are present, and how far out
the mask should extend.

__Contents__

- **Imports:** Import the required libraries.
- **Dataset:** Load the image, noise-map and PSF from FITS with the correct pixel scale.
- **Standards Check:** Verify the PSF is odd-sized and normalised, and report the S/N.
- **Plot:** Write the dataset subplot to disk for inspection.
"""

"""
__Imports__
"""
from pathlib import Path

import autogalaxy as ag
import autogalaxy.plot as aplt

DATASET_PATH = Path("dataset") / "imaging" / "my_galaxy"
PLOT_DIR = Path("scripts") / "scratch" / "my_galaxy"

"""
__Dataset__

Three ingredients are needed for galaxy modeling: the image in electrons per second, a
per-pixel RMS noise-map in the same units, and the PSF describing the blurring imposed by
the telescope optics. The PSF is *forward-convolved* onto the model rather than divided out
of the data, which is what lets a fit distinguish a genuinely compact bulge from a
seeing-broadened one.

`pixel_scales` converts pixels to arcseconds and must be correct for your instrument —
HST/ACS ~0.05", JWST/NIRCam ~0.03-0.06", Euclid VIS 0.1" and NISP 0.2", ground-based
0.2-0.3". Nothing in the FITS data can correct a wrong value for you; every inferred size
scales with it. Loading is handled by `ag.Imaging.from_fits`
(`PyAutoArray:autoarray/dataset/imaging/dataset.py`).
"""
PIXEL_SCALES = 0.1

dataset = ag.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    psf_path=DATASET_PATH / "psf.fits",
    pixel_scales=PIXEL_SCALES,
)

"""
__Standards Check__

Two properties of the PSF are cheap to check and expensive to get wrong. An **even-sized**
kernel shifts the convolved model by half a pixel, which propagates straight into the
inferred centre; and a kernel that does not **sum to unity** does not conserve flux, which
corrupts any magnitude or luminosity derived from the fit. The signal-to-noise peak is a
sanity check on the noise-map: a galaxy usually peaks somewhere around 10-300, and a value
orders of magnitude away from that is a sign the noise-map is in the wrong units or is a
variance rather than an RMS.
"""
psf_shape = dataset.psf.kernel.shape_native

print(f"PSF shape: {psf_shape}, odd: {all(s % 2 == 1 for s in psf_shape)}")
print(f"PSF sum: {float(dataset.psf.kernel.sum()):.6f} (should be 1.0)")
print(f"peak signal-to-noise: {float(dataset.signal_to_noise_map.max()):.1f}")

"""
__Plot__

The subplot shows the image, noise-map, PSF and signal-to-noise map together, which is
exactly the set needed to answer the two gate questions: what contaminating objects are
present, and how far out the galaxy's emission extends before it meets the sky.
"""
aplt.subplot_imaging_dataset(
    dataset=dataset,
    output_path=PLOT_DIR,
    output_filename="dataset",
    output_format="png",
)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

Then **quote the absolute path of `dataset.png` back to the user and offer to open it**
(`xdg-open` on Linux, `open` on macOS, `explorer.exe` or `wslview` from WSL) — one offer,
not repeated nagging. Ask the two gate questions against that specific figure, naming what
you can see in it. "There's a compact object about 2" north-east of the centre — is that a
neighbour or part of the galaxy?" is a useful question; "are there any contaminants?" in the
abstract is not.

## Branch — the three standards, and how to fix a violation

`autogalaxy_workspace:scripts/imaging/data_preparation/start_here.py` is the checklist; the
per-ingredient tools are in `examples/data.py`, `examples/noise_map.py` and
`examples/psf.py` beside it.

**The image.** Flux in **electrons per second**, galaxy near the centre, cut down to a
postage stamp. The units matter because default priors on light-profile `intensity` assume
them, and because magnitudes are computed from them. Conversions both ways are in the
preprocess module (`PyAutoArray:autoarray/dataset/preprocess.py`):

```python
exposure_time_map = ag.Array2D.full(
    fill_value=1000.0,
    shape_native=data.shape_native,
    pixel_scales=data.pixel_scales,
)

data_counts = ag.preprocess.array_eps_to_counts(
    array_eps=data, exposure_time_map=exposure_time_map
)
data_eps = ag.preprocess.array_counts_to_eps(
    array_counts=data_counts, exposure_time_map=exposure_time_map
)
```

ADUs need the gain as well — `ag.preprocess.array_eps_to_adus(array_eps=data, gain=4.0,
exposure_time_map=exposure_time_map)` and `array_adus_to_eps` back. If your reduction
produced a real per-pixel exposure-time map, load it with `ag.Array2D.from_fits` instead of
the flat `full` above; a flat map is a good approximation for many HST observations and not
for all. Trim an oversized stamp with
`ag.preprocess.array_with_new_shape(array=data, new_shape=(80, 80))`, which crops centred.
Background subtraction is better done by your reduction pipeline, but
`background_sky_level_via_edges_from` and `background_noise_map_via_edges_from` exist for
when it wasn't — and modelling the residual sky as a free parameter is often the better
answer anyway (see the sky-background note in
[`ag_build_imaging_model`](./ag_build_imaging_model.md)).

**The noise-map.** RMS standard deviation per pixel, in electrons per second, **including**
the Poisson contribution from the galaxy's own counts as well as background sky. This is the
one to be most careful about: reduction pipelines frequently drop the Poisson term, and a
noise-map that is a variance, an inverse variance, or an HST WHT map will produce a fit that
converges confidently to the wrong answer. The preprocess module has a converter for each
common input form — `noise_map_via_weight_map_from`,
`noise_map_via_inverse_noise_map_from`,
`noise_map_via_data_eps_and_exposure_time_map_from`,
`noise_map_via_data_eps_exposure_time_map_and_background_noise_map_from`,
`noise_map_via_data_eps_exposure_time_map_and_background_variances_from` and
`poisson_noise_via_data_eps_from`. If you cannot determine which form you have, the
instrument handbook is the authority; guessing here is not recoverable later.

**The PSF.** Odd dimensions, normalised to unity, centred, and roughly 11×11 to 21×21
pixels. Larger kernels (51×51) work but slow every likelihood evaluation, since convolution
runs on every model image. Load with normalisation applied:

```python
psf = ag.Convolver.from_fits(
    file_path=DATASET_PATH / "psf.fits",
    hdu=0,
    pixel_scales=PIXEL_SCALES,
    normalize=True,
)
```

`ag.Imaging.from_fits` normalises the PSF internally anyway, so this is belt-and-braces. An
even-sized kernel is a genuine problem rather than a warning:
`ag.preprocess.kernel_with_odd_dimensions_from` will interpolate one for you, but it *is*
an interpolation and the right fix is to re-derive the PSF at odd size in your reduction.
Resize with `ag.preprocess.array_with_new_shape(array=psf.kernel, new_shape=(21, 21))`.

## Branch — (a) contaminants: three strategies, one decision per object

For each neighbouring galaxy, foreground star or artefact you identified in the figure,
choose one:

**1. Scale its noise (the default).** Keep the pixels in the fit but blow their noise-map
values up so they contribute negligibly to the likelihood. Preferred over deleting pixels
because it leaves the pixel grid intact — which matters a great deal later if you move to a
pixelised reconstruction, where removed pixels create discontinuities.

```python
mask_extra_galaxies = ag.Mask2D.from_fits(
    file_path=DATASET_PATH / "mask_extra_galaxies.fits",
    pixel_scales=dataset.pixel_scales,
    invert=True,  # `True` marks the pixels whose noise is scaled.
)

dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)

aplt.subplot_imaging_dataset(
    dataset=dataset, output_path=PLOT_DIR, output_filename="dataset_scaled",
    output_format="png",
)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py`. Note `invert=True`: the
FITS convention here marks the *scaled* region as `True`. Build the mask as a union of
circles when you know the positions, following
`autogalaxy_workspace:scripts/imaging/data_preparation/examples/optional/mask_extra_galaxies.py`:

```python
import numpy as np

extra_galaxies_mask = np.zeros(data.shape_native, dtype=bool)

for centre, radius in [((1.0, 3.5), 1.5), ((-2.0, -3.5), 2.4)]:
    circle = ag.Mask2D.circular(
        shape_native=data.shape_native,
        pixel_scales=data.pixel_scales,
        centre=centre,
        radius=radius,
        invert=True,
    )
    extra_galaxies_mask = np.logical_or(extra_galaxies_mask, circle.native)

mask = ag.Mask2D(mask=extra_galaxies_mask, pixel_scales=data.pixel_scales)

aplt.fits_array(
    array=mask, file_path=DATASET_PATH / "mask_extra_galaxies.fits", overwrite=True
)
```

For irregular shapes there is a spray-paint GUI at
`autogalaxy_workspace:scripts/imaging/data_preparation/gui/mask_extra_galaxies.py`, and the
same `ag.Scribbler`-based tool appears inline at the foot of
`autogalaxy_workspace:scripts/imaging/start_here.py`. Point the user at it rather than
hand-deriving centres when the contaminant is a messy blend.

**2. Shrink the mask so it falls outside.** The simplest option, and the right one when the
contaminant sits comfortably beyond the galaxy's emission. It costs you nothing except the
sky annulus you gave up — but check it does not also cut into the outer isophotes, because
then you have traded a known bias for a worse one.

**3. Model it as an extra galaxy.** Give it its own light profile with a fixed centre. This
is the choice when its light genuinely overlaps the target's, so neither masking nor scaling
can separate them without also removing signal you need. That is a *model* decision, so it
belongs to [`ag_build_imaging_model`](./ag_build_imaging_model.md); what you produce here is
the list of centres it will consume:

```python
extra_galaxies_centres = ag.Grid2DIrregular(values=[(1.0, 3.5), (-2.0, -3.5)])

aplt.plot_array(
    array=data,
    title="Data",
    positions=[np.array(extra_galaxies_centres)],
    output_path=PLOT_DIR,
    output_filename="data_with_extra_galaxies",
    output_format="png",
)

ag.output_to_json(
    obj=extra_galaxies_centres,
    file_path=DATASET_PATH / "extra_galaxies_centres.json",
)
```

Adapted from
`autogalaxy_workspace:scripts/imaging/data_preparation/examples/optional/extra_galaxies_centres.py`.
Always plot the centres over the image before saving them — an off-by-a-sign (y,x) ordering
is obvious in a figure and invisible in a JSON file. There is a click-to-select GUI at
`autogalaxy_workspace:scripts/imaging/data_preparation/gui/extra_galaxies_centres.py` which
snaps to the brightest pixel in a 5×5 box.

The physics of choosing between the three, and what noise scaling does to the likelihood,
is
[`../wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../wiki/core/concepts/extra_galaxies_and_noise_scaling.md).

## Branch — (b) the mask extent

The mask defines which pixels enter the likelihood. Choose its radius from the figure, and
say out loud what you chose and why:

```python
MASK_RADIUS = 2.5

mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=MASK_RADIUS,
)

dataset = dataset.apply_mask(mask=mask)

aplt.subplot_imaging_dataset(
    dataset=dataset, output_path=PLOT_DIR, output_filename="dataset_masked",
    output_format="png",
)
```

Two failure directions, and they are not symmetric. **Too small** truncates the outer
isophotes and biases `effective_radius` and `sersic_index` — a real, systematic error in
your science result. **Too large** drags in sky-dominated pixels: it slows the fit and adds
little information, but it does not bias the answer, and it keeps honest sky pixels that
constrain a background level. When in doubt, err large and re-plot; the cost is run time,
not correctness.

Circular is the default and usually right for a single galaxy. Non-circular shapes exist
when the geometry calls for it — `ag.Mask2D.circular_annular(inner_radius=..., outer_radius=...)`
to exclude a saturated core, `ag.Mask2D.elliptical(major_axis_radius=..., axis_ratio=...,
angle=...)` and `ag.Mask2D.elliptical_annular(...)` for a strongly inclined disk. All four
are shown in
`autogalaxy_workspace:scripts/imaging/data_preparation/examples/optional/mask.py`, and
`autogalaxy_workspace:scripts/guides/modeling/customize.py` covers applying a custom mask to
a fit. A mask drawn by hand in the GUI
(`autogalaxy_workspace:scripts/imaging/data_preparation/gui/mask.py`) is written to
`mask.fits` and loaded back with `ag.Mask2D.from_fits`; for a genuinely irregular footprint,
`autogalaxy_workspace:scripts/imaging/data_preparation/manual/mask_irregular.py` is the
manual route.

Why the radius is a science decision rather than a default, and what the slim/native
distinction means once a mask is applied, is
[`../wiki/core/concepts/grids_and_masks.md`](../wiki/core/concepts/grids_and_masks.md).

## Branch — over-sampling

A Sersic profile's intensity varies steeply across a single central pixel, so evaluating it
once at the pixel centre under-counts the flux. Over-sampling evaluates the profile on a
finer sub-grid and averages, and it changes the inferred parameters — this is accuracy, not
cosmetics. Do it adaptively: high in the centre where the gradient is steep, low in the
outskirts where it is flat and the cost would be wasted.

```python
over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[8, 4, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)

dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py`. That reads as 8×8
sub-sampling inside 0.3", 4×4 between 0.3" and 0.6", and 2×2 beyond — note the list ends at
2, never 1, so even the outskirts keep a floor. `centre_list` takes **every** bright
centre, so if you are modelling an extra galaxy rather than masking it, add its centre here
too; a companion evaluated at 2×2 while the target gets 8×8 is a quiet accuracy loss. A
plain integer (`over_sample_size_lp=4`) applies uniform over-sampling when you want
simplicity over tuning. The `_lp` suffix names the grid used for **l**ight-**p**rofile
evaluation, which is a different grid from a pixelisation's.

## Branch — the optional sidecars

None of these are required to fit; all of them make the result easier to interpret later.

**`info.json`** — auxiliary numbers that travel with the dataset: redshift, velocity
dispersion, a stellar mass from the literature, a previous paper's measurement. Passed to
`search.fit(model=model, analysis=analysis, info=info)`, it is stored with the fit and can
be read back by the aggregator, which is what makes a population-scale comparison against
external measurements possible.

```python
import json

info = {"redshift": 0.5, "velocity_dispersion": 250.0, "stellar_mass": 1e11}

with open(DATASET_PATH / "info.json", "w+") as f:
    json.dump(info, f, indent=4)
```

Adapted from
`autogalaxy_workspace:scripts/imaging/data_preparation/examples/optional/info.py`.

**`light_centre.json`** — the galaxy's light centre as an `ag.Grid2DIrregular`, saved with
`ag.output_to_json`, for use as a fixed value in the model. Fixing the centre removes two
free parameters and rules out solutions where the model centre wanders somewhere
unphysical; it is the standard rescue when a search will not converge. Grounded in
`autogalaxy_workspace:scripts/imaging/data_preparation/examples/optional/light_centre.py`,
with a click-to-select GUI at
`autogalaxy_workspace:scripts/imaging/data_preparation/gui/light_centre.py`.

The on-disk layout these files belong to is not yet a wiki page — until it is, the
per-dataset READMEs under `autogalaxy_workspace:dataset/` and
`autogalaxy_workspace:scripts/imaging/data_preparation/start_here.py` are the ground truth
([`../PENDING.md`](../PENDING.md) tracks the page).

## Combine — where this hands off

- **The gate is satisfied and the dataset is loaded, masked and over-sampled** →
  [`ag_build_imaging_model`](./ag_build_imaging_model.md). Tell it what you decided about
  contaminants and the mask; it will ask otherwise.
- **You want to rehearse the whole loop before touching real data** →
  [`ag_simulate_dataset`](./ag_simulate_dataset.md), which builds a dataset in exactly this
  format with known truth.
- **A contaminant needs modelling rather than masking** → the model skill's extra-galaxies
  branch, fed by the `extra_galaxies_centres.json` you wrote above.
- **The data looks wrong in a way you can't place** → the environment skill
  ([`ag_setup_environment`](./ag_setup_environment.md)) if it is the *plot* misbehaving, or
  the fit-debugging skill (`ag_debug_fit_failure`) once a fit has actually run.

Offer (default-yes) to record the session as a dated
`wiki/project/YYYY-MM-DD-<slug>.md` entry — the mask radius you chose and *why*, and what
you did about each contaminant, are exactly the decisions you will want justified when you
write the paper.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Data](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_1_introduction/tutorial_2_data.ipynb):
  what a CCD image, a noise-map and a PSF actually are, and why the PSF is convolved onto
  the model rather than divided out of the data. Its companion,
  [chapter 2 tutorial 6](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_2_modeling/tutorial_6_masking.ipynb),
  is the masking lecture.
- **General reference** — [RTD: New user guide](https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_2_new_user_guide.html):
  routes by system scale and dataset type, and is the page to hand someone deciding how
  their data should be organised before they load it.
- **Experienced PyAutoGalaxy user** — [workspace: imaging/data_preparation/start_here.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/imaging/data_preparation/start_here.py):
  the standards checklist with the per-ingredient example scripts and GUIs beneath it.

## Agent procedural checklist

1. Establish the pixel scale and the noise-map's definition before writing code.
2. Load the three ingredients, plot the dataset subplot, **print and quote its absolute
   path**, and offer to open it once.
3. Run the gate against that figure: settle (a) every contaminant and (b) the mask extent
   *with the user*. On a harness that cannot plot, ask the user to do both — never waive it.
4. Check the three standards: eps units, RMS-with-Poisson noise-map, odd normalised PSF.
   Convert rather than assume.
5. Apply, in order: noise scaling for contaminants → the mask → adaptive over-sampling
   (with every bright centre in `centre_list`).
6. Write the sidecars the model will need (`extra_galaxies_centres.json`,
   `light_centre.json`, `info.json`) and plot any centres over the image before saving.
7. Save the script to `scripts/`, hand off to `ag_build_imaging_model`, and offer the
   `wiki/project/` entry recording the mask and contaminant decisions.
