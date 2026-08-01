---
title: High-redshift galaxy structure
type: concept
topics: [high-redshift, sizes, evolution]
sources:
  - Daddi 2005 — passively evolving early types at z ~ 2
  - Trujillo 2007 — strong size evolution since z ~ 2
  - van Dokkum 2008 — compactness of massive quiescent galaxies
  - van der Wel 2014 — the size-mass distribution since z = 3
  - Suess 2019 — colour gradients and half-mass radii
  - Ferreira 2023 — the JWST Hubble sequence
status: drafted
---

# High-redshift galaxy structure

## TL;DR

Massive quiescent galaxies at `z ~ 2` are several times smaller at fixed stellar
mass than their present-day counterparts. That result — established with HST
near-infrared imaging in the late 2000s and consolidated by CANDELS/3D-HST — is the
central fact of high-redshift structural work, and minor dry merging is the
favoured explanation. Two large caveats now shape the field. First, "size"
measured in the rest-frame optical is not the mass-weighted size: negative colour
gradients mean half-mass radii are systematically smaller and evolve more slowly
than half-light radii. Second, JWST has shown that the disc fraction at `z > 3` is
far higher than HST rest-frame-UV imaging implied, because at those redshifts HST
was measuring where young stars are, not where the mass is.

## What it is

The observational chain, and where each link can break:

1. **Measure `R_e` and `n`** from a PSF-convolved Sersic fit to
   near-infrared imaging. At `z = 2`, `R_e` for a compact quiescent galaxy is
   comparable to the HST WFC3 PSF FWHM, so the PSF model dominates the systematic
   error budget ([[point-spread-function]]).
2. **Convert to a rest-frame band.** Structural parameters are strongly
   wavelength-dependent; comparing `z = 2` observed-`H` to `z = 0` observed-`r`
   without matching rest frames manufactures evolution.
3. **Assign a stellar mass** from SED fitting, with all the systematics that
   carries ([[stellar-mass-estimates]]).
4. **Compare at fixed mass**, remembering that the galaxies compared at two epochs
   are not the same objects — progenitor bias is a real and quantified effect.

Key structural results as they stand:

- **Compact massive quiescent galaxies** exist in numbers at `1.4 < z < 2.5`, with
  `R_e` of order 1 kpc at `M_star ~ 10^11 M_sun`.
- **Size growth** is roughly `R_e ∝ (1+z)^-1.5` at fixed mass for quiescent
  galaxies and shallower for star-forming ones, with the quiescent relation also
  steepening in slope with time.
- **Inside-out growth**: the central mass density of massive galaxies changes far
  less than the total size, consistent with adding mass at large radii rather than
  puffing up the whole galaxy.
- **Half-mass versus half-light**: colour gradients bias light-weighted sizes high
  by tens of per cent at `z ~ 1-2.5`, absorbing a substantial part of the apparent
  evolution.
- **The JWST correction**: rest-frame optical imaging at `z = 3-9` finds disc-like
  and regular morphologies at rates several times higher than HST rest-frame-UV
  studies reported.

## Why it matters for PyAutoGalaxy

- This is the regime where **the PSF is the model**. Fitting a galaxy whose `R_e`
  is at or below the PSF FWHM without an accurate, well-sampled PSF gives a size
  that is a property of the PSF error, not of the galaxy.
- **Multi-band fitting is not optional** if the science question involves
  mass-weighted structure. Fitting all bands simultaneously with structural
  parameters tied across wavelength is the mechanism that turns colour gradients
  from a systematic into a measurement
  ([`wiki/core/concepts/multi_wavelength.md`](../../core/concepts/multi_wavelength.md)).
- Faint, small, high-redshift galaxies produce **shallow likelihood surfaces**.
  Report posteriors, not point estimates, and expect priors to matter — see
  [`wiki/core/concepts/samples_and_posteriors.md`](../../core/concepts/samples_and_posteriors.md).
- The bundled dataset ([[cosmos-web]]) is a four-band NIRCam cutout, which is a
  small-scale version of exactly this problem.

## Key results from the literature

- Daddi and others (2005) found passively evolving early-type galaxies at
  `1.4 < z < 2.5` in the Hubble Ultra Deep Field that were far smaller than local
  galaxies of the same mass ([[sources-high-redshift]]).
- Trujillo and others (2007) measured strong size evolution for the most massive
  galaxies since `z ~ 2`; Buitrago and others (2008) extended it to `1.7 < z < 3`
  with GOODS NICMOS imaging ([[sources-high-redshift]]).
- van Dokkum and others (2008) confirmed the compactness of massive quiescent
  galaxies at `z ~ 2.3` and argued against monolithic collapse; Cimatti and others
  (2008) reached the same conclusion from GMASS spectroscopy plus imaging
  ([[sources-high-redshift]]).
- Bezanson and others (2009) showed the central densities of `z ~ 2` compact
  galaxies match the cores of local massive ellipticals — the inside-out growth
  argument; Naab, Johansson & Ostriker (2009) and Oser and others (2010) supplied
  the minor-merger and two-phase theoretical account
  ([[early-type-galaxy-structure]], [[sources-high-redshift]]).
- van Dokkum and others (2010) traced the growth of massive galaxies at constant
  number density; Newman and others (2012) tested whether the observed minor-merger
  rate is sufficient to account for the size growth and found it marginal
  ([[sources-high-redshift]]).
- Barro and others (2013) identified compact star-forming galaxies as the plausible
  immediate progenitors of the compact quiescent population
  ([[sources-high-redshift]]).
- Szomoru, Franx & van Dokkum (2012) added the residual-corrected profile technique
  to test whether Sersic fits miss extended light at `z ~ 2` — they largely do not —
  and Szomoru and others (2013) measured surface density profiles and half-mass
  radii from `z = 0` to `z = 2.5` ([[sources-high-redshift]]).
- van der Wel and others (2014) produced the reference size-mass distribution from
  `z = 3` to the present using CANDELS + 3D-HST; Mowla and others (2019) extended
  it to rarer massive galaxies with wide-field COSMOS-DASH imaging, and
  Nedkova and others (2021) to low stellar masses
  ([[sources-high-redshift]], [[galaxy-scaling-relations]]).
- Wuyts and others (2011) mapped structure across the star-formation-rate-mass
  plane, showing that quenching and central concentration track each other
  ([[sources-high-redshift]]).
- Suess and others (2019) measured half-mass radii for ~7000 galaxies at
  `1.0 ≤ z ≤ 2.5` and found most of the apparent mass-size evolution is due to
  colour gradients; the companion letter showed half-mass radii evolve only slowly
  ([[sources-high-redshift]], [[stellar-mass-estimates]]).
- Kriek and others (2009) framed the `z > 2` structural landscape as a contrast
  between large star-forming and compact quiescent galaxies — the "Hubble sequence
  beyond `z = 2`" ([[sources-high-redshift]]).
- Ferreira and others (2022) reported the first JWST rest-frame optical structural
  measurements at `z > 3`, finding far more discs than expected; Ferreira and
  others (2023) extended this to `1.5 < z < 6.5`; Kartaltepe and others (2023)
  published the CEERS morphology census at `z = 3-9`; Ward and others (2024)
  measured the star-forming size-mass relation to `z = 5.5`
  ([[sources-high-redshift]], [[jwst]]).

## See also

- [[galaxy-scaling-relations]]
- [[early-type-galaxy-structure]]
- [[clumpy-and-irregular-structure]]
- [[stellar-mass-estimates]]
- [[point-spread-function]]
- [[morphology-classification]]
- [[sources-high-redshift]]
