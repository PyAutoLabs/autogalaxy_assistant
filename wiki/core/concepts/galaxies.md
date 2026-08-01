---
title: Galaxy and Galaxies
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/galaxy/galaxy.py
      - autogalaxy/galaxy/galaxies.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/galaxies.py
      - scripts/imaging/start_here.py
      - scripts/imaging/features/linear_light_profiles/modeling.py
      - scripts/guides/results/start_here.py
      - scripts/guides/units/cosmology.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 0144d127e9cc512639375a9bea805e10afbb4527979a54004d25d39e35ab5ab1
---

# Galaxy and Galaxies

`ag.Galaxy` is the object between a light profile and a fit. It bundles one or more
profiles with a **redshift**, and it is the level at which the model is addressed
(`model.galaxies.galaxy.bulge`). `ag.Galaxies` is a list-like collection whose summed
emission is what gets compared to the data.

Sources: `PyAutoGalaxy:autogalaxy/galaxy/galaxy.py` and
`PyAutoGalaxy:autogalaxy/galaxy/galaxies.py`. Worked tour:
`autogalaxy_workspace:scripts/guides/galaxies.py`.

## Galaxy

```python
import autogalaxy as ag

bulge = ag.lp.Sersic(
    centre=(0.0, 0.0),
    ell_comps=ag.convert.ell_comps_from(axis_ratio=0.9, angle=45.0),
    intensity=1.0,
    effective_radius=0.6,
    sersic_index=3.0,
)

disk = ag.lp.Exponential(
    centre=(0.0, 0.0),
    ell_comps=ag.convert.ell_comps_from(axis_ratio=0.7, angle=30.0),
    intensity=0.5,
    effective_radius=1.6,
)

galaxy = ag.Galaxy(redshift=0.5, bulge=bulge, disk=disk)

image = galaxy.image_2d_from(grid=grid)
```

`autogalaxy_workspace:scripts/guides/galaxies.py`. Four things to internalise:

- **The attribute names are arbitrary.** `bulge` and `disk` are conventions, not enum
  values. `ag.Galaxy(redshift=0.5, bar=..., nucleus=..., clump_0=...)` is equally valid,
  and the name you choose becomes the key you address in the model and in the results
  (`result.max_log_likelihood_galaxies[0].bar`). Name components for what they measure —
  the name is the only record of your physical intent that survives into `model.info`.
- **A galaxy holds arbitrarily many profiles.** `galaxy.image_2d_from(grid=...)` returns
  their **sum**. Each is still individually reachable (`galaxy.bulge.image_2d_from(...)`),
  which is how you produce a bulge/disc decomposition figure.
- **`redshift` is required**, and in a model it is normally passed as a plain float
  (fixed, not a free parameter). It does not change the shape of the light on the sky; it
  is what turns arcseconds into kiloparsecs and an intensity into a luminosity. See
  [`cosmology_and_units`](./cosmology_and_units.md).
- **A galaxy can carry a pixelisation instead of, or alongside, profiles** —
  `ag.Galaxy(redshift=0.5, bulge=..., pixelization=ag.Pixelization(...))`. See
  [`inversions_and_pixelizations`](./inversions_and_pixelizations.md).

Derived quantities available directly on a galaxy
(`PyAutoGalaxy:autogalaxy/galaxy/galaxy.py`):

```python
galaxy.image_2d_from(grid=grid)                  # summed surface brightness
galaxy.image_2d_list_from(grid=grid)             # one image per profile
galaxy.blurred_image_2d_from(...)                # PSF-convolved
galaxy.luminosity_within_circle_from(radius=np.inf)
galaxy.half_light_radius
```

`luminosity_within_circle_from(radius=np.inf)` integrates the profile to infinity and is
the honest way to get a *total* flux — summing pixels inside a mask always misses the
wings, and for a high-`n` Sersic that missing fraction is not small.
`autogalaxy_workspace:scripts/guides/units/cosmology.py`.

Because PyAutoGalaxy also ships mass profiles (`ag.mp.*`, and the combined light-and-mass
`ag.lmp.*` whose light and mass share a geometry), a galaxy additionally exposes
`convergence_2d_from(grid=...)` and `potential_2d_from(grid=...)`. Those are what you
reach for in stellar-mass or dynamical work — see
[`../api/mass_profile_catalog`](../api/mass_profile_catalog.md).

## Galaxies

`ag.Galaxies` is the collection whose **summed** emission the likelihood compares to the
data:

```python
galaxy_0 = ag.Galaxy(redshift=0.5, bulge=ag.lp.Sersic(centre=(0.0, -1.0), ...))
galaxy_1 = ag.Galaxy(redshift=0.5, bulge=ag.lp.Sersic(centre=(0.0, 1.0), ...))

galaxies = ag.Galaxies(galaxies=[galaxy_0, galaxy_1])

image = galaxies.image_2d_from(grid=grid)
```

`autogalaxy_workspace:scripts/guides/galaxies.py`. It is a genuine sequence — index it
(`galaxies[0]`), iterate it, and reach through to a component in one line
(`galaxies[0].bulge.image_2d_from(grid=grid)`).

One galaxy is the ordinary case. Several are needed when the emission of separate objects
genuinely **blends on the sky**: an interacting or merging pair, a bright companion, a
foreground star, a cluster's member population. There is no plane structure and no
redshift ordering involved — the collection simply superposes surface brightness, which
is exactly right because light adds linearly. Two galaxies at different redshifts in the
same `Galaxies` still just add: PyAutoGalaxy models the **single-plane** problem of what
the sky looks like, and the redshifts are metadata for unit conversion, not a geometry.

Useful collection-level accessors:

```python
galaxies.image_2d_list_from(grid=grid)      # one image per galaxy
galaxies.galaxy_image_2d_dict_from(...)     # keyed by galaxy
galaxies.blurred_image_2d_from(...)         # PSF-convolved sum
```

When several galaxies are in play, remember that over-sampling is applied *per centre*:
`over_sample_size_via_radial_bins_from` takes a `centre_list`, and every galaxy's centre
must be in it or that galaxy's core is under-evaluated. See
[`grids_and_masks`](./grids_and_masks.md) and
[`extra_galaxies_and_noise_scaling`](./extra_galaxies_and_noise_scaling.md).

## Galaxies in a model

For fitting, wrap the **class** in `af.Model` and pass model components as keyword
arguments:

```python
import autofit as af
import autogalaxy as ag

bulge = af.Model(ag.lp_linear.Sersic)
disk = af.Model(ag.lp_linear.Exponential)
bulge.centre = disk.centre        # one shared centre, not two

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))
```

`autogalaxy_workspace:scripts/imaging/features/linear_light_profiles/modeling.py`. Points
worth stating explicitly:

- **`redshift=0.5` is a value, so it is fixed.** Wrap it in a prior only if you really
  intend to fit it, which for imaging alone you almost never do.
- **`bulge.centre = disk.centre` identifies the two priors** rather than copying values:
  the search then samples one shared centre. This is the standard bulge/disc idiom, and it
  removes two dimensions plus a strong degeneracy. Relax it only when you have evidence
  the components are genuinely offset.
- **The outer `af.Collection(galaxies=...)` structure is what the analysis expects.** The
  key `galaxies` is fixed; the inner key (`galaxy`) is yours to choose and becomes part of
  every results path. Additional top-level keys are how non-galaxy model components enter
  — `dataset_model=af.Model(ag.DatasetModel)` for a sky level or an astrometric offset
  ([`sky_background_and_operated_profiles`](./sky_background_and_operated_profiles.md)),
  and `extra_galaxies=af.Collection(...)` for companions
  ([`extra_galaxies_and_noise_scaling`](./extra_galaxies_and_noise_scaling.md)).

## Galaxies out of a fit

A completed search returns galaxies at their inferred values:

```python
galaxies = result.max_log_likelihood_galaxies
print(galaxies[0].bulge.intensity)
```

For **linear** light profiles this object matters more than it looks: `intensity` is not a
sampled parameter, so it is absent from `samples.csv` and defaults to `1.0` in a raw
`Samples` instance. `result.max_log_likelihood_galaxies` has had the inversion performed,
so its profiles carry the solved intensities.
`autogalaxy_workspace:scripts/guides/results/start_here.py`. Details and the
`FitImaging`-based route for arbitrary posterior samples are in
[`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md).

The maximum-likelihood galaxies are also written to `files/galaxies.json` in the output
folder and reload with `ag.from_json(...)` — which returns a plain `list` of `Galaxy` objects,
**not** an `ag.Galaxies`. Wrap it (`ag.Galaxies(galaxies=galaxies)`) before calling any of the
collection methods below.

## Plotting

```python
import autogalaxy.plot as aplt

aplt.plot_array(array=galaxies.image_2d_from(grid=grid), title="Image", use_log10=True)
aplt.subplot_galaxies(galaxies=galaxies, grid=grid)
```

`use_log10=True` is worth reaching for by default: a galaxy's surface brightness spans
orders of magnitude, and a linear stretch hides everything outside the core. The plot API
is functional only — see [`../api/plotting`](../api/plotting.md).

## See also

- [`light_profiles`](./light_profiles.md) — what goes inside a galaxy.
- [`../api/analysis_objects`](../api/analysis_objects.md) — handing galaxies to a
  likelihood.
- [`extra_galaxies_and_noise_scaling`](./extra_galaxies_and_noise_scaling.md) — companions
  and contaminants in the field.
- [`inversions_and_pixelizations`](./inversions_and_pixelizations.md) — a galaxy whose
  light is reconstructed on a mesh rather than parameterised.
- [`cosmology_and_units`](./cosmology_and_units.md) — what the redshift is for.
- [`../stack/autogalaxy`](../stack/autogalaxy.md) — the library map.
