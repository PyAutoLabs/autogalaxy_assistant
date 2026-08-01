---
title: Sky background and operated light profiles
sources:
  - project: PyAutoArray
    paths:
      - autoarray/dataset/dataset_model.py
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/light/operated/
      - autogalaxy/profiles/light/linear_operated/
      - autogalaxy/profiles/light/decorators.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/imaging/features/sky_background/modeling.py
      - scripts/imaging/features/sky_background/simulator.py
      - scripts/imaging/features/operated_light_profile/modeling.py
      - scripts/imaging/features/multi_gaussian_expansion/modeling.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: ca321417a0aa39cd1adba29263cfb52e2c544e8ecc4fc01d86743e02371d70fa
---

# Sky background and operated light profiles

Two model components that are not the galaxy's stellar light but which sit on top of it in
the data: the **sky background** that was never perfectly subtracted, and the **unresolved
nuclear emission** that arrives already convolved with the instrument PSF. Both are
degenerate with real structural parameters if ignored, and both are handled by adding an
explicit component rather than by pre-processing the data.

Sources: `PyAutoArray:autoarray/dataset/dataset_model.py` and
`PyAutoGalaxy:autogalaxy/profiles/light/operated/`. Worked examples:
`autogalaxy_workspace:scripts/imaging/features/sky_background/modeling.py` and
`.../operated_light_profile/modeling.py`.

## The sky background

Every image contains light that is not the galaxy: sky glow, zodiacal light, and the
unresolved integrated emission of the faint field. Data reduction subtracts an estimate of
it, but that estimate is never exact, and the residual — a roughly constant offset across
the cutout — is **degenerate with the faint outskirts of a galaxy's light profile**.

The direction of the bias is predictable and it lands on the parameters most often quoted.
An over-subtracted sky removes flux from the wings, which pulls `effective_radius` down and
`sersic_index` with it; an under-subtracted sky adds a floor the profile tries to explain,
inflating both. Because the wings carry most of the constraint on those two parameters (see
[`light_profiles`](./light_profiles.md)), a fit that *assumes* the subtraction was perfect
also reports error bars that are too small — the sky uncertainty is simply absent from the
posterior.

The fix is to make the sky a free parameter, so every light-profile parameter is
marginalised over it:

```python
import autofit as af
import autogalaxy as ag

bulge = af.Model(ag.lp_linear.Sersic)
disk = af.Model(ag.lp_linear.Exponential)
bulge.centre = disk.centre

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)

dataset_model = af.Model(ag.DatasetModel)
dataset_model.background_sky_level = af.UniformPrior(lower_limit=0.0, upper_limit=5.0)

model = af.Collection(
    galaxies=af.Collection(galaxy=galaxy), dataset_model=dataset_model
)
```

`autogalaxy_workspace:scripts/imaging/features/sky_background/modeling.py`. Three things to
note:

- **The sky is not a galaxy.** `dataset_model` is a sibling of `galaxies` in the top-level
  `af.Collection`, because the sky is a property of the *dataset*, not of any object in it.
  It is read back from `result.instance.dataset_model.background_sky_level`.
- **You must set the prior yourself.** Unlike a light profile, whose priors come from the
  configuration, the plausible range of a sky level depends entirely on the units and
  reduction of the data in front of you. There is no sensible default, so the workspace sets
  it explicitly every time. Look at the median value in a blank corner of the image and
  bracket it.
- **The cost is negligible.** Adding a constant to the model image is free; the likelihood
  evaluation time is unchanged. The only price is one extra dimension.

Fit the sky whenever low-surface-brightness structure matters — outer isophotes, discs,
tidal features, total-flux measurements — or whenever the reduction's sky subtraction is
itself uncertain. A dataset that has *not* had the sky removed is easy to recognise: the
outskirts sit at a positive plateau instead of scattering about zero
(`autogalaxy_workspace:scripts/imaging/features/sky_background/simulator.py` builds one
deliberately).

`ag.DatasetModel` carries two further nuisance parameters — `grid_offset` and
`grid_rotation_angle` — used to absorb small astrometric misregistrations between datasets.
Those belong to multi-dataset fitting; see [`multi_wavelength`](./multi_wavelength.md).

## Operated light profiles

A galaxy with an active nucleus or a very compact nuclear starburst has a component that is
**unresolved**: intrinsically point-like, and seen in the data only as the instrument PSF.

The obvious approach — a very compact Gaussian or Sersic, convolved with the PSF like every
other profile — behaves badly. When the model emission is confined to a fraction of a pixel,
the result of the convolution depends acutely on *which* sub-pixel the centre falls in. The
likelihood surface becomes pitted on the scale of the sub-grid, which is exactly the kind of
structure a non-linear search cannot navigate, and the inferred nuclear flux ends up coupled
to a numerical artefact.

An **operated** profile sidesteps it by declaring that the profile already represents
post-PSF emission, so the fit must not convolve it again:

```python
import autofit as af
import autogalaxy as ag

bulge = af.Model(ag.lp_linear.Sersic)
psf = af.Model(ag.lp_linear_operated.Gaussian)

psf.sigma = af.UniformPrior(lower_limit=0.0, upper_limit=5.0)
bulge.centre = psf.centre

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, psf=psf)
model = af.Collection(galaxies=af.Collection(galaxy=galaxy))
```

`autogalaxy_workspace:scripts/imaging/features/operated_light_profile/modeling.py`. The
component is now fitting the *observed* shape of the point source directly — which is why a
`Gaussian` or `Moffat` is the natural choice: those are the shapes a PSF actually has.

Three families exist: `ag.lp_operated.Gaussian`, `ag.lp_operated.Moffat` and
`ag.lp_operated.Sersic`, each with a linear counterpart in `ag.lp_linear_operated.*`. Prefer
the linear form — a nuclear component's amplitude is exactly the sort of parameter the
inversion should solve, and operated profiles are hard enough to sample that any
simplification helps.

Practical notes:

- **Set the `sigma` prior from your PSF.** The default `UniformPrior(0.0, 5.0)` spans a range
  that is meaningless for most instruments; the true value is typically ~0.1″ or below, set
  by the PSF width, and leaving the prior broad wastes most of the search's effort. The
  workspace flags this as the single most important customisation for these profiles.
- **Tie the centres.** `bulge.centre = psf.centre` states the physical assumption that the
  nucleus sits at the centre of the stellar light, and it removes two dimensions.
- **They are the *fastest* profiles to evaluate**, because the expensive PSF convolution is
  skipped. The extra parameters usually make the overall fit a little slower nonetheless.
- The mechanism is general: an operated profile is simply one excluded from the convolution
  step. The fit objects carry an `operated_only` control over whether such components are
  included in a given image computation.

### The alternative: a compact MGE

A second, often better-behaved way to model unresolved emission is a compact
Multi-Gaussian Expansion — ~10 linear Gaussians sharing a centre and ellipticity, with
`sigma` values log-spaced from 0.01″ up to about twice the pixel scale:

```python
point = ag.model_util.mge_point_model_from(
    pixel_scales=0.1,
    total_gaussians=10,
    centre=(0.0, 0.0),
)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, point=point)
```

`autogalaxy_workspace:scripts/imaging/features/multi_gaussian_expansion/modeling.py`. This
*is* convolved with the PSF in the normal way, but because the basis spans a range of widths
rather than committing to one very small one, it does not sit on the pathological
sub-pixel-sensitive part of the likelihood. N = 4 (a shared centre plus two shared
ellipticity components). Details in
[`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md).

Which to use: an operated profile is the more direct statement of the physics and the faster
evaluation; a compact MGE is generally easier to sample and slots into a model that is
already MGE-based. Both are legitimate; try the MGE first if the fit is misbehaving.

## See also

- [`light_profiles`](./light_profiles.md) — the four profile namespaces, and why the wings
  drive `sersic_index`.
- [`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md) — linear variants and
  the compact-MGE nucleus.
- [`extra_galaxies_and_noise_scaling`](./extra_galaxies_and_noise_scaling.md) — the *other*
  light in the frame that is not your galaxy.
- [`multi_wavelength`](./multi_wavelength.md) — `ag.DatasetModel`'s offset parameters.
- [`../api/datasets`](../api/datasets.md) — the dataset objects these components attach to.
