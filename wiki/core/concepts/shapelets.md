---
title: Shapelets — a basis for irregular morphology
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/light/standard/shapelets/
      - autogalaxy/profiles/light/linear/
      - autogalaxy/profiles/basis.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/imaging/features/shapelets/modeling.py
      - scripts/imaging/features/shapelets/fit.py
      - scripts/guides/profiles/light.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: e3ba6dcd061ff66fe9e833f212bd444b1b8a2c2b9d87d51205421433c669686e
---

# Shapelets — a basis for irregular morphology

A shapelet is an orthonormal basis function built from a Gaussian multiplied by a
polynomial — a Gauss–Hermite function in Cartesian coordinates, a Gauss–Laguerre function
in polar coordinates. Because the set is complete, a finite sum of shapelets can represent
morphological structure that no single analytic profile can: asymmetry, disc-like features,
mild lopsidedness. The formalism is Refregier (2003),
[arXiv:astro-ph/0105178](https://arxiv.org/abs/astro-ph/0105178); its use for galaxy
structure is discussed in
[Tabor et al. 2016](https://ui.adsabs.harvard.edu/abs/2016MNRAS.457.3066T).

Sources: `PyAutoGalaxy:autogalaxy/profiles/light/standard/shapelets/`. Worked example:
`autogalaxy_workspace:scripts/imaging/features/shapelets/modeling.py`.

## The three families

| Class | Indices | Coordinates |
|---|---|---|
| `ag.lp.ShapeletPolar` | `n`, `m` | polar (Gauss–Laguerre) |
| `ag.lp.ShapeletCartesian` | `n_y`, `n_x` | Cartesian (Gauss–Hermite) |
| `ag.lp.ShapeletExponential` | `n`, `m` | polar, exponential radial weighting |

Each also has an `ag.lp_linear.*` counterpart, which is what you actually fit with. Every
one shares two more parameters: a `centre` and a scale `beta` that sets the width of the
underlying Gaussian envelope, plus `ell_comps` for the elliptical frame.

`beta` is the single most consequential choice. It fixes the physical scale the basis is
sensitive to: structure much smaller than `beta` cannot be represented by low orders, and
structure much larger than `beta * sqrt(n_max)` falls outside the basis's reach. It is
shared across every shapelet in the basis and left free for the search to determine.

## Composing a shapelet basis

Shapelets are used as a `Basis`, never individually. The indices are enumerated
deterministically and the shared parameters are tied across the whole set:

```python
import autofit as af
import autogalaxy as ag

total_n = 5
total_m = sum(range(2, total_n + 1)) + 1

shapelets_bulge_list = af.Collection(
    af.Model(ag.lp_linear.ShapeletPolar) for _ in range(total_n + total_m)
)

n_count = 1
m_count = -1

for i, shapelet in enumerate(shapelets_bulge_list):
    shapelet.n = n_count
    shapelet.m = m_count

    m_count += 2

    if m_count > n_count:
        n_count += 1
        m_count = -n_count

    shapelet.centre = shapelets_bulge_list[0].centre
    shapelet.beta = shapelets_bulge_list[0].beta

bulge = af.Model(ag.lp_basis.Basis, profile_list=shapelets_bulge_list)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)
model = af.Collection(galaxies=af.Collection(galaxy=galaxy))
```

`autogalaxy_workspace:scripts/imaging/features/shapelets/modeling.py`. The `n`/`m` indices
are **fixed** (they label basis functions, not physical quantities), the `centre` and `beta`
are **shared**, and every amplitude is solved by the inversion. Free parameters: `centre_0`,
`centre_1`, `beta` — **N = 3**, against N = 7 for a single elliptical Sersic, for a model
that captures much more structure.

The truncation order `total_n` is the flexibility dial. Raising it adds basis functions
(and hence linear amplitudes) without adding non-linear dimensions, but it also lets the
basis absorb more noise, and it slows every likelihood evaluation because each function must
be evaluated and PSF-convolved. The workspace example's ~20 shapelets cost ~0.37 s per
likelihood versus ~0.01 s for a Sersic.

A Cartesian basis is enumerated as a rectangular grid of `(n_y, n_x)` instead, and can share
`ell_comps` as well:

```python
shapelets_bulge_list = []

for x in range(5):
    for y in range(5):
        shapelets_bulge_list.append(
            ag.lp_linear.ShapeletCartesian(
                n_y=y, n_x=x, centre=(0.0, 0.0), ell_comps=(0.0, 0.0), beta=1.0
            )
        )

bulge = ag.lp_basis.Basis(profile_list=shapelets_bulge_list)
```

The polar basis is the recommended default, because a galaxy is roughly radially organised
and a polar basis is a more natural (and more compact) description of that. Reach for the
Cartesian one only when the structure you are chasing is genuinely rectilinear.

To see what a basis actually looks like before fitting anything:

```python
import autogalaxy.plot as aplt

grid = ag.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.05)
aplt.subplot_basis_image(basis=bulge, grid=grid)
```

## The signed-amplitude problem

This is the shapelet family's defining limitation, and the reason it is not the default
basis.

Every other inversion in PyAutoGalaxy uses a **positive-only** solver, because surface
brightness cannot be negative. Shapelets cannot: their ability to represent arbitrary
morphology comes from cancellation between positive and negative basis functions, exactly
as a Fourier series does. Forcing non-negative amplitudes destroys the completeness that
makes them useful. So the solver must be told to allow signed solutions:

```python
fit = ag.FitImaging(
    dataset=dataset,
    galaxies=galaxies,
    settings=ag.Settings(use_positive_only_solver=False),
)
```

`autogalaxy_workspace:scripts/imaging/features/shapelets/modeling.py`. The consequence is
that a shapelet decomposition **can and often does** reconstruct regions of negative flux,
particularly where the galaxy has structure the truncated basis cannot represent. That is
unphysical. Treat negative regions in a shapelet reconstruction as a diagnostic: they say
the basis is a poor match, not that the galaxy has negative surface brightness. It also
means a shapelet model's total flux and any derived luminosity should be regarded with more
suspicion than an MGE's.

## When to use shapelets

Shapelets occupy a genuine middle ground, and the workspace is candid that they are rarely
the best of the three options:

| Situation | Reach for |
|---|---|
| Smooth, roughly self-similar galaxy; you want `n` and `R_eff` | a parametric Sersic ([`light_profiles`](./light_profiles.md)) |
| Isophotal twists, radially varying flattening, complex but smooth light | an MGE ([`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md)) |
| Disc-like or mildly asymmetric structure a Sersic cannot hold | shapelets |
| Localised clumps, spiral arms, tidal features, star-forming knots | a pixelisation ([`inversions_and_pixelizations`](./inversions_and_pixelizations.md)) |

The specific weaknesses to know about:

- Shapelets need a **well-defined centre** to expand about. A merging pair or a system with
  a bright companion breaks that assumption.
- A truncated basis handles **global, smooth asymmetry** far better than a localised
  feature. Bars, isolated knots and sharp tidal tails are poorly represented at any
  practical order.
- The signed solver, above.
- They are slower than an MGE while typically having *more* effective freedom to overfit
  — which is why the workspace recommends trying an MGE alongside any shapelet fit and
  comparing residuals directly.

As with an MGE, a shapelet `Basis` can carry a `regularization` term penalising non-smooth
amplitudes. This is research-only and no production analysis uses it.

## See also

- [`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md) — the other basis,
  and the linear-inversion machinery both share.
- [`inversions_and_pixelizations`](./inversions_and_pixelizations.md) — full freedom on a
  mesh, when a basis is not flexible enough.
- [`light_profiles`](./light_profiles.md) — the parametric alternative.
- [`../api/light_profile_catalog`](../api/light_profile_catalog.md) — construction
  arguments for each shapelet class.
