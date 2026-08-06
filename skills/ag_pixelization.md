---
name: ag_pixelization
description: Reconstruct a galaxy's clumpy or irregular light directly on a regularized pixel mesh, using `ag.Pixelization` alongside a parametric `ag.lp_linear` bulge — the hybrid model that gives a smooth interpretable component plus a flexible flux map for everything the profile cannot explain. Covers when a pixelization is warranted and when it is overkill, choosing an `ag.mesh` and an `ag.reg` regularization scheme and what each costs in free parameters, why `mesh_shape` must be fixed before the fit, `over_sample_size_pixelization` rather than `over_sample_size_lp`, noise scaling instead of hard masking for contaminants, the positive-only solver, reading the reconstruction and its Bayesian-evidence terms out of the `Inversion`, exporting the reconstruction to CSV for collaborators, and the GPU/VRAM versus CPU run-time trade. Use when a Sersic, MGE or shapelet basis leaves structured residuals in discrete off-centre lumps. Not for morphology a basis can still fit (`ag_basis_profiles`), not for non-parametric isophote measurement (`ag_ellipse_fitting`), and not for the basics of model composition (`ag_build_imaging_model`).
---

# Reconstructing a galaxy on a pixel mesh

Every model in this workspace so far has been a *function*: you asserted a functional form and
the fit found its parameters. A pixelization drops the functional form. It lays a mesh of pixels
over the galaxy, gives each pixel its own free flux value, and solves all of them at once by
linear inversion — thousands of amplitudes, none of them in the non-linear search's parameter
space. What stops that from simply fitting the noise is **regularization**: a prior that
penalises solutions where neighbouring mesh pixels differ sharply, so the reconstruction is as
smooth as the data will allow and no smoother.

The science case is specific, and it is worth being honest about how specific. Galaxies with
spiral arms, asymmetric star-forming clumps, tidal features or low-surface-brightness
substructure have light that no smooth profile — and often no basis expansion either —
reproduces. The canonical use is therefore **hybrid**: a linear `Sersic` for the smooth central
bulge, and a pixelization for the irregular remainder. That split is the point. It gives you a
low-dimensional, physically interpretable description of the bulge *and* a flux map of exactly
what the bulge could not explain, which is the quantity you want if the science question is "how
much of this galaxy's light is in its irregular components?"

This is a **direct** reconstruction. There is no second plane, no de-projection, no inversion of
a geometric mapping — the mesh sits on the image plane, over the galaxy, at the same coordinates
the data occupies. If you have met pixelized reconstruction before in a different context, that
extra step is the one that is absent here, and its absence makes everything simpler: what the
mesh reconstructs is the galaxy's own surface brightness, and its coordinates are sky
coordinates in arcseconds.

Statistically, the fit now has two nested layers. The non-linear search explores a handful of
parameters — the bulge's shape, the regularization strength — and for each proposal an inversion
solves the mesh amplitudes exactly and returns a **Bayesian evidence** rather than a plain
likelihood. That evidence includes terms that penalise an unnecessarily complex reconstruction,
which is what lets a model with 400 free flux values not simply win by over-fitting. The theory
is [`../wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md);
chapter 3 of HowToGalaxy derives it from scratch.

The canonical scripts are
`autogalaxy_workspace:scripts/imaging/features/pixelization/modeling.py` (via a search),
`autogalaxy_workspace:scripts/imaging/features/pixelization/fit.py` (one direct fit, with the
inversion internals walked through) and
`autogalaxy_workspace:scripts/imaging/features/pixelization/galaxy_reconstruction.py` (export).

## Before you reach for one — the honest gate

A pixelization is the most powerful and the most expensive model here, with failure modes the
parametric models do not have. Three questions decide whether you need it:

- *"What do the residuals actually look like?"* Structured residuals that **follow the
  isophotes** — a twist, a four-lobed pattern, an ellipticity that changes with radius — are a
  *shape* problem, and an MGE fixes them for four free parameters
  ([`ag_basis_profiles`](./ag_basis_profiles.md)). Residuals in **discrete off-centre lumps** are
  a substructure problem, and that is what a pixelization is for. Look before you choose.
- *"Is the structure resolved?"* At low resolution the irregular structure is not in the data,
  and a pixelization will reconstruct noise while telling you it fitted well. The workspace is
  blunt about this: for low-resolution data pixelizations are unnecessary.
- *"Do you need global quantities or the light distribution?"* If you want a total flux, a size,
  an axis ratio, a Sersic index — a parametric profile, an MGE or shapelets are enough and far
  cheaper. If you want the morphology itself, particularly for faint or low-surface-brightness
  features, nothing else comes close.

If the answer to the first is "lumps" and to the second "yes", continue. Otherwise you will
spend hours to learn less.

## Ask

- *"What is the smooth component?"* Almost always a linear `Sersic`, sometimes a Sersic plus an
  Exponential disk. It matters that this exists: without it the pixelization has to reconstruct
  the bright central bulge too, which wastes mesh resolution on light a six-parameter profile
  describes perfectly and makes the regularization choice much harder.
- *"How many mesh pixels can you afford?"* This is a hardware question as much as a science one
  (see the run-time branch). 20 × 20 is the workspace's default for a GPU run; 28 × 28 to 30 × 30
  for a better-resolved reconstruction; higher only with a large-VRAM GPU or a many-core CPU.
- *"Are there neighbours inside the mask?"* For a pixelization the answer is *never* to mask
  their pixels out — that punches holes in the mesh and produces discontinuity systematics.
  Scale their noise instead (branch below).
- *"GPU or CPU?"* Genuinely depends on your pixel scale, and the answer is counter-intuitive.
  Ask before assuming.

## Branch — the hybrid model

The canonical composition. Adapted from
`autogalaxy_workspace:scripts/imaging/features/pixelization/modeling.py`.

```python
"""
Galaxy Structure: Bulge Plus Pixelized Reconstruction
=====================================================

Fit a galaxy whose light has two very different characters: a smooth central bulge, described by
a linear Sersic profile in six parameters, and asymmetric clumpy star formation, reconstructed
on a regularized rectangular mesh. The Sersic captures the smooth component interpretably; the
pixelization absorbs everything it cannot explain, and the reconstructed flux map is the
measurement of the galaxy's irregular light.

__Contents__

- **Imports:** Import the required libraries.
- **Dataset:** Load the imaging, mask it, and apply pixelization over-sampling.
- **Mesh Shape:** Fix the mesh dimensions before the model is composed.
- **Model:** Compose the linear Sersic bulge plus the pixelization.
- **Check:** Confirm the parameter count, evaluate one likelihood, and estimate VRAM.
"""

"""
__Imports__
"""
from pathlib import Path

import autofit as af
import autogalaxy as ag
import autogalaxy.plot as aplt

DATASET_PATH = Path("dataset") / "imaging" / "my_galaxy"
PIXEL_SCALES = 0.1
MASK_RADIUS = 2.0

"""
__Dataset__

The mask matters more than usual here. It defines the region the mesh is laid over, so a mask
that reaches well beyond the galaxy spends reconstruction pixels on empty sky, and one that
truncates the galaxy leaves its outer light unreconstructed
(`PyAutoArray:autoarray/dataset/imaging/dataset.py`).

The over-sampling argument changes too. A pixelization evaluates light on its *own* grid with
its own over-sampling scheme, so the size is passed as `over_sample_size_pixelization`, not the
`over_sample_size_lp` used for light profiles. Passing the wrong one silently leaves the
pixelization grid at its default.
"""
dataset = ag.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    psf_path=DATASET_PATH / "psf.fits",
    pixel_scales=PIXEL_SCALES,
)

mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=MASK_RADIUS,
)
dataset = dataset.apply_mask(mask=mask)

over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[8, 4, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)
dataset = dataset.apply_over_sampling(over_sample_size_pixelization=over_sample_size)

"""
__Mesh Shape__

The mesh dimensions are **fixed before the fit and cannot be a free parameter**. This is not a
stylistic restriction: JAX compiles the likelihood against statically shaped arrays, and the
mesh shape sets those shapes. A rectangular mesh uses the same number of pixels in y and x.
"""
mesh_pixels_yx = 20
mesh_shape = (mesh_pixels_yx, mesh_pixels_yx)

"""
__Model__

`ag.Pixelization` pairs a `mesh` — where the reconstruction pixels sit — with a `regularization`
scheme — the prior that keeps the solution smooth. It is attached to the galaxy as a component
alongside the light profiles, and the analysis knows to route it through the inversion
(`PyAutoGalaxy:autogalaxy/galaxy/galaxy.py`).

The mesh itself contributes **zero** free parameters; the reconstruction's 400 flux values are
solved, not sampled. `ag.reg.GaussianKernel` contributes two (`coefficient`, `scale`). The bulge
is `ag.lp_linear.Sersic` rather than `ag.lp.Sersic` deliberately: its `intensity` is then solved
by the *same* inversion that solves the mesh amplitudes, which removes the degeneracy between
"bright bulge, faint reconstruction" and "faint bulge, bright reconstruction" that a sampled
intensity would create.
"""
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

"""
__Check__

Three cheap checks, each catching a different class of mistake: the parameter count catches a
model error, one likelihood evaluation catches an incompatibility between model, dataset and
analysis, and `print_vram_use` catches the resource error that otherwise appears as an
out-of-memory failure mid-compile. Pixelizations use far more VRAM than profile-only models —
around 0.05 GB per batched likelihood for 400 reconstruction pixels — which is why the
workspace uses a lower `n_batch` for these fits than for any other.
"""
print(model.info)
print(f"Total free parameters = {model.total_free_parameters}")

analysis = ag.AnalysisImaging(dataset=dataset, use_jax=True)

log_likelihood = analysis.log_likelihood_function(
    instance=model.instance_from_prior_medians()
)
print(f"log evidence at prior medians: {float(log_likelihood):.2f}")
```

**N = 8**: the Sersic's centre (2), `ell_comps` (2), `effective_radius`, `sersic_index`, plus the
regularization's `coefficient` and `scale`. Eight parameters, with 400 reconstruction pixels
solved. That is dramatically more parsimonious than stacking parametric profiles until every
clump is described — a 20-plus-parameter approach that would still fail on genuinely irregular
substructure.

Extending the smooth side is exactly as you would expect — add components as further attributes
on the galaxy, keeping them linear so their intensities join the same inversion:

```python
galaxy = af.Model(
    ag.Galaxy,
    redshift=0.5,
    bulge=ag.lp_linear.Sersic,
    disk=ag.lp_linear.Exponential,
    pixelization=pixelization,
)
```

## Branch — choosing a mesh and a regularization scheme

These are the two decisions that make or break a reconstruction, and the parameter cost is
almost entirely in the regularization.

**Meshes** (`ag.mesh`, from `PyAutoArray:autoarray/inversion/mesh/`). All contribute zero free
parameters, all take `shape=(y, x)`:

| Mesh | Where the pixels go | Use when |
|---|---|---|
| `RectangularUniform` | a uniform grid over the masked region | you want the simplest, most predictable behaviour |
| `RectangularAdaptDensity` | a rectangular grid whose spacing follows the density of image pixels mapping to it | **the default** — concentrates resolution where the data is |
| `RectangularAdaptImage` | adapts to the image's own brightness distribution | the irregular light is strongly concentrated |

`Delaunay`, `KNearestNeighbor` and `KNNBarycentric` also exist for irregular tessellations. Start
with `RectangularAdaptDensity`; it is what every workspace example uses, and the rectangular
meshes are what the fixed-`mesh_shape` JAX path is built around.

**Regularization** (`ag.reg`, from `PyAutoArray:autoarray/inversion/regularization/`) is where
the free parameters are, and where the physics of "how smooth should this be?" lives:

| Scheme | Free params | What it assumes |
|---|---|---|
| `ag.reg.Constant` | 1 (`coefficient`) | one smoothing strength everywhere — the simplest, and the right first try |
| `ag.reg.GaussianKernel` | 2 (`coefficient`, `scale`) | smoothing with a Gaussian correlation length you also fit |
| `ag.reg.MaternKernel` | 3 (`coefficient`, `scale`, `nu`) | as above, with the roughness `nu` free too |

Verified counts, not guesses. `Constant` penalises the difference between neighbouring pixels
directly; the kernel schemes impose a correlation *length*, which is physically closer to what a
galaxy's light does and generally reconstructs faint extended structure better at the cost of
one or two parameters. `ag.reg.Adapt` and its variants scale the smoothing with the
reconstruction's own brightness — more flexible again, and requiring `adapt_images` on the
analysis, which is a step beyond this skill; ask if you want it.

A practical route: fit once with `ag.reg.Constant`, look at the reconstruction. Over-smoothed
(the clumps blurred into one blob) or over-fitted (isolated single-pixel spikes) both show up
immediately, and if `Constant` cannot get both the bright clumps and the faint envelope right at
one strength, that is the signal to move to `GaussianKernel`. Full discussion in
[`../wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md).

### The positive-only solver

Every pixelized reconstruction uses a **positive-only** linear solver: no mesh pixel may
reconstruct negative flux. This is not a numerical nicety. A signed solver lets the
reconstruction manufacture negative pixels that cancel positive ones to over-fit the data, and
that failure mode is a well-known systematic in the literature — many published methods allow
it. Enforcing non-negativity efficiently needs bespoke linear algebra, which is why this is
worth stating rather than assuming. You do not need to switch it on; it is the behaviour you get.
(The one place in this workspace where you *must* disable it is a shapelet basis, which needs
signed amplitudes by construction — see [`ag_basis_profiles`](./ag_basis_profiles.md).)

## Branch — contaminating neighbours: scale, never mask

The general advice for a neighbour inside the mask is to mask its pixels out. **For a
pixelization that advice is wrong.** Removing image pixels entirely removes their mapping into
the mesh, punching a hole in the reconstruction and producing discontinuities that show up as
unexplained systematics.

Instead, keep the pixels in the fit and make them contribute nothing: scale their data to zero
and their noise to an enormous value, so the likelihood is indifferent to them while the mesh
stays continuous. Adapted from
`autogalaxy_workspace:scripts/imaging/features/pixelization/fit.py`.

```python
"""
__Noise Scaling__

`mask_extra_galaxies.fits` marks the contaminated pixels. It is loaded with `invert=True`
because in this file `True` means "scale this pixel", the opposite of a modelling mask's
convention — getting this backwards scales the galaxy instead of the neighbour, so check the
subplot afterwards. `apply_noise_scaling` then zeroes those data values and inflates their
noise, driving their signal-to-noise to effectively zero without removing them from the mesh's
mapping (`PyAutoArray:autoarray/dataset/imaging/dataset.py`).

Order matters: scale first, then apply the modelling mask.
"""
mask_extra_galaxies = ag.Mask2D.from_fits(
    file_path=DATASET_PATH / "mask_extra_galaxies.fits",
    pixel_scales=PIXEL_SCALES,
    invert=True,
)

dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)

mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=PIXEL_SCALES,
    centre=(0.0, 0.0),
    radius=MASK_RADIUS,
)
dataset = dataset.apply_mask(mask=mask)

aplt.subplot_imaging_dataset(
    dataset=dataset,
    output_path="scripts/scratch/my_galaxy/",
    output_filename="noise_scaled",
    output_format="png",
)
```

The scaled pixels go to a noise value of order 1e8 — visibly so on the signal-to-noise panel of
the subplot, which is how you confirm you scaled the right region. Drawing that mask
interactively is `autogalaxy_workspace:scripts/imaging/data_preparation/gui/mask_extra_galaxies.py`;
the modelling alternative, and when to prefer it, is
[`ag_light_model_extras`](./ag_light_model_extras.md) and
[`../wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../wiki/core/concepts/extra_galaxies_and_noise_scaling.md).

## Branch — reading the reconstruction out

The reconstruction is the science product, and it lives on the `Inversion`. You can get there
from a completed fit or from a single direct `ag.FitImaging` — the latter is the fast way to
learn the objects, and is what
`autogalaxy_workspace:scripts/imaging/features/pixelization/fit.py` does.

```python
"""
__Reconstruction__

`inversion.linear_obj_list` holds the linear objects the fit solved. For a hybrid model that is
one `LightProfileLinearObjFuncList` per linear light profile plus one `Mapper` for the
pixelization; with a non-linear `ag.lp.Sersic` bulge the `Mapper` is the only entry. The
`Mapper` is the object that maps image pixels onto mesh pixels, and it is mesh-specific
(`PyAutoArray:autoarray/inversion/mappers/`).

The reconstruction is a 1D array of one flux per mesh pixel, and the (y, x) arcsecond
coordinates of those pixels are `mapper.mesh_geometry.mesh_grid`. Pair them by index — they are
the same length and the same order — and you have the flux map.
"""
inversion = fit.inversion

mapper = inversion.linear_obj_list[0]

reconstruction = inversion.reconstruction
mesh_grid = mapper.mesh_geometry.mesh_grid

print(f"{len(reconstruction)} mesh pixels reconstructed")
print(f"coordinates shape: {mesh_grid.shape}")

"""
The reconstruction's own uncertainties, and its projection back onto the image, are also on the
inversion. `mapped_reconstructed_operated_data` contains **only** the pixelized component — any
parametric light profile in the model is excluded — which is exactly the quantity you want when
asking how much light is in the irregular component.
"""
print(inversion.reconstruction_noise_map)
print(inversion.mapped_reconstructed_operated_data.native.shape)
```

A caution on the `Mapper`'s grid attributes: `mapper.image_plane_mesh_grid` is `None` for a
rectangular mesh, so do not reach for it. `mapper.mesh_geometry.mesh_grid` is the mesh pixel
centres (verified on the released stack), and `mapper.image_plane_data_grid` is the centre of
every masked *image* pixel. Some of the `Mapper`'s attribute names carry a plane-based prefix
inherited from the shared inversion library that also serves a multi-plane use case; in
PyAutoGalaxy there is only the one plane, so `mesh_geometry.mesh_grid` is both the clearer name
and the one to use.

### The evidence terms

The inversion's figure of merit is a Bayesian evidence, and its components are individually
readable — which is how you diagnose whether regularization is doing too much or too little:

```python
print(f"regularization term        = {inversion.regularization_term}")
print(f"log det regularization     = {inversion.log_det_regularization_matrix_term}")
print(f"log det curvature + reg    = {inversion.log_det_curvature_reg_matrix_term}")
```

The `regularization_term` measures how non-smooth the solution is; the two log-determinant
terms are the complexity penalty that stops a 400-pixel model winning by over-fitting. The
matrices themselves (`curvature_matrix`, `regularization_matrix`, `curvature_reg_matrix`) are
there too. The derivation is in HowToGalaxy chapter 3 and the papers it cites
(arXiv:1708.07377, arXiv:astro-ph/0601493).

### Diagnostic plots

`aplt.subplot_fit_imaging` includes the reconstruction on the mesh alongside the usual data /
model / residual panels, and is the first thing to look at. For the inversion's own internals
there are dedicated functions, which live in the shared inversion library rather than on `aplt`
and so are imported explicitly — from
`autogalaxy_workspace:scripts/imaging/features/pixelization/plot.py`:

```python
from autoarray.inversion.plot.inversion_plots import subplot_of_mapper
from autoarray.inversion.plot.mapper_plots import plot_mapper, subplot_image_and_mapper

PLOT_DIR = "scripts/scratch/my_galaxy/pixelization/"

aplt.subplot_fit_imaging(fit=fit, output_path=PLOT_DIR, output_format="png")

subplot_of_mapper(
    inversion=inversion, mapper_index=0, output_path=PLOT_DIR, output_format="png"
)

subplot_image_and_mapper(
    mapper=mapper, image=dataset.data, output_path=PLOT_DIR, output_format="png"
)

print(f"Saved to: {Path(PLOT_DIR).resolve()}")
```

`subplot_of_mapper` is the comprehensive diagnostic — reconstructed image, reconstruction, its
noise map and the regularization weights in one figure — and `mapper_index` selects which linear
object when there are several. `subplot_image_and_mapper` shows the data beside the mesh, which
is how you check the mesh covers the structure you care about. Note that none of these three are
exposed on the `aplt` module — `dir(aplt)` does not list them, so the explicit imports above are
the only route and writing them as `aplt.`-prefixed calls raises `AttributeError`. Quote the
absolute path back to the user and offer to open it.

## Branch — exporting the reconstruction for downstream science

A reconstruction that only exists inside a PyAutoGalaxy object is hard to share and hard to
analyse with other tools. Write it out as coordinates plus values and it becomes ordinary
tabular data. Adapted from
`autogalaxy_workspace:scripts/imaging/features/pixelization/galaxy_reconstruction.py`.

```python
"""
__Export__

Four columns — y, x, reconstruction, noise — is everything needed to rebuild, plot or analyse
the galaxy's irregular light without PyAutoGalaxy installed. A completed model-fit also writes
this file into its own `image/` folder automatically; glob for `*reconstruction_0.csv` there
rather than hard-coding the stem, which carries a prefix from the shared inversion library.
"""
import csv

CSV_PATH = Path("scripts/scratch/my_galaxy/reconstruction.csv")
CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

with CSV_PATH.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["y", "x", "reconstruction", "noise_map"])
    for (y, x), value, sigma in zip(
        mesh_grid, inversion.reconstruction, inversion.reconstruction_noise_map
    ):
        writer.writerow([y, x, value, sigma])

print(f"Reconstruction written to: {CSV_PATH.resolve()}")
```

Reloading needs nothing but the standard library, and from there the mesh is ordinary scattered
data. Two things the workspace does with it: a Delaunay triangulation via `scipy.spatial` for
plotting on the mesh's own geometry, and interpolation onto a regular grid via
`scipy.interpolate.griddata` for any tool that wants an image:

```python
import numpy as np
from scipy.interpolate import griddata

with CSV_PATH.open() as f:
    reader = csv.reader(f)
    header = next(reader)  # ['y', 'x', 'reconstruction', 'noise_map']
    loaded = {key: [] for key in header}
    for row in reader:
        for key, value in zip(header, row):
            loaded[key].append(float(value))

points = np.stack((np.array(loaded["x"]), np.array(loaded["y"])), axis=-1)

interpolation_grid = ag.Grid2D.from_extent(
    extent=(-1.0, 1.0, -1.0, 1.0), shape_native=(201, 201)
)

interpolated = griddata(
    points=points, values=np.array(loaded["reconstruction"]), xi=interpolation_grid
)
```

Pick the `extent` to cover the reconstruction without over-resolving it — the mesh has a few
hundred pixels, so interpolating to 201 × 201 is presentation, not information.

## Branch — run time, VRAM, and the GPU-versus-CPU choice

This is the branch that decides whether your fit takes twenty minutes or three hours, and the
answer is not "use the GPU".

Pixelized inversions do linear algebra on very large, very **sparse** matrices. JAX has no sparse
support and must work densely, which scales badly; the CPU implementation exploits the sparsity
fully via `numba`. So the trade runs against pixel scale:

- **Low resolution (`pixel_scales > 0.05`, e.g. Euclid)** — fewer sparse operations, modest VRAM.
  **GPU with JAX is usually fastest.**
- **High resolution (`pixel_scales <= 0.03`, e.g. HST or JWST)** — the linear algebra is
  sparsity-dominated. **CPU with `numba` and many cores can beat a powerful GPU.**

VRAM is the hard constraint on the GPU side. JAX must hold the whole batched likelihood in GPU
memory, and a pixelization needs far more than a profile model: around 0.05 GB per batched
likelihood at 400 reconstruction pixels, and more than 1 GB — occasionally more than 10 GB — at
high resolution with a fine mesh. Two consequences: keep `n_batch` low (the workspace uses 20 for
pixelizations against 50 elsewhere), and run

```python
analysis.print_vram_use(model=model, batch_size=search.batch_size)
```

before committing. It takes 20–30 seconds and it is the difference between knowing your limit
and discovering it as an out-of-memory error mid-compile. If VRAM is exceeded the run time does
not degrade gracefully — it goes from under ten minutes to three hours or more.

Rough scaling with resolution, from the workspace's own measurements at a 20 × 20 mesh with VRAM
under control: ~10 minutes at 0.1"/pixel, ~30 minutes at 0.05", ~1 hour at 0.03". Benchmark both
paths for your own data and hardware rather than trusting either default; the search-side
settings are [`ag_configure_search`](./ag_configure_search.md) and
[`../wiki/core/api/searches.md`](../wiki/core/api/searches.md).

## Combine — where this hands off

- **Try a basis first** → [`ag_basis_profiles`](./ag_basis_profiles.md). An MGE is four
  parameters and minutes, not hours, and it genuinely resolves the shape-mismatch case a
  pixelization is often reached for by mistake.
- **Pick and configure the search** → [`ag_configure_search`](./ag_configure_search.md), with
  `n_batch` lowered for VRAM.
- **Run the fit** → [`ag_run_search`](./ag_run_search.md); `image/fit.png` in the output folder
  refreshes on the fly and shows the reconstruction as it converges, which is worth watching for
  a fit this long.
- **Plot and inspect** → [`ag_plot_fit`](./ag_plot_fit.md), plus the `subplot_of_mapper`
  diagnostics above.
- **Load a completed fit programmatically** → [`ag_load_results`](./ag_load_results.md).
- **Over-smoothed, over-fitted or unphysical reconstruction** →
  [`ag_debug_fit_failure`](./ag_debug_fit_failure.md). The pixelization-specific causes are a
  regularization scheme too rigid for the structure, a mask that punched holes via hard masking
  where noise scaling was needed, over-sampling passed as `over_sample_size_lp` instead of
  `over_sample_size_pixelization`, and VRAM exhaustion masquerading as a hung fit.
- **Contaminating neighbours modelled rather than scaled** →
  [`ag_light_model_extras`](./ag_light_model_extras.md).
- **Make the fit robust and fast by starting simple** → the search-chaining skill
  (`ag_chain_searches`). This is the biggest available win for a pixelization: fit a parametric
  model first, pass its bulge as priors, and let the expensive model start from a sensible place.
  The workspace recommends it explicitly.
- **A non-parametric shape measurement instead of a reconstruction** →
  [`ag_ellipse_fitting`](./ag_ellipse_fitting.md).

Offer (default-yes) a dated `wiki/project/YYYY-MM-DD-<slug>.md` entry recording the mesh and its
shape, the regularization scheme and why, the mask radius, the hardware path, and what the
reconstruction showed — with a pixelization the choices *are* the result, and none of them are
recoverable from the output folder alone.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Bayesian regularization](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_3_pixelizations/tutorial_4_bayesian_regularization.ipynb):
  why a model with hundreds of free flux values does not simply over-fit, derived from scratch;
  `tutorial_6_model_fit` then runs the full fit.
- **General reference** — [RTD: Pixelization API](https://pyautogalaxy.readthedocs.io/en/latest/api/pixelization.html):
  every mesh, regularization scheme and the objects that combine them.
- **Experienced PyAutoGalaxy user** — [workspace: imaging/features/pixelization/modeling.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/imaging/features/pixelization/modeling.py):
  the hybrid fit end to end, with the run-time, VRAM and GPU-versus-CPU discussion in full.

## Agent procedural checklist

1. Look at the residual map of a parametric or basis fit first. Shape-following residuals mean
   `ag_basis_profiles`; discrete off-centre lumps mean a pixelization. Do not skip this.
2. Confirm the structure is resolved — at coarse pixel scales a pixelization reconstructs noise.
3. Always pair the pixelization with a linear light profile for the smooth component; never let
   the mesh reconstruct the bulge.
4. Fix `mesh_shape` before composing the model; it cannot be a free parameter.
5. Pass over-sampling as `over_sample_size_pixelization`, not `over_sample_size_lp`.
6. Start with `RectangularAdaptDensity` + `ag.reg.Constant`; move to `GaussianKernel` only when
   one smoothing strength demonstrably cannot serve both the bright and faint structure.
7. Scale contaminant noise (`apply_noise_scaling`, `invert=True`) — never hard-mask pixels inside
   a pixelization fit — and check the signal-to-noise panel afterwards.
8. `print(model.info)`, evaluate one likelihood, then `print_vram_use` before any GPU run; keep
   `n_batch` low.
9. Read the reconstruction via `inversion.reconstruction` +
   `mapper.mesh_geometry.mesh_grid`; export to CSV for anything downstream.
10. Save the script to `scripts/`, quote every plot's absolute path and offer to open it, then
    offer the `wiki/project/` entry recording mesh, regularization and hardware choices.
