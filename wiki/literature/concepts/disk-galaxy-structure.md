---
title: Disc galaxy structure
type: concept
topics: [disk-galaxies, light-profiles, galaxy-components]
sources:
  - Freeman 1970 — the exponential disc
  - van der Kruit 1981 — the three-dimensional light distribution of disks
  - Pohlen 2006 — the structure of galactic disks
  - Erwin 2008 — outer disks of early-type galaxies
  - Comeron 2011 — thick disks in S4G
status: drafted
---

# Disc galaxy structure

## TL;DR

To first order a galactic disc is an exponential in radius and roughly isothermal
in height, and that two-parameter description (scale length `h`, scale height
`z_0`) survives remarkably well. To second order almost no disc is a pure
exponential: outer profiles break — downward (truncated, Type II), upward
(antitruncated, Type III) or not at all (Type I) — most discs have a thicker,
older second disc component, and bars, ovals, rings and spiral arms all carry
light that a bulge + disc fit will otherwise misassign. The break radius and the
thick-disc fraction are the structural quantities that connect disc photometry to
disc formation and dynamical heating.

## What it is

**Radial structure.** The exponential disc,
`I(R) = I_0 exp(-R/h)`, is the `n = 1` case of the Sersic profile. Freeman's
original claim of a near-universal central surface brightness `μ_0` is now known to
be partly a selection effect, but the exponential form itself is robust over the
inner few scale lengths. Beyond that, profiles are classified as:

- **Type I** — a single exponential all the way out.
- **Type II** — a downward break: the profile steepens beyond a break radius.
  Common in late-type spirals; associated in barred galaxies with the outer
  Lindblad resonance, and more generally with a star-formation threshold plus
  radial migration.
- **Type III** — an upward break (antitruncation): the profile flattens beyond the
  break. Common in early-type discs, and plausibly built by accreted material or by
  a superposed spheroid.

Break type is not a fixed property of Hubble type — barred and unbarred galaxies of
the same type show different break statistics, which is direct evidence that bars
reshape discs.

**Vertical structure.** Edge-on decomposition shows most discs are two discs: a
**thin** disc and a **thick** disc that is older, more metal-poor, kinematically
hotter, and (in nearby galaxies) carries a mass comparable to the thin disc in
low-mass systems. The classical vertical form is `sech^2(z / z_0)`, tending to an
exponential at large `|z|`; the fitted scale height depends on which of the two is
assumed, so the choice must be stated.

**Bars, ovals and rings.** A bar is a distinct photometric component with a flat
or shallow profile and a sharp end, and it is the single most common reason a
bulge-disc fit overestimates the bulge. Multi-component decomposition of nearby
discs routinely needs bulge + disc + bar and sometimes an oval or nuclear disc.

## Why it matters for PyAutoGalaxy

- The exponential is a light profile like any other; the practical question is how
  many components a fit deserves, and the answer is set by
  [[isophote-analysis|the isophote and ellipticity profile]] rather than by taste.
- Breaks mean the fitted `h` **depends on the radial range**. A truncated model —
  an exponential with a break — is a modelling option worth taking when the break
  is inside the mask, because otherwise the fit compromises between the two slopes
  and gets neither.
- Inclination and internal dust bias disc parameters; near-infrared bands mitigate
  both, which is one of the strongest arguments for multi-band fitting
  ([`wiki/core/concepts/multi_wavelength.md`](../../core/concepts/multi_wavelength.md)).
- The available profile forms, including the exponential and its variants, are
  listed in
  [`wiki/core/api/light_profile_catalog.md`](../../core/api/light_profile_catalog.md).

## Key results from the literature

- Freeman (1970) established the exponential disc and the effective-radius
  relations that follow from it ([[sources-disk-galaxy-structure]]).
- van der Kruit & Searle (1981) built the three-dimensional model for edge-on
  discs — exponential in radius, isothermal in height, with a sharp outer cut-off —
  and showed the scale height is essentially independent of radius
  ([[sources-disk-galaxy-structure]]).
- de Jong (1996) introduced two-dimensional bulge/disc fitting on face-on,
  disc-dominated galaxies, and quantified how much the derived disc parameters
  depend on the bulge model ([[sources-bulge-disk-decomposition]]).
- Pohlen & Trujillo (2006) established the Type I / II / III break classification
  from SDSS imaging of late-type spirals ([[sources-disk-galaxy-structure]]).
- Erwin, Beckman & Pohlen (2005) identified antitruncated discs in early-type
  barred galaxies; Erwin, Pohlen & Beckman (2008) and Gutiérrez and others (2011)
  extended the break census to barred and unbarred early-type discs respectively
  and quantified how the break statistics differ
  ([[sources-disk-galaxy-structure]]).
- Muñoz-Mateos and others (2013) used S4G mid-infrared imaging — where dust and
  young stars matter least — to show that bars change the incidence and radius of
  disc breaks ([[sources-disk-galaxy-structure]]).
- Yoachim & Dalcanton (2006) measured thin and thick disc structural parameters for
  a sample of edge-on discs; Comerón and others (2011) found from S4G that thick
  discs carry a large mass fraction in low-mass galaxies, and Comerón and others
  (2012) measured breaks separately in the thin and thick components
  ([[sources-disk-galaxy-structure]]).
- Sheth and others (2010) described the S4G survey that made this class of
  measurement systematic; Salo and others (2015) released its multi-component
  decompositions and Buta and others (2015) its classical morphological
  classifications ([[sources-disk-galaxy-structure]]).
- Gadotti (2009) showed directly that adding a bar component to an SDSS
  decomposition changes the recovered bulge, and therefore the classical versus
  pseudo-bulge assignment ([[bulge-disk-decomposition]]).
- Kormendy & Kennicutt (2004) reviewed the secular-evolution mechanisms — bars,
  spirals, resonances — that rearrange disc material and grow pseudo-bulges
  ([[sources-bulge-disk-decomposition]]).

## See also

- [[bulge-disk-decomposition]]
- [[sersic-profile]]
- [[morphology-classification]]
- [[sky-subtraction-and-photometry]]
- [[clumpy-and-irregular-structure]]
- [[sources-disk-galaxy-structure]]
