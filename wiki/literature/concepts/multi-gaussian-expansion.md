---
title: Multi-Gaussian expansion (MGE)
type: concept
topics: [light-profiles, structural-fitting, basis-functions]
sources:
  - Bendinelli 1991 — multi-Gaussian deconvolution
  - Monnet 1992 — sums of Gaussians for triaxial galaxies
  - Emsellem 1994 — the multi-Gaussian expansion method
  - Cappellari 2002 — efficient MGE fitting
  - Miller 2021 — Bayesian MGE fitting
status: drafted
---

# Multi-Gaussian expansion (MGE)

## TL;DR

An MGE represents a galaxy's surface brightness as a sum of concentric
two-dimensional Gaussians of differing widths and axis ratios. It is a *basis*
rather than a physical model: with enough components it reproduces Sersic
profiles, bulge + disc systems, boxy or discy isophotes and radial ellipticity
gradients to within the noise. Its two decisive properties are analytic: a
Gaussian convolved with a Gaussian-decomposed PSF is again a Gaussian, and a
Gaussian surface density deprojects analytically for an assumed inclination. That
makes the MGE the natural bridge between photometry and dynamical modelling, and —
because the amplitudes enter the model linearly — an unusually well-conditioned
way to fit galaxy light.

## What it is

The surface brightness is written

```
I(x, y) = Σ_k  (L_k / (2π σ_k^2 q_k)) exp{ -[x'^2 + (y'/q_k)^2] / (2 σ_k^2) }
```

for `N` Gaussians with dispersions `σ_k`, projected axis ratios `q_k` and
luminosities `L_k`, all sharing a centre (position angles may be shared or free).

Why this particular basis:

- **Convolution is closed.** Decompose the PSF into Gaussians too, and the
  PSF-convolved model is an MGE with `σ^2 -> σ^2 + σ_PSF^2`. No numerical
  convolution is required, and the PSF is handled exactly rather than on a grid.
- **Deprojection is analytic.** For an assumed inclination (and an assumed
  axisymmetric or triaxial intrinsic shape), each projected Gaussian maps to an
  intrinsic Gaussian in closed form. This is what makes MGE the standard input to
  Jeans and Schwarzschild dynamical models.
- **Amplitudes are linear.** With `σ_k` and `q_k` fixed, the `L_k` are the
  solution of a linear least-squares problem. Only the widths and axis ratios need
  non-linear treatment — or, in a fully linear scheme, a fixed logarithmically
  spaced ladder of `σ_k` with all amplitudes solved simultaneously.

Costs and caveats:

- The parameters are **not** physical. An individual Gaussian's width has no
  meaning; only integrated quantities (total luminosity, half-light radius,
  intensity profile) do. Do not report `σ_k` as a structural measurement.
- With free amplitudes the basis can fit noise and, if amplitudes are unconstrained
  in sign, produce unphysical negative light. Non-negativity or regularisation is
  the usual guard.
- Concentric Gaussians cannot represent a lopsided (`m = 1`) galaxy, an off-centre
  component or a spiral arm. MGE flexibility is radial and elliptical, not
  arbitrary.

## Why it matters for PyAutoGalaxy

MGE is a first-class light model, and the recommended one when the goal is to
subtract a galaxy's light accurately rather than to attach physical meaning to a
Sersic index:

- The amplitudes are solved as **linear light profiles**, so an MGE with tens of
  Gaussians adds only a handful of non-linear parameters (the width range, the
  axis ratios, the centre). The mechanics are in
  [`wiki/core/concepts/linear_light_profiles_and_mge.md`](../../core/concepts/linear_light_profiles_and_mge.md).
- It is the right tool when a single Sersic leaves structured residuals but you do
  not want to commit to a specific component decomposition — an intermediate step
  between [[sersic-profile]] and [[bulge-disk-decomposition]].
- The bundled JWST/NIRCam dataset shipped with this assistant is fitted with an MGE
  bulge in its benchmark prompt, precisely because the model-PSF caveat on that
  dataset makes a single-Sersic index untrustworthy
  ([`wiki/core/operations/dataset.md`](../../core/operations/dataset.md)).
- A related but distinct basis, shapelets, is covered in
  [`wiki/core/concepts/shapelets.md`](../../core/concepts/shapelets.md).

## Key results from the literature

- Bendinelli (1991) introduced multi-Gaussian approximation as a way to invert the
  Abel integral equation and deconvolve a PSF analytically — the mathematical
  origin of the technique ([[sources-light-profile-fitting]]).
- Monnet, Bacon & Emsellem (1992) showed that if both the intensity and the
  velocity field of a triaxial galaxy are written as sums of Gaussians on
  homothetic ellipsoids, the projected observables follow from the intrinsic ones
  by simple analytic formulae — the step that made MGE usable for real galaxies
  ([[sources-light-profile-fitting]]).
- Emsellem, Monnet & Bacon (1994) is the canonical MGE method paper: the formalism
  for building photometric and kinematic models, including deconvolution for an
  arbitrary PSF and deprojection for an arbitrary triaxial shape and viewing angle
  ([[sources-light-profile-fitting]]).
- Cappellari (2002) supplied the practical fitting algorithm — a robust,
  non-negative, sector-based procedure that made MGE fitting routine, and the
  implementation almost every subsequent dynamical study uses
  ([[sources-light-profile-fitting]]).
- Cappellari (2008) built the Jeans Anisotropic MGE (JAM) machinery on top of it,
  taking the MGE of the light and an MGE of the mass to predict projected
  kinematics; Cappellari (2020) extended the solution to spherically aligned
  anisotropy. Li and others (2016) tested JAM/MGE mass recovery against the
  Illustris simulation ([[sources-ifu-spectroscopy]]).
- Cappellari and others (2012) used MGE-based dynamical models of the ATLAS-3D
  sample to show the stellar initial mass function varies systematically with
  galaxy velocity dispersion — the highest-profile science result to rest on MGE
  photometry ([[stellar-mass-estimates]]).
- Miller & van Dokkum (2021) recast MGE fitting as Bayesian inference over the
  Gaussian amplitudes rather than a deterministic decomposition, giving posterior
  uncertainties on derived structural quantities
  ([[sources-light-profile-fitting]]).

## See also

- [[sersic-profile]]
- [[bulge-disk-decomposition]]
- [[point-spread-function]]
- [[photometric-structural-fitting]]
- [[early-type-galaxy-structure]]
- [[sources-light-profile-fitting]]
