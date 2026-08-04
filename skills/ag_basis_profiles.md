---
name: ag_basis_profiles
description: Fit a galaxy's morphology with a *basis* rather than one or two smooth profiles — linear light profiles (`ag.lp_linear`), a Multi-Gaussian Expansion, or a shapelet expansion — where every component's `intensity` is solved analytically by a linear inversion instead of sampled by the search. Covers why `ag.lp_linear` is the default for any bulge-disk decomposition, when an MGE beats a Sersic pair (isophotal twists, radially varying ellipticity, asymmetry), when shapelets beat an MGE, the positive-only versus signed linear solver and what a negative amplitude means physically, `ag.model_util.mge_model_from` and the hand-rolled `ag.lp_basis.Basis` idiom behind it, a compact MGE for an unresolved nucleus, and how to read solved intensities back out of a fit. Use when a Sersic or bulge-plus-disk model leaves structure in the residuals but the galaxy still has a well-defined centre. Not for pixelized reconstruction of genuinely irregular clumps (`ag_pixelization`), not for non-parametric isophote measurement (`ag_ellipse_fitting`), and not for the basics of composing an `af.Model` tree (`ag_build_imaging_model`).
---

# Fitting morphology with a basis

A Sersic profile makes a strong claim: that the galaxy's isophotes are concentric, similar
ellipses with a single fixed axis ratio and position angle, and that its surface brightness
falls off as one power of radius. Real galaxies routinely violate all of that. Isophotes twist
with radius, the ellipticity varies from the bulge outwards, a bar or a spiral pattern breaks
the symmetry — and when a Sersic cannot represent those features it does not fail loudly. It
absorbs them, and returns an `effective_radius` and `sersic_index` biased by exactly the
structure it could not fit.

A **basis** is the answer: instead of one profile with a shape, use tens of simple profiles
whose superposition can take almost any shape. The reason this is affordable — and the reason
it is often *cheaper* than a Sersic pair — is statistical. Every basis component's `intensity`
is a **linear** parameter: given the shapes and positions of the components, the amplitudes
that maximise the likelihood follow from solving a linear system, exactly, in one step. So they
never enter the non-linear search's parameter space at all. A 60-Gaussian MGE can have four
free parameters where a two-component linear Sersic decomposition has nine.

Three tiers, same machinery, increasing flexibility:

| Tier | What it is | Free parameters | Reach for it when |
|---|---|---|---|
| `ag.lp_linear.*` | ordinary profiles with `intensity` solved | 6 per Sersic, 3 per aligned Exponential | you want interpretable bulge/disk parameters — **the default** |
| MGE (`ag.lp_basis.Basis` of `Gaussian`s) | 15–100 Gaussians on a fixed log-spaced `sigma` ladder | 4 (one basis) to 6 (two) | isophotal twists, radial ellipticity variation, mild asymmetry |
| shapelets | an orthonormal polar or Cartesian basis | 3 (spherical) to 5 (elliptical) | disky, star-forming morphology the MGE still smooths over |

The science this serves is the decomposition itself. A bulge-plus-disk fit measures the
bulge-to-total light ratio, the two components' sizes and the bulge's concentration — the
quantities that place a galaxy on the mass–size relation and separate a classical spheroid from
a pseudo-bulge. A basis fit measures something the parametric fit cannot: how the shape of the
light changes with radius. Both concepts are in
[`../wiki/core/concepts/linear_light_profiles_and_mge.md`](../wiki/core/concepts/linear_light_profiles_and_mge.md)
and [`../wiki/core/concepts/shapelets.md`](../wiki/core/concepts/shapelets.md); the catalogue of
which variant lives in which module is
[`../wiki/core/api/light_profile_catalog.md`](../wiki/core/api/light_profile_catalog.md).

This skill assumes you already have a masked, over-sampled dataset and know how to build an
`af.Model` tree — that is [`ag_build_imaging_model`](./ag_build_imaging_model.md), whose MGE
branch is the one-paragraph version of what follows.

## Ask

- *"Do you need the Sersic parameters, or the best fit?"* This is the real fork. If your science
  is a bulge-to-total ratio, an effective radius, a Sersic index — a number you will put in a
  table next to other people's — stay with `ag.lp_linear` Sersic-family profiles, because an
  MGE does not hand you those numbers. If your science is the light distribution itself, or you
  need the residuals flat before you can trust anything else, go to a basis.
- *"What does the residual map look like after a single Sersic?"* Structured residuals that
  follow the isophotes (a four-lobed or twisted pattern) say the *shape* is wrong — an MGE
  fixes that. Residuals in discrete off-centre lumps say the shape is fine but there is
  substructure — that is a pixelization ([`ag_pixelization`](./ag_pixelization.md)), not a basis.
  If you have not looked yet, look first; it is one plot and it decides the branch.
- *"Does the galaxy have a single well-defined centre?"* Every basis in this skill shares one
  centre across all its components. A merger, or a galaxy with a bright companion overlapping
  it, breaks that assumption — handle the companion first with
  [`ag_light_model_extras`](./ag_light_model_extras.md).
- *"Is there a compact nuclear source?"* An AGN or a nuclear starburst is a separate component,
  and there is a purpose-built compact MGE for it (branch four below).

## Branch — linear light profiles, the default for any decomposition

Start here even when you expect to end up with a basis. This is the same bulge-plus-disk model
`ag_build_imaging_model` composes, and the point of this branch is what happens to `intensity`.

```python
"""
Galaxy Structure: Linear Bulge-Disk Decomposition
=================================================

Decompose a galaxy's light into a Sersic bulge and an Exponential disk using *linear* light
profiles, whose `intensity` parameters are solved analytically by a linear inversion inside
every likelihood evaluation rather than sampled by the non-linear search. The ratio of the two
solved intensities, integrated, is the bulge-to-total light ratio.

__Contents__

- **Imports:** Import the required libraries.
- **Dataset:** Load the masked, over-sampled imaging dataset.
- **Model:** Compose the linear bulge and disk, with their centres paired.
- **Check:** Confirm the parameter count and evaluate one likelihood.
- **Intensities:** Read the solved intensities back out of a completed fit.
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
MASK_RADIUS = 3.0

"""
__Dataset__

Loaded from FITS, masked to a radius chosen by inspecting the data, and over-sampled adaptively
where the profile's intensity gradient is steep. All three decisions change the answer, so they
are reproduced here rather than hidden
(`PyAutoArray:autoarray/dataset/imaging/dataset.py`).
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
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

"""
__Model__

The decomposition is identifiable because the two components are *asymmetric* in what they are
allowed to be: the bulge's `sersic_index` is free, so the fit can find a concentrated spheroid
(n ~ 4), while the `Exponential` disk has n fixed at 1 by construction. Two free Sersics on one
galaxy are largely degenerate and the fit will trade light between them.

`ag.lp_linear` rather than `ag.lp` is the only change from a standard composition, and it is
not a small one: each profile's `intensity` leaves the search's parameter space and is instead
solved by a linear inversion that always returns the amplitudes maximising the likelihood given
the other parameters. Two dimensions vanish, and with them the strong degeneracies between
`intensity` and `effective_radius` / `sersic_index` that a sampler finds hardest to map
(`PyAutoGalaxy:autogalaxy/profiles/light/linear/sersic.py`).

`bulge.centre = disk.centre` asserts the components are concentric — physically reasonable for
most galaxies, and worth two parameters.
"""
bulge = af.Model(ag.lp_linear.Sersic)
disk = af.Model(ag.lp_linear.Exponential)
bulge.centre = disk.centre

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

"""
__Check__

The likelihood at the prior medians costs one evaluation and proves the model, dataset and
analysis are mutually compatible. Pass `use_jax=False` while debugging — NumPy tracebacks are
far easier to read (`PyAutoGalaxy:autogalaxy/imaging/model/analysis.py`).
"""
print(model.info)
print(f"Total free parameters = {model.total_free_parameters}")

analysis = ag.AnalysisImaging(dataset=dataset, use_jax=True)

log_likelihood = analysis.log_likelihood_function(
    instance=model.instance_from_prior_medians()
)
print(f"log likelihood at prior medians: {float(log_likelihood):.2f}")
```

N = 9: the bulge's centre (2), two `ell_comps` pairs (4), two `effective_radius` values and the
bulge's `sersic_index` — with both intensities solved. Adapted from
`autogalaxy_workspace:scripts/imaging/features/linear_light_profiles/modeling.py`, which
reduces `n_live` to 75 for exactly this reason: a simpler parameter space needs fewer live
points to map.

The cost is real but small. A linear likelihood evaluation is roughly three to five times
slower than a standard one, because the inversion has to be solved every time. The workspace
example measures ~0.05 s against ~0.01 s on a low-resolution dataset. That is repaid by fewer
iterations and a more reliable posterior, and the trade tips further towards linear the more
profiles you add — which is what makes the next two branches possible at all.

### The consequence: `intensity` is not in the model, so it is not in the results

This trips up everyone once. A linear profile has no `intensity` attribute to report, so
`model.results` does not list one, and **a linear profile cannot be plotted directly** — there
is no amplitude to evaluate. The intensities exist only after a fit, as the inversion's
solution. Three ways to get at them, all from
`autogalaxy_workspace:scripts/imaging/features/linear_light_profiles/modeling.py`:

```python
"""
__Intensities__

`max_log_likelihood_galaxies` has already performed the inversion, so its profiles carry their
solved `intensity` values and can be evaluated and plotted like ordinary profiles. The
`Fit` additionally exposes a dictionary keyed by the profile objects themselves, which is the
unambiguous route when several components share a class
(`PyAutoGalaxy:autogalaxy/imaging/fit_imaging.py`).
"""
galaxies = result.max_log_likelihood_galaxies

print(f"bulge intensity = {galaxies[0].bulge.intensity}")

fit = result.max_log_likelihood_fit

print(fit.linear_light_profile_intensity_dict[fit.galaxies[0].bulge])
print(fit.linear_light_profile_intensity_dict[fit.galaxies[0].disk])

galaxies_ordinary = fit.model_obj_linear_light_profiles_to_light_profiles

aplt.subplot_galaxies(
    galaxies=galaxies_ordinary,
    grid=dataset.grid,
    output_path="scripts/scratch/my_galaxy/",
    auto_filename="decomposition",
    output_format="png",
)
```

`model_obj_linear_light_profiles_to_light_profiles` returns the same galaxies with every linear
profile replaced by its ordinary equivalent at the solved amplitude — that is the object to
hand to any plotting or derived-quantity call. `fit.inversion.linear_obj_list` holds one
`LightProfileLinearObjFuncList` per linear component (or per `Basis`), which is where the
bookkeeping lives when you need to be certain which amplitude belongs to which profile.

Integrating those amplitudes over the two profiles is what gives you the bulge-to-total ratio;
the machinery for luminosities and magnitudes is
[`../wiki/core/concepts/cosmology_and_units.md`](../wiki/core/concepts/cosmology_and_units.md).
Ask if you want the derived-quantity route spelled out.

## Branch — a Multi-Gaussian Expansion, when the *shape* is wrong

A Gaussian is a poor galaxy profile on its own and an excellent basis function in company:
sum enough of them at fixed, logarithmically spaced widths and you can build any monotonic
radial profile, and — if you let separate groups of them carry separate ellipticities — an
isophote shape that changes with radius. That last property is the one a Sersic cannot have at
any parameter count, and it is why an MGE is the workspace's recommended default model.

The composition is long, so the library ships a helper:

```python
"""
__Model__

An MGE bulge: 20 linear Gaussians sharing one centre and one ellipticity, with every `sigma`
fixed on a logarithmic ladder running from below the pixel scale out to `mask_radius`, and
every intensity solved by the inversion. `mask_radius` sets the outer end of that ladder, so
pass the radius you actually masked at — a ladder that stops short of the data leaves the
outer isophotes unrepresented (`PyAutoGalaxy:autogalaxy/analysis/model_util.py`).
"""
bulge = ag.model_util.mge_model_from(
    mask_radius=MASK_RADIUS,
    total_gaussians=20,
    centre_prior_is_uniform=True,
)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

print(model.info)
print(f"Total free parameters = {model.total_free_parameters}")
```

**N = 4** — a shared centre and a shared `ell_comps`. Twenty Gaussians, four dimensions, more
morphological freedom than a Sersic's six. Adapted from
`autogalaxy_workspace:scripts/imaging/start_here.py`, where the MGE is the recommended default.

The full signature is
`mge_model_from(mask_radius, total_gaussians=30, gaussian_per_basis=1,
centre_prior_is_uniform=True, centre=(0.0, 0.0), centre_fixed=None, centre_per_basis=False,
centre_sigma=0.3, ell_comps_prior_is_uniform=False, ell_comps_uniform_width=0.2,
ell_comps_sigma=0.3, use_spherical=False)`. The arguments worth knowing:

- **`gaussian_per_basis=2`** splits the ladder into two bases with *independent* ellipticities.
  N goes 4 → 6 and you buy the ability to fit an isophotal twist: an inner group and an outer
  group free to be differently elongated and differently oriented. This is the single most
  useful knob here, and the reason to prefer an MGE over a Sersic pair for an early-type galaxy.
- **`centre_fixed=(y, x)`** pins the centre entirely, dropping two more parameters. Used for
  contaminating neighbours ([`ag_light_model_extras`](./ag_light_model_extras.md)).
- **`use_spherical=True`** drops the ellipticity — for a genuinely round system, or as a
  deliberately rigid comparison model.
- **`total_gaussians`** buys radial resolution, not shape freedom. 15 is enough for a smooth
  profile; 60 for a well-resolved one; beyond that you are mostly paying for likelihood
  evaluations. Cost scales with the count, because every Gaussian's image must be computed and
  PSF-convolved: the workspace measures ~0.5 s per evaluation for 60 Gaussians, against ~0.01 s
  for a standard Sersic. VRAM rises too — 10–50 MB per batched likelihood at 60 Gaussians, so
  check `analysis.print_vram_use(model=model, batch_size=search.batch_size)` before a GPU run
  with hundreds of components.

That run time is why the overall comparison is not obvious, and the workspace is honest about
it: the MGE's likelihood is much slower, but its parameter space is so much simpler — and
crucially contains *no parameter that scales the galaxy's size* — that the search converges far
faster. Net, it usually wins, and it fits better.

### The hand-rolled `Basis`, and why you might want it

The helper is a convenience over one explicit idiom. Compose it yourself when you need
something the arguments do not offer — a bespoke `sigma` range, a third basis, per-basis
priors. From `autogalaxy_workspace:scripts/imaging/features/multi_gaussian_expansion/modeling.py`:

```python
"""
__Model__

Two groups of 30 Gaussians. Within a group every Gaussian shares the centre and ellipticity of
the first, and every `sigma` is *fixed* to a value on a log10 ladder spanning a tenth of the
pixel scale to the mask radius. `ag.lp_basis.Basis` then groups the whole list into one model
component the galaxy can hold (`PyAutoGalaxy:autogalaxy/profiles/basis.py`).

The lower end matters: anchoring it to the pixel scale stops the basis spending Gaussians on
scales the data cannot resolve. `mge_model_from` exposes this as `sigma_min` (default `1e-4`,
which reproduces the historical ladder exactly).
"""
import numpy as np

total_gaussians = 30
gaussian_per_basis = 2

log10_sigma_list = np.linspace(
    np.log10(dataset.pixel_scales[0] / 10.0), np.log10(MASK_RADIUS), total_gaussians
)

centre_0 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)
centre_1 = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)

bulge_gaussian_list = []

for _ in range(gaussian_per_basis):

    gaussian_list = af.Collection(
        af.Model(ag.lp_linear.Gaussian) for _ in range(total_gaussians)
    )

    for i, gaussian in enumerate(gaussian_list):
        gaussian.centre.centre_0 = centre_0  # one shared y centre
        gaussian.centre.centre_1 = centre_1  # one shared x centre
        gaussian.ell_comps = gaussian_list[0].ell_comps  # shared within this basis
        gaussian.sigma = 10 ** log10_sigma_list[i]  # fixed, not sampled

    bulge_gaussian_list += gaussian_list

bulge = af.Model(ag.lp_basis.Basis, profile_list=bulge_gaussian_list)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))
```

N = 6. `print(model.info)` prints all sixty Gaussians and looks alarming; almost every
parameter shown is fixed. Trust `model.total_free_parameters`, not the length of the printout.

Two details that are load-bearing. Assigning `gaussian.sigma = <float>` **fixes** it — the
whole scheme depends on the widths not being sampled, because a free `sigma` reintroduces the
size-scaling degeneracy the MGE exists to remove. And sharing `ell_comps` *within* a basis but
not *between* bases is precisely what makes the twist fittable.

The `Basis` constructor also accepts a `regularization` argument that penalises non-smooth
amplitude solutions. Treat it as research-only: the positive-only solver below already fixes
the pathology it was introduced for, and no production analysis uses it — the workspace moved
that branch out of the user-facing script deliberately.

## Branch — a compact MGE for an unresolved nucleus

An AGN or nuclear starburst is not the extended stellar light, and forcing one basis to cover
both makes the fit choose between them. Model it as a second, deliberately compact basis: the
same construction with the `sigma` ladder capped at about twice the pixel scale, so the
component cannot be broader than a PSF-convolved point source.

```python
"""
__Model__

The galaxy's light becomes the sum of a diffuse stellar `bulge` MGE and a compact `point` MGE.
The point basis is 10 linear Gaussians sharing one centre and ellipticity with `sigma` values
log-spaced from `sigma_min` (default 0.01") to twice the pixel scale — compact relative to the
resolution of the data, which is what makes it read as a point source rather than a small galaxy
(`PyAutoGalaxy:autogalaxy/analysis/model_util.py`).
"""
point = ag.model_util.mge_point_model_from(
    pixel_scales=PIXEL_SCALES,
    total_gaussians=10,
    centre=(0.0, 0.0),
)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, point=point)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

print(model.info)
```

Adapted from `autogalaxy_workspace:scripts/imaging/features/multi_gaussian_expansion/modeling.py`,
whose `__Point Source__` section builds the same basis line by line first if you want to see
inside the helper. Four extra parameters on top of the bulge MGE.

There is a genuinely different approach to the same problem — an **operated** light profile,
which is assumed to be already PSF-convolved and so bypasses the convolution entirely. Which
to pick, and why a compact model source is so sensitive to sub-pixel placement, is
[`ag_light_model_extras`](./ag_light_model_extras.md) and
[`../wiki/core/concepts/sky_background_and_operated_profiles.md`](../wiki/core/concepts/sky_background_and_operated_profiles.md).

## Branch — shapelets, and the price of a signed solver

Shapelets are an orthonormal basis of Gauss–Hermite (Cartesian) or Gauss–Laguerre (polar)
functions on a single scale `beta`, introduced for exactly this problem
(Refregier 2003, arXiv:astro-ph/0105178). Because the basis is complete, it can represent
morphology an MGE smooths over — the disky, star-forming structure the workspace cites them
for. But completeness has a price, and it is a physical one.

**Shapelets require negative amplitudes.** The higher-order basis functions oscillate in sign,
and reproducing an arbitrary shape means combining them with signed coefficients. Every other
branch in this skill uses a positive-only linear solver, because a negative surface brightness
is not a thing a galaxy has. Shapelets cannot: you must pass
`ag.Settings(use_positive_only_solver=False)`, and the reconstructed light *will* contain
negative flux — verified, not assumed. That is not a numerical wrinkle to ignore; it is the
model telling you it is a mathematical fit rather than a physical decomposition, and it is why
the workspace recommends trying an MGE alongside.

```python
"""
__Model__

A polar shapelet basis to order n = 5: 11 `ShapeletPolar` components whose `n` and `m` indices
are fixed by construction, sharing one centre, one ellipticity and one scale `beta`. `beta` is
the only shape parameter — it sets the physical size the whole basis is expressed on, so its
prior matters more here than any single amplitude
(`PyAutoGalaxy:autogalaxy/profiles/light/linear/shapelets/polar.py`).
"""
total_n = 5
total_m = sum(range(2, total_n + 1)) + 1

shapelets_bulge_list = af.Collection(
    af.Model(ag.lp_linear.ShapeletPolar) for _ in range(total_n + total_m)
)

n_count = 1
m_count = -1

for shapelet in shapelets_bulge_list:
    shapelet.n = n_count
    shapelet.m = m_count

    m_count += 2

    if m_count > n_count:
        n_count += 1
        m_count = -n_count

    shapelet.centre = shapelets_bulge_list[0].centre
    shapelet.ell_comps = shapelets_bulge_list[0].ell_comps
    shapelet.beta = shapelets_bulge_list[0].beta

bulge = af.Model(ag.lp_basis.Basis, profile_list=shapelets_bulge_list)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

print(f"Total free parameters = {model.total_free_parameters}")

"""
__Analysis__

The signed solver is requested through `ag.Settings`, which is passed to the analysis rather
than to the model — it is a property of how the inversion is solved, not of what is being
fitted (`PyAutoArray:autoarray/settings.py`).
"""
analysis = ag.AnalysisImaging(
    dataset=dataset,
    settings=ag.Settings(use_positive_only_solver=False),
    use_jax=True,
)
```

**N = 5**: centre (2), `ell_comps` (2), `beta` (1). Adapted from
`autogalaxy_workspace:scripts/imaging/features/shapelets/modeling.py` — note that the workspace
loop as written does *not* link `ell_comps` across the basis, which leaves each shapelet's
ellipticity free and inflates the model to N = 43 rather than the N = 3 its prose claims. The
line `shapelet.ell_comps = shapelets_bulge_list[0].ell_comps` above is the fix; N = 3 is what
you get from the spherical variant `ag.lp_linear.ShapeletPolarSph`, which has no `ell_comps` at
all. Check `model.total_free_parameters` rather than trusting a comment — including this one.

Polar shapelets suit radially organised light, which is most galaxies.
`ag.lp_linear.ShapeletCartesian` (indexed by `n_y`, `n_x` instead of `n`, `m`) and
`ag.lp_linear.ShapeletExponential` are the other two families; the Cartesian basis is not
generally recommended for galaxies. You can see what a basis actually looks like before fitting
anything:

```python
shapelets = [
    ag.lp_linear.ShapeletCartesian(
        n_y=y, n_x=x, centre=(0.0, 0.0), ell_comps=(0.0, 0.0), beta=1.0
    )
    for x in range(5)
    for y in range(5)
]

basis = ag.lp_basis.Basis(profile_list=shapelets)

aplt.subplot_basis_image(
    basis=basis,
    grid=ag.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.05),
    output_path="scripts/scratch/shapelet_basis/",
    output_format="png",
)
```

`subplot_basis_image` renders every component of the basis on a grid, which is the fastest way
to build intuition for what `beta` and the order limit are buying you. It takes `output_path` /
`output_format` but **not** `output_filename` — give each variant its own directory
([`../wiki/core/api/plotting.md`](../wiki/core/api/plotting.md) tabulates that split). Print the
absolute path and offer to open it.

Shapelets also cost about 0.37 s per likelihood evaluation for ~60 components in the workspace's
measurement — slower than linear profiles, comparable to an MGE, and with more free parameters
than an MGE of similar flexibility. The workspace's own recommendation is to run both and
compare; the concept page
[`../wiki/core/concepts/shapelets.md`](../wiki/core/concepts/shapelets.md) has the full
when-to-use discussion.

## Choosing between the three

Fit them in order and let the residuals decide, because each step is cheap given the last:

1. **Single linear Sersic** — the reference every other fit is judged against, and the source of
   the size and concentration you will actually quote. Six parameters.
2. **Linear bulge plus disk** — if the science is a bulge-to-total ratio, this *is* the answer;
   a basis will fit better and tell you less. Nine parameters.
3. **MGE, `gaussian_per_basis=2`** — if the residuals show a twist or a radially varying
   ellipticity. Six parameters, better fit, less interpretable.
4. **Shapelets** — if the MGE still leaves disky or asymmetric structure and you accept a signed
   solution. Five parameters.
5. **Neither is enough** — the residuals sit in discrete off-centre lumps, and no basis with a
   single shared centre will absorb them. That is
   [`ag_pixelization`](./ag_pixelization.md).

An MGE and a shapelet basis can be compared by Bayesian evidence only with care, because they
solve different linear problems (positive-only versus signed). Compare them on the residual map
and the chi-squared first, and ask if you want the evidence caveats spelled out.

## Combine — where this hands off

- **Pick a search** → [`ag_configure_search`](./ag_configure_search.md). Basis models want
  *fewer* live points than a parametric fit, not more — the workspace drops `n_live` to 75 for
  both linear profiles and the MGE — because the parameter space is simpler.
- **Run it and read the output folder** → [`ag_run_search`](./ag_run_search.md).
- **Plot the fit** → [`ag_plot_fit`](./ag_plot_fit.md), remembering that a linear profile has to
  go through `model_obj_linear_light_profiles_to_light_profiles` before it can be plotted.
- **The basis fits worse than you expected, or the search stalls** →
  [`ag_debug_fit_failure`](./ag_debug_fit_failure.md). The two failure modes specific to this
  skill are a `sigma` ladder that stops short of the mask radius, and a free `sigma` or `beta`
  reintroducing a size degeneracy.
- **Structured residuals a basis cannot reach** → [`ag_pixelization`](./ag_pixelization.md).
- **A neighbour overlapping the galaxy, a residual sky, or a nuclear point source** →
  [`ag_light_model_extras`](./ag_light_model_extras.md).
- **A non-parametric shape measurement instead of a model** →
  [`ag_ellipse_fitting`](./ag_ellipse_fitting.md), which measures the isophotal twist directly
  rather than inferring it from a two-basis MGE.
- **The same galaxy in several bands** → the multi-dataset skill (`ag_multi_dataset`). A basis
  across bands is where the factor graph earns its keep, since the shape can be shared while
  the amplitudes are solved per band.
- **Chaining a parametric fit into a basis fit** → the search-chaining skill
  (`ag_chain_searches`); a Sersic fit's centre and ellipticity make excellent starting priors
  for an MGE.

Offer (default-yes) a dated `wiki/project/YYYY-MM-DD-<slug>.md` entry recording which tier you
used, `total_gaussians` / `gaussian_per_basis` or the shapelet order, the solver you chose, and
what the residuals looked like at each step — the last is the evidence for the model choice and
the first thing a referee will ask for.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Linear profiles](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_2_modeling/tutorial_5_linear_profiles.ipynb):
  builds up from a standard profile to a linear one to a basis, showing what the inversion
  actually solves at each step.
- **General reference** — [RTD: Light profiles API](https://pyautogalaxy.readthedocs.io/en/latest/api/light.html):
  every standard, linear, operated and basis variant with its module and parameters.
- **Experienced PyAutoGalaxy user** — [workspace: imaging/features/multi_gaussian_expansion/modeling.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/imaging/features/multi_gaussian_expansion/modeling.py):
  the MGE end to end, including the compact nuclear basis and the run-time and VRAM discussion.

## Agent procedural checklist

1. Ask whether the user needs interpretable Sersic parameters or the best achievable fit — that
   choice, not the API, picks the branch.
2. Look at the residual map of a single linear Sersic first; structured-but-smooth residuals mean
   a basis, discrete lumps mean `ag_pixelization`.
3. Default to `ag.lp_linear` for every parametric component; never use `ag.lp` in a model
   without a reason.
4. For an MGE, pass the real `mask_radius`, and reach for `gaussian_per_basis=2` when the
   isophotes twist.
5. For shapelets, pass `ag.Settings(use_positive_only_solver=False)` on the *analysis*, link
   `ell_comps` across the basis, and tell the user the reconstruction may contain negative flux.
6. Always check `model.total_free_parameters` against what you intended — a basis's `model.info`
   is long and mostly fixed, and one unlinked parameter multiplies by the component count.
7. Evaluate one likelihood before committing to a search; run `print_vram_use` before a GPU run
   with a large basis.
8. Read intensities out via `max_log_likelihood_galaxies`,
   `fit.linear_light_profile_intensity_dict`, or
   `model_obj_linear_light_profiles_to_light_profiles` — never expect them in `model.results`.
9. Save the script to `scripts/`, quote every plot's absolute path and offer to open it, then
   offer the `wiki/project/` entry.
