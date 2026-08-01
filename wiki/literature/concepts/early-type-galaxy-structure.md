---
title: Early-type galaxy structure
type: concept
topics: [elliptical-galaxies, galaxy-components, assembly]
sources:
  - Caon 1993 — the shape of early-type light profiles
  - Kormendy 2009 — structure and formation of ellipticals and spheroidals
  - Huang 2013 — three-component structure of nearby ellipticals
  - Emsellem 2011 — fast and slow rotators
  - Oser 2010 — the two phases of galaxy formation
status: drafted
---

# Early-type galaxy structure

## TL;DR

Early-type galaxies are not the structureless `R^(1/4)` spheroids of the classical
picture. Their Sersic indices vary systematically with luminosity; their central
regions split into "cored" and "cusped" families at a luminosity threshold; deep
imaging shows most of them have multiple photometric components and extended,
accreted outer envelopes; and integral-field kinematics divides them into fast and
slow rotators along a line that visual morphology does not draw. The modern
synthesis is two-phase assembly: an early, dissipative, in-situ phase that builds a
compact core, followed by prolonged accretion of stripped satellites that builds the
outskirts. Almost every structural observable listed here is a consequence of that
split.

## What it is

The structural facts a fit has to accommodate:

- **The index is not 4.** Sersic `n` correlates with luminosity and with `R_e`,
  running from `n ≈ 2` for faint ellipticals to `n ≳ 6-10` for brightest cluster
  galaxies. Forcing `n = 4` biases both the size and the total luminosity, and the
  bias is luminosity-dependent, so it distorts scaling relations rather than just
  offsetting them.
- **Cores and cusps.** Above roughly `M_V ≈ -21.5`, the inner profile flattens
  relative to the inward extrapolation of the outer Sersic — a "core", widely
  attributed to scouring by a binary supermassive black hole. Below it, the profile
  continues to rise ("cuspy" or "extra light"), attributed to a dissipative central
  starburst. The **core-Sersic** model parameterises this with an inner power law
  and a break radius.
- **Multiple components.** Careful decomposition of nearby ellipticals typically
  needs three photometric components — a compact inner one, an intermediate one and
  an extended envelope — rather than one Sersic. Whether these correspond to
  distinct formation events or are simply what a flexible model does to a smoothly
  varying profile is still argued.
- **Outer envelopes.** Deep imaging reveals shells, streams, tidal features and
  low-surface-brightness haloes around a large fraction of nearby early types. This
  material carries a small fraction of the light but a large fraction of the
  information about the accretion history — and it is exactly the light that
  aggressive sky subtraction removes ([[sky-subtraction-and-photometry]]).
- **Fast and slow rotators.** Integral-field kinematics splits early types by the
  specific angular momentum proxy `λ_R` within `R_e`. Slow rotators are rarer, more
  massive, rounder, boxier and often have kinematically distinct cores; fast
  rotators are essentially disc galaxies with a large bulge fraction. The split
  correlates with isophote shape ([[isophote-analysis]]) but not with the `E`/`S0`
  label.

## Why it matters for PyAutoGalaxy

- The bundled dataset is a real early-type galaxy at `z = 0.3422`, imaged in four
  JWST/NIRCam bands, so these are not abstractions: they are the decisions a user
  faces on the first fit ([`wiki/core/operations/dataset.md`](../../core/operations/dataset.md)).
- Expect the single-Sersic fit to leave structured residuals in a massive early
  type. The productive responses are, in order: check the mask extent, check the
  sky, then add flexibility — either components ([[bulge-disk-decomposition]]) or a
  basis ([[multi-gaussian-expansion]]).
- **Never let the mask truncate the outer isophotes silently.** The outer profile
  is where `n` is determined, so a mask that is too small biases the index directly
  — this is why the real-data inspection gate in this repo's `AGENTS.md` treats the
  mask radius as a science decision.
- Neighbouring galaxies inside a mask wide enough to reach the outskirts must be
  masked or modelled; the machinery is in
  [`wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../../core/concepts/extra_galaxies_and_noise_scaling.md).

## Key results from the literature

- de Vaucouleurs (1948) established the `R^(1/4)` law; Caon, Capaccioli & D'Onofrio
  (1993) showed the exponent varies with luminosity and effective radius, replacing
  it with a fitted Sersic index ([[sources-elliptical-galaxies]]).
- Lauer and others (1995), Byun and others (1996) and Faber and others (1997)
  surveyed the centres of early types with HST and established the core/power-law
  dichotomy and its central parameter relations
  ([[sources-elliptical-galaxies]]).
- Graham and others (2003) and Trujillo and others (2004) introduced the
  core-Sersic model as a replacement for the Nuker model, arguing the Nuker
  parameters are not radius-independent and therefore not physical
  ([[sources-elliptical-galaxies]]).
- Ferrarese and others (2006) and Côté and others (2006) analysed ACS Virgo Cluster
  Survey early types, extending the structural census to nuclei and to the dwarf
  regime ([[sources-elliptical-galaxies]]).
- Kormendy and others (2009) fitted Sersic profiles over an exceptional dynamic
  range for Virgo early types, quantified the core/extra-light distinction, and
  argued that spheroidal galaxies are a separate family from ellipticals
  ([[sources-elliptical-galaxies]]).
- Huang and others (2013) showed that nearby ellipticals are generally fitted better
  by three Sersic components than by one, with each component occupying a distinct
  scale ([[sources-elliptical-galaxies]]).
- Cappellari and others (2011) defined the volume-limited ATLAS-3D sample;
  Emsellem and others (2011) used it to establish the fast/slow rotator split;
  Cappellari (2016) is the review of what integral-field spectroscopy did to
  early-type classification ([[sources-ifu-spectroscopy]]).
- Kormendy & Bender (2011) proposed a revised parallel-sequence classification in
  which S0 galaxies sit alongside spirals of matched bulge fraction rather than
  between ellipticals and spirals ([[morphology-classification]]).
- Naab, Johansson & Ostriker (2009) and Oser and others (2010) supplied the
  theoretical frame: compact in-situ formation followed by size growth through minor,
  dry mergers — the "two phases" ([[sources-elliptical-galaxies]]).
- Duc and others (2015) imaged ATLAS-3D early types to very low surface brightness
  and found tidal features, shells and discs in a large fraction, tying the outer
  structure to the accretion history ([[sources-stellar-halos]]).
- D'Souza, Vegetti & Kauffmann (2015) showed that the massive end of the stellar
  mass function depends strongly on how much of the outer envelope the photometry
  captures — a structural systematic with cosmological consequences
  ([[sky-subtraction-and-photometry]], [[sources-stellar-halos]]).

## See also

- [[sersic-profile]]
- [[isophote-analysis]]
- [[galaxy-scaling-relations]]
- [[high-z-galaxy-structure]]
- [[multi-gaussian-expansion]]
- [[sky-subtraction-and-photometry]]
- [[sources-elliptical-galaxies]]
