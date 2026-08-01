---
title: Aggregator — loading many completed fits
sources:
  - project: PyAutoFit
    paths:
      - autofit/aggregator/aggregator.py
      - autofit/aggregator/summary/
      - autofit/database/aggregator/aggregator.py
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/aggregator/
      - autogalaxy/aggregator/subplot.py
      - autogalaxy/aggregator/agg_util.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/results/start_here.py
      - scripts/guides/results/aggregator/
      - scripts/guides/results/database/start_here.py
      - scripts/guides/results/workflow/
      - scripts/ellipse/database.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 765f038d0ede9d9517685d0bf9d9f0da2fb2be5e78a506fcce0427c8f0593902
---

# Aggregator

The aggregator is what you reach for when the unit of work stops being *one fit*. A single result
is simpler to read straight off `search.fit(...)` (see [`analysis_objects`](./analysis_objects.md)).
For a sample — a hundred galaxies fitted with the same model, or one galaxy fitted with ten
different models — the aggregator gives you one query surface over all of them, and a way to turn
that surface into science-ready tables and figures.

Two layers stack:

1. **PyAutoFit's aggregator** loads whatever a search wrote to disk: samples, the model, the
   dataset, stored FITS and PNG files.
2. **PyAutoGalaxy's `ag.agg`** rebuilds *galaxy-domain* objects from those files — `ag.Galaxies`,
   `ag.FitImaging`, `ag.Ellipse` — as generators, so you can compute a galaxy quantity per fit
   without holding every fit in memory.

## Opening an aggregator

There are two different classes, and they are easy to confuse.

**Directory-backed** — scrapes an `output/` tree. This is the one every `guides/results` example
uses, and the right default:

```python
from pathlib import Path
from autofit.aggregator.aggregator import Aggregator

agg = Aggregator.from_directory(
    directory=Path("output") / "results_folder",
)
```

Adapted from `autogalaxy_workspace:scripts/guides/results/start_here.py`. Note the explicit import:
`Aggregator.from_directory` lives in `PyAutoFit:autofit/aggregator/aggregator.py` and is **not** the
same class as `af.Aggregator`. It also takes `completed_only=False` and `reference=None`. Its
methods are `from_directory`, `add_directory`, `values`, `child_values`, `query`, `group_by`,
`map`, `model_results`, `grid_searches`, `remove_unzipped`.

**Database-backed** — `af.Aggregator` wraps a SQLite file, and is the stable choice once the fit
count reaches the hundreds, because querying is much faster than re-reading a directory tree:

```python
import autofit as af

sqlite_path = Path("output") / f"{database_name}.sqlite"
if sqlite_path.exists():
    sqlite_path.unlink()

agg = af.Aggregator.from_database(
    filename=f"{database_name}.sqlite", completed_only=False
)

agg.add_directory(directory=Path("output") / database_name)
```

Adapted from `autogalaxy_workspace:scripts/ellipse/database.py` and
`autogalaxy_workspace:scripts/guides/results/database/start_here.py` — note that
`from_database(filename, completed_only=False, top_level_only=True)` has no overwrite flag, which
is why the example deletes a stale `.sqlite` itself. Source:
`PyAutoFit:autofit/database/aggregator/aggregator.py`. Its methods are `from_database`,
`add_directory`, `values`, `child_values`, `query`, `order_by`, `map`, `fits`, `info`, `search`,
`model`, `grid_searches`.

Start with the directory version; move to the database when loading from disk becomes the slow part.

## Everything is a generator

`agg.values(name)` returns a **generator**, not a list. That is deliberate: a sample of a thousand
fits would not fit in memory as concrete objects. The consequence is that a generator is consumed
once — remake it rather than storing it.

```python
for samples in agg.values("samples"):
    print(samples.parameter_lists[0])
```

Keys worth knowing: `"samples"` (the full sampling record), `"samples_info"`,
`"samples_summary"` (pre-computed maximum-likelihood values and 1σ/3σ errors — much faster,
because it does not re-derive anything from the full sample list), `"model"`, `"search"`,
`"dataset"`. `autogalaxy_workspace:scripts/guides/results/aggregator/samples_via_aggregator.py`
works through the `Samples` surface itself: `max_log_likelihood()`, `median_pdf()`,
`values_at_upper_sigma(sigma=3.0)`, `errors_at_lower_sigma(...)`, `log_likelihood_list`,
`log_evidence`.

## Querying

Queries are built from objects, and each returns a **new** aggregator, so filtering composes:

```python
unique_tag = agg.search.unique_tag
agg_query = agg.query(unique_tag == "simple")

bulge = agg.model.galaxies.galaxy.bulge
agg_query = agg.query((bulge == ag.lp_linear.Sersic) & (bulge.effective_radius > 3.0))
```

Adapted from `autogalaxy_workspace:scripts/guides/results/aggregator/queries.py`. Two query
surfaces:

- **`agg.search`** — fit-level fields: `name`, `unique_tag`, `path_prefix`, `is_complete`,
  `is_grid_search`.
- **`agg.model`** — the fitted model's own structure. `agg.model.galaxies.galaxy.bulge` addresses
  the model by the *names you chose* when composing it, so you can select on a component's class
  or on an inferred parameter value.

`agg.order_by(...)` (database aggregator) sorts; `agg.map(func)` applies a function per fit and
collects the results — the standard derived-quantity pattern for building a sample-level table.

## `ag.agg` — galaxy objects from stored fits

Each `*Agg` class takes an aggregator and hands back a generator of PyAutoGalaxy objects.

| Class | Yields |
|---|---|
| `ag.agg.ImagingAgg` | `ag.Imaging` datasets as fitted |
| `ag.agg.InterferometerAgg` | `ag.Interferometer` datasets |
| `ag.agg.GalaxiesAgg` | `ag.Galaxies` |
| `ag.agg.FitImagingAgg` | `ag.FitImaging` |
| `ag.agg.FitInterferometerAgg` | `ag.FitInterferometer` |
| `ag.agg.EllipsesAgg` | `ag.Ellipse` lists |
| `ag.agg.FitEllipseAgg` | `ag.FitEllipse` lists |
| `ag.agg.MultipolesAgg` | `ag.EllipseMultipole` lists |

```python
galaxies_agg = ag.agg.GalaxiesAgg(aggregator=agg)
galaxies_gen = galaxies_agg.max_log_likelihood_gen_from()

dataset_agg = ag.agg.ImagingAgg(aggregator=agg)
dataset_gen = dataset_agg.dataset_gen_from()

for galaxies, dataset in zip(galaxies_gen, dataset_gen):
    aplt.subplot_galaxies(galaxies=galaxies, grid=dataset.grid)
```

Adapted from `autogalaxy_workspace:scripts/guides/results/aggregator/models.py`.

The dataset classes expose `dataset_gen_from()`. The model classes share four generators, which is
where the aggregator earns its keep for population work:

| Generator | What you get |
|---|---|
| `max_log_likelihood_gen_from()` | the single best-fit object per fit |
| `randomly_drawn_via_pdf_gen_from(total_samples=...)` | objects drawn from the posterior — propagate uncertainty into a derived quantity |
| `all_above_weight_gen_from(minimum_weight=...)` | every sample above a posterior weight |
| `weights_above_gen_from(minimum_weight=...)` | the matching weights |
| `object_via_gen_from(...)` | the general hook the four above are built on |

`randomly_drawn_via_pdf_gen_from` is the honest way to put an error bar on something the fit did not
parameterise directly (a half-light radius, a luminosity within an aperture, a bulge-to-total
ratio): recompute it for each drawn galaxy and take the spread.

## The three figure/HDU enumerations

`ag.agg` exposes exactly three enumerations, which name the panels and HDUs that a completed fit
already has on disk. They are what you pass to the PyAutoFit export helpers below — you are
*extracting* existing output, not re-rendering it.

| Enumeration | Members |
|---|---|
| `ag.agg.fits_fit` | `model_data`, `residual_map`, `normalized_residual_map`, `chi_squared_map` |
| `ag.agg.subplot_dataset` | `data`, `data_log_10`, `noise_map`, `psf`, `psf_log_10`, `signal_to_noise_map`, `over_sample_size_lp`, `over_sample_size_pixelization` |
| `ag.agg.subplot_fit` | `data`, `signal_to_noise_map`, `model_data`, `normalized_residual_map`, `normalized_residual_map_one_sigma`, `chi_squared_map` |

Source: `PyAutoGalaxy:autogalaxy/aggregator/subplot.py`. (`ag.agg.agg_util` holds the shared
reconstruction helpers the `*Agg` classes use.)

## Workflow exports — CSV, FITS, PNG

The `guides/results/workflow/` examples use the aggregator as the layer between completed fits and
publishable products. Three PyAutoFit helpers, each taking `aggregator=agg`:

### `af.AggregateCSV`

```python
agg_csv = af.AggregateCSV(aggregator=agg)
agg_csv.add_variable(
    argument="galaxies.galaxy.bulge.sersic_index",
    value_types=[af.ValueType.Median, af.ValueType.ValuesAt3Sigma],
)
agg_csv.save(path=workflow_path / "results.csv")
```

Adapted from `autogalaxy_workspace:scripts/guides/results/workflow/csv_make.py`. Methods:
`add_variable`, `add_computed_column`, `add_label_column`, `fieldnames`, `save`.
`af.ValueType` has four members: `Median`, `MaxLogLikelihood`, `ValuesAt1Sigma`, `ValuesAt3Sigma`.

### `af.AggregateFITS`

```python
agg_fits = af.AggregateFITS(aggregator=agg)

hdu_list = agg_fits.extract_fits(
    hdus=[ag.agg.fits_fit.model_data, ag.agg.fits_fit.residual_map],
)
hdu_list.writeto("fits_make_single.fits", overwrite=True)

agg_fits.output_to_folder(
    folder=workflow_path,
    name="unique_tag",
    hdus=[ag.agg.fits_fit.model_data, ag.agg.fits_fit.residual_map],
)
```

Adapted from `autogalaxy_workspace:scripts/guides/results/workflow/fits_make.py`. `extract_fits`
returns one astropy `HDUList` holding the requested extensions for *every* fit;
`output_to_folder` writes one `.fits` per fit instead, named from a search attribute or from an
explicit list. `extract_csv` pulls tabular data out of any `.csv` a fit wrote into its `image/`
folder, returning a list of dictionaries.

### `af.AggregateImages`

```python
agg_image = af.AggregateImages(aggregator=agg)

image = agg_image.extract_image(
    subplots=[
        ag.agg.subplot_fit.data,
        ag.agg.subplot_fit.model_data,
        ag.agg.subplot_fit.normalized_residual_map,
    ],
)
image.save(workflow_path / "png_make_single_subplot.png")

agg_image.output_to_folder(
    folder=workflow_path,
    name="unique_tag",
    subplots=[
        ag.agg.subplot_fit.data,
        ag.agg.subplot_fit.model_data,
        ag.agg.subplot_fit.normalized_residual_map,
    ],
)
```

Adapted from `autogalaxy_workspace:scripts/guides/results/workflow/png_make.py`. `extract_image`
returns a PIL `Image` covering every fit the aggregator holds; `output_to_folder` writes one file
per fit instead, named from a search attribute (`name="unique_tag"` gives you the dataset names) or
from an explicit list. Panels can be mixed across subplots — `subplot_dataset.data` next to
`subplot_fit.chi_squared_map` — which is how you build a single figure per galaxy for a paper
appendix.

A folder of one-file-per-fit is often easier to review than a single tall image: you can click
through it in an IDE.

## The pattern that makes this worth it

Fitting is expensive; post-processing should not be. The stable shape is:

1. **Query** the subset of fits you care about.
2. **Load or derive** the quantity of interest per fit, via `agg.values(...)`, an `ag.agg`
   generator, or `agg.map(func)`.
3. **Export** it under a uniform naming scheme with `AggregateCSV` / `AggregateFITS` /
   `AggregateImages`.

That keeps the search stage separate from cheap, repeatable analysis — and means a change of mind
about which columns you want costs seconds, not another run.

## See also

- [`../concepts/samples_and_posteriors`](../concepts/samples_and_posteriors.md) — the per-fit
  `Samples` interface the aggregator generalises.
- [`../concepts/hierarchical_models`](../concepts/hierarchical_models.md) — modelling a
  population's distribution rather than tabulating it.
- [`analysis_objects`](./analysis_objects.md) — the single-fit `Result`.
- [`ellipse`](./ellipse.md) — the isophote-fitting aggregator classes in context.
- [`plotting`](./plotting.md) — rendering figures directly rather than extracting stored ones.
