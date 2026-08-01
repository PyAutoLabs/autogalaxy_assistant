---
title: Kinematic structure and the rotator classes
type: concept
topics: [kinematics, ifu-spectroscopy, dynamics]
sources:
  - Emsellem 2011 — fast and slow rotators
  - Cappellari 2016 — the IFS view of early-type structure
  - Krajnovic 2006 — kinemetry
  - Cappellari 2008 — Jeans anisotropic MGE models
  - Cappellari 2013 — the ATLAS-3D Mass Plane
status: drafted
---

# Kinematic structure and the rotator classes

## TL;DR

Integral-field spectroscopy answers a question photometry cannot: is a galaxy's
shape supported by rotation or by random motions? The answer splits early-type
galaxies into **fast rotators** (the large majority — essentially disc galaxies
with a big bulge, often discy isophotes) and **slow rotators** (rare, massive,
round or boxy, frequently with a kinematically distinct core). That division cuts
across the visual E/S0 classification and correlates instead with the structural
diagnostics photometry does measure — Sersic index, bulge fraction, `a_4`. For a
photometric fitter this matters in two directions: kinematics is the independent
check that a photometric decomposition is physically meaningful, and photometry —
specifically a multi-Gaussian expansion of the light — is the standard input to the
dynamical model.

## What it is

**The observable.** An integral-field unit gives a spectrum per spatial element, so
the line-of-sight velocity distribution is measured across the galaxy's face. Its
moments are extracted by fitting stellar templates convolved with a parameterised
velocity distribution, yielding maps of mean velocity `V`, dispersion `σ` and the
higher-order Gauss-Hermite terms `h_3`, `h_4`.

**The classifier.** The specific angular momentum proxy

```
λ_R = ⟨R |V|⟩ / ⟨R sqrt(V^2 + σ^2)⟩
```

measured within one effective radius, separates fast from slow rotators along a
locus in the `λ_R`-ellipticity plane. Unlike `V/σ` it is a light-weighted radial
average, which makes it comparable between galaxies of different sizes.

**Kinemetry** generalises isophote fitting to the velocity field: fit ellipses to
the kinematic maps and expand the residual in harmonics, in exact analogy to the
`a_4` machinery of [[isophote-analysis]]. This is how kinematically distinct cores,
counter-rotating discs and misalignments between the photometric and kinematic axes
are quantified.

**From photometry to mass.** The standard dynamical pipeline is:

1. Fit a multi-Gaussian expansion to the surface brightness
   ([[multi-gaussian-expansion]]).
2. Deproject it analytically for an assumed inclination and intrinsic shape.
3. Scale it by a mass-to-light ratio, optionally adding a dark matter component.
4. Solve the Jeans equations (or build a Schwarzschild orbit library) and compare
   the predicted second moments to the observed maps.

Every step inherits the photometry's systematics: the MGE's outer extent depends on
the sky, and the deprojection depends on an inclination that photometry constrains
only weakly for near-round systems.

## Why it matters for PyAutoGalaxy

PyAutoGalaxy models **imaging and interferometer data**, not stellar kinematics.
The relevance is therefore indirect but real:

- The MGE that a dynamical model needs is exactly the MGE a PyAutoGalaxy fit
  produces, and producing it well — correct PSF, correct sky, mask wide enough — is
  the photometric half of the dynamical measurement
  ([`wiki/core/concepts/linear_light_profiles_and_mge.md`](../../core/concepts/linear_light_profiles_and_mge.md)).
- Kinematics is the **external validation** for a photometric decomposition: if a
  bulge-disc fit says `B/T = 0.6` and the galaxy is a fast rotator with a rising
  rotation curve throughout, one of the two is wrong.
- Interferometric data — resolved gas emission — is fitted natively, and its
  structural interpretation shares this vocabulary; see
  [`wiki/core/concepts/interferometer_theory.md`](../../core/concepts/interferometer_theory.md).
- The rotator classes are the reason "elliptical" is a poor sample definition. If
  the science depends on pressure support, select on kinematics or on a
  photometric proxy calibrated against it, and say which.

## Key results from the literature

- Cappellari & Emsellem (2004) introduced the penalised pixel-fitting method for
  extracting line-of-sight velocity distributions, which almost all subsequent
  integral-field work uses ([[sources-ifu-spectroscopy]]).
- Krajnović and others (2006) generalised photometric harmonic analysis to the
  kinematic maps ("kinemetry"), giving a uniform language for photometric and
  kinematic structure ([[isophote-analysis]], [[sources-isophotes-and-multipoles]]).
- Cappellari and others (2011) defined the volume-limited ATLAS-3D sample of 260
  nearby early-type galaxies — the sample the rotator classification was built on
  ([[sources-ifu-spectroscopy]]).
- Emsellem and others (2011) established the fast/slow rotator division using
  `λ_R` within `R_e`, and showed slow rotators are a small, massive minority
  ([[early-type-galaxy-structure]], [[sources-ifu-spectroscopy]]).
- Cappellari (2016) is the review: what integral-field spectroscopy did to
  early-type galaxy classification, and why the kinematic division supersedes the
  E/S0 split ([[sources-ifu-spectroscopy]]).
- Cappellari (2008) built the Jeans Anisotropic MGE machinery that turns an MGE of
  the light plus kinematic maps into a mass model; Cappellari (2020) extended it to
  spherically aligned anisotropy; Li and others (2016) tested how faithfully the
  method recovers masses using the Illustris simulation
  ([[multi-gaussian-expansion]], [[sources-ifu-spectroscopy]]).
- Cappellari and others (2013) used 260 such models to construct the Mass Plane,
  showing that replacing luminosity with dynamical mass removes most of the
  Fundamental Plane tilt; the companion paper argued bulge fraction is the variable
  that organises early-type scaling relations
  ([[galaxy-scaling-relations]], [[sources-ifu-spectroscopy]]).
- Cappellari and others (2012) used the same modelling to show the stellar initial
  mass function varies systematically with velocity dispersion — a dynamical result
  with direct consequences for photometric stellar masses
  ([[stellar-mass-estimates]], [[sources-ifu-spectroscopy]]).
- Bershady and others (2010) set out the DiskMass survey and, unusually, published
  its full error budget — a useful model for how to account for the systematic
  chain from photometry through inclination to dynamical mass
  ([[sources-ifu-spectroscopy]]).
- Bender, Döbereiner & Möllenhoff (1988) and Bender and others (1989) had already
  established the photometric side of the same division: boxy ellipticals are the
  slowly rotating, radio- and X-ray-bright ones, discy ones rotate
  ([[isophote-analysis]], [[sources-isophotes-and-multipoles]]).

## See also

- [[early-type-galaxy-structure]]
- [[multi-gaussian-expansion]]
- [[isophote-analysis]]
- [[galaxy-scaling-relations]]
- [[stellar-mass-estimates]]
- [[manga]]
- [[sami]]
