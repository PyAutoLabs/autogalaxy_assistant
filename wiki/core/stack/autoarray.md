---
title: PyAutoArray (autoarray)
sources:
  - project: PyAutoArray
    paths:
      - autoarray/structures/
      - autoarray/dataset/
      - autoarray/mask/
      - autoarray/operators/
      - autoarray/inversion/
      - autoarray/config/
      - pyproject.toml
      - README.md
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
last_updated: 2026-08-01
content_sha256: 8f4425d067e527e01d00fa5a512a91dcf96de18071acb8cb5adfe1b43fe4e9a0
---

# PyAutoArray — arrays, grids, masks, datasets

Project: [`PyAutoArray`](https://github.com/PyAutoLabs/PyAutoArray). Import:
`autoarray`. PyAutoGalaxy re-exports the user-facing classes, so you meet them as
`ag.Array2D`, `ag.Grid2D`, `ag.Mask2D`, `ag.Imaging`, `ag.Interferometer`, etc., and
rarely import `autoarray` yourself.

PyAutoArray is the data + geometry layer. It defines the array containers a galaxy
analysis fits, the masks that select which pixels are fitted, the grids on which light
profiles are evaluated, and the dataset wrappers that hold imaging and visibility data
along with their PSFs and noise maps.

## Headline classes

| Class | Purpose | Source |
|---|---|---|
| `Array2D` | 2D array with native (y, x) layout + slim (1D over mask) layout | `autoarray/structures/arrays/uniform_2d.py` |
| `Grid2D` | 2D grid of (y, x) coordinates with over-sampling support | `autoarray/structures/grids/uniform_2d.py` |
| `Mask2D` | Boolean 2D mask, with `.circular`, `.elliptical`, `.from_fits` constructors | `autoarray/mask/mask_2d.py` |
| `Imaging` | Image + noise map + PSF dataset wrapper | `autoarray/dataset/imaging/dataset.py` |
| `Interferometer` | Visibilities + noise map + uv-coverage wrapper | `autoarray/dataset/interferometer/dataset.py` |
| `Convolver` | PSF + image-convolution operator | `autoarray/operators/convolver.py` |

## Slim vs. native

Arrays have two layouts:

- **`native`** — `(y_pixels, x_pixels)` 2D shape. This is what you'd plot.
- **`slim`** — 1D, only the pixels inside a mask. Most internal computation runs on the
  slim layout for speed.

```python
arr.native   # 2D for inspection / plotting
arr.slim     # 1D, masked subset, for fast math
```

The conversion is handled by the array's `Mask2D`.

## Over-sampling

For pixels near the centre of a steep light profile, single-point evaluation aliases the
analytic intensity. PyAutoArray supports adaptive sub-grid integration:

```python
import autogalaxy as ag

grid = ag.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.05)
over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=grid, sub_size_list=[8, 4, 2], radial_list=[0.3, 0.6], centre_list=[(0.0, 0.0)]
)
grid = grid.apply_over_sampling(over_sample_size=over_sample_size)
```

Sub-grids are denser where it matters and coarser everywhere else. Source:
`PyAutoArray:autoarray/operators/over_sampling/over_sample_util.py`.

## Inversions

Pixelised reconstruction of a galaxy's light lives in `autoarray/inversion/`. The
classes you touch through PyAutoGalaxy are `ag.Pixelization`, `ag.mesh.*`, `ag.reg.*`
and `ag.image_mesh.*` — these wrap the lower-level mesh / regularisation / mapper
machinery in `autoarray/inversion/mesh/`, `autoarray/inversion/regularization/` and
`autoarray/inversion/pixelization/`.

## Configuration

`autoarray/config/` ships `general.yaml`, `logging.yaml` and a `visualize/` directory.
The plot-label notation and output settings a user is more likely to edit live in
`autofit/config/` and `autogalaxy/config/` instead.

## Dependencies

`autonerves`, `astropy`, `decorator`, `dill`, `matplotlib`, `scipy`, `scikit-image`,
`scikit-learn`, `tqdm`. Optional extras add `numba` for JIT-acceleration of geometry
kernels, and `nufftax` / `pynufft` for visibility transforms.

## See also

- [`stack/autogalaxy`](./autogalaxy.md) — the profiles evaluated on these grids.
- [`stack/overview`](./overview.md) — where autoarray sits in the dependency chain.
