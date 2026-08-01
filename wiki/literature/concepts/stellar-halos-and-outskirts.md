---
title: Stellar haloes and galaxy outskirts
type: concept
topics: [low-surface-brightness, stellar-halos, assembly]
sources:
  - Duc 2015 — deep imaging of ATLAS-3D early types
  - Trujillo 2016 — beyond 31 mag/arcsec^2
  - DSouza 2015 — the massive end of the stellar mass function
  - Sandin 2014 — the influence of diffuse scattered light
  - Mihos 2005 — diffuse light in the Virgo Cluster
status: drafted
---

# Stellar haloes and galaxy outskirts

## TL;DR

Beyond a few effective radii, galaxies do not simply end. They have accreted
envelopes, shells, streams, thick discs and — in clusters — light that belongs to
no single galaxy at all. This material carries only a few per cent of the total
luminosity but a disproportionate share of the information about how the galaxy was
assembled, because it is the part with the longest dynamical time and therefore the
longest memory. It is also the hardest photometry in the field: at
~28-31 mag/arcsec^2 the measurement is limited by flat fielding, scattered light and
the PSF wings rather than by photon noise, and the same instrumental effects that
mimic a stellar halo also destroy a real one if over-subtracted.

## What it is

**What lives out there:**

- **Accreted stellar haloes** — the debris of disrupted satellites, predicted by
  two-phase assembly models to dominate the mass beyond a few `R_e` in massive
  early-type galaxies.
- **Tidal features** — shells, fans, streams and plumes, each with a rough
  characteristic timescale, so their incidence constrains the recent merger rate.
- **Thick discs** — older, hotter, more metal-poor disc components, visible mainly
  in edge-on systems ([[disk-galaxy-structure]]).
- **Antitruncated (Type III) outer profiles**, where the light flattens rather than
  falls — plausibly the transition from disc to halo.
- **Intracluster light** — in groups and clusters, a diffuse component that is not
  bound to any one galaxy and has no unambiguous boundary with the central
  galaxy's own halo.

**Why it is hard:**

- The signal is a fraction of a per cent of the sky, so a sky error at that level
  erases it. Sky determination and outer-profile measurement are the same problem
  ([[sky-subtraction-and-photometry]]).
- Extended PSF wings scatter light from the bright inner galaxy outwards. Without
  an extended (many-arcsecond) PSF model, part of any measured "halo" is the
  galaxy's own core, redistributed ([[point-spread-function]]).
- Internal reflections, ghosts and flat-field residuals in wide-field imagers
  produce structures at exactly the surface brightness of interest.
- Neighbouring galaxies, foreground stars and their haloes must be masked or
  modelled at radii where they overlap the target.

**Why it matters scientifically.** The fraction of a galaxy's stellar mass in its
outskirts is not a rounding error at the massive end: how much of the envelope the
photometry captures changes the measured shape of the high-mass end of the stellar
mass function, and therefore the constraint any given galaxy formation model has to
match.

## Why it matters for PyAutoGalaxy

- **Mask extent is the whole ballgame.** A mask chosen to capture the outer
  isophotes admits neighbours and sky structure; one chosen to exclude them
  truncates the profile and biases `n` and `R_e`. This repo's real-data gate makes
  that choice explicit rather than a default
  ([`wiki/core/concepts/grids_and_masks.md`](../../core/concepts/grids_and_masks.md)).
- Contaminating sources at large radius should be masked or modelled, not ignored:
  [`wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../../core/concepts/extra_galaxies_and_noise_scaling.md).
  The bundled dataset has a real neighbour 2.6 arcsec from the centre — inside any
  mask wide enough to reach the outskirts — which is exactly this problem in
  miniature ([`wiki/core/operations/dataset.md`](../../core/operations/dataset.md)).
- Fitting the sky as a free parameter puts the sky-versus-outer-profile degeneracy
  in the posterior where it can be seen
  ([`wiki/core/concepts/sky_background_and_operated_profiles.md`](../../core/concepts/sky_background_and_operated_profiles.md)).
- Do not present a fitted outer envelope as a detection of a stellar halo unless
  the PSF model extends far enough to rule out scattered light. This is the single
  most common overclaim in low-surface-brightness structural work.

## Key results from the literature

- Mihos and others (2005) measured diffuse intracluster light in the Virgo cluster
  with dedicated low-surface-brightness technique, showing what is reachable when
  flat fielding and scattered light are treated as first-class problems
  ([[sources-stellar-halos]]).
- Slater, Harding & Mihos (2009) characterised internal reflections in deep imaging
  and showed how to remove them — an instrumental artefact that closely mimics
  faint extended emission ([[sources-stellar-halos]]).
- Sandin (2014, 2015) demonstrated that the extended PSF and diffuse scattered
  light dominate the outermost measured surface brightness, and that a number of
  published faint haloes and thick discs are consistent with instrumental
  scattering ([[point-spread-function]], [[sources-stellar-halos]]).
- Karabal and others (2017) developed a deconvolution technique to correct deep
  galaxy images for instrumental scattered light, making the corrected outer
  profiles usable ([[sources-stellar-halos]]).
- Duc and others (2015) imaged ATLAS-3D early-type galaxies to very low surface
  brightness and found shells, streams and outer discs in a large fraction, tying
  outer structure directly to accretion history
  ([[early-type-galaxy-structure]], [[sources-stellar-halos]]).
- Trujillo & Fliri (2016) reached beyond 31 mag/arcsec^2 and enumerated the
  limiting factors at that depth, none of which is exposure time
  ([[sources-stellar-halos]]).
- Watkins, Mihos & Harding (2015) mapped the extended tidal debris of M51 in deep
  imaging, an example of the structures that only appear below the usual
  surface-brightness floor ([[sources-stellar-halos]]).
- D'Souza, Vegetti & Kauffmann (2015) showed the massive end of the stellar mass
  function depends strongly on how much outer light the photometry captures;
  Bernardi and others (2013) reached the same conclusion from the light-profile
  side ([[stellar-mass-estimates]], [[sky-subtraction-and-photometry]]).
- Naab, Johansson & Ostriker (2009) and Oser and others (2010) supply the
  theoretical expectation that the outskirts are accreted while the core is
  in-situ — the reason the outskirts are where the assembly history is written
  ([[early-type-galaxy-structure]], [[sources-elliptical-galaxies]]).
- Kormendy and others (2009) pushed single-galaxy Sersic fitting over an
  exceptional surface-brightness range, which is what makes the departures from a
  single profile in the outskirts measurable at all
  ([[sources-elliptical-galaxies]]).
- Erwin, Pohlen & Beckman (2008) and Gutiérrez and others (2011) classified
  antitruncated outer disc profiles, the disc-galaxy counterpart of an outer
  envelope; Comerón and others (2011) measured thick disc masses from S4G
  ([[disk-galaxy-structure]], [[sources-disk-galaxy-structure]]).
- Blanton and others (2011) fixed the SDSS background subtraction that had been
  removing exactly this light from large galaxies — the cautionary example of what
  a pipeline sky can do ([[sky-subtraction-and-photometry]]).

## See also

- [[sky-subtraction-and-photometry]]
- [[point-spread-function]]
- [[early-type-galaxy-structure]]
- [[disk-galaxy-structure]]
- [[stellar-mass-estimates]]
- [[sources-stellar-halos]]
