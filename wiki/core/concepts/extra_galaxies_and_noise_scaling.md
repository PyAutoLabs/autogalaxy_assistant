---
title: Extra galaxies and noise scaling
sources:
  - project: PyAutoArray
    paths:
      - autoarray/dataset/imaging/dataset.py
      - autoarray/mask/mask_2d.py
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/galaxy/galaxy.py
      - autogalaxy/analysis/model_util.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/imaging/features/extra_galaxies/modeling.py
      - scripts/imaging/features/extra_galaxies/README.md
      - scripts/imaging/start_here.py
      - scripts/imaging/data_preparation/gui/mask_extra_galaxies.py
      - scripts/imaging/data_preparation/examples/optional/extra_galaxies_centres.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: f5cfa83472eff8a88d69976437b1271e6826392bd7d79ce8c21bddb690cee67d
---

# Extra galaxies and noise scaling

An **extra galaxy** is any light in the frame that is not the galaxy you are modelling: a
companion or neighbour, a projected background object, a foreground star, a diffraction
spike, a reduction artefact. Its emission blends into the field around your target and, left
untreated, the fit will try to explain it with your galaxy's model — inflating the effective
radius, dragging the centre, distorting the ellipticity.

**This is the most common way a real-data fit goes wrong.** Plot the dataset and look for
contaminants *before* composing a model; that is a standing requirement of this assistant
(see [`../../../AGENTS.md`](../../../AGENTS.md), the real-data gate), not a suggestion.

Sources: `PyAutoArray:autoarray/dataset/imaging/dataset.py` (`apply_noise_scaling`) and
`PyAutoArray:autoarray/mask/mask_2d.py`. Worked example:
`autogalaxy_workspace:scripts/imaging/features/extra_galaxies/modeling.py`.

## Three strategies

Which one is right depends on how close the contaminant is and whether its light overlaps
the emission you are measuring.

1. **Noise-scale it — the recommended default.** Keep the pixels in the dataset, but set
   their data values to zero and inflate their noise-map values to very large numbers, so
   they contribute negligibly to the likelihood.
2. **Model it.** Add the extra galaxy to the model as its own `Galaxy` with a light profile,
   so its emission is fitted and subtracted. Use this when its light genuinely overlaps your
   target's.
3. **Shrink the mask.** Exclude the contaminant geometrically. Simplest, and fine when it is
   well separated — but it removes pixels rather than down-weighting them.

Strategies 1 and 3 differ in a way that matters: `apply_mask` **removes** pixels from the
fit; `apply_noise_scaling` **keeps** them and makes them uninformative. For a fit using a
pixelisation that distinction is decisive, because hard-removing a patch inside the modelled
region can create discontinuities in the mesh and generate systematics. Prefer noise scaling
near any pixelised reconstruction. See
[`inversions_and_pixelizations`](./inversions_and_pixelizations.md) and
[`grids_and_masks`](./grids_and_masks.md).

## Noise scaling

Noise scaling needs a FITS mask flagging the contaminating pixels. Load it **inverted**, so
that `True` marks the pixels to scale, and apply it *before* the modelling mask and
over-sampling:

```python
import autogalaxy as ag

mask_extra_galaxies = ag.Mask2D.from_fits(
    file_path=dataset_path / "mask_extra_galaxies.fits",
    pixel_scales=dataset.pixel_scales,
    invert=True,  # `True` means a pixel is scaled.
)

dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)

mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=6.0,
)
dataset = dataset.apply_mask(mask=mask)
```

`autogalaxy_workspace:scripts/imaging/start_here.py`. After it is applied,
`aplt.subplot_imaging_dataset(dataset=dataset)` shows the scaled regions as zeroed data with
a very large noise-map — their signal-to-noise is effectively zero.

Two ordering traps:

- **Scale first, mask second.** Masking trims the array for the FFT, so a mask applied first
  can leave the noise-scaling mask misaligned with the data. The workspace reloads the
  dataset from FITS before noise scaling for exactly this reason.
- **Only the region inside the eventual modelling mask matters.** Scaling noise far outside
  the mask is harmless but pointless; what you must get right is the overlap.

The `mask_extra_galaxies.fits` itself is produced interactively with the data-preparation GUI
(`autogalaxy_workspace:scripts/imaging/data_preparation/gui/mask_extra_galaxies.py`), or by
hand. `ag.Scribbler` is the brush-based tool behind the GUI; `autogalaxy_workspace:scripts/imaging/start_here.py`
shows it in use, ending with `aplt.fits_array(...)` to write the mask out.

When a bundled or shared dataset ships with a `mask_extra_galaxies.fits`, apply it — and say
out loud which region it scales away. Silently removing part of someone's data is never
acceptable.

## Modelling the extra galaxies

When a neighbour's light overlaps your target's, down-weighting it also down-weights the
target. Then it is better to fit it. Extra galaxies enter the model as their own top-level
collection:

```python
import autofit as af
import autogalaxy as ag

extra_galaxies_centres = ag.Grid2DIrregular(
    ag.from_json(file_path=dataset_path / "extra_galaxies_centres.json")
)

extra_galaxies_list = []

for extra_galaxy_centre in extra_galaxies_centres:
    extra_galaxy = af.Model(
        ag.Galaxy,
        redshift=0.5,
        bulge=ag.lp_linear.SersicSph,
    )
    extra_galaxy.bulge.centre = extra_galaxy_centre
    extra_galaxies_list.append(extra_galaxy)

extra_galaxies = af.Collection(extra_galaxies_list)

model = af.Collection(
    galaxies=af.Collection(galaxy=galaxy), extra_galaxies=extra_galaxies
)
```

`autogalaxy_workspace:scripts/imaging/features/extra_galaxies/modeling.py`. The design
decisions inside that snippet are the whole point of the feature:

- **Centres are fixed to measured positions.** A model with free centres for several faint
  companions is usually unfittable: the parameter space is multi-modal, and a common failure
  is one companion's profile wandering onto another object. Fixing the centres (or putting
  tight priors on them) collapses that. Measure them from the brightest pixel of each object
  with
  `autogalaxy_workspace:scripts/imaging/data_preparation/examples/optional/extra_galaxies_centres.py`,
  which writes them to a `.json`.
- **`SersicSph`, not `Sersic`.** A spherical profile drops the two ellipticity parameters. For
  a faint companion the data rarely constrains ellipticity anyway, and with a **linear**
  profile solving the amplitude the whole companion costs ~2 free parameters.
- **`extra_galaxies` is a sibling of `galaxies`.** It is a separate top-level key so the
  results and visualisation treat those objects as accessories rather than as the subject.

For a companion with genuinely irregular morphology, or once the number of extras grows
beyond a handful, swap the spherical Sersic for an MGE basis with a fixed centre:

```python
bulge = ag.model_util.mge_model_from(
    mask_radius=mask_radius,
    total_gaussians=10,
    centre_fixed=tuple(extra_galaxy_centre),
)
```

In the linear-light limit this costs the same two free parameters per galaxy while being far
more flexible. See [`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md).

### Don't forget the over-sampling centres

An extra galaxy has its own steep core, and the adaptive over-sampling scheme only refines
the centres you list:

```python
over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[4, 2, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)] + extra_galaxies_centres.in_list,
)

dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)
```

`autogalaxy_workspace:scripts/imaging/features/extra_galaxies/modeling.py`. Omit a
companion's centre and its core is numerically under-evaluated, which shows up as a residual
that looks like a bad model but is really a bad grid. See
[`grids_and_masks`](./grids_and_masks.md).

### Enlarge the mask

If you are modelling the extras, they must be *inside* the mask. The workspace example moves
from the usual 3.0″ radius to 6.0″ so both companions are included — the opposite of the
mask-shrinking strategy, and a reminder that the mask radius follows from the model you have
chosen.

### Cost

Evaluating a couple of extra `SersicSph` profiles is cheap. The real cost is dimensional: a
handful of extra parameters, and hence a longer search. VRAM also rises on a GPU, since each
component adds arrays JAX holds in memory.

## Why there is no scaling-relation tier

If you have met the companion-population machinery elsewhere in the PyAuto stack, note that
its shared-parameter trick does not carry over to a light-only fit. Tying many faint
companions' amplitudes to a small number of shared parameters is degenerate here, because a
linear light profile already solves each amplitude exactly by inversion — scaling it by a
further shared free parameter adds a dimension that the data cannot distinguish from the
solved value. `autogalaxy_workspace:scripts/imaging/features/extra_galaxies/README.md`
discusses this.

The right response to *many* companions in a light-only fit is a fixed-centre MGE per object
(above), which keeps the per-galaxy dimensionality at two regardless of how irregular each
one is.

## See also

- [`grids_and_masks`](./grids_and_masks.md) — `apply_mask` versus `apply_noise_scaling`, and
  multi-centre over-sampling.
- [`galaxies`](./galaxies.md) — several galaxies whose light superposes on the sky.
- [`inversions_and_pixelizations`](./inversions_and_pixelizations.md) — why hard masks and
  meshes do not mix.
- [`sky_background_and_operated_profiles`](./sky_background_and_operated_profiles.md) — the
  diffuse, rather than discrete, contaminant.
- [`../api/datasets`](../api/datasets.md) — the `apply_*` methods in full.
