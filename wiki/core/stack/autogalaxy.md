---
title: PyAutoGalaxy (autogalaxy)
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/light/
      - autogalaxy/profiles/mass/
      - autogalaxy/profiles/basis.py
      - autogalaxy/galaxy/
      - autogalaxy/ellipse/
      - autogalaxy/imaging/
      - autogalaxy/interferometer/
      - autogalaxy/analysis/
      - autogalaxy/cosmology/
      - autogalaxy/config/
      - pyproject.toml
      - README.md
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
last_updated: 2026-08-01
content_sha256: edcdfaee1873806090b90e1a7537646c94fd2c78e699ffaf3ab447ef3f3bb84d
---

# PyAutoGalaxy — galaxy structure and galaxy modelling

Project: [`PyAutoGalaxy`](https://github.com/PyAutoLabs/PyAutoGalaxy). Imports:

```python
import autogalaxy as ag
import autogalaxy.plot as aplt
```

PyAutoGalaxy is the library this assistant is about: the *galaxy-structure* layer, and
the top of the dependency chain. It answers "what shape is this galaxy's light, and what
model best describes it?" — decomposing a galaxy into bulges, discs, bars and clumps,
measuring its isophotes, and fitting all of it to CCD imaging or interferometer
visibilities.

It defines:

- A catalogue of **light profiles** (Sersic family, Exponential, DevVaucouleurs,
  Gaussian, Moffat, Chameleon, Elson–Free–Fall, Shapelets), in standard, linear,
  operated and signal-to-noise flavours.
- **Basis expansions** — many linear profiles summed into one flexible model, the
  Multi-Gaussian Expansion (MGE) and shapelet bases.
- **`Galaxy` / `Galaxies`** — profiles composed with a redshift, and a collection of
  galaxies whose light blends on the sky.
- **Ellipse fitting** — non-parametric isophote measurement as an alternative to a
  parametric decomposition.
- **Pixelised reconstruction** — a mesh + regularisation fit for galaxies too irregular
  or clumpy for any analytic profile.
- The **`Analysis` classes** that hand a log-likelihood to PyAutoFit, plus fit,
  simulator and plotting objects.

## Light profiles

Live under `autogalaxy/profiles/light/`, in four families:

- **Standard** (`autogalaxy/profiles/light/standard/`) — `ag.lp.Sersic`,
  `ag.lp.Exponential`, `ag.lp.DevVaucouleurs`, `ag.lp.Gaussian`, `ag.lp.Moffat`,
  `ag.lp.SersicCore`, `ag.lp.SersicMultipole`, `ag.lp.ShapeletPolar`, … Each has an
  `image_2d_from(grid=...)` method and a `Sph` spherical variant.
- **Linear** (`autogalaxy/profiles/light/linear/`) — `ag.lp_linear.*`, the same shapes
  but with the `intensity` solved *analytically* during the fit rather than sampled.
  Linear profiles cut search dimensionality without reducing model expressiveness,
  which makes them the right default for most galaxy-light models.
- **Operated** (`autogalaxy/profiles/light/operated/`) — `ag.lp_operated.*`, profiles
  that represent light *already* convolved with the PSF (an unresolved AGN or nuclear
  point source), so the fit does not convolve them again.
- **SNR-scaled** (`autogalaxy/profiles/light/snr/`) — `ag.lp_snr.*`, where the intensity
  is set from a target signal-to-noise instead of a physical value; used when simulating
  data.

## Basis expansions and MGE

A `Basis` sums many (usually linear) profiles into a single flexible light model:

```python
bulge = ag.lp_basis.Basis(profile_list=[ag.lp_linear.Gaussian(sigma=0.5)])
```

With a series of Gaussians of increasing width this is the Multi-Gaussian Expansion —
the standard way to model a galaxy whose light is not well described by one Sersic.
`ag.model_util.mge_model_from(...)` builds a ready-made MGE `af.Model` for a fit, and a
shapelet basis (`ag.lp_linear.ShapeletPolar`, `ag.lp_linear.ShapeletCartesian`) covers
irregular, asymmetric structure. Source: `PyAutoGalaxy:autogalaxy/profiles/basis.py`.

## Mass profiles

`autogalaxy/profiles/mass/` also ships a full mass-profile catalogue (`ag.mp.*`:
Isothermal, PowerLaw, NFW and variants, external shear, mass sheets, point mass,
multipole terms) plus combined light-and-mass profiles (`ag.lmp.*`) whose light and mass
share a geometry. In a galaxy-structure context these are what you reach for when the
science needs a convergence, potential or deflection field — decomposed stellar-plus-dark
mass models, mass-to-light comparisons, dynamical work. Each implements
`convergence_2d_from(grid=...)`, `deflections_yx_2d_from(grid=...)` and
`potential_2d_from(grid=...)`.

## Galaxy and Galaxies

```python
galaxy = ag.Galaxy(
    redshift=0.5,
    bulge=ag.lp.Sersic(
        centre=(0.0, 0.0),
        ell_comps=ag.convert.ell_comps_from(axis_ratio=0.9, angle=45.0),
        intensity=1.0,
        effective_radius=0.8,
        sersic_index=4.0,
    ),
)
galaxies = ag.Galaxies([galaxy])
```

Galaxy attribute names are arbitrary (`bulge`, `disk`, `clump`, …); they become the keys
you address in the model later, e.g. `model.galaxies.galaxy.bulge`. `Galaxies` is the
collection whose summed light is compared to the data — one galaxy for a single-galaxy
fit, several for interacting pairs or a cluster's members. Sources:
`PyAutoGalaxy:autogalaxy/galaxy/galaxy.py` and
`PyAutoGalaxy:autogalaxy/galaxy/galaxies.py`.

## Ellipse fitting

Instead of assuming a parametric form, `ag.Ellipse` fits the isophotes directly: an
ellipse of a given `major_axis` and `ell_comps` is fitted to the data at each radius, so
the returned profile of ellipticity and position angle is measured, not assumed.
`ag.EllipseMultipole` adds angular harmonics for boxy/discy deviations, `ag.FitEllipse`
is the fit object, and `ag.AnalysisEllipse` is the likelihood PyAutoFit maximises.
Source: `PyAutoGalaxy:autogalaxy/ellipse/`.

## Pixelised reconstruction

For a galaxy whose light is too clumpy or asymmetric for any analytic profile, a
pixelisation reconstructs it on an adaptive mesh with a regularisation prior:

```python
pixelization = ag.Pixelization(
    mesh=ag.mesh.RectangularAdaptDensity(shape=(30, 30)),
    regularization=ag.reg.Constant(coefficient=1.0),
)
```

`ag.mesh.*` supplies the mesh (rectangular uniform / adaptive, Delaunay, KNN),
`ag.reg.*` the regularisation scheme, and `ag.image_mesh.*` (Overlay, Hilbert, KMeans)
the rule that places mesh points from the image. The linear algebra itself lives in
autoarray — see [`stack/autoarray`](./autoarray.md).

## Analyses, fits and simulators

- **`ag.AnalysisImaging`** — the log-likelihood for CCD imaging (PSF convolution, mask,
  noise map). `ag.AnalysisInterferometer` is its visibility-plane counterpart, and
  `ag.AnalysisEllipse` the isophote-fitting one. All three are handed to
  `search.fit(model=..., analysis=...)`.
- **`ag.FitImaging`** / **`ag.FitInterferometer`** / **`ag.FitEllipse`** — the fit
  objects a completed search returns (`result.max_log_likelihood_fit`), carrying model
  image, residuals, chi-squared map and log likelihood.
- **`ag.SimulatorImaging`** / **`ag.SimulatorInterferometer`** — turn a `Galaxies` into
  simulated data with a PSF, exposure time and Poisson noise.

Plotting is functional: `aplt.subplot_imaging_dataset`, `aplt.subplot_fit_imaging`,
`aplt.subplot_galaxies`, `aplt.subplot_galaxy_light_profiles`, `aplt.subplot_fit_ellipse`,
`aplt.plot_array`.

## Cosmology

`autogalaxy/cosmology/` exposes an astropy-backed cosmology API (`ag.cosmo.Planck15`,
`ag.cosmo.FlatLambdaCDM`) for redshift → angular diameter distance and the
angular ↔ physical unit conversions a galaxy's `effective_radius` needs to become a
physical size.

## Configuration

`autogalaxy/config/` adds priors-by-class entries to the autonerves system: when you
write `af.Model(ag.lp.Sersic)`, the default prior for each parameter comes from
`autogalaxy/config/priors/`. It also ships `general.yaml`, `notation.yaml`,
`output.yaml`, `latent.yaml` and a `visualize/` directory of plot defaults.

## Dependencies

`autofit`, `autoarray`, `astropy`, `nautilus-sampler`. Optional extras add `numba`,
`pynufft`, `zeus-mcmc`, `getdist`, and — via `autogalaxy[jax]` — `autofit[jax]`
(JAX, jaxlib, jaxnnls, optax) plus `jax_zero_contour`.

## See also

- [`stack/autofit`](./autofit.md) — the model + search machinery around the `Analysis`.
- [`stack/autoarray`](./autoarray.md) — the grids, masks and datasets the profiles are
  evaluated on.
- [`stack/overview`](./overview.md) — the dependency chain in one page.
