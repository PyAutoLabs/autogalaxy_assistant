---
title: Mass profile catalogue
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/mass/total/
      - autogalaxy/profiles/mass/dark/
      - autogalaxy/profiles/mass/stellar/
      - autogalaxy/profiles/mass/sheets/
      - autogalaxy/profiles/mass/point/
      - autogalaxy/profiles/light_and_mass_profiles.py
      - autogalaxy/profiles/light_linear_and_mass_profiles.py
      - autogalaxy/profiles/scaling_relations.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/galaxies.py
      - scripts/guides/data_structures.py
      - scripts/guides/units/cosmology.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: d18005775f5820aac4d52d5b2fb24ab742ed0b68c3ff811cacffa6c6cee24aee
---

# Mass profile catalogue

PyAutoGalaxy owns the mass-profile library, and `ag.mp.*` is where it lives. In a
galaxy-structure context you reach for these when the science needs a **mass distribution**
rather than a surface-brightness distribution: a dynamical mass model, a decomposed
stellar-plus-dark decomposition, a mass-to-light ratio, or a projected mass within an aperture
to compare against a dynamical or scaling-relation measurement.

Every mass profile implements the same three field methods, evaluated on a `Grid2D`:

```python
import autogalaxy as ag

mass = ag.mp.Isothermal(centre=(0.0, 0.0), ell_comps=(0.1, 0.05))

convergence = mass.convergence_2d_from(grid=grid)     # dimensionless surface density
potential = mass.potential_2d_from(grid=grid)          # 2D projected potential
deflections = mass.deflections_yx_2d_from(grid=grid)   # (y, x) deflection field
```

Plus the integrated quantities that turn a profile into a measurement:
`mass_angular_within_circle_from(...)`, `density_between_circular_annuli(...)`,
`average_convergence_of_1_radius`, `shear_yx_2d_from(...)`. `ag.Galaxy` exposes the same three
field methods summed over all of its mass components, alongside
`luminosity_within_circle_from(...)` for the light — which is how you form a mass-to-light ratio
from a single fitted galaxy (`autogalaxy_workspace:scripts/guides/galaxies.py`). The returned
objects are the stack's `Array2D` / `VectorYX2D` structures with their `slim` and `native`
views — `autogalaxy_workspace:scripts/guides/data_structures.py` evaluates
`galaxy.deflections_yx_2d_from(grid=dataset.grid)` and walks through both.

Converting any of this into solar masses or kiloparsecs needs a cosmology and a redshift:
`autogalaxy_workspace:scripts/guides/units/cosmology.py` is the worked example, and
`ag.cosmo.Planck15()` the usual starting point.

**Naming note.** The total-mass and point-mass families below inherit their normalisation
keyword from the deflection formalism these profiles were originally written for. This
galaxy-structure catalogue names the classes and their remaining parameters and points you at
the source module for that one keyword rather than restating it — get it exactly with
`inspect.signature(ag.mp.Isothermal)` or by reading the cited file. Nothing else in the
catalogue is abbreviated.

## Total mass — `ag.mp`

One profile for the whole mass distribution, luminous plus dark, with no attempt to separate
them. This is the right choice when the measurement you want is the *total* projected mass or
the logarithmic slope of the total density.

| Class | Parameters (besides the normalisation radius) | Notes |
|---|---|---|
| `Isothermal` | `centre`, `ell_comps` | singular isothermal ellipsoid; density ∝ r⁻² |
| `IsothermalSph` | `centre` | circular isothermal sphere |
| `IsothermalCore` | `centre`, `ell_comps`, `core_radius` | isothermal with a finite core |
| `IsothermalCoreSph` | `centre`, `core_radius` | circular cored isothermal |
| `PowerLaw` | `centre`, `ell_comps`, `slope` | free density slope; `slope = 2` recovers `Isothermal` |
| `PowerLawSph` | `centre`, `slope` | circular power law |
| `PowerLawCore` | `centre`, `ell_comps`, `slope`, `core_radius` | cored power law |
| `PowerLawCoreSph` | `centre`, `slope`, `core_radius` | circular cored power law |
| `PowerLawBroken` | `centre`, `ell_comps`, `inner_slope`, `outer_slope`, `break_radius` | two slopes joined at a break |
| `PowerLawBrokenSph` | `centre`, `inner_slope`, `outer_slope`, `break_radius` | circular broken power law |
| `PowerLawMultipole` | `m`, `centre`, `slope`, `multipole_comps` | adds an `m = 3` or `m = 4` angular harmonic |
| `PowerLawIntermediate` | `centre`, `ell_comps`, `slope` | intermediate-axis convention variant |

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/total/`.

### Pseudo-isothermal profiles — the dynamical entry point

The dual pseudo-isothermal elliptical (dPIE) family is parameterised by a **velocity
dispersion** and two physical radii, which makes it the natural bridge between a photometric
mass model and a dynamical one.

| Class | Parameters |
|---|---|
| `dPIEMass` | `centre`, `ellipticity`, `angle_pos`, `sigma`, `r_core`, `r_cut`, `redshift_object`, `redshift_source`, `H0`, `Om0` |
| `dPIEMassSph` | `centre`, `sigma`, `r_core`, `r_cut`, `redshift_object`, `redshift_source`, `H0`, `Om0` |
| `dPIEMassB0` / `dPIEMassB0Sph` | `centre`, `ell_comps`, `ra`, `rs`, `b0` |
| `dPIEPotential` / `dPIEPotentialSph` | `centre`, `ell_comps`, `ra`, `rs`, `b0` |
| `PIEMass` | `centre`, `ell_comps`, `ra`, `b0` |

`sigma` is the velocity dispersion in km/s; `r_core` and `r_cut` are the inner core and outer
truncation radii. The `B0` variants take a dimensionless normalisation instead. Sources:
`PyAutoGalaxy:autogalaxy/profiles/mass/total/dual_pseudo_isothermal_mass.py` and
`PyAutoGalaxy:autogalaxy/profiles/mass/total/dual_pseudo_isothermal_potential.py`.

## Dark matter — `ag.mp`

The NFW family and its variants. `kappa_s` is the dimensionless normalisation and
`scale_radius` the NFW scale radius; the MCR variants replace both with a halo mass and a
mass–concentration relation, so you fit a physically interpretable mass instead.

| Class | Parameters | Notes |
|---|---|---|
| `NFW` | `centre`, `ell_comps`, `kappa_s`, `scale_radius` | elliptical NFW |
| `NFWSph` | `centre`, `kappa_s`, `scale_radius` | spherical NFW |
| `NFWTruncatedSph` | `centre`, `kappa_s`, `scale_radius`, `truncation_radius` | truncated at a finite radius |
| `NFWMCRDuffySph` | `centre`, `mass_at_200`, `redshift_object`, `redshift_source` | Duffy mass–concentration relation |
| `NFWMCRLudlow` / `NFWMCRLudlowSph` | `centre`, (`ell_comps`,) `mass_at_200`, `redshift_object`, `redshift_source` | Ludlow (2016) relation |
| `NFWMCRScatterLudlow` / `NFWMCRScatterLudlowSph` | as above `+ scatter_sigma` | Ludlow relation with scatter |
| `NFWTruncatedMCRDuffySph` / `NFWTruncatedMCRLudlowSph` / `NFWTruncatedMCRScatterLudlowSph` | as above | truncated MCR variants |
| `NFWVirialMassConcSph` | `centre`, `virial_mass`, `concentration`, `virial_overdens`, `redshift_object`, `redshift_source` | parameterised by virial mass and concentration |
| `gNFW` / `gNFWSph` | `centre`, (`ell_comps`,) `kappa_s`, `inner_slope`, `scale_radius` | generalised NFW with a free inner slope |
| `gNFWMCRLudlow` | `centre`, `ell_comps`, `mass_at_200`, `redshift_object`, `redshift_source`, `inner_slope` | gNFW on the Ludlow relation |
| `gNFWVirialMassConcSph` | `centre`, `log10m_vir`, `c_2`, `overdens`, `redshift_object`, `redshift_source`, `inner_slope` | gNFW by virial mass |
| `gNFWVirialMassgNFWConcSph` | as above | gNFW-specific concentration definition |
| `cNFW` / `cNFWSph` | `centre`, (`ell_comps`,) `kappa_s`, `scale_radius`, `core_radius` | cored NFW |
| `cNFWMCRLudlow` / `cNFWMCRLudlowSph` / `cNFWMCRScatterLudlow` / `cNFWMCRScatterLudlowSph` | MCR forms of `cNFW` | |
| `KaplinghatCoredNFWSph` | `centre`, `kappa_s`, `scale_radius`, `sigma_over_m`, `t_age`, `interaction_radius` | self-interacting dark matter core |
| `KaplinghatCoredNFWMCRLudlowSph` | `centre`, `mass_at_200`, `sigma_over_m`, `t_age`, `redshift_object`, `redshift_source` | MCR form of the above |

Source: `PyAutoGalaxy:autogalaxy/profiles/mass/dark/`. `redshift_object` and `redshift_source`
appear because a mass–concentration relation needs distances; see
[`../concepts/cosmology_and_units`](../concepts/cosmology_and_units.md).

## Stellar mass — `ag.mp`

Each of these is a light profile's shape converted into a mass distribution by a
`mass_to_light_ratio`. They are how you turn a fitted surface-brightness decomposition into a
stellar-mass model — and, paired with an NFW halo, how you decompose a galaxy's mass into stars
and dark matter.

| Class | Parameters |
|---|---|
| `Sersic` | `centre`, `ell_comps`, `intensity`, `effective_radius`, `sersic_index`, `mass_to_light_ratio` |
| `SersicSph` | `centre`, `intensity`, `effective_radius`, `sersic_index`, `mass_to_light_ratio` |
| `SersicCore` / `SersicCoreSph` | as above `+ radius_break`, `gamma`, `alpha` |
| `SersicGradient` / `SersicGradientSph` | as `Sersic` `+ mass_to_light_gradient` |
| `Exponential` / `ExponentialSph` | `centre`, (`ell_comps`,) `intensity`, `effective_radius`, `mass_to_light_ratio` |
| `DevVaucouleurs` / `DevVaucouleursSph` | same shape as `Exponential`, with `n = 4` |
| `Gaussian` | `centre`, `ell_comps`, `intensity`, `sigma`, `mass_to_light_ratio` |
| `GaussianGradient` | `centre`, `ell_comps`, `intensity`, `sigma`, `mass_to_light_ratio_base`, `mass_to_light_gradient`, `mass_to_light_radius` |
| `Chameleon` / `ChameleonSph` | `centre`, (`ell_comps`,) `intensity`, `core_radius_0`, `core_radius_1`, `mass_to_light_ratio` |

The `Gradient` variants let the mass-to-light ratio vary with radius as a power law — a direct
handle on stellar-population or IMF gradients rather than a single global M/L. Source:
`PyAutoGalaxy:autogalaxy/profiles/mass/stellar/`.

`ag.mp.MGEDecomposer(mass_profile=...)` decomposes an arbitrary mass profile into a
Multi-Gaussian Expansion, the mass-side analogue of the light MGE in
[`light_profile_catalog`](./light_profile_catalog.md).

## Light-and-mass profiles — `ag.lmp` / `ag.lmp_linear`

A light-and-mass profile is one object that is *both*: its light and its mass share a single
geometry (`centre`, `ell_comps`, `effective_radius`, …) and are linked by a
`mass_to_light_ratio`. Composing a galaxy from these rather than from an independent `ag.lp` and
`ag.mp` pair enforces that the stars you see and the stellar mass you infer are the same
distribution.

```python
galaxy = ag.Galaxy(
    redshift=0.5,
    bulge=ag.lmp.Sersic(
        centre=(0.0, 0.0),
        ell_comps=(0.0, 0.05),
        intensity=0.5,
        effective_radius=0.3,
        sersic_index=2.5,
        mass_to_light_ratio=0.05,
    ),
)
```

Adapted from `autogalaxy_workspace:scripts/guides/galaxies.py`.

Available in `ag.lmp`: `Sersic`, `SersicSph`, `SersicCore`, `SersicCoreSph`, `SersicGradient`,
`SersicGradientSph`, `Exponential`, `ExponentialSph`, `ExponentialGradient`,
`ExponentialGradientSph`, `DevVaucouleurs`, `DevVaucouleursSph`, `Gaussian`,
`GaussianGradient`, `Chameleon`, `ChameleonSph`. `ag.lmp_linear` mirrors the set with the light
side's `intensity` solved analytically, minus `Chameleon` / `ChameleonSph`. Sources:
`PyAutoGalaxy:autogalaxy/profiles/light_and_mass_profiles.py` and
`PyAutoGalaxy:autogalaxy/profiles/light_linear_and_mass_profiles.py`.

## Sheets, external terms and point masses — `ag.mp`

| Class | Parameters | Notes |
|---|---|---|
| `MassSheet` | `centre`, `kappa` | uniform convergence sheet |
| `ExternalShear` | `gamma_1`, `gamma_2` | constant background shear |
| `ExternalPotential` | `centre`, `gamma_1`, `gamma_2`, `tau_1`, `tau_2`, `delta_1`, `delta_2` | third-order line-of-sight potential expansion (Powell et al. 2022, Eq. 4): `gamma` reproduces `ExternalShear`, `tau` adds a linear convergence gradient, `delta` a spin-3 term |
| `PointMass` | `centre` (+ the normalisation radius) | ideal point mass |
| `SMBH` | `centre`, `mass`, `redshift_object`, `redshift_source` | supermassive black hole, parameterised by mass in solar masses |
| `SMBHBinary` | `centre`, `separation`, `angle_binary`, `mass`, `mass_ratio`, `redshift_object`, `redshift_source` | binary black hole |

`SMBH` is the entry point for a central black hole on top of a stellar-mass model — the
component a dynamical mass measurement of a galaxy nucleus needs. Sources:
`PyAutoGalaxy:autogalaxy/profiles/mass/sheets/` and
`PyAutoGalaxy:autogalaxy/profiles/mass/point/`.

## Interpolated and relation-tied profiles

- **`ag.mp.InputDeflections`** (`deflections_y`, `deflections_x`, `image_plane_grid`, `mask`,
  `extrapolate`, `Hy`, `Hx`) and **`ag.mp.InputPotential`** wrap a mass field computed
  externally — by a simulation snapshot or another code — as a first-class profile, so it can be
  summed with analytic components and evaluated on any grid. Source:
  `PyAutoGalaxy:autogalaxy/profiles/mass/input/`.
- **`ag.mp.GaussianRandomField`** (`mask`, `power_amplitude`, `power_slope`, `seed`) draws a
  stochastic convergence field with a power-law power spectrum — a way to add unresolved
  small-scale structure rather than another smooth component. Source:
  `PyAutoGalaxy:autogalaxy/profiles/mass/input/gaussian_random_field.py`.
- **`ag.sr.MassLightRelation`**, **`ag.sr.IsothermalMLR`** and **`ag.sr.IsothermalSphMLR`** tie a
  profile's mass normalisation to its luminosity through a scaling relation, so a sample of
  galaxies shares two relation parameters instead of carrying one free mass each. Source:
  `PyAutoGalaxy:autogalaxy/profiles/scaling_relations.py`.

## Picking a mass model at a glance

| Science goal | Model |
|---|---|
| Total projected mass inside an aperture | `ag.mp.Isothermal`, then `mass_angular_within_circle_from(...)` |
| Logarithmic slope of the total density | `ag.mp.PowerLaw`, `slope` free |
| Dynamical comparison via velocity dispersion | `ag.mp.dPIEMass` (or `dPIEMassSph`) |
| Stellar mass from a fitted light model | the matching `ag.mp` stellar profile, or `ag.lmp.*` |
| Stars-plus-dark decomposition | `ag.lmp.Sersic` + `ag.mp.NFWMCRLudlow` |
| Radially varying M/L (population or IMF gradient) | `ag.mp.SersicGradient` |
| Central black hole | `ag.mp.SMBH` on top of a stellar component |
| Mass field from a simulation | `ag.mp.InputDeflections` |
| A sample sharing one mass–light relation | `ag.sr.MassLightRelation` |

## See also

- [`light_profile_catalog`](./light_profile_catalog.md) — the surface-brightness side.
- [`../concepts/galaxies`](../concepts/galaxies.md) — how profiles compose into an `ag.Galaxy`.
- [`../concepts/cosmology_and_units`](../concepts/cosmology_and_units.md) — turning
  dimensionless convergence and arcsecond radii into solar masses and kiloparsecs.
- [`analysis_objects`](./analysis_objects.md) — putting a mass model into a fit.
- [`configuration`](./configuration.md) — the default priors under `config/priors/mass/`.
