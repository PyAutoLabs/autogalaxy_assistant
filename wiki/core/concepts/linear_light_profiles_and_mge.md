---
title: Linear light profiles and the Multi-Gaussian Expansion
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/light/linear/
      - autogalaxy/profiles/basis.py
      - autogalaxy/abstract_fit.py
      - autogalaxy/imaging/fit_imaging.py
      - autogalaxy/analysis/model_util.py
    pinned_commit: 13d3023cc312ce3e523598a024cb8430fe6f8ab8
  - project: autogalaxy_workspace
    paths:
      - scripts/imaging/features/linear_light_profiles/modeling.py
      - scripts/imaging/features/multi_gaussian_expansion/modeling.py
      - scripts/imaging/start_here.py
      - scripts/guides/profiles/light.py
      - scripts/guides/results/start_here.py
    pinned_commit: 1f821bad4c243019ee0d8c68740eba0b879b6638
last_updated: 2026-08-04
content_sha256: 45e30fc64927fbb5038baed4f86c537e6ec8ee0480afd40a88bef246c58316e9
---

# Linear light profiles and the Multi-Gaussian Expansion

A **linear light profile** has the same shape as its standard counterpart but its
`intensity` is not a free parameter: it is solved analytically, by linear algebra, at every
likelihood evaluation. A **basis** groups many such profiles into a single component whose
amplitudes are all solved together — which is what makes the Multi-Gaussian Expansion (MGE)
practical.

Sources: `PyAutoGalaxy:autogalaxy/profiles/light/linear/` and
`PyAutoGalaxy:autogalaxy/profiles/basis.py`. Worked examples:
`autogalaxy_workspace:scripts/imaging/features/linear_light_profiles/modeling.py` and
`autogalaxy_workspace:scripts/imaging/features/multi_gaussian_expansion/modeling.py`.

## Why solve intensity instead of sampling it

For a fixed set of shape parameters, the predicted image is **linear** in each component's
`intensity`. The best-fitting amplitudes therefore have a closed-form solution given the
data and noise-map — there is nothing for a non-linear search to explore. Sampling them
anyway costs you twice:

- **One extra dimension per component.** A bulge plus a disc plus an unresolved nucleus is
  three wasted dimensions.
- **A hard degeneracy.** `intensity` correlates strongly with `effective_radius` and
  `sersic_index` (make the profile bigger and fainter, or smaller and brighter, and the
  data barely notices). These curved, narrow ridges are exactly what nested samplers and
  gradient optimizers struggle to map.

Removing them makes the parameter space smaller *and* better conditioned, which is why the
workspace recommends linear profiles as the default for essentially every fit.
`autogalaxy_workspace:scripts/imaging/features/linear_light_profiles/modeling.py`.

The API is the standard profile minus `intensity`:

```python
import autofit as af
import autogalaxy as ag

bulge = af.Model(ag.lp_linear.Sersic)
disk = af.Model(ag.lp_linear.Exponential)
bulge.centre = disk.centre

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)
model = af.Collection(galaxies=af.Collection(galaxy=galaxy))
```

Every profile in `ag.lp.*` has an `ag.lp_linear.*` counterpart, including the multipole
variants (`ag.lp_linear.SersicMultipole`, `ag.lp_linear.GaussianMultipole`) — the multipole
components remain non-linear parameters; only the overall amplitude is solved.

### The cost

The linear solve is not free: the likelihood evaluation is roughly 3–5× slower than for
standard profiles (~0.05 s versus ~0.01 s in the workspace's reference dataset). In
practice the two roughly cancel, because a lower-dimensional and better-conditioned
parameter space converges in fewer evaluations and tolerates fewer live points (the linear
examples drop `n_live` from 100 to 75). The reason to prefer linear profiles is therefore
**reliability**, with run time about a wash.

### The positive-only solver

An unconstrained least-squares solve can return negative amplitudes, which is unphysical:
surface brightness cannot be negative. PyAutoGalaxy uses a bespoke non-negative solver,
optimised to be as fast as a positive-negative one, so every solved intensity is positive.
This matters most for a basis, where an unconstrained solve produces "ringing" — adjacent
components alternating between large positive and negative amplitudes — a mathematically
valid fit that is physically nonsense.

The one exception is a shapelet basis, which *requires* signed amplitudes to work at all;
see [`shapelets`](./shapelets.md).

## Basis expansions

`ag.lp_basis.Basis` groups a `profile_list` into one component that behaves, everywhere
downstream, like a single profile:

```python
basis = ag.lp_basis.Basis(profile_list=[ag.lp_linear.Gaussian(sigma=0.5)])
```

When the constituents are linear, **all** their amplitudes are solved in one combined
inversion. So a basis of 30 Gaussians contributes 30 amplitudes to the fit while adding
only the shared geometric parameters to the search. That single fact is what makes the MGE
work. `autogalaxy_workspace:scripts/guides/profiles/light.py`.

## The Multi-Gaussian Expansion

An MGE decomposes a galaxy's light into a superposition of ~15–100 concentric Gaussians.
The construction that makes it a *low-dimensional* model rather than a high-dimensional one
is:

- **Shared `centre`** across every Gaussian (2 free parameters).
- **Shared `ell_comps`** across every Gaussian (2 free parameters).
- **Fixed `sigma` values**, spaced logarithmically from a tenth of the pixel scale out to the
  mask radius (0 free parameters). The lower end is set by `mge_model_from`'s `sigma_min`
  (default `1e-4`, reproducing the historical ladder); anchoring it to the pixel scale stops
  the basis spending Gaussians on scales the data cannot resolve.
- **Amplitudes solved by the inversion** (0 free parameters).

```python
import numpy as np
import autofit as af
import autogalaxy as ag

total_gaussians = 30
gaussian_per_basis = 2

mask_radius = 3.0
log10_sigma_list = np.linspace(
    np.log10(dataset.pixel_scales[0] / 10.0), np.log10(mask_radius), total_gaussians
)

centre_0 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)
centre_1 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)

bulge_gaussian_list = []

for j in range(gaussian_per_basis):
    gaussian_list = af.Collection(
        af.Model(ag.lp_linear.Gaussian) for _ in range(total_gaussians)
    )

    for i, gaussian in enumerate(gaussian_list):
        gaussian.centre.centre_0 = centre_0
        gaussian.centre.centre_1 = centre_1
        gaussian.ell_comps = gaussian_list[0].ell_comps
        gaussian.sigma = 10 ** log10_sigma_list[i]

    bulge_gaussian_list += gaussian_list

bulge = af.Model(ag.lp_basis.Basis, profile_list=bulge_gaussian_list)
```

`autogalaxy_workspace:scripts/imaging/features/multi_gaussian_expansion/modeling.py`. Two
groups of 30 Gaussians (`gaussian_per_basis = 2`) with independent ellipticities gives
**N = 6** free parameters in total — fewer than a single elliptical Sersic (N = 7), for a
model that is far more flexible.

### Why it fits real galaxies better

A single Sersic imposes strict self-similarity: one ellipticity, one position angle and one
radial shape at all radii. Real galaxies routinely violate this — isophotal twists,
ellipticity that varies with radius, a bulge and disc with different flattening. Those
violations show up as structured residuals that no amount of tweaking a Sersic will remove.

Because each Gaussian in an MGE has its own amplitude but a shared geometry, and two or
more groups can carry different ellipticities, the sum can reproduce a radially varying
profile shape and (with multiple groups) a radially varying flattening. Critically, none of
the free parameters *scales* the galaxy — there is no `effective_radius` and no
`sersic_index` — so the worst degeneracies of a parametric fit simply do not exist, and the
search converges quickly and reliably.

### What you give up

Interpretability. "Sersic index 4.1, effective radius 0.62″" is a sentence an astronomer
understands; a list of 60 Gaussian amplitudes is not. If your science *is* the Sersic index
or the bulge-to-total ratio, fit the parametric model — possibly after using an MGE to
check that a parametric form can describe the galaxy at all. If your science needs an
accurate light model (subtracting the galaxy, measuring total flux, colour gradients,
low-surface-brightness structure), the MGE is usually the better instrument.

Cost: evaluating and PSF-convolving 60 Gaussians takes ~0.5 s per likelihood versus ~0.01 s
for a Sersic. The simpler parameter space normally more than repays it.

### The helper

The composition above is verbose, so the library ships it as one call:

```python
bulge = ag.model_util.mge_model_from(
    mask_radius=mask_radius, total_gaussians=20, centre_prior_is_uniform=True
)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)
```

`autogalaxy_workspace:scripts/imaging/start_here.py`. It is the default galaxy model in
every `start_here.py`. Useful keywords (`ag.model_util.mge_model_from`):
`gaussian_per_basis` (independent ellipticity groups), `centre_fixed` (pin the centre —
used for companions), `use_spherical`, and the prior-shape controls
`centre_prior_is_uniform` / `ell_comps_prior_is_uniform`. Note that `mask_radius` sets the
largest Gaussian `sigma`, so it must match the mask you actually applied — another reason
the workspace keeps `mask_radius` in a variable
([`grids_and_masks`](./grids_and_masks.md)).

### A compact MGE for an unresolved nucleus

The same machinery models a point-like central component (AGN, nuclear starburst) if the
`sigma` values are capped near the pixel scale instead of the mask radius:

```python
point = ag.model_util.mge_point_model_from(
    pixel_scales=0.1,
    total_gaussians=10,
    centre=(0.0, 0.0),
)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, point=point)
```

`autogalaxy_workspace:scripts/imaging/features/multi_gaussian_expansion/modeling.py`. Ten
Gaussians with `sigma` log-spaced from `sigma_min` (default 0.01″) to twice the pixel scale, sharing one centre
and ellipticity: N = 4. This is one of two ways to model unresolved emission — the other,
an already-PSF-convolved profile, is in
[`sky_background_and_operated_profiles`](./sky_background_and_operated_profiles.md).

## Reading intensities out of a fit

This is the one place linear profiles complicate life. Because `intensity` is not a model
parameter, **it is not in `samples.csv`**, and a raw `Samples` instance reports it as its
default `1.0`. The solved values only exist once the inversion has been performed against a
dataset.

Three routes, in order of convenience:

```python
# 1. The result object has already performed the inversion.
galaxies = result.max_log_likelihood_galaxies
print(galaxies[0].bulge.intensity)

# 2. The fit object, likewise, plus a per-profile dictionary.
fit = result.max_log_likelihood_fit
print(fit.linear_light_profile_intensity_dict[fit.galaxies[0].bulge])

# 3. For any other posterior sample, rebuild a fit from that instance.
instance = result.samples.max_log_likelihood()
fit = ag.FitImaging(dataset=dataset, galaxies=instance.galaxies)
galaxies = fit.galaxies_linear_light_profiles_to_light_profiles
print(galaxies[0].bulge.intensity)
```

`autogalaxy_workspace:scripts/guides/results/start_here.py` and
`autogalaxy_workspace:scripts/imaging/features/linear_light_profiles/modeling.py`. Route 3
is the one to use for **uncertainties**: draw many samples from the posterior, rebuild the
fit for each, and take the spread of the solved intensities — see
[`samples_and_posteriors`](./samples_and_posteriors.md).

`fit.galaxies_linear_light_profiles_to_light_profiles` (and the generic
`fit.model_obj_linear_light_profiles_to_light_profiles`) returns galaxies in which every
linear profile has been replaced by an ordinary one carrying its solved `intensity`. You
need this for plotting too: a linear profile has no `intensity`, so it cannot produce an
image on its own.

## Under the hood

The solve happens inside an `Inversion`, whose `linear_obj_list` holds one
`LightProfileLinearObjFuncList` per linear component (a `Basis` counts as one, with all its
constituents inside). The same object handles a pixelised reconstruction via a `Mapper`, so
a hybrid model — a linear Sersic bulge plus a pixelisation — solves both in a **single**
combined inversion, which is precisely what removes the brightness degeneracy between them.
`autogalaxy_workspace:scripts/imaging/features/linear_light_profiles/modeling.py` and
[`inversions_and_pixelizations`](./inversions_and_pixelizations.md).

A `Basis` can also carry a `regularization` term penalising non-smooth amplitude solutions.
This is a **research-only** feature: the positive-only solver already prevents the ringing
that regularisation was introduced to suppress, and no production analysis uses it. Do not
add it to a science fit without a specific reason.

## See also

- [`light_profiles`](./light_profiles.md) — the shapes and the four namespaces.
- [`shapelets`](./shapelets.md) — the other basis, and why it needs a signed solver.
- [`inversions_and_pixelizations`](./inversions_and_pixelizations.md) — the same linear
  algebra applied to a free-form mesh.
- [`samples_and_posteriors`](./samples_and_posteriors.md) — errors on a solved intensity.
- [`../api/light_profile_catalog`](../api/light_profile_catalog.md) — the full menu.
- [`../stack/autoarray`](../stack/autoarray.md) — where the inversion linear algebra lives.
