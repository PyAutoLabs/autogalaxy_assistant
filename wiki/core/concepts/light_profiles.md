---
title: Light profiles — Sersic and friends
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/light/standard/sersic.py
      - autogalaxy/profiles/light/standard/
      - autogalaxy/profiles/light/abstract.py
      - autogalaxy/convert.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/profiles/light.py
      - scripts/imaging/start_here.py
      - scripts/guides/galaxies.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 18fc976bb3e49ea01490aa394c39c090e0b63f0d3a273cb8cc6c8ff35c4df373
---

# Light profiles — Sersic and friends

A light profile is an analytic function that describes a galaxy's **surface brightness**
as a function of position on the sky. It is the atom of galaxy-structure modelling: you
compose one or more of them into a `Galaxy`, evaluate them on a grid, blur the result
with the instrument PSF, and compare it to the data.

Sources: `PyAutoGalaxy:autogalaxy/profiles/light/` (implementation) and
`autogalaxy_workspace:scripts/guides/profiles/light.py` (the single-page tour of every
profile the library ships). The full menu with construction arguments is in
[`../api/light_profile_catalog`](../api/light_profile_catalog.md).

## The Sersic profile

The Sersic (1968) profile is the workhorse of galaxy morphology:

```
I(R) = I_eff * exp{ -b_n * [ (R / R_eff)^(1/n) - 1 ] }
```

`b_n` is not free — it is fixed by `n` so that `R_eff` encloses exactly half the
profile's total flux (`PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py`, the
`sersic_constant` property). Three parameters therefore control the radial shape:

- **`intensity`** — `I_eff`, the surface brightness **at** the effective radius, not at
  the centre and not a total flux. Its units are inherited from the data being fitted
  (conventionally electrons per second per pixel).
- **`effective_radius`** — `R_eff`, the **circular** half-light radius in arcseconds. For
  a flattened system the major-axis half-light radius is larger; the profile exposes it
  as `elliptical_effective_radius` (`= R_eff / sqrt(axis_ratio)`). Quote which one you
  mean — mixing the two is a real and common error when comparing to a catalogue.
- **`sersic_index`** — `n`, the concentration. `n = 1` is an exponential disc, `n = 4` is
  de Vaucouleurs. Higher `n` puts more light in both a steeper core and a more extended
  envelope, which is why `n` and `R_eff` are strongly degenerate and why the outer mask
  radius matters so much (see [`grids_and_masks`](./grids_and_masks.md)).

```python
import autogalaxy as ag

sersic = ag.lp.Sersic(
    centre=(0.0, 0.0),
    ell_comps=ag.convert.ell_comps_from(axis_ratio=0.8, angle=45.0),
    intensity=1.0,
    effective_radius=0.6,
    sersic_index=3.0,
)

image = sersic.image_2d_from(grid=grid)
```

`autogalaxy_workspace:scripts/guides/profiles/light.py`. Every profile in the library
implements this same `image_2d_from(grid=...)` method and returns an `Array2D` with
`slim` and `native` views — see [`grids_and_masks`](./grids_and_masks.md).

### Nested special cases

`ag.lp.Exponential` fixes `n = 1` and `ag.lp.DevVaucouleurs` fixes `n = 4`. Using them
instead of a free-`n` Sersic is a *physical* statement — "this component is a disc" /
"this component is a classical spheroid" — and it removes one parameter and one
degeneracy from the search. Prefer them when the science justifies the assumption; use
the free-index `Sersic` when the index itself is the measurement.

## The `ell_comps` convention

Every elliptical profile is parameterised by two **elliptical components** rather than an
axis-ratio and a position angle (`PyAutoGalaxy:autogalaxy/convert.py`):

```
ell_comps[0] = e_y = (1 - q) / (1 + q) * sin(2 * phi)
ell_comps[1] = e_x = (1 - q) / (1 + q) * cos(2 * phi)
```

where `q` is the minor-to-major axis ratio `b/a` and `phi` is the position angle
counter-clockwise from the positive x-axis. The reason is inferential, not aesthetic: a
position angle is periodic and degenerate at `phi` and `phi + 180`, and it becomes
completely unconstrained as `q → 1`, so a non-linear search wastes effort exploring a
pathological boundary. The `(e_y, e_x)` pair is a smooth 2D vector that goes to `(0, 0)`
for a round profile, with no periodic boundary at all.

Convert in both directions when talking to humans or catalogues:

```python
ell_comps = ag.convert.ell_comps_from(axis_ratio=0.8, angle=45.0)
axis_ratio, angle = ag.convert.axis_ratio_and_angle_from(ell_comps=ell_comps)
```

`axis_ratio_and_angle_from` deliberately returns an angle in `(-45, 135]` degrees so that
marginalising a posterior does not straddle a wrap-around and inflate the error bar. Two
practical consequences:

- **Report `axis_ratio` and `angle`, not `ell_comps`,** in a paper — the components are a
  sampling convenience, not a physical quantity a reader recognises.
- **Propagate errors on the converted quantity by converting every posterior sample**,
  not by converting the median and the error separately. See
  [`samples_and_posteriors`](./samples_and_posteriors.md).

Every elliptical profile has a spherical sibling whose name ends in `Sph`
(`ag.lp.SersicSph`, `ag.lp.GaussianSph`, …) which fixes `ell_comps = (0.0, 0.0)` and
therefore drops two parameters. Use it for a genuinely round system, or for a faint
companion whose ellipticity the data cannot constrain.

## The rest of the family

Grouped by what they are *for*:

- **Cored variants** — `ag.lp.SersicCore`, `ag.lp.ExponentialCore` add `radius_break`,
  `gamma` and `alpha`, replacing the central cusp with a shallower inner power law.
- **`ag.lp.Gaussian`** — a single Gaussian, parameterised by `sigma` instead of an
  effective radius and index. Rarely used alone; it is the building block of the
  Multi-Gaussian Expansion (see
  [`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md)).
- **`ag.lp.Moffat`** — `alpha`/`beta` parameterisation with broader wings than a
  Gaussian; the standard analytic PSF shape, and useful for compact nuclear emission.
- **`ag.lp.Chameleon`** and **`ag.lp.ElsonFreeFall`** — specialised double-isothermal and
  King-like forms.
- **Shapelets** — `ag.lp.ShapeletPolar`, `ag.lp.ShapeletCartesian`,
  `ag.lp.ShapeletExponential`, used as a basis rather than individually. See
  [`shapelets`](./shapelets.md).

## Multipole perturbations

`ag.lp.SersicMultipole` and `ag.lp.GaussianMultipole` perturb the eccentric radius of a
base profile with `m = 3` and `m = 4` Fourier harmonics:

```
r' = r * (1 + c3 cos(3θ) + s3 sin(3θ) + c4 cos(4θ) + s4 sin(4θ))
```

with `multipole_3_comps = (c3, s3)` and `multipole_4_comps = (c4, s4)` measured in the
profile's own elliptical frame. The `m = 4` term is the classic **boxy / discy**
deviation of an elliptical galaxy's isophotes; `m = 3` captures a lopsided, three-fold
distortion. Both default to `(0.0, 0.0)`, at which the profile reduces *exactly* to its
parent — so swapping `Sersic` for `SersicMultipole` never changes a prediction, it only
adds four parameters that can absorb real angular structure.

There is deliberately no spherical multipole variant: the perturbation is an angular
distortion defined relative to an elliptical frame, and a round profile has no preferred
angle. `autogalaxy_workspace:scripts/guides/profiles/light.py`.

For a *non-parametric* measurement of the same physics — isophote ellipticity, position
angle and harmonic amplitudes as functions of radius, measured rather than assumed — see
[`ellipse_fitting_and_multipoles`](./ellipse_fitting_and_multipoles.md).

## Standard, linear, operated, SNR

The same shapes ship in four namespaces, which differ in how `intensity` is treated:

| Namespace | `intensity` | Use |
|---|---|---|
| `ag.lp.*` | free parameter, sampled by the search | evaluating a known profile; simulating |
| `ag.lp_linear.*` | absent — solved analytically each likelihood call | **the default for fitting** |
| `ag.lp_operated.*` | free, but the profile is assumed *already* PSF-convolved | unresolved nuclear emission |
| `ag.lp_snr.*` | set from a target signal-to-noise | simulating data at a chosen S/N |

`ag.lp_basis.Basis` is a fifth entry that is not a shape at all but a *grouping* of
profiles behaving as one component.

Why linear profiles are the default, and what an MGE basis buys you, is
[`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md). Why an
already-convolved profile is the right model for an AGN point source is
[`sky_background_and_operated_profiles`](./sky_background_and_operated_profiles.md).
`ag.lp_linear_operated.*` combines the last two.

## Profiles in a model

A concrete profile has numbers; a model has priors. Wrapping the class (not an instance)
in `af.Model` turns every constructor argument with a numerical default into a prior read
from the configuration (`PyAutoGalaxy:autogalaxy/config/priors/`, see
[`../api/configuration`](../api/configuration.md)):

```python
import autofit as af
import autogalaxy as ag

bulge = af.Model(ag.lp.Sersic)
bulge.sersic_index = af.UniformPrior(lower_limit=0.5, upper_limit=8.0)
bulge.effective_radius = af.UniformPrior(lower_limit=0.01, upper_limit=10.0)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)
model = af.Collection(galaxies=af.Collection(galaxy=galaxy))
```

`autogalaxy_workspace:scripts/guides/profiles/light.py`. `model.info` prints every
parameter and its prior — read it before launching a long fit. To see what the priors
imply before any data is involved, `model.instance_from_prior_medians()` returns a real
profile instance you can evaluate and plot.

## 1D radial profiles

There is no separate 1D API: you build a 2D grid whose coordinates lie along a ray and
evaluate `image_2d_from` on it. `grid.grid_2d_radial_projected_from(centre=..., angle=...)`
produces such a grid aligned with a profile's major axis, and `ag.Grid2DIrregular` lets
you specify radii by hand. 1D plotting is left to matplotlib, deliberately, because the
choices (which centre, which angle, log or linear radii) are scientific ones.
`autogalaxy_workspace:scripts/guides/galaxies.py`.

Note the caveat that guide raises: a decomposed 1D plot evaluates each component along
*its own* major axis, so a genuine 2D misalignment between a bulge and a disc does not
appear in the figure.

## See also

- [`../api/light_profile_catalog`](../api/light_profile_catalog.md) — every profile,
  every argument.
- [`galaxies`](./galaxies.md) — composing profiles into a `Galaxy`.
- [`grids_and_masks`](./grids_and_masks.md) — where profiles are evaluated, and why a
  steep centre needs over-sampling.
- [`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md) — the linear
  flavour and basis expansions.
- [`../api/mass_profile_catalog`](../api/mass_profile_catalog.md) — the mass-side
  counterpart (`ag.mp.*`, `ag.lmp.*`) for stellar-mass and dynamical work.
- [`../stack/autogalaxy`](../stack/autogalaxy.md) — where profiles sit in the library.
