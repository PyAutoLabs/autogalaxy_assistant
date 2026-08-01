---
title: Stellar mass estimates
type: concept
topics: [stellar-populations, stellar-mass, sed-fitting]
sources:
  - Bell 2001 — stellar mass-to-light ratios from colour
  - Bruzual 2003 — stellar population synthesis
  - Kauffmann 2003 — SDSS stellar masses and star formation histories
  - Conroy 2013 — modelling panchromatic SEDs
  - Cappellari 2012 — systematic IMF variation
  - Suess 2019 — colour gradients and half-mass radii
status: drafted
---

# Stellar mass estimates

## TL;DR

Stellar mass is not measured; it is inferred from light through a mass-to-light
ratio, and every step of that inference is a modelling choice. The cheapest route
is a colour-`M/L` relation calibrated on population synthesis models; the standard
route is full SED fitting; the independent check is dynamical mass from kinematics.
The dominant systematic is the initial mass function, which shifts masses by up to
a factor of ~2 in normalisation and — as dynamical work has shown — is not
universal. For structural work there is a second, structure-specific trap: a
galaxy's `M/L` varies with radius, so a mass computed from integrated colours and
applied to a light-weighted size gives a half-mass radius that is systematically
too large.

## What it is

Three routes, in increasing order of cost:

1. **Colour-based `M/L`.** A single optical or optical-near-infrared colour maps to
   `log(M/L)` through a near-linear relation calibrated on synthetic populations.
   Cheap, surprisingly accurate for normal star-forming and quiescent galaxies, and
   badly wrong for dusty or post-starburst systems where age and dust are
   degenerate along the same colour direction.
2. **SED fitting.** Fit the multi-band photometry with a library of star formation
   histories, metallicities, dust attenuation laws and (optionally) nebular
   emission, marginalising to a mass posterior. The formal uncertainty is small;
   the systematic — from the assumed star formation history family, the dust law,
   the stellar library and the IMF — is not.
3. **Dynamical masses.** Kinematics plus a dynamical model give the total mass
   inside some radius, which bounds the stellar mass from above and, combined with
   a dark matter model, constrains the IMF. Dynamical modelling of nearby early
   types is what turned "the IMF is universal" into an open question.

The systematics that dominate:

- **IMF normalisation.** A Chabrier or Kroupa IMF gives masses roughly 0.2-0.25 dex
  lower than a Salpeter IMF. Because this is a near-constant offset it does not
  affect relative trends, so always state the IMF and, if comparing catalogues,
  convert rather than assume.
- **IMF variation.** Dynamical and spectral evidence indicates the IMF varies
  systematically with velocity dispersion in early-type galaxies, which turns a
  constant offset into a mass-dependent one — directly relevant to scaling
  relations ([[galaxy-scaling-relations]]).
- **Spatially unresolved photometry underestimates mass.** Integrated colours are
  luminosity-weighted, so they are biased towards the youngest, brightest
  component. Fitting resolved pixels or radial bins and summing gives a larger
  total mass, with the discrepancy largest for galaxies with strong colour
  gradients.
- **Half-mass is not half-light.** Negative colour gradients (redder centres) put
  the mass-weighted half-light radius inside the light-weighted one. At `z ~ 1-2.5`
  this accounts for a substantial fraction of the apparent size evolution
  ([[high-z-galaxy-structure]]).
- **Aperture and profile.** The mass you get depends on how much of the outer
  envelope your photometry captured, which is a sky-subtraction question
  ([[sky-subtraction-and-photometry]]).

## Why it matters for PyAutoGalaxy

- Structural fitting produces *luminosities*, not masses. The conversion is
  downstream and carries its own error budget; keep the two separate when
  reporting.
- **Multi-band fitting is the bridge.** Fitting bands simultaneously with tied
  structure yields per-component fluxes in every band, which is exactly the input a
  component-wise `M/L` needs — a bulge mass and a disc mass rather than one galaxy
  mass ([`wiki/core/concepts/multi_wavelength.md`](../../core/concepts/multi_wavelength.md)).
- To recover a **mass-weighted** size rather than a light-weighted one, either fit
  the resolved colour information or fit a model whose parameters vary smoothly with
  wavelength and integrate. Quoting a light-weighted `R_e` as a mass size is a
  common and avoidable error.
- Unit and cosmology conventions used when converting fluxes and angular sizes to
  physical quantities are in
  [`wiki/core/concepts/cosmology_and_units.md`](../../core/concepts/cosmology_and_units.md).

## Key results from the literature

- Bell & de Jong (2001) established the colour-`M/L` relations from population
  synthesis models — still the standard shortcut; Bell and others (2003) applied
  them to optical and near-infrared survey data to derive luminosity and stellar
  mass functions ([[sources-galaxy-formation-misc]]).
- Bruzual & Charlot (2003) supplied the stellar population synthesis models that
  most of these estimates rest on ([[sources-galaxy-formation-misc]]).
- Kauffmann and others (2003) derived stellar masses and star formation histories
  for ~10^5 SDSS galaxies from spectral indices rather than broad-band colours
  ([[sources-galaxy-formation-misc]]).
- Kroupa (2001) and Chabrier (2003) define the two IMFs in near-universal use;
  the choice between them and Salpeter is the largest single normalisation
  systematic ([[sources-galaxy-formation-misc]]).
- Conroy (2013) is the review of panchromatic SED modelling: what the assumptions
  are, which ones dominate, and how large the resulting systematic floor is
  ([[sources-galaxy-formation-misc]]).
- Cappellari and others (2012) showed from dynamical modelling of the ATLAS-3D
  sample that the IMF varies systematically with galaxy velocity dispersion,
  breaking the universal-IMF assumption ([[multi-gaussian-expansion]],
  [[sources-ifu-spectroscopy]]).
- Zibetti, Charlot & Rix (2009) built resolved stellar mass maps and showed the
  totals differ from those derived from integrated photometry;
  Sorba & Sawicki (2015) quantified the effect and showed spatially unresolved SED
  fitting underestimates mass, most severely for galaxies with strong internal
  colour variation ([[sources-galaxy-formation-misc]]).
- Roediger & Courteau (2015) systematically compared colour-based `M/L`
  prescriptions and quantified the spread between them
  ([[sources-galaxy-formation-misc]]).
- Taylor and others (2011) produced the GAMA stellar mass catalogue and documented
  the precision achievable from optical SED fitting alone;
  Mendel and others (2014) went further and published separate bulge, disc and
  total masses for SDSS galaxies, tying stellar mass directly to a structural
  decomposition ([[bulge-disk-decomposition]], [[sources-bulge-disk-decomposition]]).
- Bernardi and others (2013) showed the massive end of the stellar mass function
  moves substantially depending on which light profile the photometry assumed
  ([[sky-subtraction-and-photometry]]).
- Suess and others (2019) measured half-mass radii for ~7000 galaxies at
  `1.0 ≤ z ≤ 2.5`, finding them ~25% smaller than half-light radii on average and
  showing the discrepancy drives much of the reported mass-size evolution
  ([[high-z-galaxy-structure]], [[sources-high-redshift]]).

## See also

- [[galaxy-scaling-relations]]
- [[high-z-galaxy-structure]]
- [[bulge-disk-decomposition]]
- [[sky-subtraction-and-photometry]]
- [[multi-gaussian-expansion]]
- [[sources-galaxy-formation-misc]]
