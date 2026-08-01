---
title: MaNGA
type: entity
topics: [survey, ifu, kinematics]
sources:
  - arXiv:1412.1482
  - arXiv:1607.08613
status: drafted
---

# MaNGA — Mapping Nearby Galaxies at Apache Point Observatory

## What it is

The integral-field spectroscopic survey carried out within SDSS-IV, mapping nearby galaxies
with fibre bundles feeding the BOSS spectrographs rather than observing them with a single
fibre ([[sources-ifu-spectroscopy#bundy-2015-manga]]). It is the largest survey of its kind:
where earlier IFS surveys measured hundreds of galaxies, MaNGA measured thousands, released
in full with SDSS DR17 ([[sources-collaborations-and-surveys#abdurrouf-2022-sdss-data-release-17]]).

## Key facts

- **Host survey:** SDSS-IV ([[sdss]]).
- **Instrument:** hexagonal fibre bundles ("IFUs") of several sizes, feeding the BOSS
  spectrographs — the bundle size sets the field of view for each galaxy
  ([[sources-ifu-spectroscopy#drory-2015-the-manga-fibre-bundle-system]]).
- **Design:** the observing strategy sets radial coverage in units of effective radius, so
  each galaxy is mapped to a comparable fraction of its own size rather than to a fixed
  angular radius ([[sources-ifu-spectroscopy#yan-2016-manga-survey-design-and-execution]]).
- **Data products:** reconstructed data cubes with their own effective PSF, produced by a
  dedicated reduction pipeline ([[sources-ifu-spectroscopy#law-2016-the-manga-data-reduction-pipeline]]).

## Why it matters for galaxy structure

Two reasons a photometric-fitting user should care:

1. **The cube has a PSF too, and it is much broader than the imaging.** Comparing a
   structural parameter from arcsecond-scale imaging against a MaNGA map means degrading one
   or accounting for the other. This is the single most common mistake in joint
   photometric-kinematic work ([[point-spread-function]]).
2. **It tests what a decomposition means.** A photometric bulge/disk split is a hypothesis
   about a galaxy's components; resolved kinematics is how you find out whether those
   components rotate differently ([[bulge-disk-decomposition]],
   [[early-type-galaxy-structure]]).

## Key papers

- **Bundy and others 2015** — the survey overview (arXiv:1412.1482, ApJ 798, 7).
- **Drory and others 2015** — the fibre-feed system (arXiv:1412.1535).
- **Law and others 2016** — the data reduction pipeline (arXiv:1607.08619).
- **Yan and others 2016** — survey design and execution (arXiv:1607.08613).

Full entries in [[sources-ifu-spectroscopy]].

## See also

- [[sami]], [[sdss]]
- [[bulge-disk-decomposition]], [[early-type-galaxy-structure]],
  [[point-spread-function]]
- [[sources-ifu-spectroscopy]]
