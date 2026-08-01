---
title: Sources — isophotes and multipoles
type: sources
topics: [isophotes, multipoles, morphology]
status: drafted
---

# Sources: isophotes and multipoles

Fitting ellipses to a galaxy's isophotes, and measuring how far those isophotes depart from
ellipses. This is the non-parametric counterpart to profile fitting, and the origin of the
boxy/discy distinction that still organises how early-type galaxies are classified.

## Carter 1978 — the structure of elliptical isophotes

**Canonical BibTeX key:** `Carter1978`
**Reference:** Carter 1978, MNRAS 182, 797 — "The structure of the isophotes of elliptical
galaxies"
**Concepts:** [[isophote-analysis]], [[early-type-galaxy-structure]]

**Supports:**
- Elliptical-galaxy isophotes are not exactly elliptical, and the departures are measurable.

**Use when:**
- Citing the early recognition that isophotal shape carries structural information.

**Do not use for:**
- The Fourier formalism now used to quantify it.

## Lauer 1985 — high-resolution surface photometry

**Canonical BibTeX key:** `Lauer1985`
**Reference:** Lauer 1985, ApJS 57, 473 — "High-resolution surface photometry of elliptical
galaxies" (ADS: 1985ApJS...57..473L)
**Concepts:** [[isophote-analysis]], [[early-type-galaxy-structure]]

**Supports:**
- High-resolution isophotal photometry of elliptical galaxies, including isophotal
  ellipticity and position-angle profiles.

**Use when:**
- Citing pre-HST isophotal measurement practice.

**Do not use for:**
- Nuclear structure, which needed HST resolution.

## Jedrzejewski 1987 — the isophote-fitting algorithm

**Canonical BibTeX key:** `Jedrzejewski1987`
**Reference:** Jedrzejewski 1987, MNRAS 226, 747 — "CCD surface photometry of elliptical
galaxies – I. Observations, reduction and results"
**Concepts:** [[isophote-analysis]]

**Supports:**
- The iterative ellipse-fitting method — fit an ellipse at each semi-major axis, expand the
  residual intensity along the ellipse in a Fourier series, and use the harmonic amplitudes
  to update the ellipse — that essentially all isophote analysis still uses.
- The interpretation of the fourth harmonic (a4/b4) as the boxy/discy indicator.

**Use when:**
- Citing the isophote-fitting algorithm itself, including PyAutoGalaxy's ellipse fitting.

**Do not use for:**
- Higher-order multipole formalisms beyond the fourth harmonic.

## Bender 1987 — morphological analysis of early-type isophotes

**Canonical BibTeX key:** `Bender1987`
**Reference:** Bender & Moellenhoff 1987, A&A 177, 71 — "Morphological analysis of massive
early-type galaxies in the Virgo Cluster" (ADS: 1987A&A...177...71B)
**Concepts:** [[isophote-analysis]], [[early-type-galaxy-structure]]

**Supports:**
- Systematic Fourier analysis of early-type galaxy isophotes and the separation of the
  population by isophotal shape.

**Use when:**
- Citing the origin of boxy/discy classification as a population property.

**Do not use for:**
- Quantitative modern samples.
- Note: the ADS abstract page for this paper does not render for automated fetching; the
  metadata here was corroborated from multiple independent citing sources rather than from
  the primary record.

## Bender 1988 — isophote shapes of elliptical galaxies

**Canonical BibTeX key:** `Bender1988`
**Reference:** Bender, Doebereiner & Moellenhoff 1988, A&AS 74, 385 — "Isophote shapes of
elliptical galaxies. I. The data" (ADS: 1988A&AS...74..385B)
**Concepts:** [[isophote-analysis]], [[early-type-galaxy-structure]]

**Supports:**
- A tabulated dataset of isophote shape parameters for a sample of elliptical galaxies.

**Use when:**
- Citing the reference dataset behind the boxy/discy distinction.

**Do not use for:**
- Kinematic correlations, which are argued elsewhere.

## Kormendy 1996 — a proposed revision of the Hubble sequence

**Canonical BibTeX key:** `Kormendy1996`
**Reference:** Kormendy & Bender 1996, ApJL 464, L119, doi:10.1086/310095 — "A Proposed
Revision of the Hubble Sequence for Elliptical Galaxies"
**Concepts:** [[isophote-analysis]], [[morphology-classification]],
[[early-type-galaxy-structure]]

**Supports:**
- Ordering elliptical galaxies by isophotal shape (boxy versus discy) rather than by
  apparent flattening produces a physically meaningful sequence.

**Use when:**
- Explaining why isophotal shape is treated as a classification axis and not just a residual.

**Do not use for:**
- Spiral or lenticular classification.

## Hao 2006 — isophotal shapes in SDSS

**Canonical BibTeX key:** `Hao2006`
**Reference:** arXiv:astro-ph/0605319, MNRAS 370, 1339 — "Isophotal shapes of
elliptical/lenticular galaxies from the Sloan Digital Sky Survey"
**Concepts:** [[isophote-analysis]], [[sdss]]

**Supports:**
- Isophotal shape measured for a large SDSS sample rather than a few tens of nearby galaxies,
  giving population-level distributions of the boxy/discy parameter.

**Use when:**
- Comparing a measured a4/b4 against a large local sample.

**Do not use for:**
- Faint outer isophotes — SDSS depth and seeing limit the radial range.
- Note: an erratum was published (MNRAS 373, 1264).

## Ferrarese 2006 — ACS Virgo Cluster Survey isophotal analysis

**Canonical BibTeX key:** `Ferrarese2006`
**Reference:** arXiv:astro-ph/0602297, ApJS 164, 334 — "The ACS Virgo Cluster Survey. VI.
Isophotal Analysis and the Structure of Early-Type Galaxies"
**Concepts:** [[isophote-analysis]], [[early-type-galaxy-structure]], [[hst]]

**Supports:**
- Homogeneous HST isophotal analysis of a large cluster sample, including surface-brightness
  profiles, ellipticity, position angle and isophotal shape as functions of radius.

**Use when:**
- You need a well-characterised HST-resolution reference for isophotal parameter profiles.

**Do not use for:**
- Field galaxies.

## Ciambur 2015 — Isofit and Cmodel

**Canonical BibTeX key:** `Ciambur2015`
**Reference:** arXiv:1507.02691, ApJ 810, 120 — "Beyond Ellipse(s): Accurately Modelling the
Isophotal Structure of Galaxies with Isofit and Cmodel"
**Concepts:** [[isophote-analysis]]

**Supports:**
- Standard ellipse fitting parameterises the isophote by eccentric anomaly in a way that
  breaks down for strongly non-elliptical isophotes; a corrected sampling recovers them.
- Higher-order harmonics beyond the fourth can be measured reliably with the corrected
  method.

**Use when:**
- Fitting isophotes of a strongly boxy, discy or edge-on system, where the classical method
  degrades.

**Do not use for:**
- The classical algorithm's provenance — that is Jedrzejewski.

## Krajnovic 2006 — kinemetry

**Canonical BibTeX key:** `Krajnovic2006`
**Reference:** arXiv:astro-ph/0512200, MNRAS 366, 787 — "Kinemetry: a generalisation of
photometry to the higher moments of the line-of-sight velocity distribution"
**Concepts:** [[isophote-analysis]]

**Supports:**
- The harmonic-expansion machinery of isophote fitting generalises to velocity and velocity
  dispersion maps.

**Use when:**
- Connecting photometric isophote analysis to integral-field kinematic analysis
  ([[sources-ifu-spectroscopy]]).

**Do not use for:**
- Photometric measurements alone.

## Peng 2010 — multipoles inside a parametric fit

**Canonical BibTeX key:** `Peng2010`
**Reference:** arXiv:0912.0731, AJ 139, 2097 — "Detailed Decomposition of Galaxy Images. II.
Beyond Axisymmetric Models"
**Concepts:** [[isophote-analysis]], [[photometric-structural-fitting]]

**Supports:**
- Fourier (multipole) perturbations can be built into a parametric model directly, rather
  than measured afterwards from isophotes.

**Use when:**
- Choosing between a parametric multipole term and a non-parametric isophote analysis.

**Do not use for:**
- Model-independent isophote measurement.

## See also

- [[isophote-analysis]] — the concept page.
- [[sources-elliptical-galaxies]] — what isophotal shape correlates with.
- [[sources-light-profile-fitting]] — the parametric alternative.
