---
title: SDSS (Sloan Digital Sky Survey)
type: entity
topics: [survey, catalogue, structural-parameters]
sources:
  - arXiv:astro-ph/0006396
  - arXiv:1107.1518
  - arXiv:1406.4179
status: drafted
---

# SDSS — the Sloan Digital Sky Survey

## What it is

The wide-field imaging and spectroscopic survey that turned galaxy structure into a
statistical science ([[sources-collaborations-and-surveys#york-2000-the-sloan-digital-sky-survey]]). For structural
work, SDSS matters less as a telescope than as a *catalogue*: hundreds of thousands to
millions of galaxies with imaging in five bands, spectroscopic redshifts for the main galaxy
sample, and — crucially — several independent, publicly released catalogues of parametric
light-profile fits to the same galaxies.

## Key facts

- **Imaging:** *ugriz*, ~1.3″ typical seeing, over roughly a third of the sky.
- **Spectroscopy:** redshifts and velocity dispersions for the main galaxy sample, which is
  what makes SDSS structural parameters interpretable as physical sizes and masses.
- **Structural catalogues** (the reason this page exists):
  - **Simard and others 2011** — bulge+disk decompositions and updated photometry for 1.12
    million galaxies, fitted with three model families
    ([[sources-bulge-disk-decomposition#simard-2011-112-million-sdss-decompositions]]).
  - **Meert and others 2015** — 2D photometric decompositions of the DR7 spectroscopic main
    galaxy sample, with an explicit preferred-model and systematics analysis
    ([[sources-bulge-disk-decomposition#meert-2015-sdss-dr7-2d-decompositions-and-systematics]]).
  - **Bernardi and others 2013 / 2017 and Fischer and others 2017** — what the choice of
    fitted profile and the treatment of background sky do to the massive end of the
    luminosity and stellar-mass functions
    ([[sources-light-profile-fitting#bernardi-2013-the-fitted-profile-changes-the-mass-function]],
    [[sources-light-profile-fitting#fischer-2017-sky-background-and-model-fitting-effects]]).
- **Later phases:** SDSS-IV added the [[manga]] integral-field survey to the same
  infrastructure.

## Why it matters for galaxy structure

Three things a PyAutoGalaxy user should take from SDSS:

1. **It is the comparison sample.** Almost any local structural measurement — a Sersic index,
   a bulge-to-total ratio, a size — is quoted against an SDSS distribution.
2. **It is the cautionary tale.** Because several groups fitted the *same* galaxies
   independently, SDSS is where the field learned how much a structural parameter depends on
   the fitting choices: the model family, the fitting region, and above all the sky
   background ([[sky-subtraction-and-photometry]]). Disagreements at the massive end are
   large enough to change the inferred stellar-mass function.
3. **It is low resolution.** SDSS seeing is comparable to the effective radii of many
   galaxies in the sample, so the PSF is not a correction — it is a central part of the
   model ([[point-spread-function]]).

## Key papers

- **York and others 2000** — the SDSS technical summary (arXiv:astro-ph/0006396).
- **Simard and others 2011** — the 1.12-million-galaxy bulge+disk catalogue
  (arXiv:1107.1518).
- **Meert and others 2015** — SDSS-DR7 2D decompositions and their systematics
  (arXiv:1406.4179).
- **Bernardi and others 2013** — the dependence of the massive end on the fitted profile
  (arXiv:1304.7778).

## See also

- [[manga]], [[cosmos-survey]]
- [[bulge-disk-decomposition]], [[sky-subtraction-and-photometry]],
  [[photometric-structural-fitting]]
- [[sources-bulge-disk-decomposition]], [[sources-light-profile-fitting]],
  [[sources-collaborations-and-surveys]]
