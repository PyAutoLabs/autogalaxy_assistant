---
title: Light profile catalogue
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/light/standard/
      - autogalaxy/profiles/light/linear/
      - autogalaxy/profiles/light/operated/
      - autogalaxy/profiles/light/linear_operated/
      - autogalaxy/profiles/light/snr/
      - autogalaxy/profiles/basis.py
      - autogalaxy/analysis/model_util.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/profiles/light.py
      - scripts/imaging/modeling.py
      - scripts/imaging/features/linear_light_profiles/modeling.py
      - scripts/imaging/features/multi_gaussian_expansion/modeling.py
      - scripts/imaging/features/shapelets/modeling.py
      - scripts/imaging/features/operated_light_profile/modeling.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 76631ba282e12d561599be6da2c1decba0f99b3b435d52f1eedaecf82d10b341
---

# Light profile catalogue

A light profile is an analytic surface-brightness law: give it a `Grid2D` and it returns the
galaxy's image. Every profile in this page implements `image_2d_from(grid=...)`, and every one
can be wrapped in `af.Model(...)` and fitted.

Five namespaces, one shape family each time:

| Namespace | `intensity` | Use it for |
|---|---|---|
| `ag.lp` | free model parameter | plotting, simulating, and any fit where you want the luminosity in the posterior |
| `ag.lp_linear` | solved analytically during the fit | **the default for model-fitting** |
| `ag.lp_operated` | free, but the profile is already PSF-convolved | unresolved nuclear emission (an AGN point source) |
| `ag.lp_linear_operated` | solved analytically, already PSF-convolved | the same, inside a linear model |
| `ag.lp_snr` | replaced by `signal_to_noise_ratio` | simulating data at a chosen S/N |

The single-page tour with runnable code for every family is
`autogalaxy_workspace:scripts/guides/profiles/light.py`. Concept page:
[`../concepts/light_profiles`](../concepts/light_profiles.md).

Every entry below was enumerated from the installed stack
(`sorted(dir(ag.lp))` and friends), not from memory.

## Sersic family — `ag.lp`

The workhorses. `sersic_index` sets how centrally concentrated the light is: `n ≈ 1` is an
exponential disk, `n ≈ 4` a de Vaucouleurs spheroid, and leaving it free is how a fit
distinguishes the two.

| Class | Parameters | Notes |
|---|---|---|
| `Sersic` | `centre`, `ell_comps`, `intensity`, `effective_radius`, `sersic_index` | the general case |
| `SersicSph` | `centre`, `intensity`, `effective_radius`, `sersic_index` | circular; fewer parameters, faster |
| `SersicCore` | `centre`, `ell_comps`, `effective_radius`, `sersic_index`, `radius_break`, `intensity`, `gamma`, `alpha` | flattens to a finite core inside `radius_break` |
| `SersicCoreSph` | as above without `ell_comps` | circular cored Sersic |
| `Exponential` | `centre`, `ell_comps`, `intensity`, `effective_radius` | Sersic with `n = 1` fixed — the disk |
| `ExponentialSph` | `centre`, `intensity`, `effective_radius` | circular exponential |
| `ExponentialCore` | `centre`, `ell_comps`, `effective_radius`, `radius_break`, `intensity`, `gamma`, `alpha` | cored exponential |
| `ExponentialCoreSph` | as above without `ell_comps` | circular cored exponential |
| `DevVaucouleurs` | `centre`, `ell_comps`, `intensity`, `effective_radius` | Sersic with `n = 4` fixed — the bulge |
| `DevVaucouleursSph` | `centre`, `intensity`, `effective_radius` | circular de Vaucouleurs |

Source: `PyAutoGalaxy:autogalaxy/profiles/light/standard/`.

Ellipticity is always parameterised by `ell_comps`, never by an axis-ratio/position-angle pair,
because a periodic angle creates a boundary pathology for a non-linear search. Convert with
`ag.convert.ell_comps_from(axis_ratio=0.9, angle=45.0)` and back with
`ag.convert.axis_ratio_and_angle_from(...)`.

## Gaussian, Moffat and the rest — `ag.lp`

| Class | Parameters | Notes |
|---|---|---|
| `Gaussian` | `centre`, `ell_comps`, `intensity`, `sigma` | the MGE building block |
| `GaussianSph` | `centre`, `intensity`, `sigma` | circular Gaussian |
| `Moffat` | `centre`, `ell_comps`, `intensity`, `alpha`, `beta` | Moffat / King-like wings |
| `MoffatSph` | `centre`, `intensity`, `alpha`, `beta` | circular Moffat |
| `Chameleon` | `centre`, `ell_comps`, `intensity`, `core_radius_0`, `core_radius_1` | difference of two cored isothermal terms |
| `ChameleonSph` | `centre`, `intensity`, `core_radius_0`, `core_radius_1` | circular Chameleon |
| `ElsonFreeFall` | `centre`, `ell_comps`, `intensity`, `effective_radius`, `eta` | EFF profile, used for star clusters |
| `ElsonFreeFallSph` | `centre`, `intensity`, `effective_radius`, `eta` | circular EFF |

Source: `PyAutoGalaxy:autogalaxy/profiles/light/standard/`.

## Multipole profiles — `ag.lp`

Isophotes are not perfectly elliptical. A multipole term adds an `m = 3` (lopsided) or `m = 4`
(boxy / discy) Fourier perturbation to the eccentric radius, which is how you fit the same
deviations that isophote fitting measures non-parametrically.

| Class | Parameters |
|---|---|
| `SersicMultipole` | `centre`, `ell_comps`, `intensity`, `effective_radius`, `sersic_index`, `multipole_3_comps`, `multipole_4_comps` |
| `GaussianMultipole` | `centre`, `ell_comps`, `intensity`, `sigma`, `multipole_3_comps`, `multipole_4_comps` |

Both have `ag.lp_linear` counterparts. Build the components with
`ag.convert.multipole_comps_from(...)`. The non-parametric alternative is
[`ellipse`](./ellipse.md); concept page
[`../concepts/ellipse_fitting_and_multipoles`](../concepts/ellipse_fitting_and_multipoles.md).

## Shapelets — `ag.lp`

Orthonormal basis functions indexed by order. A single shapelet is rarely useful; you sum many
of them in a `Basis` to fit clumpy, asymmetric, spiral or merging structure that no smooth
profile captures.

| Class | Parameters |
|---|---|
| `ShapeletCartesian` | `n_y`, `n_x`, `centre`, `ell_comps`, `intensity`, `beta` |
| `ShapeletCartesianSph` | `n_y`, `n_x`, `centre`, `intensity`, `beta` |
| `ShapeletPolar` | `n`, `m`, `centre`, `ell_comps`, `intensity`, `beta` |
| `ShapeletPolarSph` | `n`, `m`, `centre`, `intensity`, `beta` |
| `ShapeletExponential` | `n`, `m`, `centre`, `ell_comps`, `intensity`, `beta` |
| `ShapeletExponentialSph` | `n`, `m`, `centre`, `intensity`, `beta` |

`beta` is the characteristic scale of the expansion. Source:
`PyAutoGalaxy:autogalaxy/profiles/light/standard/`; workflow:
`autogalaxy_workspace:scripts/imaging/features/shapelets/modeling.py`. Concept page:
[`../concepts/shapelets`](../concepts/shapelets.md).

## Linear light profiles — `ag.lp_linear`

Same shapes, but `intensity` is removed from the parameter vector and solved for analytically
(by a linear inversion) at every likelihood evaluation. You lose nothing in expressiveness and
gain a dimension per profile, which is why every `modeling.py` example in the workspace uses
them:

```python
import autofit as af
import autogalaxy as ag

bulge = af.Model(ag.lp_linear.Sersic)
disk = af.Model(ag.lp_linear.Exponential)
bulge.centre = disk.centre

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py`, which composes exactly this
N=11 bulge-plus-disk model.

Present in `ag.lp_linear`: `Sersic`, `SersicSph`, `SersicCore`, `SersicCoreSph`,
`SersicMultipole`, `Exponential`, `ExponentialSph`, `ExponentialCore`, `ExponentialCoreSph`,
`DevVaucouleurs`, `DevVaucouleursSph`, `Gaussian`, `GaussianSph`, `GaussianMultipole`,
`Moffat`, `MoffatSph`, and all six shapelets.

**Not** present: `Chameleon` / `ChameleonSph` / `ElsonFreeFall` / `ElsonFreeFallSph` have no
linear counterparts — use `ag.lp` for those. Source:
`PyAutoGalaxy:autogalaxy/profiles/light/linear/`; concept page
[`../concepts/linear_light_profiles_and_mge`](../concepts/linear_light_profiles_and_mge.md).

After the fit, the solved intensities are recovered from the result via
`result.max_log_likelihood_fit.galaxies_linear_light_profiles_to_light_profiles`, which converts
the linear profiles back into ordinary `ag.lp` instances with their `intensity` filled in
(`autogalaxy_workspace:scripts/guides/results/start_here.py`).

## Basis expansions and MGE — `ag.lp_basis`

`ag.lp_basis.Basis(profile_list=[...])` sums many profiles into one composite light model. With
a series of concentric Gaussians of increasing `sigma` this is the **Multi-Gaussian Expansion** —
the workspace's recommended starting model, because it captures a real galaxy's morphology far
better than one Sersic while staying fast to evaluate.

```python
basis = ag.lp_basis.Basis(profile_list=[ag.lp_linear.Gaussian(sigma=0.5)])
```

Composing 20–30 Gaussians by hand is verbose, so the library ships a helper that builds the
whole `af.Model` for you:

```python
bulge = ag.model_util.mge_model_from(
    mask_radius=mask_radius, total_gaussians=20, centre_prior_is_uniform=True
)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)
```

Adapted from `autogalaxy_workspace:scripts/imaging/start_here.py`. `mge_model_from` takes
`mask_radius`, `total_gaussians`, `gaussian_per_basis`, `centre_prior_is_uniform`, `centre`,
`centre_fixed`, `centre_per_basis`, `centre_sigma`, `ell_comps_prior_is_uniform`,
`ell_comps_uniform_width`, `ell_comps_sigma` and `use_spherical`; it spaces the Gaussian widths
logarithmically out to `mask_radius` and ties their centres and ellipticities together. Source:
`PyAutoGalaxy:autogalaxy/analysis/model_util.py` and
`PyAutoGalaxy:autogalaxy/profiles/basis.py`.

Build a `Basis` from **linear** profiles when fitting: their amplitudes are then all solved
analytically in one inversion, and a 30-Gaussian expansion costs no extra search dimensions.
Plot one with `aplt.subplot_basis_image(basis=basis, grid=grid)`.

## Operated profiles — `ag.lp_operated` / `ag.lp_linear_operated`

An operated profile represents light that has **already** been convolved with the PSF, so the
fit does not convolve it a second time. The use case is an unresolved nuclear point source: its
observed shape *is* the PSF, and modelling it with an ordinary profile would double-blur it.

| Namespace | Classes |
|---|---|
| `ag.lp_operated` | `Sersic`, `Gaussian`, `Moffat` |
| `ag.lp_linear_operated` | `Sersic`, `Gaussian`, `Moffat` |

```python
bulge = af.Model(ag.lp_linear.Sersic)
psf = af.Model(ag.lp_linear_operated.Gaussian)
psf.sigma = af.UniformPrior(lower_limit=0.0, upper_limit=5.0)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, psf=psf)
```

Adapted from `autogalaxy_workspace:scripts/imaging/features/operated_light_profile/modeling.py`.
Sources: `PyAutoGalaxy:autogalaxy/profiles/light/operated/` and
`PyAutoGalaxy:autogalaxy/profiles/light/linear_operated/`. Concept page:
[`../concepts/sky_background_and_operated_profiles`](../concepts/sky_background_and_operated_profiles.md).

## Signal-to-noise profiles — `ag.lp_snr`

For **simulation only**. `intensity` is replaced by `signal_to_noise_ratio`, so you specify the
S/N you want the simulated galaxy to have and the library scales the brightness to match — far
more useful than guessing an intensity in instrument units.

Available: `Sersic`, `SersicSph`, `SersicCore`, `Exponential`, `ExponentialSph`,
`DevVaucouleurs`, `DevVaucouleursSph`, `Gaussian`, `GaussianSph`, `Chameleon`, `ChameleonSph`,
`ElsonFreeFall`, `ElsonFreeFallSph`. Source:
`PyAutoGalaxy:autogalaxy/profiles/light/snr/`; `ag.Galaxy.set_snr_of_snr_light_profiles` is what
applies the scaling.

## Picking a model at a glance

| Science goal | Model |
|---|---|
| First fit of almost any galaxy | MGE via `ag.model_util.mge_model_from(...)` |
| Bulge-to-total light ratio | `ag.lp_linear.Sersic` bulge + `ag.lp_linear.Exponential` disk |
| Sersic index of an early-type | `ag.lp_linear.Sersic` alone, `sersic_index` free |
| Fix the bulge to de Vaucouleurs | `ag.lp_linear.DevVaucouleurs` |
| Boxy / discy or lopsided isophotes | `ag.lp_linear.SersicMultipole`, or [`ellipse`](./ellipse.md) |
| Clumpy, spiral or merging structure | a `Basis` of `ag.lp_linear.ShapeletPolar` |
| Nothing analytic fits it | a pixelisation — see [`../concepts/inversions_and_pixelizations`](../concepts/inversions_and_pixelizations.md) |
| Unresolved nuclear source | `ag.lp_linear_operated.Gaussian` |
| Simulating at a target S/N | `ag.lp_snr.Sersic` |

## See also

- [`../concepts/light_profiles`](../concepts/light_profiles.md) — what these parameters mean
  physically.
- [`../concepts/linear_light_profiles_and_mge`](../concepts/linear_light_profiles_and_mge.md) —
  why the linear solve is free.
- [`../concepts/shapelets`](../concepts/shapelets.md) — the shapelet basis.
- [`analysis_objects`](./analysis_objects.md) — composing these into a fittable model.
- [`mass_profile_catalog`](./mass_profile_catalog.md) — the `ag.mp` / `ag.lmp` counterparts.
- [`configuration`](./configuration.md) — where each profile's default priors come from.
