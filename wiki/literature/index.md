# PyAutoGalaxy Galaxy Structure Wiki — Index

Top-level navigation. See [`AGENTS.md`](./AGENTS.md) for the schema and how the assistant
should use this wiki.

## Start here

- [[photometric-structural-fitting]] — what it means to fit a galaxy's light with a
  parametric model, and what the fit is actually measuring.
- [[sersic-profile]] — the one profile the whole field is built on.
- [[morphology-classification]] — how galaxies are sorted into types, and how that
  relates to the structural parameters a fit returns.

## Light-profile fitting

- [[sersic-profile]] — the R^(1/n) law, effective radius, Sersic index.
- [[photometric-structural-fitting]] — forward-modelling the image: likelihood,
  masking, the parameters that actually get constrained.
- [[multi-gaussian-expansion]] — MGE as a flexible, near-arbitrary light model.
- [[point-spread-function]] — why the PSF sets the floor on every structural
  measurement.
- [[sky-subtraction-and-photometry]] — the systematic that dominates the outskirts.

## Bulge / disk decomposition

- [[bulge-disk-decomposition]] — two-component fits, their degeneracies, and when
  the components mean something physical.
- [[stellar-mass-estimates]] — turning fitted light into stellar mass.

## Isophotes and multipoles

- [[isophote-analysis]] — ellipse fitting, boxy/discy deviations, isophotal twists.

## Scaling relations

- [[galaxy-scaling-relations]] — size-mass, Kormendy, Faber-Jackson, the fundamental
  plane, and what structural measurement systematics do to each.

## Early-type galaxy structure

- [[early-type-galaxy-structure]] — cores, envelopes, the two families of
  ellipticals, and the massive end.

## Disk galaxies

- [[disk-galaxy-structure]] — exponential disks, scale lengths, truncations and
  breaks, bars and pseudo-bulges.

## High-redshift structure

- [[high-z-galaxy-structure]] — size evolution, compact quiescent galaxies, and what
  JWST changed.
- [[clumpy-and-irregular-structure]] — when a smooth parametric model is the wrong
  model.

## Surveys and catalogues (named entities)

- Wide-field legacy fields: [[cosmos-survey]], [[cosmos-web]], [[candels]],
  [[zcosmos]].
- Structural catalogues: [[sdss]].
- Integral-field surveys: [[manga]], [[sami]].
- Missions: [[euclid]].

## Instruments

- [[hst]] — the instrument that defined resolved structural measurement.
- [[jwst]] — the instrument that extended it into the rest-frame optical at high
  redshift.

## Sources (bibliography by topic)

These pages describe claim support. Canonical citation metadata and key-management rules
live in [`bibliography/`](./bibliography/README.md).

- [[sources-light-profile-fitting]]
- [[sources-bulge-disk-decomposition]]
- [[sources-isophotes-and-multipoles]]
- [[sources-galaxy-scaling-relations]]
- [[sources-elliptical-galaxies]]
- [[sources-massive-ellipticals]]
- [[sources-disk-galaxy-structure]]
- [[sources-stellar-halos]]
- [[sources-high-redshift]]
- [[sources-ifu-spectroscopy]]
- [[sources-halo-galaxy-connection]]
- [[sources-cosmos-survey]]
- [[sources-collaborations-and-surveys]]

## Meta

- [[AGENTS]] — schema and usage rules.
- [[log]] — compilation history.
