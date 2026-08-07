---
title: Inversions and pixelisations — reconstructing clumpy galaxies
sources:
  - project: PyAutoArray
    paths:
      - autoarray/inversion/pixelization.py
      - autoarray/inversion/mesh/
      - autoarray/inversion/regularization/
      - autoarray/inversion/inversion/
      - autoarray/inversion/mappers/
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/profiles/light/linear/
      - autogalaxy/imaging/fit_imaging.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/imaging/features/pixelization/modeling.py
      - scripts/imaging/features/pixelization/fit.py
      - scripts/imaging/features/pixelization/galaxy_reconstruction.py
      - scripts/guides/advanced/over_sampling.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-07
content_sha256: 488dca78b0570e321a64e9edeb0308b6753ce9ed297ad5be22608f6789e70986
---

# Inversions and pixelisations — reconstructing clumpy galaxies

Some galaxies are not describable by any analytic function. Spiral arms, asymmetric
star-forming knots, tidal features, low-surface-brightness substructure: a Sersic fits the
smooth part and leaves structured residuals exactly where the interesting physics is, and
adding more parametric components chases the structure without ever catching it.

A **pixelisation** abandons the analytic form for that component. The galaxy's light is
reconstructed **directly** as a set of free flux values on a mesh, solved by linear algebra
at every likelihood evaluation, with a regularisation prior supplying the only smoothness
assumption. This is a reconstruction of the galaxy's own surface brightness on the sky —
there is no ray-tracing and no second plane involved.

Sources: `PyAutoArray:autoarray/inversion/`. Worked examples:
`autogalaxy_workspace:scripts/imaging/features/pixelization/modeling.py` (the fit) and
`.../fit.py` (the internals).

## Three ingredients

- **Mesh** — how the reconstruction is discretised, and how many free flux values there
  are.
- **Regularisation** — the prior that penalises unsmooth solutions and stops the mesh
  fitting noise.
- **Mapper** — the linear operator connecting image pixels to mesh elements, built for you
  from the mesh and the (over-sampled) data grid.

```python
import autogalaxy as ag

pixelization = ag.Pixelization(
    mesh=ag.mesh.RectangularAdaptDensity(shape=(28, 28)),
    regularization=ag.reg.GaussianKernel(),
)
```

`PyAutoArray:autoarray/inversion/pixelization.py`. The pixelisation is attached to a galaxy
just like a light profile, under a `pixelization` keyword.

## The canonical model — parametric plus pixelised

The recommended use is a **hybrid**: keep an analytic profile for the smooth component and
give the pixelisation only what the profile cannot explain.

```python
import autofit as af
import autogalaxy as ag

mesh_shape = (28, 28)

pixelization = af.Model(
    ag.Pixelization,
    mesh=ag.mesh.RectangularAdaptDensity(shape=mesh_shape),
    regularization=ag.reg.GaussianKernel,
)

galaxy = af.Model(
    ag.Galaxy,
    redshift=0.5,
    bulge=ag.lp_linear.Sersic,
    pixelization=pixelization,
)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))
```

`autogalaxy_workspace:scripts/imaging/features/pixelization/modeling.py`. That is **N = 8**:
six for the linear Sersic's geometry, zero for the mesh, two for the `GaussianKernel`
regularisation. Extra smooth components (`disk=ag.lp_linear.Exponential`) slot in the same
way.

Two details in that snippet matter more than they look:

- **`lp_linear.Sersic`, not `lp.Sersic`.** The bulge's `intensity` is then solved by the
  *same* inversion that solves the mesh fluxes, in one combined linear system. That removes
  the brightness degeneracy between the two components, rather than leaving the search to
  negotiate it. See
  [`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md).
- **`mesh_shape` is fixed, not a free parameter.** JAX needs statically shaped arrays to
  compile the likelihood, so the mesh dimensions are baked in at model composition; a
  rectangular mesh also requires the same count in `y` and `x`. Choosing a different
  resolution means a different model and a different fit.

## Mesh choices

`PyAutoArray:autoarray/inversion/mesh/`:

| Mesh | Character |
|---|---|
| `ag.mesh.RectangularUniform(shape=(N, N))` | uniform grid; simplest, best for debugging and for understanding a fit |
| `ag.mesh.RectangularAdaptDensity(shape=(N, N))` | rectangular grid whose knots adapt to the data's own density — the workspace default |
| `ag.mesh.RectangularAdaptImage(shape=(N, N))` | adapts using an image of the galaxy from an earlier fit |
| `ag.mesh.Delaunay(pixels=N)` | irregular triangulation |
| `ag.mesh.KNearestNeighbor` / `ag.mesh.KNNBarycentric` | k-nearest-neighbour interpolants |

The trade-off is straightforward: more mesh elements means more freedom to capture fine
structure and more freedom to absorb noise, at higher run time and VRAM. The adaptive
families concentrate elements where the signal is, which is how you buy resolution in the
clumpy regions without paying for it in the empty ones.

`ag.image_mesh.*` (`Overlay`, `Hilbert`, `KMeans`) supplies the rule that places mesh points
from the image for meshes that need one.

## Regularisation

Without a prior the inversion has far more degrees of freedom than the data constrains and
will happily reconstruct the noise. Regularisation adds a penalty on differences between
neighbouring mesh values, so the posterior prefers the smoothest reconstruction consistent
with the data. `PyAutoArray:autoarray/inversion/regularization/`:

- **`ag.reg.Constant(coefficient=...)`** — one uniform smoothing strength. The simplest and
  the easiest to reason about.
- **`ag.reg.GaussianKernel(coefficient=..., scale=...)`** — a Gaussian smoothing kernel with
  its own length scale, so the strength and the correlation length are separately
  controlled. Used by the workspace's pixelisation example.
- **`ag.reg.MaternKernel`**, **`ag.reg.ExponentialKernel`** — other kernel families, with
  different tail behaviour.
- **`ag.reg.ConstantSplit`**, **`ag.reg.Adapt`**, **`ag.reg.MaternAdaptKernel`**,
  **`ag.reg.BrightnessZeroth`**, **`ag.reg.Zeroth`** — variants that vary the penalty across
  the mesh or add a term pulling the solution toward zero.

Its coefficient is a **free parameter of the fit**, usually with a broad log-uniform prior:
the data determines how much smoothing it supports. Under-regularise and the reconstruction
grows spurious pixel-scale structure; over-regularise and real clumps are smoothed into the
bulge. Neither failure is subtle in a residual map, which is why you should always look at
one.

## The positive-only solver

Every pixelised reconstruction uses a non-negative solver: a mesh element may only hold
positive flux. Surface brightness cannot be negative, and an unconstrained solve exploits
negative pixels to over-fit the data — producing a formally better likelihood with a
physically meaningless reconstruction. Enforcing non-negativity efficiently needs
non-trivial linear algebra, and the workspace notes that many methods in the literature
omit it and therefore permit those unphysical solutions.
`autogalaxy_workspace:scripts/imaging/features/pixelization/modeling.py`.

## The Bayesian evidence

A pixelised fit cannot be compared on chi-squared alone, because the mesh can always be made
to fit better. The inversion therefore evaluates a **Bayesian evidence** that balances
goodness of fit against the effective complexity the regularised reconstruction actually
used (Suyu et al. 2006, [arXiv:astro-ph/0601493](https://arxiv.org/abs/astro-ph/0601493);
Nightingale et al. 2018, [arXiv:1708.07377](https://arxiv.org/abs/1708.07377)). It is the
figure of merit the search maximises, and its terms are inspectable:

```python
inversion = result.max_log_likelihood_fit.inversion

print(inversion.regularization_term)
print(inversion.log_det_regularization_matrix_term)
print(inversion.log_det_curvature_reg_matrix_term)
```

`autogalaxy_workspace:scripts/imaging/features/pixelization/fit.py`, which also exposes the
matrices themselves (`inversion.curvature_matrix`, `inversion.regularization_matrix`,
`inversion.curvature_reg_matrix`) and `fit.log_evidence`. The log-determinant terms are what
penalise complexity: they grow as the reconstruction uses more effective degrees of freedom,
so a mesh that is finer than the data warrants scores *worse*, not better.

## Inspecting a reconstruction

```python
inversion = result.max_log_likelihood_fit.inversion

print(inversion.linear_obj_list)                              # Mappers + linear profiles
print(inversion.reconstruction)                               # 1D flux per mesh element
print(inversion.mapped_reconstructed_operated_data.native)    # its image-plane contribution
```

`autogalaxy_workspace:scripts/imaging/features/pixelization/fit.py`. In a hybrid fit
`linear_obj_list` contains both a `Mapper` (for the mesh) and a
`LightProfileLinearObjFuncList` (for the linear bulge) — check which index is which before
indexing into it. `mapped_reconstructed_operated_data` is the pixelisation's contribution
*alone*, so it is the right thing to plot when you want to see the clumps without the bulge.

A dedicated diagnostic subplot lives in the shared inversion plot module:

```python
from autoarray.inversion.plot.inversion_plots import subplot_of_mapper

subplot_of_mapper(inversion=inversion, mapper_index=0)
```

For downstream science and for collaborators without the library installed, a fit also
writes the reconstruction — mesh coordinates, reconstructed values and their noise — to a
`.csv` in the run's `image/` folder. Its filename carries a legacy prefix from the shared
inversion machinery; read
`autogalaxy_workspace:scripts/imaging/features/pixelization/galaxy_reconstruction.py` for the
exact name and a loading recipe rather than guessing it.

## Over-sampling and masking

A pixelisation uses its **own** grid, with its own over-sampling keyword:

```python
dataset = dataset.apply_over_sampling(over_sample_size_pixelization=4)
```

The sub-grid here controls how finely each image pixel's fractional mappings onto the mesh
are computed, not how a smooth profile is integrated, so a uniform `4` is a reasonable
default. In a hybrid fit set `over_sample_size_lp` as well, adaptively about the parametric
component's centre. See [`grids_and_masks`](./grids_and_masks.md).

Masking needs more care than for a purely parametric fit. **Hard-removing** pixels inside
the modelled region can create discontinuities in the mesh and generate systematics; the
right treatment for a contaminant is `apply_noise_scaling`, which keeps the pixels but makes
them contribute negligibly. See
[`extra_galaxies_and_noise_scaling`](./extra_galaxies_and_noise_scaling.md).

## Run time, VRAM and hardware

Pixelisations are the most expensive models in the library, and — unusually — the fastest
hardware depends on your data:

- **JAX on a GPU** wins for lower-resolution imaging (`pixel_scales > 0.05`, e.g. Euclid),
  provided the VRAM holds the batch. JAX has no sparse-matrix support, so it works with
  dense matrices.
- **CPU with `numba`** can win at high resolution (`pixel_scales <= 0.03`, e.g. HST/JWST),
  where the linear algebra is dominated by very large sparse matrices whose sparsity the CPU
  implementation exploits, especially with many cores.

The workspace's recommendation is to benchmark both for your own dataset rather than assume.
`autogalaxy_workspace:scripts/imaging/features/pixelization/modeling.py`.

VRAM is the usual failure mode on a GPU, and it scales with mesh size and batch size (~0.05
GB per batched likelihood for 400 mesh elements). Lower `n_batch` when memory is tight, and
check before committing to a long run:

```python
analysis.print_vram_use(model=model, batch_size=search.batch_size)
```

## When to use one — and when not to

Use a pixelisation when the morphology is genuinely irregular and the morphology is the
science: clumpy star formation, spiral structure, tidal features, faint asymmetric
substructure, or anywhere a smooth model leaves visibly structured residuals. It is also the
right choice when you need an accurate light model to subtract.

Do **not** reach for one when:

- The galaxy is well described by a smooth profile. You add run time and failure modes
  without adding fidelity.
- You only want global quantities — total flux, size, axis ratio. A Sersic, MGE or shapelet
  fit is sufficient and far more interpretable.
- The data does not resolve the structure. At low resolution there is nothing for the mesh to
  reconstruct.
- It is your first fit of this dataset. Start parametric, then chain into the pixelised
  model with the parametric result as its starting priors — the initialisation is what makes
  pixelised fits robust and fast. See [`non_linear_search`](./non_linear_search.md), and
  chapter 3 of the HowToGalaxy lectures for the underlying linear algebra and Bayesian
  statistics.

## See also

- [`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md) — the same inversion,
  applied to basis functions with fixed shapes.
- [`shapelets`](./shapelets.md) — the intermediate step between a basis and a free mesh.
- [`grids_and_masks`](./grids_and_masks.md) — the pixelisation over-sampling grid.
- [`extra_galaxies_and_noise_scaling`](./extra_galaxies_and_noise_scaling.md) — why hard
  masks and meshes do not mix.
- [`interferometer_theory`](./interferometer_theory.md) — pixelised reconstruction of
  visibility data.
- [`../api/analysis_objects`](../api/analysis_objects.md) — `ag.Settings` and the analysis
  keywords that configure an inversion.
- [`../stack/autoarray`](../stack/autoarray.md) — where the meshes, mappers and solvers live.
