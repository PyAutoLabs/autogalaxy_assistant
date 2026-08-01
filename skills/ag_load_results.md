---
name: ag_load_results
description: Get a completed fit's results back into Python and turn them into science — the in-session `Result` object (max-log-likelihood instance, galaxies and fit), direct loading of one fit's output folder via `from_json` and `SamplesNest.from_table`, the `Samples` API for medians and errors, and the aggregator for a whole sample of fits with its `ag.agg` generators, queries and CSV/FITS/PNG workflow exports. Also covers the traps: linear light-profile intensities are solved rather than sampled and are absent from the samples, derived-quantity errors need posterior draws, and test-mode results are not physically meaningful. Use when a search has finished (or is mid-run) and the user wants numbers, errors, derived quantities, a results table, or a comparison across fits. Not for running the fit (`ag_run_search`), not for rendering figures of a single fit (`ag_plot_fit`), and not for diagnosing a fit that converged somewhere wrong (`ag_debug_fit_failure`).
---

# Reading a finished fit

The search is over; the question is what it measured. This skill is the bridge from an
`output/` folder to a sentence you could put in a paper: *"the bulge has an effective radius
of 1.62 ± 0.08 arcseconds and a Sersic index of 3.9 ± 0.3"*.

Loading is never the goal on its own — the user already wants something specific: a
parameter with errors, a derived quantity the fit did not parameterise directly, the
residuals, a table across fifty galaxies. The job here is to establish which, load only that,
and be honest about what the fit can and cannot support.

Two things about the statistics are worth stating before any API. First, the default view of a
result is the **maximum log likelihood** model — the single best-fitting parameter vector.
That is not the same as the posterior, and quoting it without errors is quoting half a
measurement. Second, a nested-sampling run gives you the full posterior, so errors,
covariances and the Bayesian evidence are all available; a gradient optimiser such as
`MultiStartProdigy` is a maximum-a-posteriori method and gives you **no errors at all**
(`autogalaxy_workspace:scripts/imaging/start_here.py` `__Posterior__`). If the fit used the
optimiser and the user wants uncertainties, the answer is to re-run with `Nautilus`, not to
manufacture them.

The concept page behind everything below is
[`wiki/core/concepts/samples_and_posteriors.md`](../wiki/core/concepts/samples_and_posteriors.md);
the aggregator's full API surface is
[`wiki/core/api/aggregator.md`](../wiki/core/api/aggregator.md).

## Ask

Two questions, and they choose the branch outright:

- **What do you want out of it?** *"A parameter and its error"* → the `Samples` branch.
  *"The residuals / how good is the fit"* → the fit branch, then
  [`ag_plot_fit`](./ag_plot_fit.md). *"A physical quantity in kpc or solar luminosities"* →
  the derived-quantities branch. *"A table over all my galaxies"* → the aggregator branch.
- **One fit, or many?** One fit you already have a path to → simple loading. More than a
  handful, or you want to iterate and filter → the aggregator, which is generator-based and
  keeps memory bounded no matter how many fits the tree holds.

If they give you a path, list it and confirm which sub-folder: the layout is
`output/<path_prefix>/<name>/<unique_tag>/<unique_hash>/`, and a parent path can hold many
fits. If the path contains a `test_mode` segment, say so immediately — every number in it is a
wiring check, not a measurement
([`wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md)).

## Branch — the result you already have in the session

If the fit just ran, `search.fit(...)` returned everything, no disk access needed:

```python
result = search.fit(model=model, analysis=analysis)

print(result.info)                            # human-readable summary, parameters + errors
print(result.max_log_likelihood_instance)      # best-fit model as concrete objects

galaxies = result.max_log_likelihood_galaxies  # ag.Galaxies at the best-fit values
fit = result.max_log_likelihood_fit            # ag.FitImaging: model image, residuals, chi²
samples = result.samples                       # the full posterior
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py` `__Result__` and
`autogalaxy_workspace:scripts/guides/results/start_here.py`. The full member list —
`result.samples_summary`, `result.model`, `result.instance`, `result.dataset`, `result.grids`,
`result.unmasked_model_image`, the per-galaxy image dictionaries — is tabulated in
[`wiki/core/api/analysis_objects.md`](../wiki/core/api/analysis_objects.md)
"What the result gives you". Sources: `PyAutoGalaxy:autogalaxy/analysis/result.py` and
`PyAutoGalaxy:autogalaxy/imaging/model/result.py`.

`result.samples_summary` is worth knowing about: it holds pre-computed maximum-likelihood
values and 1σ/3σ errors, so reaching for it instead of re-deriving from `samples` is
substantially faster and gives the same answer.

## Branch — loading one fit from disk

Everything the `Result` holds was also written to the output folder, and each file loads back
into a full Python object in one line — much cheaper than re-running the search:

```python
from pathlib import Path

import autofit as af
import autogalaxy as ag
from autogalaxy import from_json

FIT_PATH = Path("output") / "imaging" / "<your_galaxy>" / "sersic" / "<unique_hash>"
files_path = FIT_PATH / "files"
image_path = FIT_PATH / "image"

galaxies = from_json(file_path=files_path / "galaxies.json")
model = from_json(file_path=files_path / "model.json")

samples = af.SamplesNest.from_table(filename=files_path / "samples.csv", model=model)
print(samples.max_log_likelihood())
```

Adapted from `autogalaxy_workspace:scripts/guides/results/start_here.py`
"Simple Loading". If the fit ran in the same session, `search.paths.output_path` already
points at the right folder, so you never have to know the hash.

Two things to know about what comes back:

- **`galaxies.json` deserialises to a plain Python list of `Galaxy` objects, not an
  `ag.Galaxies`.** The list is enough for `ag.FitImaging(dataset=dataset, galaxies=galaxies)`
  and for indexing (`galaxies[0].bulge`), but it has no `image_2d_from`. Wrap it when you need
  the collection's own methods: `galaxies = ag.Galaxies(galaxies=galaxies)`.
- **`model.json` is the *prior* model, with free parameters** — not the best-fit instance. It
  is what you pass to `SamplesNest.from_table` so the sample columns can be mapped back onto
  named parameters, and it is worth printing (`model.info`) to confirm what was actually
  fitted.

The `image/` folder holds the imaging products as FITS, loadable with the standard readers —
`ag.Imaging.from_fits` for `dataset.fits` (multi-HDU, so pass the `*_hdu` arguments) and
`ag.Array2D.from_fits` for the per-galaxy image stacks. The annotated tree of everything the
fit wrote is `__Output Folder Layout__` in
[`autogalaxy_workspace/scripts/imaging/modeling.py`](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/imaging/modeling.py),
also condensed in
[`wiki/core/concepts/non_linear_search.md`](../wiki/core/concepts/non_linear_search.md)
"The output folder".

The whole `<unique_hash>/` folder is portable: a collaborator with a compatible environment
loads it exactly as above. `files/*.json`, `files/samples.csv`, the `image/*.fits` products
and the human-readable `model.info` / `model.results` are what matter to them.

## Branch — parameters with errors, from `Samples`

The `Samples` object holds every accepted sample and its likelihood, which is what makes error
estimation possible at all:

```python
samples = result.samples

median_instance = samples.median_pdf()
u3 = samples.values_at_upper_sigma(sigma=3.0)
l3 = samples.values_at_lower_sigma(sigma=3.0)

print(median_instance.galaxies.galaxy.bulge)
print(u3.galaxies.galaxy.bulge, "\n", l3.galaxies.galaxy.bulge)
```

Adapted from `autogalaxy_workspace:scripts/guides/results/start_here.py` `__Samples__`. Each
of these returns a **model instance** — the same shape of object as the model you composed, so
`instance.galaxies.galaxy.bulge.sersic_index` addresses a parameter by the names you chose.
`samples.max_log_likelihood()` gives the best-fit instance, `samples.parameter_lists` the raw
vectors, `samples.log_likelihood_list` and `samples.log_evidence` the statistics.
`samples.errors_at_upper_sigma(...)` returns the error rather than the value.

Two disciplines when reporting:

- **Quote the sigma level and the summary you used.** "Effective radius 1.62, +0.08/−0.07 at
  1σ from the marginalised PDF" is a result. "1.62" is not.
- **Be explicit about units.** PyAutoGalaxy works in arcseconds and instrumental flux units.
  "Effective radius = 1.6 arcsec" is fine; "effective radius = 1.6" is a bug waiting to
  happen.

### Linear intensities are not in the samples

This one catches everyone. A linear light profile (`ag.lp_linear.*`, and every basis built
from them — a Multi-Gaussian Expansion, a shapelet expansion) has its `intensity` solved by
linear inversion at every iteration rather than sampled. So in the `Samples` object those
intensities are placeholders of 1.0, and reading them there gives you nothing
(`autogalaxy_workspace:scripts/guides/results/start_here.py` `__Linear Light Profiles__`).

The solved values live on the fit. Either take them off the result directly:

```python
print(result.max_log_likelihood_galaxies[0].bulge.intensity)
```

or, if you are working from a `Samples` instance you loaded yourself, rebuild the fit and let
it solve:

```python
ml_instance = samples.max_log_likelihood()

fit = ag.FitImaging(dataset=dataset, galaxies=ml_instance.galaxies)
galaxies = fit.galaxies_linear_light_profiles_to_light_profiles

print(galaxies[0].bulge.intensity)
```

The same conversion is what lets you plot a linear-profile model at all
([`ag_plot_fit`](./ag_plot_fit.md)). Background:
[`wiki/core/concepts/linear_light_profiles_and_mge.md`](../wiki/core/concepts/linear_light_profiles_and_mge.md).
The same principle applies to a pixelised reconstruction's pixel fluxes —
[`wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md).

## Branch — derived quantities, and their errors

Most interesting numbers are not model parameters. A bulge-to-total light ratio, a luminosity
inside an aperture, an effective radius in kiloparsecs — each is a *function* of the
parameters, so its error has to be propagated rather than read off.

Compute the quantity from the best-fit galaxies:

```python
galaxies = result.max_log_likelihood_galaxies

luminosity = galaxies[0].luminosity_within_circle_from(radius=10.0)

cosmology = ag.cosmo.Planck15()
kpc_per_arcsec = cosmology.kpc_per_arcsec_from(redshift=galaxies[0].redshift)
effective_radius_kpc = galaxies[0].bulge.effective_radius * kpc_per_arcsec
```

Adapted from `autogalaxy_workspace:scripts/guides/results/aggregator/models.py` and
`autogalaxy_workspace:scripts/guides/results/start_here.py`
`__Units and Cosmological Quantities__`. The angular-to-physical machinery, fluxes, magnitudes
and luminosities are
[`wiki/core/concepts/cosmology_and_units.md`](../wiki/core/concepts/cosmology_and_units.md);
the runnable guides are `autogalaxy_workspace:scripts/guides/units/cosmology.py` and
`autogalaxy_workspace:scripts/guides/units/flux.py`.

For the **error** on a derived quantity, recompute it for galaxies drawn from the posterior
and take the spread. The aggregator's `randomly_drawn_via_pdf_gen_from` exists for exactly
this, and `all_above_weight_gen_from` / `weights_above_gen_from` give you the weighted version
(`autogalaxy_workspace:scripts/guides/results/aggregator/models.py`). Anything else — scaling
the parameter's own error, or quoting the best-fit value with no error — is guesswork.

Quantities the library can compute but the model never sampled can also be recorded during the
fit as **latent variables**, which puts them in the samples with errors like any other
parameter. That machinery, including subclassing `ag.LatentGalaxy` for your own, is
`autogalaxy_workspace:scripts/guides/results/latent_variables.py` and
[`wiki/core/concepts/samples_and_posteriors.md`](../wiki/core/concepts/samples_and_posteriors.md)
"Latent variables". Note that any active `PYAUTO_TEST_MODE` level skips the latent pass, so a
smoke run never has them.

## Branch — many fits, with the aggregator

Once the unit of work is a *sample* — a hundred galaxies with one model, or one galaxy with
ten models — the aggregator gives you one query surface over all of them and, crucially,
returns **generators** rather than lists, so memory stays bounded:

```python
from pathlib import Path
from autofit.aggregator.aggregator import Aggregator

agg = Aggregator.from_directory(directory=Path("output") / "imaging")

for samples in agg.values("samples"):
    print(samples.parameter_lists[0])
```

Adapted from `autogalaxy_workspace:scripts/guides/results/start_here.py`
"Aggregator". Note the explicit import: `Aggregator.from_directory` lives in
`PyAutoFit:autofit/aggregator/aggregator.py` and is **not** `af.Aggregator`, which is the
database-backed class. Keys worth knowing for `agg.values(...)`: `"samples"`,
`"samples_summary"` (much faster — nothing re-derived), `"samples_info"`, `"model"`,
`"search"`, `"info"`, `"covariance"`, `"cosmology"`, and the `"dataset/..."` family.

A generator is consumed once. Remake it rather than storing it — this is why the workspace
examples build each one at the point of use.

**Queries** compose, because each returns a new aggregator
(`autogalaxy_workspace:scripts/guides/results/aggregator/queries.py`):

```python
unique_tag = agg.search.unique_tag
agg_query = agg.query(unique_tag == "<your_galaxy>")

bulge = agg.model.galaxies.galaxy.bulge
agg_query = agg.query((bulge == ag.lp_linear.Sersic) & (bulge.effective_radius > 3.0))
```

`agg.search` addresses fit-level fields (`name`, `unique_tag`, `path_prefix`, `is_complete`);
`agg.model` addresses the fitted model by the names you chose, so you can select on a
component's class or on an inferred value.

### `ag.agg` — galaxy objects back out of stored fits

PyAutoFit's aggregator loads what the search wrote; PyAutoGalaxy's `ag.agg` rebuilds
*galaxy-domain* objects from those files, as generators. The classes are `ImagingAgg`,
`InterferometerAgg`, `GalaxiesAgg`, `FitImagingAgg`, `FitInterferometerAgg`, `EllipsesAgg`,
`FitEllipseAgg` and `MultipolesAgg`:

```python
import autogalaxy.plot as aplt

galaxies_agg = ag.agg.GalaxiesAgg(aggregator=agg)
galaxies_gen = galaxies_agg.max_log_likelihood_gen_from()

dataset_agg = ag.agg.ImagingAgg(aggregator=agg)
dataset_gen = dataset_agg.dataset_gen_from()

for dataset_list, galaxies_list in zip(dataset_gen, galaxies_gen):
    dataset = dataset_list[0]          # one entry per analysis in the fit
    galaxies = galaxies_list[0]

    fit = ag.FitImaging(dataset=dataset, galaxies=galaxies)
    galaxies = fit.galaxies_linear_light_profiles_to_light_profiles

    print(galaxies[0].bulge.intensity)
```

Adapted from `autogalaxy_workspace:scripts/guides/results/aggregator/models.py`. The inner
`[0]` is not noise: a fit can hold several analyses (a multi-band factor graph, for instance),
so each generator yields a *list* per fit. The dataset classes expose `dataset_gen_from()`;
the model classes share `max_log_likelihood_gen_from()`,
`randomly_drawn_via_pdf_gen_from(total_samples=...)`,
`all_above_weight_gen_from(minimum_weight=...)` and
`weights_above_gen_from(minimum_weight=...)`, all built on `object_via_gen_from(...)`.
`FitImagingAgg` also takes a `settings=` argument if you need to rebuild the fit with
different settings than it ran with
(`autogalaxy_workspace:scripts/guides/results/aggregator/data_fitting.py`).

### The three enumerations, and the workflow exports

`ag.agg` exposes exactly three enumerations, naming panels and HDUs the completed fits
**already have on disk** — you are extracting stored output, not re-rendering it
(`PyAutoGalaxy:autogalaxy/aggregator/subplot.py`):

| Enumeration | Members |
|---|---|
| `ag.agg.fits_fit` | `model_data`, `residual_map`, `normalized_residual_map`, `chi_squared_map` |
| `ag.agg.subplot_dataset` | `data`, `data_log_10`, `noise_map`, `psf`, `psf_log_10`, `signal_to_noise_map`, `over_sample_size_lp`, `over_sample_size_pixelization` |
| `ag.agg.subplot_fit` | `data`, `signal_to_noise_map`, `model_data`, `normalized_residual_map`, `normalized_residual_map_one_sigma`, `chi_squared_map` |

They feed three PyAutoFit export helpers, each taking `aggregator=agg`
(`autogalaxy_workspace:scripts/guides/results/workflow/csv_make.py`,
`fits_make.py` and `png_make.py`):

```python
import autofit as af

workflow_path = Path("output") / "workflow"

agg_csv = af.AggregateCSV(aggregator=agg)
agg_csv.add_variable(
    argument="galaxies.galaxy.bulge.sersic_index",
    value_types=[af.ValueType.Median, af.ValueType.ValuesAt3Sigma],
)
agg_csv.add_variable(argument="galaxies.galaxy.bulge.effective_radius")
agg_csv.save(path=workflow_path / "results.csv")

agg_fits = af.AggregateFITS(aggregator=agg)
agg_fits.output_to_folder(
    folder=workflow_path,
    name="unique_tag",
    hdus=[ag.agg.fits_fit.model_data, ag.agg.fits_fit.residual_map],
)

agg_image = af.AggregateImages(aggregator=agg)
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

`af.ValueType` has four members — `Median`, `MaxLogLikelihood`, `ValuesAt1Sigma`,
`ValuesAt3Sigma`. `AggregateCSV` also offers `add_computed_column` (a function of the loaded
objects, for a derived quantity) and `add_label_column` (an explicit per-fit label, e.g. the
dataset names from `[search.unique_tag for search in agg.values("search")]`). `extract_fits`
and `extract_image` return one combined object across all fits; `output_to_folder` writes one
file per fit instead, which is usually easier to click through when reviewing a sample.

Full API surface, including the database-backed `af.Aggregator.from_database` route for
hundreds of fits: [`wiki/core/api/aggregator.md`](../wiki/core/api/aggregator.md). The
database walkthrough is `autogalaxy_workspace:scripts/guides/results/database/start_here.py`
— note that `from_database` has no overwrite flag, which is why that example deletes a stale
`.sqlite` itself. Start with the directory aggregator and move to the database only when
reading from disk becomes the slow part.

The shape that makes this worth the setup: **query** the subset you care about, **load or
derive** the quantity per fit, **export** it under a uniform naming scheme. Fitting is
expensive; changing your mind about which columns you wanted should cost seconds.

## Branch — the honest caveats

Say these out loud rather than letting a user discover them:

- **A test-mode result is not a measurement.** Any `PYAUTO_TEST_MODE` level truncates or mocks
  the sampler, so the parameters are whatever the short-circuited run produced, the errors are
  degenerate, and latent variables were skipped. The `test_mode` path segment is the tell.
- **A gradient-optimiser fit has no errors.** `MultiStartProdigy` returns one best-fit model.
  If the science needs uncertainties, re-run with `Nautilus`
  ([`ag_configure_search`](./ag_configure_search.md)).
- **A resumed fit may not be the fit you think.** The unique identifier does not hash the
  pixel values, so a result can be a silent resume of an earlier run on different data — see
  [`ag_run_search`](./ag_run_search.md) "Resuming".
- **An unconverged search still produces a `samples.csv`.** Check `search.summary` and the
  log-evidence before trusting a posterior width.

## Combine

- [`ag_plot_fit`](./ag_plot_fit.md) — turn the loaded fit into figures, and read the residuals
  properly before quoting anything.
- [`ag_debug_fit_failure`](./ag_debug_fit_failure.md) — the numbers loaded fine but they are
  not believable.
- [`ag_run_search`](./ag_run_search.md) — the run that produced this output, and what it wrote
  where.
- [`ag_configure_search`](./ag_configure_search.md) — the posterior is too coarse, or you need
  errors an optimiser cannot give.

There is a second, lighter route to a result planned for this assistant: an MCP tool surface
for inspecting a fit's output folder without writing a script. It is **not built yet** —
[`../PENDING.md`](../PENDING.md) tracks it with its grounding module. Until it lands, this
skill's Python is the way in; do not tell a user to invoke a tool that does not exist.

When a load turns into real analysis — a table, a derived quantity, a comparison across fits —
offer (default-yes) the dated `wiki/project/YYYY-MM-DD-<slug>.md` entry: the science question,
what was inferred and how, and the script produced (per [`_style.md`](./_style.md) property
#5).

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Results](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_2_modeling/tutorial_7_results.ipynb):
  the `Result` object from first principles — best-fit model, galaxies, posterior samples, and
  pulling parameter values with uncertainties out of them.
- **General reference** — [RTD: Fitting API reference](https://pyautogalaxy.readthedocs.io/en/latest/api/fitting.html):
  the generated reference for the fit objects a loaded result rebuilds.
- **Experienced PyAutoGalaxy user** — [workspace: guides/results/start_here.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/guides/results/start_here.py):
  both routes in one runnable script — direct JSON/CSV loading of one fit, then the aggregator
  over many.

## Agent procedural checklist

1. Establish what the user wants out of the result before loading anything.
2. Establish one fit or many; pick simple loading or the aggregator accordingly.
3. Check the path for a `test_mode` segment and say so if it is there.
4. Check which search ran — no errors are available from a gradient optimiser.
5. For any linear light profile or pixelisation, get intensities from the fit, never from the
   samples.
6. Quote a sigma level, a summary statistic and a unit with every number.
7. For a derived quantity's error, draw from the posterior; never scale a parameter error.
8. Write the loading recipe to a script in `scripts/` rather than leaving it inline.
9. Route figures to the fit-plotting skill and unbelievable numbers to the debug skill.
10. Offer the `wiki/project/` entry when the load became analysis.
