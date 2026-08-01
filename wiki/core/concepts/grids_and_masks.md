---
title: Grids, masks and over-sampling
sources:
  - project: PyAutoArray
    paths:
      - autoarray/structures/grids/uniform_2d.py
      - autoarray/mask/mask_2d.py
      - autoarray/operators/over_sampling/over_sample_util.py
      - autoarray/dataset/imaging/dataset.py
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/data_structures.py
      - scripts/guides/advanced/over_sampling.py
      - scripts/imaging/start_here.py
      - scripts/imaging/features/linear_light_profiles/modeling.py
      - scripts/imaging/features/extra_galaxies/modeling.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 47519ec342e5f3d8a5a22ab9c462b1a439554ef0942264eb68eccada68e51e4b
---

# Grids, masks and over-sampling

Three geometric decisions sit underneath every galaxy fit: **where** the model is
evaluated (`Grid2D`), **which** pixels enter the likelihood (`Mask2D`), and **how
accurately** each pixel's flux is integrated (over-sampling). All three are numerical
choices with direct scientific consequences — a mask that clips the outer isophotes biases
the effective radius and Sersic index; an under-sampled centre biases the concentration.

Sources: `PyAutoArray:autoarray/structures/grids/uniform_2d.py`,
`PyAutoArray:autoarray/mask/mask_2d.py` and
`PyAutoArray:autoarray/operators/over_sampling/over_sample_util.py`. Worked guides:
`autogalaxy_workspace:scripts/guides/data_structures.py` and
`autogalaxy_workspace:scripts/guides/advanced/over_sampling.py`.

## Grid2D

A `Grid2D` is a set of 2D `(y, x)` coordinates **in arcseconds**, on which profiles are
evaluated:

```python
import autogalaxy as ag

grid = ag.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.1)
```

- **`shape_native`** — `(y_pixels, x_pixels)`.
- **`pixel_scales`** — arcseconds per pixel; a scalar for square pixels or `(dy, dx)`.
  Getting this wrong silently rescales every angular result in the fit, so check it
  against your instrument (JWST/NIRCam ≈ 0.03″, HST/ACS ≈ 0.05″, Euclid VIS ≈ 0.1″).

Coordinates are centred on `(0.0, 0.0)`, which is also where the modelling examples assume
the galaxy sits. If your galaxy is not near the centre of the cutout, either re-cut the
data or override the centre priors — do not leave it to chance.

Other constructors: `ag.Grid2D.from_mask(mask=mask)` (only unmasked pixels),
`ag.Grid2D.no_mask(values=..., pixel_scales=...)` (from an explicit array), and
`ag.Grid2DIrregular(values=[(y, x), ...])` for an arbitrary list of coordinates — the tool
for 1D radial profiles.

### slim and native

Every data structure in the stack carries two views of the same numbers:

- **`.slim`** — a flat 1D array of length `total_unmasked_pixels`. This is what the
  likelihood actually operates on.
- **`.native`** — the 2D `(y, x)` layout, for display and FITS output.

`Array2D` (images, noise-maps, chi-squared maps), `Grid2D` and `VectorYX2D` all share this
API. `autogalaxy_workspace:scripts/guides/data_structures.py`. The practical rule: index
and plot with `.native`, do arithmetic with `.slim`, and never assume a returned array is
2D — most methods hand back `slim` by default.

## Mask2D

A boolean array marking which pixels are **excluded**. The convention is that `True` means
masked out.

```python
mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=2.5,
)

dataset = dataset.apply_mask(mask=mask)
```

`autogalaxy_workspace:scripts/imaging/start_here.py`. Constructors on
`PyAutoArray:autoarray/mask/mask_2d.py` include `circular`, `circular_annular`,
`elliptical`, `elliptical_annular`, `all_false`, and `from_fits(file_path=...,
pixel_scales=..., invert=False)` for a mask drawn by hand or by a preparation GUI.

### Choosing the radius is a science decision

For galaxy structure the mask radius is not a performance knob, it is part of the
measurement:

- **Too tight** and the outer isophotes are cut off. Because `sersic_index` and
  `effective_radius` are constrained mostly by the *wings* of the profile, truncating them
  biases both — typically toward a smaller radius and a lower index — and the formal error
  bars will not reveal it.
- **Too loose** and you pay for empty sky in every likelihood evaluation, and drag in
  neighbouring objects and reduction artefacts.

So the radius should be set from looking at the data: large enough to enclose the emission
out to where it meets the sky, small enough to exclude contaminants. The workspace
examples make this explicit by naming a `mask_radius` variable and reusing it downstream
(for the MGE's Gaussian widths, for ellipse major axes), which keeps the model's radial
extent consistent with the data actually being fitted.

Anything inside the mask that is *not* the galaxy you are modelling — a companion, a
foreground star, a diffraction spike — should be handled with noise scaling rather than by
shrinking the mask. See
[`extra_galaxies_and_noise_scaling`](./extra_galaxies_and_noise_scaling.md).

## Over-sampling

Evaluating a light profile only at each pixel's centre assumes the surface brightness is
constant across the pixel. For a Sersic core that assumption fails badly: the
`over_sampling` guide measures fractional errors above **10%** in the central pixels of an
`n = 3`, `R_eff = 0.2″` profile at `0.1″` pixels when no over-sampling is used, falling
below 1% only once each pixel is split into a fine sub-grid.
`autogalaxy_workspace:scripts/guides/advanced/over_sampling.py`.

Over-sampling fixes this by evaluating the profile on an `N × N` sub-grid inside each pixel
and averaging. `over_sample_size` may be a single integer (uniform) or an array with a
value per pixel (adaptive). The sub-grid lives on `grid.over_sampled`; `grid` itself is
unchanged, which is why printing a grid before and after setting `over_sample_size` looks
identical.

The cost is quadratic: a `32 × 32` sub-grid evaluates 1024 sub-pixels per pixel and is
~1000× slower than none. Since the residuals fall off rapidly away from a profile's centre,
the right answer is to spend the sub-pixels only where the gradient is steep.

### Adaptive radial binning

```python
over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[8, 4, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)

dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)
```

`autogalaxy_workspace:scripts/imaging/features/linear_light_profiles/modeling.py`. Read it
as: `8 × 8` inside `0.3″`, `4 × 4` between `0.3″` and `0.6″`, `2 × 2` beyond `0.6″`. The
`radial_list` has one fewer entry than `sub_size_list` because the last bin runs to the
mask edge, and `centre_list` may hold **several** centres so that each galaxy in a blended
field is over-sampled about its own core
(`autogalaxy_workspace:scripts/imaging/features/extra_galaxies/modeling.py` passes three).

### The 2×2 outer floor

**`sub_size_list` never ends in `1`.** Every current workspace script terminates it at `2`
— `[4, 2, 2]`, `[8, 4, 2]`, `[24, 8, 2]`, `[32, 8, 2]` — and a `2 × 2` outer floor is the
convention to follow in any script you write.

The reason is that `1` means *no* over-sampling at all in the outskirts, and the outskirts
are precisely where a galaxy's shallow-but-wide wings contribute most of its total flux.
The per-pixel error out there is small, but it is systematic in one direction across a
large number of pixels, so it accumulates into a bias on exactly the quantities the wings
constrain: total luminosity, effective radius and Sersic index. A `2 × 2` sub-grid is four
sub-pixels — a negligible cost next to the `8 × 8` or `24 × 24` core — and it removes that
bias. Ending the list at `1` saves almost nothing and buys a measurement you cannot fully
trust.

If you inherit a script whose list ends in `1`, change it to `2`; prose in older material
that describes a `1 × 1` outer bin is stale.

### lp vs pixelization

Light profiles and pixelised reconstructions use **separate** grids with separate
over-sampling, so `apply_over_sampling` takes two keywords:

```python
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)
dataset = dataset.apply_over_sampling(over_sample_size_pixelization=4)
```

`autogalaxy_workspace:scripts/guides/advanced/over_sampling.py`. For a pixelisation the
sub-grid controls how finely each image pixel's fractional mappings onto the mesh are
computed rather than how a smooth profile is integrated; a uniform `4` is the usual
starting point. In a hybrid fit (a parametric bulge plus a pixelisation) set both, and
remember the `lp` scheme only needs to be aggressive at the parametric component's centre.
See [`inversions_and_pixelizations`](./inversions_and_pixelizations.md).

### Defaults

A bare `Grid2D` defaults to `over_sample_size=4` — uniform `4 × 4` across the whole image
(`PyAutoArray:autoarray/structures/grids/uniform_2d.py`). That is a deliberately
centre-agnostic default: adaptive binning needs to be told where the galaxy is, and the
library cannot know. Uniform `4 × 4` is fine for quick exploration; every modelling
example switches to an adaptive scheme, because a fit *does* assume the galaxy is at
`(0.0, 0.0)` and can therefore afford a much finer core.

## Common mistakes

- **A mask that clips the outer isophotes** — biases `effective_radius` and
  `sersic_index`, invisibly.
- **`sub_size_list` ending in `1`** — see above.
- **Forgetting a second galaxy in `centre_list`** — its core is under-evaluated while the
  main galaxy's is not, so the residual map looks like a model failure rather than a
  numerical one.
- **Applying over-sampling before `apply_mask`** — build the scheme from
  `dataset.grid` *after* masking, since the grid it must match is the masked one.
- **A wrong `pixel_scales`** — every arcsecond in the result is wrong by the same factor
  and nothing in the fit complains.

## See also

- [`../api/datasets`](../api/datasets.md) — `ag.Imaging` / `ag.Interferometer` and their
  `apply_*` methods.
- [`light_profiles`](./light_profiles.md) — why a steep core needs the sub-grid.
- [`extra_galaxies_and_noise_scaling`](./extra_galaxies_and_noise_scaling.md) —
  down-weighting contaminants instead of masking them away.
- [`inversions_and_pixelizations`](./inversions_and_pixelizations.md) — the second
  over-sampling scheme.
- [`interferometer_theory`](./interferometer_theory.md) — the real-space mask plays the
  same role for visibility data.
- [`../stack/autoarray`](../stack/autoarray.md) — where these structures live.
