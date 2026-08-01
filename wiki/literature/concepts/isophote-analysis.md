---
title: Isophote analysis and boxy/discy structure
type: concept
topics: [isophotes, morphology, non-parametric]
sources:
  - Carter 1978 — the structure of elliptical isophotes
  - Jedrzejewski 1987 — the isophote-fitting algorithm
  - Bender 1988 — isophote shapes of elliptical galaxies
  - Kormendy 1996 — a proposed revision of the Hubble sequence
  - Hao 2006 — isophotal shapes in SDSS
  - Ciambur 2015 — Isofit and Cmodel
status: drafted
---

# Isophote analysis and boxy/discy structure

## TL;DR

Isophote fitting is the non-parametric complement to profile fitting: rather than
assuming a functional form for `I(R)`, it traces the contours of constant surface
brightness and records, at each semi-major axis, the intensity, centre,
ellipticity, position angle and the Fourier coefficients of the departure from a
perfect ellipse. The fourth cosine coefficient `a_4` is the classical diagnostic —
positive for **discy** isophotes, negative for **boxy** ones — and it correlates
with rotation, radio and X-ray luminosity, and with what we now call the fast/slow
rotator split. Isophote analysis is also the honest way to discover that a
parametric model is wrong: twists, ellipticity gradients and centre shifts are
invisible in a single Sersic fit's parameters but obvious in its isophotes.

## What it is

The standard algorithm fits, at each of a series of semi-major axis lengths `a`,
an ellipse to the isophote and then expands the residual intensity around that
ellipse in a Fourier series in the eccentric anomaly `ψ`:

```
I(ψ) = I_0 + Σ_m [ a_m cos(m ψ) + b_m sin(m ψ) ]
```

The first-order terms are absorbed by adjusting the centre, and the second-order
terms by adjusting the ellipticity and position angle, so the fitted ellipse is
the one for which `a_1 = b_1 = a_2 = b_2 = 0`. What is left carries the shape
information:

- **`a_4 / a` > 0 — discy.** Pointed isophotes; usually an embedded stellar disc.
  Typical amplitudes are a few times `10^-3` to `10^-2`.
- **`a_4 / a` < 0 — boxy.** Rectangular isophotes; associated with the most
  luminous, slowly rotating, pressure-supported ellipticals.
- **`a_3`, `b_3` — `m = 3`** asymmetry; **`b_4`** the sine counterpart of `a_4`,
  non-zero when the discy or boxy distortion is not aligned with the isophote axes.
- **`m = 1`** lopsidedness is not captured by the classical scheme, because the
  centre is refitted at each radius to absorb it. Measuring lopsidedness requires
  holding the centre fixed.

Two derived diagnostics matter as much as the coefficients themselves:

- **Isophotal twist** — position angle changing with radius, the projected
  signature of a triaxial figure or of two misaligned components.
- **Ellipticity profile** — a rising `ε(a)` in a disc galaxy usually means the disc
  is taking over from the bulge, and its shape sets where a two-component
  decomposition can succeed.

At high inclination the ellipse-based expansion breaks down for strongly
non-elliptical isophotes; a generalised expansion in eccentric anomaly (rather
than in polar angle) is the modern fix.

## Why it matters for PyAutoGalaxy

- Isophote (ellipse) fitting is a supported analysis in its own right, with its own
  API surface and multipole handling — see
  [`wiki/core/api/ellipse.md`](../../core/api/ellipse.md) and
  [`wiki/core/concepts/ellipse_fitting_and_multipoles.md`](../../core/concepts/ellipse_fitting_and_multipoles.md).
- It is the recommended **diagnostic before committing to a parametric model**. Run
  it, look at `ε(a)`, `PA(a)` and `a_4(a)`, and let those decide whether one Sersic,
  two components, or an [[multi-gaussian-expansion|MGE]] is appropriate.
- Because a Sersic model imposes concentric aligned ellipses by construction,
  isophotal twists and `a_4` structure appear in the **residual map** as
  characteristic four-lobed or spiral patterns. Recognising them is the difference
  between "the fit is bad" and "the model is missing an ingredient".
- Multipole terms can be added to a parametric fit instead of measured separately;
  which route to take is a modelling decision, not a fixed rule.

## Key results from the literature

- Carter (1978) reported that elliptical galaxy isophotes are not pure ellipses —
  the observation the whole field descends from
  ([[sources-isophotes-and-multipoles]]).
- Jedrzejewski (1987) gave the iterative ellipse-fitting-plus-Fourier-residual
  algorithm that is still the standard implementation, including the convention
  that `a_1, b_1, a_2, b_2` are zeroed by the fit itself
  ([[sources-isophotes-and-multipoles]]).
- Bender, Döbereiner & Möllenhoff (1988) published isophote shapes for a large
  sample of bright ellipticals, and Bender and others (1989) tied `a_4/a` to global
  optical, radio and X-ray properties: boxy ellipticals are the radio- and
  X-ray-luminous, slowly rotating ones ([[sources-isophotes-and-multipoles]]).
- Peletier and others (1990) combined CCD surface photometry with dynamical data
  for 39 ellipticals, establishing the isophote-shape-versus-kinematics link on a
  common sample ([[sources-elliptical-galaxies]]).
- Kormendy & Bender (1996) proposed reordering the elliptical branch of the Hubble
  sequence by isophote shape rather than by apparent flattening, because `a_4`
  tracks the physics (rotation support) and `E0-E7` does not
  ([[morphology-classification]], [[sources-isophotes-and-multipoles]]).
- Ferrarese and others (2006) carried out a homogeneous isophotal analysis of the
  ACS Virgo Cluster Survey early types, extending the measurement to HST resolution
  and to the faint dwarf regime ([[sources-isophotes-and-multipoles]]).
- Hao and others (2006) measured isophotal shapes for a large SDSS
  elliptical/lenticular sample, moving the boxy/discy statistic from tens of
  galaxies to tens of thousands ([[sources-isophotes-and-multipoles]]).
- Krajnović and others (2006) generalised the same harmonic decomposition from
  surface brightness to the higher moments of the line-of-sight velocity
  distribution ("kinemetry"), which is how the fast/slow rotator classification is
  operationalised ([[sources-isophotes-and-multipoles]]).
- Ciambur (2015) reformulated the expansion so that strongly non-elliptical
  isophotes — highly inclined discs, strong bars — are fitted correctly, and
  supplied a matched model-image reconstruction
  ([[sources-isophotes-and-multipoles]]).
- Peng and others (2010) took the opposite route, folding Fourier and bending modes
  directly into a parametric two-dimensional fit rather than measuring them from
  isophotes ([[photometric-structural-fitting]]).

## See also

- [[early-type-galaxy-structure]]
- [[morphology-classification]]
- [[sersic-profile]]
- [[photometric-structural-fitting]]
- [[clumpy-and-irregular-structure]]
- [[sources-isophotes-and-multipoles]]
