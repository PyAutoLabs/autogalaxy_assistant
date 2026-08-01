---
title: Sersic profile
type: concept
topics: [light-profiles, structural-fitting]
sources:
  - de Vaucouleurs 1948 — the R^(1/4) law
  - Sersic 1963 — atmospheric and instrumental dispersion
  - Sersic 1968 — Atlas de Galaxias Australes
  - Ciotti 1999 — analytical properties of the R^(1/m) law
  - Graham 2005 — a concise reference to Sersic quantities
  - Caon 1993 — the shape of early-type light profiles
status: drafted
---

# Sersic profile

## TL;DR

The Sersic profile, `I(R) = I_e exp{ -b_n [ (R/R_e)^(1/n) - 1 ] }`, is the single
functional form on which almost all quantitative galaxy morphology rests. Three
parameters — effective radius `R_e`, intensity at that radius `I_e`, and index `n`
— describe everything from an exponential disc (`n = 1`) to a giant elliptical
(`n ≈ 4-10`). The constant `b_n` is not free: it is fixed by the requirement that
`R_e` enclose half the total light, and must be solved for numerically or from an
asymptotic series. Fitted `n` is not a robust observable in the way `R_e` is — it
is strongly covariant with the sky level, the PSF and the fitted radial range, and
that covariance is the source of most disagreements between published structural
catalogues.

## What it is

The profile generalises de Vaucouleurs' `R^(1/4)` law for elliptical galaxies to a
free exponent. Written in the "effective" parameterisation:

```
I(R) = I_e exp{ -b_n [ (R/R_e)^(1/n) - 1 ] }
```

- `R_e` — the **effective (half-light) radius**: the radius of the isophote
  enclosing half the profile's total flux, in projection.
- `I_e` — the surface brightness at `R_e`.
- `n` — the **Sersic index**, controlling how centrally concentrated the light is.
  Larger `n` means a steeper core and a more extended outer wing simultaneously.
- `b_n` — a dimensionless constant defined implicitly by `Γ(2n) = 2 γ(2n, b_n)`,
  i.e. by the half-light condition. It is **not** a free parameter, and hardcoding
  the common approximation `b_n ≈ 2n - 1/3` is only accurate for large `n`.

Special cases in wide use: `n = 0.5` a Gaussian, `n = 1` an exponential disc,
`n = 4` the de Vaucouleurs profile.

Two structural facts follow directly from the definition and matter in practice:

- **Total flux is finite** for all `n > 0`, and has a closed form in `Γ(2n)`.
  But the fraction of the flux beyond a few `R_e` grows quickly with `n`: a high-`n`
  fit places real luminosity at radii where the data are dominated by sky, which is
  why `n` and the sky level are the most degenerate pair in the whole problem
  ([[sky-subtraction-and-photometry]]).
- **`R_e` and `n` are covariant**, positively, along a ridge in the likelihood. A
  fit that overestimates `n` almost always overestimates `R_e` too. This is not a
  fitting bug; it is the geometry of the model.

Ellipticity is imposed by evaluating the profile on elliptical coordinates,
`R -> sqrt(x'^2 + (y'/q)^2)` for axis ratio `q` at some position angle. That makes
the isophotes exact, concentric, aligned ellipses — an idealisation that
[[isophote-analysis]] exists to test.

## Why it matters for PyAutoGalaxy

The Sersic profile is the default light model, and every parameter above is a
model parameter with a prior. The practical consequences:

- **The index is the parameter to watch.** A prior that lets `n` run to 8-10
  will let the fit trade `n` against the sky and against `R_e`. Whether that is
  desirable depends on the science: for a size measurement it usually is not.
- **`R_e` is measured, `n` is inferred.** Sizes are comparatively robust across
  codes and data; indices are not. Quote the two with different confidence.
- **Linear light profiles** solve for `I_e` analytically rather than sampling it,
  which removes one strongly covariant dimension from the non-linear parameter
  space — see [`wiki/core/concepts/linear_light_profiles_and_mge.md`](../../core/concepts/linear_light_profiles_and_mge.md).
- The available parameterisations and their variants (spherical, elliptical,
  cored, exponential, dev) are catalogued in
  [`wiki/core/api/light_profile_catalog.md`](../../core/api/light_profile_catalog.md);
  the conceptual treatment is in
  [`wiki/core/concepts/light_profiles.md`](../../core/concepts/light_profiles.md).

## Key results from the literature

- de Vaucouleurs (1948) established the `R^(1/4)` law from surface photometry of
  bright ellipticals, and introduced the effective radius as the natural scale
  ([[sources-light-profile-fitting]]).
- Sersic (1963, 1968) generalised the exponent to a free index `n`. The 1963 note
  showed the generalised law is preserved to first order under Gaussian smearing;
  the 1968 *Atlas de Galaxias Australes* is the canonical citation for the profile
  itself ([[sources-light-profile-fitting]]).
- Ciotti (1991) worked out the intrinsic and dynamical properties of the `R^(1/m)`
  family; Ciotti & Bertin (1999) derived the full asymptotic expansion for `b_n`,
  which is the standard way the constant is computed today
  ([[sources-light-profile-fitting]]).
- Graham & Driver (2005) is the practical reference: closed forms relating `n` to
  concentration, profile slopes, Petrosian indices and Kron magnitudes, and the
  conversions between the effective, central and mean-surface-brightness
  parameterisations ([[sources-light-profile-fitting]]).
- Caon, Capaccioli & D'Onofrio (1993) showed that `n` in early-type galaxies is not
  a constant near 4 but correlates with luminosity and effective radius — the
  result that turned `n` from a fixed exponent into a measured structural
  parameter ([[sources-elliptical-galaxies]]).
- Andredakis, Peletier & Balcells (1995) found the same for spiral bulges: bulge
  `n` decreases along the Hubble sequence rather than sitting at 4, which is the
  photometric root of the classical/pseudo-bulge distinction
  ([[bulge-disk-decomposition]], [[sources-bulge-disk-decomposition]]).
- Trujillo and others (2001, and its Moffat-PSF sequel) quantified how seeing
  biases recovered `n` and `R_e` — the standard reference for why the PSF must be
  convolved into the model rather than corrected afterwards
  ([[point-spread-function]], [[sources-light-profile-fitting]]).
- Graham and others (2003) and Trujillo and others (2004) introduced the
  **core-Sersic** model, adding an inner power law and break radius, and argued it
  replaces the Nuker model for the inner profiles of luminous ellipticals
  ([[early-type-galaxy-structure]], [[sources-elliptical-galaxies]]).
- Kormendy and others (2009) is the deepest single-galaxy application: Sersic fits
  over a very large dynamic range in surface brightness, and the argument that
  deviations from a single Sersic form are themselves the physically interesting
  signal ([[sources-elliptical-galaxies]]).

## See also

- [[bulge-disk-decomposition]]
- [[photometric-structural-fitting]]
- [[point-spread-function]]
- [[sky-subtraction-and-photometry]]
- [[galaxy-scaling-relations]]
- [[multi-gaussian-expansion]]
- [[sources-light-profile-fitting]]
