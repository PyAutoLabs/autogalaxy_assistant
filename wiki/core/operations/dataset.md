---
title: Dataset layout and info.json
sources:
  - project: PyAutoArray
    paths:
      - autoarray/dataset/imaging/dataset.py
      - autoarray/structures/arrays/uniform_2d.py
      - autoarray/operators/convolver.py
      - autoarray/dataset/dataset_model.py
      - autoarray/util/dataset_util.py
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: autogalaxy_workspace
    paths:
      - scripts/imaging/start_here.py
      - scripts/imaging/data_preparation/start_here.py
      - dataset/.gitignore
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
  - project: autogalaxy_assistant
    paths:
      - dataset/imaging/cosj100020+015344/README.md
      - dataset/imaging/cosj100020+015344/info.json
      - dataset/imaging/cosj100020+015344/reduction_manifest.json
    pinned_commit: db52604f13305cb8a251fb3bb08bb5cc0ab84a55
last_updated: 2026-08-01
content_sha256: b84a33bbbab1269544755a2648e5337bc4b8962ec1b6bf9a523fbd84c13a0a00
---

# Dataset layout and info.json

How imaging datasets are organised on disk in this repository, what the `info.json` beside
each one actually contains, and how to load a single waveband. There is one bundled dataset
today — the JWST/NIRCam cutout of **COSJ100020+015344** — and this page describes the
convention it establishes rather than a general schema invented ahead of use.

Two things are deliberately *not* on this page. Data **preparation** (masking, centring,
converting your own `.fits` files into this layout) is a procedure, and belongs to
[`ag_prepare_imaging_data`](../../../skills/ag_prepare_imaging_data.md). The bundled
dataset's **provenance** — which MAST exposures, which pipeline, which catalogue the redshift
comes from — is in the dataset's own README, which is the authority for every number quoted
here.

## Directory layout

```
dataset/
└── imaging/                          # grouped by data type
    └── cosj100020+015344/            # one galaxy
        ├── README.md                 # provenance: exposures, pipeline, caveats, citations
        ├── info.json                 # dataset-level summary + every band nested under `per_band`
        ├── reduction_manifest.json   # per-band reduction and PSF record
        └── wavebands/
            ├── F115W/                # 419 x 419 @ 0.03"/pix
            │   ├── data.fits
            │   ├── noise_map.fits
            │   ├── psf.fits          # 21 x 21, unit sum
            │   └── info.json         # this band's measurements
            ├── F150W/                # 419 x 419 @ 0.03"/pix
            ├── F277W/                # 209 x 209 @ 0.06"/pix
            └── F444W/                # 209 x 209 @ 0.06"/pix
```

Two conventions are load-bearing:

- **`wavebands/<BAND>/` is one dataset directory per band.** A multi-band set is *not* one
  directory with suffixed filenames. Each band carries its own `data.fits`,
  `noise_map.fits`, `psf.fits` and `info.json`, because each band has its own pixel scale,
  its own PSF and its own measured shape. Single-band datasets may sit directly under
  `dataset/imaging/<name>/` with no `wavebands/` level.
- **The pixel scale differs between bands.** The NIRCam short-wave bands are sampled at
  0.03"/pixel and the long-wave bands at 0.06"/pixel. Reading `pixel_scale` from the band's
  own `info.json` rather than hard-coding one value for the dataset is not optional — get it
  wrong and every angular quantity the fit reports is wrong by a factor of two, silently. The
  four cutouts cover the same ~12.5" field despite the different array shapes.

## Loading one waveband

`ag.Imaging.from_fits` (`PyAutoArray:autoarray/dataset/imaging/dataset.py`) takes the three
FITS paths plus the pixel scale:

```python
import json
from pathlib import Path

import autogalaxy as ag

dataset_path = Path("dataset") / "imaging" / "cosj100020+015344" / "wavebands" / "F277W"

info = json.loads((dataset_path / "info.json").read_text())

dataset = ag.Imaging.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    psf_path=dataset_path / "psf.fits",
    pixel_scales=info["pixel_scale"],
)
```

**`dataset.psf` is a `Convolver`, not an array.** This catches people out: the attribute
returns the convolution operator (`PyAutoArray:autoarray/operators/convolver.py`), and the
kernel array itself is `dataset.psf.kernel` — an `Array2D`, so `dataset.psf.kernel.native`
is the 21x21 numpy view and `.shape_native` its shape. Writing `dataset.psf.native` from
memory raises `AttributeError`.

Data are in **MJy/sr**, NIRCam's native surface-brightness unit as `calwebb_image3` writes
it, not converted to counts. Nothing in PyAutoGalaxy cares which flux unit you use as long as
the data, noise map and any `intensity` prior agree, but a prior written for counts will be
wildly mis-scaled here.

## `info.json`

Two levels, with the same field names at each. The **per-band** `info.json` under
`wavebands/<BAND>/` describes that band. The **dataset-level** `info.json` at the dataset root
promotes one band's values to the top (`reference_band`, F277W for this dataset — highest
signal-to-noise and uniform coverage), adds a cross-band scatter, and nests all four bands
under `per_band`.

### Every field, and where it comes from

All of these are **measured from the delivered cutouts** by the reduction run's own
measurement script. That is the point of the schema: nothing in `info.json` is copied from a
catalogue and nothing is estimated by eye.

| Field | Level | Meaning |
|---|---|---|
| `pixel_scale` | both | Arcsec/pixel for this band — 0.03 short-wave, 0.06 long-wave |
| `centre_ra`, `centre_dec` | both | Flux-weighted centroid of the central source (degrees, J2000), through the cutout WCS |
| `axis_ratio` | both | `semiminor/semimajor` from second-order central moments, measured over the source's own segment so a neighbour cannot pull the shape |
| `position_angle` | both | Major-axis angle from the same moments, degrees counter-clockwise from +x, wrapped to [0, 180) |
| `effective_radius_arcsec_rough` | both | **Rough and biased low.** Half-light radius of an elliptical curve of growth truncated at 3". *Not* a Sersic `effective_radius` — a prior scale, not a measurement to reproduce |
| `moment_semimajor_sigma_arcsec` | per-band | Second-moment semimajor sigma from the same measurement |
| `peak_snr`, `peak_value` | per-band | Max of `data / noise_map`, and of the background-subtracted data, over the source segment |
| `background_sky_level` | per-band (and `background_sky_level_per_band` at dataset level) | Sigma-clipped median outside every detected segment — the **un-subtracted** sky, see below |
| `background_sky_rms` | per-band | Standard deviation of that same sky estimate |
| `segment_area_pixels` | per-band | Pixel count of the detection segment the measurements were made over |
| `curve_of_growth_max_arcsec` | per-band | The 3" truncation radius the rough half-light radius was measured inside |
| `data_name`, `reference_band` | dataset | The dataset's name, and which band's values are promoted to the top level |
| `band_to_band_scatter` | dataset | Standard deviation of `axis_ratio` and `effective_radius_arcsec_rough` across the four bands — **the honest error bar on those two numbers** |
| `measurement_note` | dataset | Prose restating the `_rough` caveat in the file itself |
| `per_band` | dataset | The four per-band blocks, keyed by band name |

### What is *not* in `info.json`, on purpose

- **No redshift.** COSJ100020+015344's z = 0.3422 is a published spectroscopic value, not
  something measured from these pixels, so it is cited in the dataset README instead of
  sitting in a file that otherwise contains only measurements. Read it from the README (or
  ask the user) and pass it to `ag.Galaxy(redshift=...)` explicitly.
- **No `mask_radius`.** There is no default mask hiding in the metadata. The mask extent is a
  science decision the assistant must settle with the user on every real-data fit — a mask
  that truncates the outer isophotes biases the effective radius and Sersic index directly.
  See the real-data gate in [`../../../AGENTS.md`](../../../AGENTS.md).
- **No magnitudes, stellar mass or physical size.** The surface-brightness-to-AB conversion,
  aperture correction and Galactic-extinction treatment needed to publish those honestly were
  not carried out. The dataset README cites COSMOS2020 photometry for anyone who needs them.
- **No catalogue identifiers.** They are in the README, with their VizieR table references.

## Two caveats that change how you fit this data

Both are properties of *this* dataset rather than of the layout, but an agent that loads the
data without reading them will produce a biased fit that looks fine.

**The sky is not subtracted.** `calwebb_image3`'s skymatch step matches the exposures'
backgrounds to each other but does not remove them, so `data.fits` carries the real JWST sky
as a positive pedestal — between 4.5x and 19x the median noise depending on the band. A
light-profile fit that ignores it absorbs the pedestal into the profile wings and returns an
inflated effective radius and Sersic index. Either subtract `background_sky_level` first, or
model it: `background_sky_level` is a constructor parameter of `ag.DatasetModel`
(`PyAutoArray:autoarray/dataset/dataset_model.py`), so freeing it means assigning a prior on an
`af.Model` of that class —

```python
import autofit as af

dataset_model = af.Model(ag.DatasetModel)
dataset_model.background_sky_level = af.UniformPrior(lower_limit=0.0, upper_limit=0.4)

model = af.Collection(galaxies=..., dataset_model=dataset_model)
```

Note that `af.Model(ag.DatasetModel)` starts with **no free parameters** — every constructor
argument holds its default until you assign a prior to it, so omitting the assignment above
silently fixes the sky at 0.0 rather than fitting it. `background_sky_level` is not a class
attribute either; `ag.DatasetModel.background_sky_level` raises `AttributeError`. See
[`../concepts/sky_background_and_operated_profiles.md`](../concepts/sky_background_and_operated_profiles.md).

**The PSF is a model PSF.** `psf.fits` is an STPSF model kernel composed per detector and
position, not an empirical star-stacked kernel — the pipeline's empirical PSF builder fails on
this field, because its star selection is dominated by compact galaxies rather than stars. The
shipped kernels are physically sane and correctly ordered with wavelength, but come out
consistently *sharper* than an empirical reference, most so in the most undersampled band
(F115W). Expect a fitted size to compensate slightly large, and **treat the PSF as the
dominant systematic in any fit to this dataset**. The measured comparison, and why the
empirical kernels were rejected, are in the dataset README; `reduction_manifest.json` records
both the shipped kernel and the rejected one per band.

## Datasets that are *not* bundled

Most `autogalaxy_workspace` examples do not ship their data — `dataset/.gitignore` there
ignores the whole tree (`*`, with only itself un-ignored), and each example **simulates its
dataset on first run** instead. The pattern, from
`autogalaxy_workspace:scripts/imaging/start_here.py`, is a guard plus a subprocess call to the
matching simulator:

```python
if ag.util.dataset.should_simulate(str(dataset_path)):
    subprocess.run(
        [sys.executable, "scripts/imaging/features/extra_galaxies/simulator.py"],
        check=True,
    )
```

`ag.util.dataset.should_simulate` (`PyAutoArray:autoarray/util/dataset_util.py`) is an
**existence check on the directory** — it returns `not Path(dataset_path).exists()`, with one
extra behaviour: when `PYAUTO_SMALL_DATASETS=1` is set it *deletes* an existing dataset first,
so the simulator regenerates it at the reduced resolution and the FITS shapes cannot disagree
with the capped mask and grid. Two consequences worth knowing:

- Because the check is existence-only, a **partially written or stale** dataset directory is
  treated as present and will not be regenerated. If a simulated dataset looks wrong, delete
  the directory rather than re-running the script.
- Never point this pattern at a bundled dataset. The guard would see
  `dataset/imaging/cosj100020+015344/` exists and skip — but under `PYAUTO_SMALL_DATASETS=1`
  it would **delete real observational data** that no simulator can regenerate.

For a user's own data, the job is to get it into the layout at the top of this page and then
load it exactly as above; the conversion procedure, including how to build a noise map and PSF
when the archive does not hand you one, belongs to
[`ag_prepare_imaging_data`](../../../skills/ag_prepare_imaging_data.md), grounded in
`autogalaxy_workspace:scripts/imaging/data_preparation/start_here.py`.

## See also

- [`api/datasets.md`](../api/datasets.md) — the `Imaging` and `Interferometer` objects, their
  settings, masking and over-sampling.
- [`concepts/grids_and_masks.md`](../concepts/grids_and_masks.md) — why the mask extent and
  the over-sampling scheme change your answer.
- [`concepts/multi_wavelength.md`](../concepts/multi_wavelength.md) — fitting the four bands
  jointly rather than one at a time.
- [`operations/sandbox.md`](./sandbox.md) — `PYAUTO_SMALL_DATASETS`, `PYAUTO_TEST_MODE` and
  the writable-cache environment variables.
- The bundled dataset's own `README.md` — the authority for its provenance, its measurements
  and its caveats.
