---
title: Galaxy structural scaling relations
type: concept
topics: [scaling-relations, sizes, populations]
sources:
  - Kormendy 1977 — structure parameters of the spheroidal component
  - Djorgovski 1987 — fundamental properties of elliptical galaxies
  - Dressler 1987 — the Dn-sigma relation
  - Shen 2003 — the SDSS size distribution
  - Lange 2015 — GAMA mass-size relations
  - van der Wel 2014 — the size-mass distribution since z = 3
status: drafted
---

# Galaxy structural scaling relations

## TL;DR

Galaxies do not populate their structural parameter space uniformly: size,
luminosity, surface brightness, stellar mass and velocity dispersion lie on tight,
low-scatter relations. The two-dimensional projections — Kormendy's
`⟨μ⟩_e - R_e`, Faber-Jackson's `L - σ`, the mass-size relation — are slices through
the three-dimensional **Fundamental Plane** (and its stellar-mass counterpart, the
Mass Plane). These relations are the main scientific output of structural fitting,
which makes their systematics a structural-fitting problem: every relation inherits
the sky treatment, the PSF treatment and the profile choice used to measure `R_e`.

## What it is

The relations most often measured from imaging alone:

- **Kormendy relation** — mean surface brightness within the effective radius
  against `R_e` for elliptical galaxies. Purely photometric, so it is the one a
  structural fit produces directly.
- **Mass-size (and luminosity-size) relation** — `R_e` against stellar mass. Its
  slope, normalisation and scatter all differ between early- and late-type
  galaxies, and the split is sharper in Sersic index or colour than in visual
  morphology. Below a transition mass around `10^10 M_sun` the early-type relation
  flattens markedly.
- **Faber-Jackson** — luminosity against central velocity dispersion for
  ellipticals; the `L - σ` projection of the Fundamental Plane.
- **Tully-Fisher** — luminosity against H I line width (rotation velocity) for
  spirals; the disc-galaxy analogue.
- **Fundamental Plane** — `log R_e = a log σ + b ⟨μ⟩_e + c`, a plane with
  ~0.05 dex scatter in `log R_e`. Its **tilt** away from the virial expectation is
  the long-standing puzzle, attributed to a systematic variation of `M/L` (or of
  the IMF, or of the dark matter fraction) with mass.
- **Mass Plane** — replacing luminosity with dynamically or photometrically
  measured stellar mass largely removes the tilt, which is the strongest evidence
  that the tilt is an `M/L` effect rather than a structural one.

Three systematics affect every one of these:

1. **`R_e` depends on the profile fitted.** A single Sersic gives a larger `R_e`
   than a de Vaucouleurs fit for the same galaxy, and the difference grows with
   luminosity. Comparing catalogues that used different models is a common error.
2. **Half-light is not half-mass.** Colour gradients mean the mass-weighted radius
   is smaller than the light-weighted one, typically by tens of per cent, and by
   more at high redshift ([[stellar-mass-estimates]]).
3. **Selection and aperture.** The relation you measure depends on where you stop
   integrating, which is a sky-subtraction question
   ([[sky-subtraction-and-photometry]]).

## Why it matters for PyAutoGalaxy

- Scaling relations are the usual *downstream* product of a fitting campaign, so
  the priors and model choices made per galaxy propagate into a population-level
  result. Model the population explicitly where possible: hierarchical models fit
  many galaxies simultaneously with a shared parent distribution rather than
  stacking independent point estimates — see
  [`wiki/core/concepts/hierarchical_models.md`](../../core/concepts/hierarchical_models.md).
- Report `R_e` with its definition attached (which profile, which band, which
  radial range). The wiki's convention for the derived quantities a fit exposes is
  in [`wiki/core/api/aggregator.md`](../../core/api/aggregator.md).
- Because the relations are tight, they are also a *diagnostic*: a galaxy that
  falls far off the mass-size relation is usually a fitting failure before it is a
  discovery.

## Key results from the literature

- Kormendy (1977) established the surface-brightness-radius relation for the
  spheroidal components of galaxies ([[sources-elliptical-galaxies]]).
- Faber & Jackson (1976) found `L ∝ σ^4` for ellipticals; Tully & Fisher (1977)
  found the luminosity-line-width relation for spirals. Both predate the plane
  they are projections of ([[sources-elliptical-galaxies]]).
- Djorgovski & Davis (1987) and Dressler and others (1987) independently identified
  the Fundamental Plane — the former as the `R_e - σ - ⟨μ⟩_e` plane, the latter in
  the `D_n - σ` form used for peculiar-velocity work
  ([[sources-elliptical-galaxies]]).
- Bender, Burstein & Faber (1992) recast the plane in orthogonal "κ-space"
  coordinates that separate mass, `M/L` and surface brightness, making the tilt
  legible ([[sources-elliptical-galaxies]]).
- Shen and others (2003) measured the size distribution of ~10^5 SDSS galaxies,
  establishing the separate early- and late-type mass-size relations and their
  log-normal scatter ([[galaxy-scaling-relations]], [[sources-elliptical-galaxies]]).
- Bernardi and others (2003) measured the Fundamental Plane for a large homogeneous
  SDSS early-type sample; Hyde & Bernardi (2009) showed that the plane's
  coefficients shift when luminosity is replaced by stellar mass
  ([[sources-elliptical-galaxies]]).
- Graham & Worley (2008) quantified how inclination and internal dust change bulge
  and disc parameters, and therefore the size-luminosity relations derived from
  them ([[sources-bulge-disk-decomposition]]).
- Lange and others (2015) measured GAMA mass-size relations subdivided by Sersic
  index, colour and visual morphology, and showed the divisions do not give the
  same answer — the cleanest demonstration that "early type" is a definition, not
  an observable ([[sources-bulge-disk-decomposition]]).
- Cappellari and others (2013) presented the ATLAS-3D Mass Plane from 260 dynamical
  models, showing that replacing luminosity with dynamical mass removes most of the
  Fundamental Plane tilt; the companion paper mapped the mass-size and
  mass-`σ` distributions and argued bulge fraction is the driving variable
  ([[sources-ifu-spectroscopy]]).
- van der Wel and others (2014) measured the size-mass distribution from `z = 3` to
  the present with CANDELS + 3D-HST, the standard reference for size evolution
  ([[high-z-galaxy-structure]], [[sources-high-redshift]]);
  Nedkova and others (2021) extended it to low stellar masses
  ([[sources-high-redshift]]).

## See also

- [[sersic-profile]]
- [[early-type-galaxy-structure]]
- [[high-z-galaxy-structure]]
- [[stellar-mass-estimates]]
- [[bulge-disk-decomposition]]
- [[sky-subtraction-and-photometry]]
- [[sources-elliptical-galaxies]]
