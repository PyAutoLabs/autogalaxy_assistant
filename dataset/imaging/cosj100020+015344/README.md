# COSJ100020+015344 — a four-band JWST/NIRCam galaxy-structure dataset

A real multi-band JWST cutout of a **bright, resolved, non-lens** galaxy, reduced from
MAST level-2 exposures for use as the `autogalaxy_assistant` demonstration dataset: Sersic
and bulge+disk decomposition, multi-band modelling, and isophote / ellipse fitting.

```
README.md                                              this file
info.json                                              dataset-level summary (F277W values)
reduction_manifest.json                                per-band reduction + PSF provenance
wavebands/F115W/{data,noise_map,psf}.fits, info.json   419 x 419 @ 0.03"/pix  (12.57")
wavebands/F150W/{data,noise_map,psf}.fits, info.json   419 x 419 @ 0.03"/pix  (12.57")
wavebands/F277W/{data,noise_map,psf}.fits, info.json   209 x 209 @ 0.06"/pix  (12.54")
wavebands/F444W/{data,noise_map,psf}.fits, info.json   209 x 209 @ 0.06"/pix  (12.54")
```

Every `psf.fits` is a 21x21 unit-sum kernel. Data units are **MJy/sr** (native NIRCam
surface brightness — `calwebb_image3`'s own convention, not converted). Every cutout keeps
its WCS in the FITS header.

That tree is the whole dataset. This README describes the reduction that produced it, so it
also refers to intermediate products that are deliberately **not** shipped: the 61x61 PSF
kernels, the rejected tier-1 empirical PSFs (§5b), the pipeline's own `reduction.json` /
`reduction_summary.json` / `psf_tier2b.json` records, the preview and selection figures, and
the working scripts (§9). Those are retained with the reduction run, not in this tree, and
nothing below depends on reading them: every number quoted in this README is either in the
prose itself, in `info.json`, or in `reduction_manifest.json`.

**Read §5 before fitting.** Three properties of this data will silently bias a model that
ignores them: the sky is not subtracted, the PSF is a model PSF, and the short-wave depth
is not uniform across the cutout.

## 1. What the target is

| | |
|---|---|
| Name used here | **COSJ100020+015344** (the COWLS `COSJ<HHMMSS><sign><DDMMSS>` convention) |
| Position | RA = 150.08531°, Dec = +1.89582° (J2000) = 10:00:20.47 +01:53:44.9 |
| COSMOS2020 | Classic ID **499609** (Weaver et al. 2022, ApJS 258, 11; VizieR `J/ApJS/258/11/classic`) |
| zCOSMOS | ID **812167** |
| NED | `WISEA J100020.46+015344.7` |
| Redshift | **z = 0.3422**, spectroscopic — zCOSMOS-Bright DR3, confidence class 4.5, spectrum `zCOSMOS_BRIGHT_DR3_000812167_ZCMRa53_M2_Q4_17_1.fits` (Lilly et al. 2007, ApJS 172, 70; VizieR `J/ApJS/172/70/zcosmos3`). Independently z = 0.3426 in the zCOSMOS 20k group catalogue (Knobel et al. 2012, ApJ 753, 121; VizieR `J/ApJ/753/121`) |
| Catalogue photometry | Ks(AUTO) = 18.82, ACS F814W(AUTO) = 20.21, I = 20.21 |
| Catalogue stellar mass | log M\*/M☉ = 10.54 (COSMOS2020 LePhare median) / 10.64 (Knobel et al. 2012) |
| Morphology | smooth, centrally concentrated, mildly elongated — an early-type / bulge-dominated galaxy. COSMOS2020 records ACS axis ratio 0.92 and `ACSmuClass = 1` (galaxy) |
| Environment | member of zCOSMOS 20k group 379 at z ≈ 0.342. The next-brightest member (COSMOS2020 504922) is 16.5" away — outside the delivered cutout |
| Isolation | nearest catalogued neighbour 5.7". Measured on the delivered F277W cutout, the galaxy holds 989 of the 1043 detected flux units in the frame; the brightest neighbour is **8.0" north-west** (5% of the galaxy's flux) and a faint second sits **2.6"** away (0.3%) |

**It is not a lens.** Cross-matched against the full COWLS catalogue
(<https://github.com/Jammy2211/COWLS_COSMOS_Web_Lens_Survey>, `catalogue.csv`, 440 entries
— the candidate list from COWLS I's visual inspection of the COSMOS-Web galaxy sample,
Nightingale et al. 2025, MNRAS 543, 203): the nearest COWLS entry is **55.5" away** —
`COSJ100024+015334`, the COSMOS-Web Ring itself, which was excluded from selection by
construction. NED lists no lens classification here.

The cross-match was checked in both directions: it recovers the ring at 0.1" from its
published position, so a null result at this target is a real absence, not a coordinate
mismatch.

## 2. How the target was selected

The exposures already cached for the COSMOS-Web Ring reduction were reused (§3), so the
search was confined to the sky those exposures cover.

1. **Footprint** — the sky area of the cached program-1727 `_cal` exposures was read from
   their SCI-extension WCS: RA 150.039–150.139, Dec +1.802–+1.920, in two NIRCam module
   pointings. `footprints.py`
2. **Scout mosaic** — one throwaway F277W mosaic was drizzled from the 8 module-B
   exposures around the ring by calling `autoreduce`'s combine stage directly (381 s).
   `scout_drizzle.py`
3. **Catalogue** — 914 COSMOS2020 Classic sources within 80" of the ring were pulled from
   VizieR. Cuts: `lptype == 0` (LePhare galaxy classification), `ACSmuClass == 1`
   (ACS star/galaxy class = galaxy), Ks(AUTO) < 20.5, nearest catalogued neighbour > 2".
   `candidates.py`
4. **Coverage** — for each surviving candidate, the number of exposures covering a 15×15
   grid across a 13" box (the delivered cutout extent) was counted per band, using the
   pipeline's own containment test. This rejects positions that look covered at the centre
   but fall into a NIRCam short-wave detector gap at the edges. `cand_coverage_box.py`
5. **Visual inspection** — 13" F277W stamps of every candidate were rendered and inspected.
   `inspect_scout.py`
6. **Lens exclusion** — the COWLS cross-match above.

Coverage — exposures covering the 13" box, as min–median–max, with the COSMOS-Web Ring
position as a reference point:

| | F115W | F150W | F277W | F444W |
|---|---|---|---|---|
| COSMOS-Web Ring (reference) | 2–4–6 | 2–4–6 | 1–4–4 | 1–4–4 |
| **COSJ100020+015344 (chosen)** | 2–4–4 | 2–4–4 | **4–4–4** | **4–4–4** |

The chosen position is the brightest candidate whose *entire* long-wavelength cutout is
covered by all four exposures — better long-wavelength coverage than the ring dataset
itself. Brighter candidates were rejected on evidence: COSMOS2020 513945 (Ks = 17.4) falls
outside the cached footprint entirely, and 504922 (Ks = 18.1) sits in a 2-exposure region
with a weight edge crossing its cutout.

Selection evidence was rendered as figures during the reduction run and is retained there:
the scout mosaic with the chosen galaxy marked, the excluded ring marked and every candidate
considered, plus a 13" zoom on the choice, and the 13" F277W stamp grid that the visual
inspection in step 5 was made on. Neither figure is part of the shipped dataset.

## 3. Exposures and provenance of the inputs

All science comes from **JWST GO program 1727, COSMOS-Web**, NIRCam imaging, level-2
`_cal` products from MAST. No new download was made: the exposures were already in
`PyAutoReduce/scripts/cache/cosmos_web_ring_<band>/` (fetched 2026-07-08/09 for the ring
integration test) and were **symlinked** into a scratch `ExposureCache` under this target's
names, with a manifest recording that origin (`seed_cache.py`). The CRDS reference store
was symlinked, never copied. Nothing under `PyAutoReduce/` was modified.

Exposures entering each mosaic, after the pipeline's usability screen and
detector-footprint filter:

| Band | Exposures combined | Detectors | Skipped off-target | Runtime |
|---|---|---|---|---|
| F115W | 12 | `nrcb1`–`nrcb4`, visit `jw01727138001`, `02101` dithers 1–4 | 52 | 522 s |
| F150W | 12 | `nrcb1`–`nrcb4`, visit `jw01727138001`, `04101` dithers 1–4 | 52 | 483 s |
| F277W | 4 | `nrcblong`, visit `jw01727138001`, `02101` dithers 1–4 | 12 | 197 s |
| F444W | 4 | `nrcblong`, visit `jw01727138001`, `04101` dithers 1–4 | 12 | 194 s |

Total exposure time on the target: **1030.7 s** in every band. The exact exposure filenames
that entered each band ship here, in `reduction_manifest.json` under `<BAND>.exposures`. The
pipeline's fuller per-band records (`reduction.json`, `reduction_summary.json`) are retained
with the reduction run.

The short-wave counts are higher because a NIRCam short-wave module is four detectors and
each is its own `_cal` file: 4 dithers × the ~3 chips that come within the footprint
filter's margin of the target = 12 files. That is **not** extra depth — the number of
exposures actually covering any given point in the cutout is 2–4 (§2's coverage table), and
the step between those two values is exactly the non-uniformity of §5c.

## 4. The pipeline

`PyAutoReduce` (`autoreduce`) at commit **d7bd916a86c37b236bf3470b9bd5e43fcab28a62**
(`main`, 2026-07-29), driven by `reduce_cosj100020.py`, which mirrors the repository's own
`scripts/reduce_cosmos_web_ring.py`: same `TargetSpec` shape, same COSMOS-Web conventions
(short-wave 419×419 @ 0.03"/pix, long-wave 209×209 @ 0.06"/pix, `pixfrac = 1.0`,
`kernel = square`, program 1727 only). **No `autoreduce` source file was modified.**

Stages: `acquire` (cache + CRDS + usability screen + footprint filter) → `align`
(a-priori WCS accepted, no TweakReg refinement pass) → `drizzle` (`calwebb_image3`:
tweakreg / skymatch / outlier_detection / resample, with `rotation = 0` and
`weight_type = ivm`) → `noise` → `psf` → `package`.

Software: Python 3.12.10, `jwst` **2.0.1**, `astropy` 8.0.1, `numpy` 2.2.6,
`photutils` 2.3.0, `drizzlepac` 3.11.0, `astroquery` 0.4.11, `stpsf` 2.2.0,
`poppy` 1.1.2. CRDS context **`jwst_1535.pmap`** (JWST CRDS server).
No bad pixels required masking in any band (`n_masked_bad_pixels = 0` throughout).

### Noise maps

Read, not constructed: the `ERR` array `calwebb_image3`'s resample propagates
(Poisson + read noise + flat), multiplied by the Casertano correlated-noise factor **R**
that corrects for drizzle's pixel-to-pixel correlation. The pipeline's own blank-sky
consistency check (`sky_over_err_floor`) compares the empirical sky RMS against the `ERR`
floor — 1.0 means perfect agreement:

| Band | R | `sky_over_err_floor` | median noise (MJy/sr) |
|---|---|---|---|
| F115W | 1.5254 | 1.095 | 0.0580 |
| F150W | 1.5254 | 1.017 | 0.0454 |
| F277W | 1.5384 | 0.961 | 0.0108 |
| F444W | 1.5384 | 0.880 | 0.0135 |

The noise maps agree with the measured sky scatter to within 2–12%. F444W's 0.88 means the
noise map is ~12% *conservative* against the sky scatter there.

## 5. Three things to know before you fit this data

### 5a. The sky is **not** subtracted

`calwebb_image3`'s skymatch step *matches* the exposures' backgrounds to each other but
does not subtract them, and `autoreduce` keeps the pipeline default. The delivered
`data.fits` therefore carries the real JWST sky as a positive pedestal, large compared
with the noise:

| Band | background (MJy/sr) | median noise | pedestal / noise |
|---|---|---|---|
| F115W | 0.2624 | 0.0580 | 4.5 |
| F150W | 0.2551 | 0.0454 | 5.6 |
| F277W | 0.1246 | 0.0108 | 11.5 |
| F444W | 0.2614 | 0.0135 | 19.4 |

**A light-profile fit that ignores this absorbs the pedestal into the Sersic wings** and
returns an inflated effective radius and Sersic index. Model it:

```python
dataset_model = af.Model(ag.DatasetModel)
dataset_model.background_sky_level = af.UniformPrior(lower_limit=0.0, upper_limit=0.4)
model = af.Collection(galaxies=..., dataset_model=dataset_model)
```

or subtract the measured value (`info.json` → `background_sky_level`) first. The smoke fit
in §7 does the former and recovers the measured value.

### 5b. The PSF is a **model** PSF, because the pipeline's empirical PSF is broken here

This is the one place where the shipped products are not what `autoreduce`'s default path
produced. The reason is a real, measured defect that should be reported upstream.

`autoreduce`'s tier-1 mosaic PSF builds an empirical ePSF from `DAOStarFinder` detections
on the drizzled mosaic. **In a deep JWST extragalactic field that selection is dominated
by compact galaxies, not stars.** Measured on this target's F277W scout mosaic
(`psf_diag.py`):

* 327 candidates pass the star cuts and **only 24% are point-like**. The median half-light
  radius of the selected "stars" is **3.2 native pixels** against **1.4** for a true F277W
  point source; the 75th percentile is 5 px and the 95th is 13 px.
* The stacked kernel is therefore far too broad, and rings negative. Flux in the central
  pixel, and the kernel half-light radius, against the COWLS COSMOS-Web reference kernels
  for the same bands (`psf_table.py`):

  | Band | tier-1 central pixel | tier-1 r½ | COWLS reference central pixel | COWLS r½ |
  |---|---|---|---|---|
  | F115W | 1.7% | 0.222" | 16.2% | 0.042" |
  | F150W | 4.5% | 0.153" | 14.3% | 0.042" |
  | F277W | 0.6% | 0.537" | 14.1% | 0.085" |
  | F444W | 1.2% | 0.379" | 9.0% | 0.085" |

  (F277W's r½ measured on the tier-1 61×61 kernel rather than the 21×21 box is 1.47",
  ~17× the correct value; its minimum is −0.6 × its peak. Neither tier-1 kernel ships.)
* The failure reproduces on both the scout mosaic and the delivered reduction, in all four
  bands — it is systematic, not one unlucky star list. It equally affects
  `PyAutoReduce`'s own reference driver `scripts/reduce_cosmos_web_ring.py`, which runs the
  identical code path on the identical field; that driver's acceptance check
  (`autoreduce.validation.registered_ratios(new_data, new_noise, ref_data, ref_noise)`)
  takes no PSF argument, which is why the defect has not been caught there.
* The other back-end the mosaic PSF stage offers, `TargetSpec(psf_backend="starred")`
  (STARRED tier-1b), consumes the **same** star list, and **it fails the same way** — this
  was measured, not assumed. Run on the identical 327-star list and scout mosaic, STARRED
  returns a kernel with r½ = **1.11"** against tier-1's 1.445" and the correct ≈ 0.085":
  13× too broad, in 2436 s (41 min) for one band. Its own diagnostics report
  `sampling_fwhm_px = 7.76` (0.47") and `undersampled: False` — it does not detect that
  anything is wrong. **The defect is the star selection, not the back-end**, so the upstream
  fix belongs in `autoreduce.psf.stars.find_stars` (a concentration cut — e.g. reject
  candidates whose own half-light radius exceeds the point-source value by more than a small
  margin), not in either PSF builder.

Those kernels are **not shipped here.** The pipeline's tier-1 output was preserved with the
reduction run so the defect stays inspectable, and `reduction_manifest.json` records it per
band under `<BAND>.psf_pipeline_tier1_rejected` — the star count, the measured kernel width,
and why it was rejected — so the rejection is auditable from what ships.

The shipped `psf.fits` (and the 61×61 kernel that stays with the reduction run) are
instead the **tier-2b STPSF model PSF** that
`PyAutoReduce`'s own JWST design doc names as the JWST fallback tier
(`docs/design/jwst.md`: *"STPSF is the tier-2b fallback (per-detector, per-position)"*).
They are built by `psf_tier2b.py` entirely out of `autoreduce`'s own components — no new
algorithm is introduced:

1. `autoreduce.psf.stpsf_model.model_frame_psf` — an STPSF model at each contributing
   exposure's detector (`NRCBLONG`, `NRCB1`–`NRCB4`) and at the target's position on that
   detector, from the `DET_DIST` extension (detector-sampled, geometric distortion
   included);
2. `autoreduce.psf.frame_combine._drop_convolve` — convolution with the drizzle drop (the
   `pixfrac = 1.0` box in native pixels);
3. `autoreduce.psf.frame_combine._resample_to_mosaic` — resampling onto the mosaic grid
   through the local frame→mosaic WCS Jacobian at the target;
4. exposure-time-weighted average over the contributing exposures, then unit-normalised to
   21×21 and 61×61. Only the 21×21 kernel ships, as `psf.fits`; the 61×61 version is
   retained with the reduction run.

Steps 2–4 are exactly what `TargetSpec(psf_from_frames=True)` does; the only substitution
is the STPSF kernel for the galaxy-contaminated ePSF, which the mosaic PSF stage offers no
way to select. Per-band details — STPSF version, the contributing detectors and their
positions on each, the exposure weights, and the measured kernel FWHM and central-pixel
fraction — ship in `reduction_manifest.json` under `<BAND>.psf`.

**How good the shipped kernels are**, against the COWLS empirical reference:

| Band | shipped central pixel | shipped r½ | COWLS central pixel | COWLS r½ |
|---|---|---|---|---|
| F115W | 24.7% | 0.030" | 16.2% | 0.042" |
| F150W | 18.3% | 0.037" | 14.3% | 0.042" |
| F277W | 18.4% | 0.074" | 14.1% | 0.085" |
| F444W | 10.2% | 0.085" | 9.0% | 0.085" |

Physically sane, no negative ringing, and the right ordering with wavelength — but
**consistently sharper than the empirical reference**: the central-pixel fraction is ~50%
high in the most undersampled band (F115W) and converges to agreement in the best-sampled
one (F444W). (Compare the central-pixel fractions, not r½: for kernels this compact the r½
estimator quantises onto the pixel grid — 0.030" and 0.042" at 0.03"/pix are adjacent grid
radii, not a resolved difference.) That is the expected
signature of a model PSF: STPSF does not carry the as-flown wavefront drift at the epoch of
these exposures, and the drop convolution plus local-affine resample capture drizzle's
broadening only to first order. **Treat the PSF as the dominant systematic in any fit to
this dataset**, and expect a fitted size to come out slightly *large* to compensate for a
slightly-too-sharp kernel — most so at F115W.

### 5c. Coverage is uniform at long wavelength, stepped at short wavelength

The pipeline records the drizzle weight uniformity over the delivered cutout as
`wht_rms_over_median`, against its own limit of 0.2:

| Band | cutout weight uniformity | verdict |
|---|---|---|
| F115W | 0.286 | **exceeds the 0.2 limit** |
| F150W | 0.287 | **exceeds the 0.2 limit** |
| F277W | 0.085 | within limit |
| F444W | 0.079 | within limit |

The short-wave 419×419 cutouts straddle a NIRCam short-wave detector-gap boundary: part of
the box has 4 exposures and part has 2, a √2 step in depth. The noise map tracks it
correctly (it is the propagated `ERR`), so this is a depth gradient, not an error.

It is *not* the reason the short-wave peak S/N is lower (48 and 72, against F277W's 181):
that is mostly the 4× smaller pixel area at 0.03"/pix collecting 4× fewer photons per
pixel, plus the galaxy being intrinsically fainter blueward at z = 0.34. The depth step is a
gradient across the frame, not an overall sensitivity loss.

A modelling mask of radius ≲ 4" keeps the fit inside the uniform region and excludes the
8.0" neighbour of §1. It does **not** exclude the faint source 2.6" from the centre — that
one has to be masked explicitly or modelled (it is visible in the smoke fit's residual
map, §7).

## 6. `info.json` — where every number comes from

`info.json` at the dataset root, and one per band under `wavebands/<BAND>/`. All of them
were written by the reduction run's `measure.py` (§9), which is the only place these numbers
are produced.
**Nothing is copied from a catalogue and nothing is estimated by eye.**

| Key | Origin |
|---|---|
| `pixel_scale` | The reduction's `package.pixel_scale` — the `TargetSpec.final_scale` the instrument adapter recommends (0.03 short-wave, 0.06 long-wave) |
| `centre_ra`, `centre_dec` | Flux-weighted centroid of the segmentation-detected central source on the background-subtracted `data.fits`, through the cutout WCS |
| `axis_ratio` | `semiminor_sigma / semimajor_sigma` from the source's second-order central moments (`photutils.morphology.data_properties`), measured over that source's own segment only so a neighbour cannot pull the shape |
| `position_angle` | Major-axis angle from the same moments, counter-clockwise from +x, wrapped to [0, 180) |
| `effective_radius_arcsec_rough` | **Rough, and biased low.** Radius of the elliptical aperture (at the measured axis ratio and angle) enclosing half the flux inside a 3" truncation. A truncated curve-of-growth half-light radius, **not** a Sersic `effective_radius`: the aperture is truncated and nothing extrapolates the wings. Published as a scale for priors |
| `moment_semimajor_sigma_arcsec` | Second-moment semimajor sigma, same measurement |
| `background_sky_level`, `background_sky_rms` | Sigma-clipped median and standard deviation of `data.fits` outside every detected segment — the un-subtracted sky of §5a |
| `peak_snr`, `peak_value` | Max of `data / noise_map`, and of the background-subtracted data, over the source segment |
| `segment_area_pixels`, `curve_of_growth_max_arcsec` | Bookkeeping for the two measurements above |
| `band_to_band_scatter` | Standard deviation of `axis_ratio` and `effective_radius_arcsec_rough` across the four bands. **This is the honest error bar on those numbers** |
| redshift | **Not measured, and not in `info.json` as a measurement.** z = 0.3422 is a published catalogue value, cited in §1 |

Measured values, all four bands:

| | F115W | F150W | F277W | F444W |
|---|---|---|---|---|
| centre RA | 150.085317 | 150.085321 | 150.085325 | 150.085320 |
| centre Dec | +1.895805 | +1.895825 | +1.895828 | +1.895825 |
| axis ratio | 0.886 | 0.849 | 0.834 | 0.872 |
| position angle | 98.8° | 93.1° | 95.1° | 89.8° |
| rough effective radius | 0.297" | 0.288" | 0.370" | 0.373" |
| peak S/N | 47.8 | 71.7 | 180.0 | 124.2 |

The dataset-level `info.json` promotes the **F277W** values (highest S/N, uniform
coverage). The four bands agree on the centre to **0.08"**, on the axis ratio to 0.05, and
on the position angle to 9°; the rough size steps from ≈ 0.29" short-ward to ≈ 0.37"
long-ward, which is a genuine wavelength dependence mixed with the PSF difference, not a
measurement error. The measured F277W centre is **0.02" from the COSMOS2020 catalogue
position** — an independent check that the reduction centred where it claims to.

No magnitudes are published here. The surface-brightness-to-AB conversion, aperture
correction and Galactic-extinction treatment needed to do that honestly were not carried
out; use the COSMOS2020 photometry cited in §1 if you need magnitudes.

## 7. Validation

* **Loads** — every band loads through `ag.Imaging.from_fits` at its own pixel scale with a
  unit-sum PSF, at the shapes listed at the top of this file. The per-band dataset subplots
  this was checked on are retained with the reduction run. (`validate.py`)
* **Smoke fit** — a single `ag.lp.Sersic` plus a free
  `ag.DatasetModel.background_sky_level`, maximum likelihood via `af.LBFGS`, on the F277W
  data inside a 3" circular mask (7825 pixels). It converges:

  | | fitted | start point | independent value |
  |---|---|---|---|
  | log likelihood | **+23988** | −31824 | |
  | reduced χ² | **0.797** | | |
  | normalised residual RMS | **0.893** | | |
  | centre offset from cutout centre | (−0.054", −0.032") | (0, 0) | ≤ 1 pixel |
  | axis ratio | 0.916 | 0.834 | 0.83–0.89 across bands (§6) |
  | position angle | 89.5° | 95.1° | 89.8–98.8° across bands (§6) |
  | effective radius | 0.351" | 0.370" | 0.370" rough measurement (§6) |
  | Sersic index | 4.697 | 4.0 | — |
  | background sky level | 0.12278 | 0.12458 | 0.12458 measured (§5a) |

  The free sky recovers the independently measured pedestal to **1.4%**, the reduced χ² of
  0.80 says the noise map is if anything slightly conservative (consistent with §4's
  `sky_over_err_floor`), and n ≈ 4.7 is a de Vaucouleurs-like early type, which is what
  the image looks like. The fit's result files and residual figure are retained with the
  reduction run; the table above is the record of it that ships. (`smoke_fit.py`)

  The residual map is flat except for a few-pixel dipole at the very centre (the usual
  PSF/centring residual on a peak-S/N-181 core) and the faint neighbour 2.6" from the
  centre, which sits inside the 3" mask and which a single-Sersic model has nothing to
  represent.

  Two implementation notes, because both changed the answer:
  * The optimiser is started from `measure.py`'s moment measurements, with the start
    `intensity` obtained by rendering a unit-intensity trial profile through the dataset's
    own PSF and grid and matching its total flux to the data. Started from a random prior
    draw instead, L-BFGS-B walks into the prior corner (`effective_radius` pinned at its
    lower limit, reduced χ² = 140) and reports a "converged" fit that is nonsense.
  * With JAX enabled, L-BFGS-B terminates at iteration **zero** and returns its start
    point unchanged (reduced χ² = 15.1) while still logging "Search complete". The fit
    above needs `PYAUTO_DISABLE_JAX=1`. That is worth chasing separately — it is not a
    property of this dataset.

  This is a **smoke test, not a science fit**: no sampler, no error bars, no
  PSF-systematic budget, and §5b applies in full. It exists to show that the data, the
  noise map and the PSF are mutually consistent and that a light profile converges on
  them.

## 8. What is deliberately *not* claimed

* No magnitudes, stellar mass, or physical size in kpc measured from this data (§6).
* No Sersic `effective_radius`, index or ellipticity presented as a measurement — the
  smoke fit's values are a smoke fit's values, and the published `effective_radius` is
  labelled `_rough` because it is.
* No redshift beyond the published catalogue value, which is cited rather than derived.
* No claim that the PSF is empirical (§5b), that the sky is subtracted (§5a), or that the
  short-wave depth is uniform (§5c).

## 9. Reproducing this

The scripts that produced this dataset are **working scripts, not part of the dataset**, and
are retained with the reduction run rather than shipped here. They expect to run from the
working directory they were written in (they resolve the exposure cache and the scout mosaic
relative to their own location) and they import `autoreduce` by `sys.path`, exactly as
`PyAutoReduce`'s own `scripts/` do. They are listed so the provenance chain above is legible
end to end, in the order they must run:

```
seed_cache.py            symlink the cached program-1727 exposures under this target's names
footprints.py            sky area of the cached exposures, per band
scout_drizzle.py         one throwaway F277W mosaic for the target search
candidates.py            COSMOS2020 shortlist
cand_coverage.py         per-band coverage at a list of candidate positions
cand_coverage_all.py     per-band coverage of every catalogue source
cand_coverage_box.py     per-band coverage across the 13" cutout box
inspect_scout.py         candidate stamps + field figure
psf_diag.py              what the tier-1 star selection actually selected (§5b)
psf_backend_test.py      tier-1 vs STARRED on the same star list (§5b)
reduce_cosj100020.py     THE REDUCTION — --band F115W|F150W|F277W|F444W|all
assemble.py              copy the shipping products into this directory
psf_tier2b.py            the tier-2b STPSF PSFs, replacing tier-1 (§5b)
psf_table.py             the PSF comparison tables in §5b
measure.py               info.json
selection_figure.py      preview/target_selection.png
validate.py              load every band + preview subplots
smoke_fit.py             the F277W smoke fit
```

`smoke_fit.py` needs `PYAUTO_DISABLE_JAX=1`: with JAX enabled, L-BFGS-B terminates at
iteration zero and returns its own start point unchanged.
