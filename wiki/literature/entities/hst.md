---
title: HST
type: entity
topics: [instrument, space-telescope]
sources:
  - arXiv:astro-ph/0507614
  - arXiv:1105.3754
status: drafted
---

# HST — the Hubble Space Telescope

## What it is

The 2.4 m optical/near-infrared space telescope whose stable, diffraction-limited PSF made
resolved galaxy structure measurable beyond the local universe. Two instruments dominate
galaxy-structure work:

- **ACS** (Advanced Camera for Surveys) — the optical workhorse, and the camera behind the
  COSMOS F814W mosaic and the deep fields
  ([[sources-collaborations-and-surveys#sirianni-2005-hst-acs-photometric-calibration]]).
- **WFC3**, particularly its IR channel — the instrument that made rest-frame optical
  imaging at z ~ 2 possible, and therefore made [[candels]] possible
  ([[sources-collaborations-and-surveys#kimble-2008-hst-wide-field-camera-3]]).

## Key facts

- **Resolution:** roughly 0.05–0.1″ depending on camera and wavelength — a factor of ten
  better than typical ground-based seeing, which is why space-based data changed structural
  measurement rather than merely improving it.
- **A stable, well-characterised PSF.** Not a Gaussian, but stable enough to be modelled and
  reused, which is what makes deconvolution-free forward modelling reliable
  ([[point-spread-function]]).
- **Legacy fields:** GOODS, the Ultra Deep Field, COSMOS and CANDELS are all HST programmes,
  and between them define the imaging most high-redshift structural catalogues rest on.

## Why it matters for galaxy structure

Essentially every claim in this wiki about resolved structure beyond the nearby universe —
size evolution, bulge/disk decomposition at z ~ 2, nuclear cores and cusps in early-type
galaxies — was first established with HST. It is also the *comparison baseline* for JWST:
when a JWST size differs from an HST size, the question is whether the difference is
wavelength, resolution or method ([[jwst]], [[high-z-galaxy-structure]]).

For nearby galaxies, HST's angular resolution is what resolves the central regions where the
core/cusp distinction lives ([[early-type-galaxy-structure]]).

## Key papers

- **Sirianni and others 2005** — ACS photometric performance and calibration
  (arXiv:astro-ph/0507614, PASP 117, 1049).
- **Kimble and others 2008** — the WFC3 instrument (Proc. SPIE 7010, 70101E).
- **Koekemoer and others 2011** — CANDELS HST observations and mosaics (arXiv:1105.3754), the
  worked example of how HST imaging becomes a science-ready mosaic.

Full entries in [[sources-collaborations-and-surveys]].

## See also

- [[jwst]], [[candels]], [[cosmos-survey]], [[euclid]]
- [[point-spread-function]], [[early-type-galaxy-structure]]
- [[sources-collaborations-and-surveys]]
