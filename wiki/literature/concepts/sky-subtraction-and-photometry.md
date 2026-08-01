---
title: Sky subtraction and outer-profile photometry
type: concept
topics: [sky-background, systematics, low-surface-brightness]
sources:
  - Blanton 2011 — improved SDSS background subtraction
  - Pohlen 2006 — the structure of galactic disks
  - Trujillo 2016 — beyond 31 mag/arcsec^2
  - Bernardi 2013 — the massive end and the light profile
  - Sandin 2014 — the influence of diffuse scattered light
status: drafted
---

# Sky subtraction and outer-profile photometry

## TL;DR

The sky level is the parameter that structural fitting cannot escape. Sersic index
and effective radius are both determined largely by the outermost measurable
isophotes, and out there the galaxy contributes a small fraction of the sky. A sky
error of a fraction of a per cent changes `n` at the tens-of-per-cent level and can
change total magnitudes by several tenths. Worse, the classical failure mode is
systematic rather than random: pipelines that estimate the background from an
annulus or a spline over the frame subtract part of the galaxy along with the sky,
biasing every large galaxy in a survey in the same direction. The choice between
fitting the sky simultaneously with the galaxy and fixing it from a prior
measurement is one of the most consequential decisions in a structural analysis.

## What it is

The components of a "sky" in a real image:

- **True sky** — zodiacal light, airglow, unresolved background sources, and (in
  space) thermal and stray-light contributions.
- **Instrumental pedestal and gradients** — flat-field residuals, amplifier
  offsets, persistence.
- **Scattered light from the PSF wings** of the galaxy itself and its neighbours,
  which is not sky at all but is indistinguishable from it without an extended PSF
  model ([[point-spread-function]]).
- **Genuine faint galaxy light** — outer envelopes, tidal features, thick discs.
  The whole difficulty is that this is the signal.

How it is handled, and the trade:

- **Pipeline sky, fixed.** Fast and reproducible, but inherits whatever the survey
  pipeline did. If the pipeline models the background on scales comparable to the
  galaxy, large galaxies are over-subtracted. This was a documented, correctable
  problem in early SDSS data releases.
- **Local sky measured in an annulus.** Only unbiased if the annulus is genuinely
  beyond the galaxy, which for a massive early-type in deep data may be many
  effective radii out.
- **Sky as a free model parameter.** Statistically the cleanest: the sky's
  covariance with `n` and `R_e` is then explicit in the posterior rather than
  hidden. The cost is that a flat sky component and a high-`n` outer wing are
  strongly degenerate, so the posterior is broad — which is honest.
- **Masking.** The mask sets the outermost radius that enters the likelihood. A
  mask that truncates the galaxy's outer isophotes biases `n` and `R_e` low; one
  that is too wide drags in neighbours and background structure. Neither default is
  safe on real data.

**Depth limits.** Deep imaging programmes reach ~30-31 mag/arcsec^2 in the optical.
At those depths flat-fielding, scattered light and the PSF wings — not photon noise
— set the limit, and each requires its own dedicated treatment.

## Why it matters for PyAutoGalaxy

- The sky can be included as a model component, and on real data usually should be.
  The available treatments, including operated/sky profiles, are in
  [`wiki/core/concepts/sky_background_and_operated_profiles.md`](../../core/concepts/sky_background_and_operated_profiles.md).
- The bundled dataset's `README.md` and
  [`wiki/core/operations/dataset.md`](../../core/operations/dataset.md) both flag a
  **residual sky pedestal**. Its benchmark prompt therefore fits the sky level
  freely rather than assuming zero — the correct response to a known pedestal.
- **Mask extent is a science decision.** This repo's `AGENTS.md` makes inspecting
  the data and choosing the mask radius a non-negotiable gate before any real-data
  fit, precisely because a silently-defaulted mask biases `R_e` and `n` directly.
  Masking machinery: [`wiki/core/concepts/grids_and_masks.md`](../../core/concepts/grids_and_masks.md).
- Neighbouring sources inside the mask must be masked or modelled:
  [`wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../../core/concepts/extra_galaxies_and_noise_scaling.md).

## Key results from the literature

- Blanton and others (2011) diagnosed and fixed the SDSS background-subtraction
  problem, showing that the standard pipeline sky removed part of the light of
  large galaxies and that correcting it changes their measured sizes and
  magnitudes ([[sources-light-profile-fitting]]).
- Pohlen & Trujillo (2006) and Erwin, Pohlen & Beckman (2008) set out the practical
  procedure for measuring outer disc profiles and breaks — how far out the sky must
  be measured, and how the break classification depends on it
  ([[disk-galaxy-structure]], [[sources-disk-galaxy-structure]]).
- Bernardi and others (2013) showed that the massive end of the luminosity and
  stellar mass functions depends strongly on which light profile is fitted and how
  much outer light it captures — a sky-and-profile systematic with cosmological
  consequences ([[stellar-mass-estimates]], [[sources-elliptical-galaxies]]).
- Sandin (2014, 2015) demonstrated that diffuse scattered light and the extended
  PSF wings dominate the faintest measured surface brightness, and that reported
  thick discs and stellar haloes must be corrected for them before being believed
  ([[point-spread-function]], [[sources-stellar-halos]]).
- Slater, Harding & Mihos (2009) characterised and removed internal reflections in
  deep imaging data, an instrumental effect that mimics faint extended emission
  ([[sources-stellar-halos]]).
- Mihos and others (2005) measured diffuse intracluster light in Virgo, an early
  demonstration of what dedicated low-surface-brightness technique can reach;
  Watkins, Mihos & Harding (2015) applied the same approach to the extended tidal
  debris of M51 ([[sources-stellar-halos]]).
- Trujillo & Fliri (2016) pushed to beyond 31 mag/arcsec^2 and enumerated what
  limits deep imaging at that level — flat fielding, scattered light and sky
  modelling, not exposure time ([[sources-stellar-halos]]).
- Duc and others (2015) used very deep optical imaging of ATLAS-3D early types to
  reveal shells, streams and outer discs that shallower photometry misses
  ([[early-type-galaxy-structure]]); Karabal and others (2017) developed the
  scattered-light deconvolution needed to trust such features
  ([[sources-stellar-halos]]).
- D'Souza, Vegetti & Kauffmann (2015) quantified how much the massive end of the
  stellar mass function shifts once the outer envelopes of massive galaxies are
  properly accounted for ([[sources-stellar-halos]]).

## See also

- [[point-spread-function]]
- [[sersic-profile]]
- [[disk-galaxy-structure]]
- [[early-type-galaxy-structure]]
- [[photometric-structural-fitting]]
- [[stellar-mass-estimates]]
- [[sources-stellar-halos]]
