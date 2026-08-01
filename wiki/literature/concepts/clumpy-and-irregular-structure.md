---
title: Clumpy and irregular structure
type: concept
topics: [high-redshift, morphology, non-parametric, residuals]
sources:
  - Elmegreen 2005 — chain and clump-cluster galaxies
  - Elmegreen 2007 — resolved clumpy disks in the UDF
  - Foerster Schreiber 2011 — kiloparsec-scale clumps at z ~ 2
  - Guo 2015 — clumpy galaxies in CANDELS
  - Dekel 2009 — cold streams, clumpy disks and compact spheroids
status: drafted
---

# Clumpy and irregular structure

## TL;DR

A large fraction of star-forming galaxies at `z ~ 1-3` are not smooth: their
rest-frame ultraviolet and optical light is dominated by a handful of
kiloparsec-scale, `10^8-10^9 M_sun` clumps embedded in a rotating disc. Whether
these clumps are long-lived structures that migrate inwards to build a bulge, or
transient associations that disperse within a few tens of Myr, remains open and is
sensitive to resolution and to which wavelength is observed. For a structural
fitter, clumpiness is both a science signal and a systematic: a smooth Sersic model
fitted to a clumpy galaxy returns a size and index that describe the clump
distribution as much as the underlying disc, and the diagnostic lives in the
residual map rather than in the parameters.

## What it is

**The phenomenon.** In deep rest-frame-UV imaging, `z ~ 2` star-forming galaxies
appear as "clump-cluster" and "chain" systems — a few bright knots in a linear or
scattered arrangement, often with no obvious nucleus. Follow-up in the rest-frame
optical and in ionised-gas kinematics shows most of these are rotating discs whose
star formation is concentrated into a small number of giant complexes, rather than
merging fragments.

**Formation picture.** The favoured mechanism is gravitational instability in a
gas-rich, turbulent, high-velocity-dispersion disc fed by cold accretion. Such
discs fragment on scales far larger than local giant molecular clouds, producing
clumps with a substantial fraction of the disc mass. Dynamical friction can then
drag the clumps inwards on a few orbital times, plausibly building a bulge — if
they survive stellar feedback long enough.

**Measurement caveats that dominate the observational picture:**

- **Wavelength.** Clump fractions measured in the rest-frame UV are much higher
  than in the rest-frame optical, because clumps are young and the underlying disc
  is not. A "clumpy galaxy" is a statement about a band.
- **Resolution and surface-brightness limits.** Apparent clump masses and sizes are
  resolution-limited; higher-resolution data consistently breaks single clumps into
  several smaller ones.
- **Definition.** "Clump" needs an operational definition — a contrast threshold
  above a smoothed model, a minimum fraction of the galaxy's flux, a deblending
  criterion. Different definitions give different clump fractions on the same data.

**Non-parametric quantification.** Clumpiness is one of the CAS statistics, and
residual-based measures — the fraction of flux left after subtracting a smooth
model, or the higher-order MID statistics — are designed exactly for this regime
([[morphology-classification]]).

## Why it matters for PyAutoGalaxy

- **Read the residual map, not just the parameters.** A single Sersic fitted to a
  clumpy galaxy converges perfectly happily. The evidence that the model is wrong is
  the structured, positive residual at the clump positions — see
  [`wiki/core/api/plotting.md`](../../core/api/plotting.md) for the fit subplots that
  show it.
- Two modelling routes when smooth models fail:
  - **Add discrete components** — extra light profiles at the clump positions,
    which turns "clumpy" into a set of measured clump fluxes and sizes. The
    machinery for adding extra emitters is in
    [`wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../../core/concepts/extra_galaxies_and_noise_scaling.md).
  - **Use a flexible reconstruction** — a pixelised source-plane-free
    reconstruction of the galaxy's light, which fits irregular structure without
    committing to a component list. See
    [`wiki/core/concepts/inversions_and_pixelizations.md`](../../core/concepts/inversions_and_pixelizations.md).
- **Noise scaling** matters here: if a smooth model cannot reproduce clumps, the
  formal `chi^2` is dominated by a handful of pixels and the posterior on the smooth
  parameters becomes over-confident and biased.
- Fitting the same galaxy in several bands separates the young clumps from the
  older underlying disc, and is the cheapest way to tell a clump from an artefact
  ([`wiki/core/concepts/multi_wavelength.md`](../../core/concepts/multi_wavelength.md)).

## Key results from the literature

- Elmegreen and others (2005) classified the linear "chain" and "clump-cluster"
  morphologies that dominate the faint end of the Hubble Ultra Deep Field;
  Elmegreen & Elmegreen (2005) analysed the stellar populations of ten
  clump-cluster galaxies ([[sources-high-redshift]]).
- Elmegreen and others (2007) resolved clumpy discs in the UDF and argued the
  clumps are star-forming complexes within discs rather than merger debris
  ([[sources-high-redshift]]).
- Bournaud, Elmegreen & Elmegreen (2007) showed with simulations that clump-cluster
  and chain galaxies evolve rapidly into exponential discs with central bulges —
  the clump-migration bulge-building channel
  ([[bulge-disk-decomposition]], [[sources-high-redshift]]).
- Dekel, Sari & Ceverino (2009) set out the cold-stream-fed, violently unstable
  disc framework that predicts giant clumps, rapid inflow and compact spheroid
  formation ([[sources-high-redshift]]).
- Förster Schreiber and others (2011) measured the rest-frame optical properties of
  kiloparsec-scale clumps in `z ~ 2` star-forming galaxies, and the companion paper
  provided the detailed rest-frame optical morphologies on which the analysis rests
  ([[sources-high-redshift]]).
- Genzel and others (2011) measured the kinematics of giant clumps in the SINS
  sample, showing they sit in rotating discs and are dynamically distinct from
  merging components ([[sources-high-redshift]]).
- Guo and others (2015) gave a reproducible operational definition of a UV clump
  and measured the clumpy fraction from `z = 0.5` to `3` in CANDELS; Guo and others
  (2018) derived the clumps' physical properties, including how much of the host's
  star formation they carry ([[sources-high-redshift]]).
- Wuyts and others (2011) placed clumpy, disc-like and compact morphologies on the
  star-formation-rate-mass plane, connecting irregular structure to where a galaxy
  sits relative to the main sequence ([[high-z-galaxy-structure]]).
- Conselice (2003) defined the clumpiness statistic within CAS;
  Freeman and others (2013) introduced the MID statistics specifically because CAS
  and Gini-`M20` lose sensitivity to the disturbed morphologies common at high
  redshift ([[morphology-classification]]).
- Ferreira and others (2022, 2023) and Kartaltepe and others (2023) showed with
  JWST that at `z > 3` the rest-frame optical morphology is far more regular and
  disc-dominated than the rest-frame UV picture suggested — a direct demonstration
  that "irregular" was partly a wavelength artefact
  ([[high-z-galaxy-structure]], [[sources-high-redshift]]).

## See also

- [[high-z-galaxy-structure]]
- [[morphology-classification]]
- [[disk-galaxy-structure]]
- [[bulge-disk-decomposition]]
- [[photometric-structural-fitting]]
- [[sources-high-redshift]]
