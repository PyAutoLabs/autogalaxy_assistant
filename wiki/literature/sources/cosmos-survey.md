---
title: Sources — the COSMOS field
type: sources
topics: [surveys, deep-fields, photometric-redshifts]
status: drafted
---

# Sources: the COSMOS field

The survey, catalogue and spectroscopy papers that define the COSMOS field — the field the
dataset bundled with this assistant was cut from. Structural work in COSMOS almost always
cites one of these for the redshift, the stellar mass, or the imaging itself.

## Scoville 2007 — COSMOS overview

**Canonical BibTeX key:** `Scoville2007`
**Reference:** arXiv:astro-ph/0612305 — "The Cosmic Evolution Survey (COSMOS) — Overview"
**Concepts:** [[cosmos-survey]], [[morphology-classification]]

**Supports:**
- COSMOS is a ~2 deg² equatorial survey designed to measure galaxy evolution as a joint
  function of redshift and environment.
- The field was built around a large contiguous HST/ACS mosaic with deep multi-wavelength
  follow-up.

**Use when:**
- Citing the existence, design or scientific motivation of the COSMOS field.

**Do not use for:**
- Specific catalogue contents, depths or photometric-redshift accuracies — cite the
  catalogue paper instead.

## Scoville 2007 — large structures in COSMOS

**Canonical BibTeX key:** `Scoville2007a`
**Reference:** arXiv:astro-ph/0612384 — "Large Structures and Galaxy Evolution in COSMOS at
z < 1.1"
**Concepts:** [[cosmos-survey]], [[galaxy-scaling-relations]]

**Supports:**
- COSMOS contains large-scale structures over z < 1.1 that can be identified and used as an
  environment measure.

**Use when:**
- Motivating an environment-dependent analysis within the COSMOS field.

**Do not use for:**
- Group membership of an individual galaxy — use the spectroscopic group catalogue
  ([[sources-cosmos-survey#knobel-2012-zcosmos-20k-group-catalogue|Knobel 2012]]).

## Koekemoer 2007 — COSMOS HST/ACS imaging

**Canonical BibTeX key:** `Koekemoer2007`
**Reference:** arXiv:astro-ph/0703095, ApJS 172, 196 — "The COSMOS Survey: Hubble Space
Telescope / Advanced Camera for Surveys (HST/ACS) Observations and Data Processing"
**Concepts:** [[cosmos-survey]], [[hst]], [[sky-subtraction-and-photometry]]

**Supports:**
- The COSMOS ACS F814W mosaic and the drizzling/calibration procedure behind it.
- The imaging products that COSMOS morphological and structural measurements are made on.

**Use when:**
- Citing the provenance or processing of COSMOS HST imaging used for a structural fit.

**Do not use for:**
- JWST-era COSMOS imaging — that is [[cosmos-web|COSMOS-Web]].

## Capak 2007 — first-release COSMOS photometry

**Canonical BibTeX key:** `Capak2007`
**Reference:** arXiv:0704.2430, ApJS 172, 99 — "The First Release COSMOS Optical and Near-IR
Data and Catalog"
**Concepts:** [[cosmos-survey]], [[stellar-mass-estimates]]

**Supports:**
- The first public multi-band optical/near-IR photometric catalogue of the COSMOS field.

**Use when:**
- Citing the origin of COSMOS ground-based photometry.

**Do not use for:**
- Current photometric redshifts or stellar masses — superseded by COSMOS2015/COSMOS2020.

## Sanders 2007 — S-COSMOS

**Canonical BibTeX key:** `Sanders2007`
**Reference:** arXiv:astro-ph/0701318, ApJS 172, 86 — "S-COSMOS: The Spitzer Legacy Survey of
the HST-ACS 2 sq. deg. COSMOS Field I"
**Concepts:** [[cosmos-survey]], [[stellar-mass-estimates]]

**Supports:**
- Spitzer IRAC/MIPS coverage of the full COSMOS field, providing the mid-infrared photometry
  that anchors stellar-mass estimates.

**Use when:**
- A stellar mass in COSMOS depends on infrared photometry.

**Do not use for:**
- Resolved structural measurement — Spitzer's resolution is far too coarse.

## Ilbert 2009 — COSMOS photometric redshifts

**Canonical BibTeX key:** `Ilbert2009`
**Reference:** arXiv:0809.2101, ApJ 690, 1236 — "COSMOS Photometric Redshifts with 30-bands
for 2-deg2"
**Concepts:** [[cosmos-survey]], [[stellar-mass-estimates]]

**Supports:**
- 30-band photometric redshifts across the COSMOS field, calibrated against the
  spectroscopic samples.

**Use when:**
- Justifying the use of photometric redshifts to convert angular sizes to physical sizes in
  COSMOS.

**Do not use for:**
- A specific galaxy's redshift when a spectroscopic value exists ([[zcosmos]]).

## Laigle 2016 — COSMOS2015

**Canonical BibTeX key:** `Laigle2016`
**Reference:** arXiv:1604.02350 — "The COSMOS2015 Catalog: Exploring the 1<z<6 Universe with
half a million galaxies"
**Concepts:** [[cosmos-survey]], [[stellar-mass-estimates]]

**Supports:**
- A half-million-object multi-band photometric catalogue with redshifts and stellar masses
  over 1 < z < 6.

**Use when:**
- Citing COSMOS stellar masses or photometric redshifts for work predating COSMOS2020.

**Do not use for:**
- The deepest current COSMOS photometry — that is COSMOS2020.

## Weaver 2022 — COSMOS2020

**Canonical BibTeX key:** `Weaver2022`
**Reference:** arXiv:2110.13923 — "COSMOS2020: A panchromatic view of the Universe to z~10
from two complementary catalogs"
**Concepts:** [[cosmos-survey]], [[stellar-mass-estimates]]

**Supports:**
- The current reference photometric catalogue of the COSMOS field, released as two
  independently constructed catalogues.
- Photometric redshifts and physical parameters (including stellar masses) to z ~ 10.

**Use when:**
- Quoting a COSMOS galaxy's catalogue identifier, photometric redshift or stellar mass
  today — including for the galaxy in the bundled dataset.

**Do not use for:**
- Morphological or structural parameters; COSMOS2020 is a photometric catalogue.

## Lilly 2007 — zCOSMOS

**Canonical BibTeX key:** `Lilly2007`
**Reference:** arXiv:astro-ph/0612291 — "zCOSMOS: A Large VLT/VIMOS redshift survey covering
0 < z < 3 in the COSMOS field"
**Concepts:** [[zcosmos]], [[cosmos-survey]]

**Supports:**
- The design of the zCOSMOS bright and deep spectroscopic tiers and their selection.

**Use when:**
- Citing the survey a COSMOS spectroscopic redshift came from.

**Do not use for:**
- The redshift catalogue itself — cite the data-release paper.

## Lilly 2009 — zCOSMOS 10k-bright sample

**Canonical BibTeX key:** `Lilly2009`
**Reference:** Lilly and others 2009, "The zCOSMOS 10k-Bright Spectroscopic Sample",
ApJS 184, 218 (ADS: 2009ApJS..184..218L)
**Concepts:** [[zcosmos]]

**Supports:**
- ~10,000 spectroscopic redshifts with I_AB < 22.5, average accuracy ~110 km/s.
- Per-object confidence classes calibrated empirically against repeat observations.

**Use when:**
- Quoting a zCOSMOS-bright redshift *and* its reliability class.

**Do not use for:**
- The completed 20k sample or its group catalogue.

## Knobel 2012 — zCOSMOS 20k group catalogue

**Canonical BibTeX key:** `Knobel2012`
**Reference:** arXiv:1207.0002, ApJ 753, 121 — "The zCOSMOS 20k Group Catalog"
**Concepts:** [[zcosmos]], [[cosmos-survey]]

**Supports:**
- An optical group catalogue over 0.1 < z < 1 built from ~16,500 high-quality zCOSMOS-bright
  redshifts, containing ~1500 groups.

**Use when:**
- Assigning a COSMOS galaxy to a group, or motivating an environmental comparison.

**Do not use for:**
- Halo masses inferred by other methods ([[sources-halo-galaxy-connection]]).

## Casey 2023 — COSMOS-Web

**Canonical BibTeX key:** `Casey2023`
**Reference:** arXiv:2211.07865, ApJ 954, 31, doi:10.3847/1538-4357/acc2bc — "COSMOS-Web: An
Overview of the JWST Cosmic Origins Survey"
**Concepts:** [[cosmos-web]], [[jwst]], [[high-z-galaxy-structure]]

**Supports:**
- COSMOS-Web is a 255-hour JWST Cycle 1 treasury programme imaging 0.54 deg² with NIRCam in
  F115W, F150W, F277W and F444W, with 0.19 deg² of parallel MIRI F770W.
- Reported 5σ point-source depths of ~27.5–28.2 mag (NIRCam) and ~25.3–26.0 mag (MIRI).
- The survey's goals are reionization-era galaxy identification, massive-galaxy assembly
  over z ~ 2–6, and the dependence of galaxy evolution on environment.

**Use when:**
- Citing the survey the bundled dataset's exposures come from, or the provenance of any
  COSMOS-Web NIRCam imaging.

**Do not use for:**
- Structural or morphological measurements of individual COSMOS-Web galaxies — the overview
  paper defines the survey, not a morphological catalogue.

## See also

- [[cosmos-survey]], [[cosmos-web]], [[zcosmos]] — the entity pages.
- [[sources-collaborations-and-surveys]] — the wider survey landscape.
- [[sources-high-redshift]] — what the field is used to measure.
