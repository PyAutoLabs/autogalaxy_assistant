---
title: Samples and posteriors
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/samples/
      - autofit/non_linear/result.py
      - autofit/aggregator/
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/convert.py
      - autogalaxy/imaging/fit_imaging.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/results/start_here.py
      - scripts/guides/results/aggregator/samples.py
      - scripts/guides/results/latent_variables.py
      - scripts/guides/units/flux.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 927b725b1dde11c399bf9f2925683f06a21131d8496e57f6e315e074c46ae89a
---

# Samples and posteriors

A completed search returns a `Result`, and inside it a `Samples` object holding every model
the search accepted. This is where a fit stops being a fit and becomes a **measurement**:
median values, error bars, covariances, and derived quantities with uncertainties propagated
properly.

Sources: `PyAutoFit:autofit/non_linear/samples/`. Worked examples:
`autogalaxy_workspace:scripts/guides/results/start_here.py` and
`.../results/aggregator/samples.py`.

## What a Samples object holds

Per accepted sample: the parameter vector, the `log_likelihood`, the `log_prior`, the
`log_posterior` (their sum), and a `weight`. It also carries the `model`, which is what lets a
flat vector be turned back into named structure.

```python
samples = result.samples

print(samples.parameter_lists[0])     # every parameter of the first sample
print(samples.log_likelihood_list[0])
print(samples.log_prior_list[0])
print(samples.log_posterior_list[0])
print(samples.weight_list[0])
print(samples.model.parameter_names)
```

`autogalaxy_workspace:scripts/guides/results/aggregator/samples.py`. The **weights** matter:
for a nested sampler such as Nautilus every sample carries a different, non-zero weight
summing to one, and ignoring them when you aggregate anything by hand gives a wrong answer.
The class flavour follows the search — `SamplesNest` for nested sampling, `SamplesMCMC` for
Emcee/Zeus — but the accessor API below is shared.

## Instances

Most accessors return an **instance**: the model with numbers filled in, traversable by the
same attribute paths you composed it with.

```python
instance = samples.max_log_likelihood()

print(instance.galaxies.galaxy.bulge.effective_radius)
print(instance.galaxies.galaxy.bulge.sersic_index)
```

Add `as_instance=False` to any of them to get a flat list instead, in the order given by
`samples.model.paths` / `samples.model.parameter_names`. Other single-sample accessors:
`samples.from_sample_index(sample_index=-1)`, and `samples.draw_randomly_via_pdf()` for a
random posterior draw.

## Median, errors and evidence

```python
median = samples.median_pdf()

values_upper = samples.values_at_upper_sigma(sigma=3.0)
values_lower = samples.values_at_lower_sigma(sigma=3.0)

errors_upper = samples.errors_at_upper_sigma(sigma=3.0)
errors_lower = samples.errors_at_lower_sigma(sigma=3.0)
```

`autogalaxy_workspace:scripts/guides/results/aggregator/samples.py`. All four are computed by
**1D marginalisation** of the posterior for each parameter. `values_at_*` gives the parameter
*value* at the confidence bound; `errors_at_*` gives the *offset* from the median — the number
you write after a `±`. `sigma=1.0` spans 68.3% of the 1D PDF, `sigma=3.0` spans 99.7%.

Because these are 1D marginals, they say nothing about correlations. A galaxy fit has strong
ones — `intensity` against `effective_radius` against `sersic_index` — so a pair of 1D error
bars is not a description of the posterior. Look at `files/covariance.csv`, or plot the joint
distribution:

```python
import autogalaxy.plot as aplt

aplt.corner_anesthetic(samples=result.samples)
```

`aplt.corner_cornerpy` is the alternative backend. This is not optional diligence: a banana-
shaped degeneracy is invisible in a results table and obvious in a corner plot, and it changes
how you should quote the result.

For model comparison:

```python
print(max(samples.log_likelihood_list))   # best fit achieved
print(samples.log_evidence)               # nested samplers only
```

Prefer the **Bayesian evidence**. A more complex model always achieves a higher maximum
likelihood, so comparing peak likelihoods systematically favours over-fitting; the evidence
penalises unwarranted complexity. Compare evidences only between fits to the *same* data with
the same masking and noise treatment — and note that ellipse fitting has no evidence at all
(see [`ellipse_fitting_and_multipoles`](./ellipse_fitting_and_multipoles.md)).

## Derived quantities

The posterior covers the parameters the search sampled. Anything you compute *from* them —
axis ratio, position angle, total luminosity, physical size in kpc, bulge-to-total ratio —
needs its own PDF built by recomputing the quantity for every sample and marginalising with
the sample weights:

```python
import autofit as af
import autogalaxy as ag

axis_ratio_list = []

for sample in samples.sample_list:
    instance = sample.instance_for_model(model=samples.model, ignore_assertions=True)
    ell_comps = instance.galaxies.galaxy.bulge.ell_comps
    axis_ratio_list.append(ag.convert.axis_ratio_from(ell_comps=ell_comps))

median, lower, upper = af.marginalize(
    parameter_list=axis_ratio_list, sigma=3.0, weight_list=samples.weight_list
)
```

`autogalaxy_workspace:scripts/guides/results/aggregator/samples.py`. **Do not** convert the
median and the error separately — for any non-linear function of the parameters that is wrong,
and `ell_comps → axis_ratio` is exactly such a function.

If the derived quantity is expensive, sample the PDF instead of walking every accepted model:

```python
values = []
for _ in range(50):
    instance = samples.draw_randomly_via_pdf()
    ...
```

Draws already account for the weights, so **omit** `weight_list` from `af.marginalize` in that
case. Given enough draws the accuracy is comparable.

## Solved (linear) quantities are not in the samples

This is the trap specific to galaxy-light modelling. A linear light profile's `intensity`, a
basis's amplitudes, and a pixelisation's mesh fluxes are **not** sampled parameters — they are
solved by inversion against the dataset. They are therefore absent from `samples.csv`, and a
raw `Samples` instance reports `intensity = 1.0`.

To get a solved value you must rebuild a fit:

```python
instance = samples.max_log_likelihood()

fit = ag.FitImaging(dataset=dataset, galaxies=instance.galaxies)
galaxies = fit.galaxies_linear_light_profiles_to_light_profiles

print(galaxies[0].bulge.intensity)
```

`autogalaxy_workspace:scripts/guides/results/start_here.py`. For an **uncertainty** on a solved
intensity, wrap that in the derived-quantity loop above: draw from the PDF, rebuild the fit,
collect the solved value, marginalise. It is more expensive than a sampled parameter's error —
each draw costs a likelihood evaluation — which is a real cost of using linear profiles and
worth planning for. See
[`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md).

## Latent variables

Some derived quantities are computed and written out **during** the fit, so you can read them
straight from a column instead of recomputing them. They land in `latent/samples.csv` beside
the search output, and the set is controlled by `config/latent.yaml`. `total_galaxy_0_flux` —
the integrated flux of the first galaxy in the fit's raw image units — ships default-on;
converted variants (for example a µJy version) need an instrument zero point passed as
`magzero=` to the analysis and are default-off.

`autogalaxy_workspace:scripts/guides/results/latent_variables.py` and
`.../guides/units/flux.py`. Because latents are recorded per sample, their errors come for
free — this is the cheapest correct route to an uncertainty on a total flux. The latent set is
extensible: subclass `ag.LatentGalaxy` and declare it on your analysis.

## Loading a finished fit from disk

Everything above works on a `Result` in memory. For a fit that has already run, load the
pieces directly:

```python
import autofit as af
import autogalaxy as ag

files_path = search.paths.output_path / "files"

galaxies = ag.from_json(file_path=files_path / "galaxies.json")
model = ag.from_json(file_path=files_path / "model.json")
samples = af.SamplesNest.from_table(filename=files_path / "samples.csv", model=model)

print(samples.max_log_likelihood())
```

`autogalaxy_workspace:scripts/guides/results/start_here.py`. `search.paths.output_path` saves
you from constructing the `<unique_hash>` by hand. `galaxies.json` already carries the solved
intensities of any linear profile, so the profiles themselves are as good as the in-memory ones
— but **it deserialises to a plain `list` of `Galaxy` objects, not an `ag.Galaxies`**. Indexing
(`galaxies[0].bulge`) and `ag.FitImaging(dataset=…, galaxies=galaxies)` work on the list;
collection methods like `image_2d_from` do not. Re-wrap for those:
`galaxies = ag.Galaxies(galaxies=galaxies)`.

## Many fits — the aggregator

Loading a hundred `samples.csv` files into memory at once will not end well. The aggregator
scrapes a directory and yields the same objects through **generators**, so memory stays
bounded:

```python
from autofit.aggregator.aggregator import Aggregator

agg = Aggregator.from_directory(directory=Path("output") / "results_folder")

for samples in agg.values("samples"):
    print(samples.median_pdf().galaxies.galaxy.bulge.sersic_index)
```

A generator is single-use — remake it rather than storing it. `agg.values(...)` reaches
`model`, `search`, `samples`, `samples_summary`, `covariance`, `cosmology`, `settings` and the
dataset arrays. Prefer `samples_summary` when it has what you need: it is a stored summary, so
it does not recompute anything from the full sample list.

For a table across a sample of galaxies:

```python
agg_csv = af.AggregateCSV(aggregator=agg)
agg_csv.add_variable(argument="galaxies.galaxy.bulge.sersic_index")
agg_csv.save(path=workflow_path / "results.csv")
```

Full treatment, including the `.sqlite` back end for very large samples, is
[`../api/aggregator`](../api/aggregator.md).

## Writing it up

`af.text.Samples.latex(samples=result.samples, median_pdf_model=True, sigma=3.0, ...)` emits a
LaTeX table row with values and asymmetric errors, using the parameter labels from
`notation.yaml` ([`../api/configuration`](../api/configuration.md)).

Two habits worth keeping regardless:

- **Always give units.** "`effective_radius = 1.23`" is not a result — arcseconds and
  kiloparsecs differ by a redshift-dependent factor. See
  [`cosmology_and_units`](./cosmology_and_units.md).
- **Quote the marginalised quantity a reader recognises**, not the sampling convention:
  `axis_ratio` and `angle` rather than `ell_comps`, and say which of the circular or
  major-axis effective radius you mean.

## See also

- [`non_linear_search`](./non_linear_search.md) — what produces the samples.
- [`../api/aggregator`](../api/aggregator.md) — bulk loading and querying.
- [`cosmology_and_units`](./cosmology_and_units.md) — propagating a posterior into physical
  units.
- [`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md) — why solved
  intensities need special handling.
- [`hierarchical_models`](./hierarchical_models.md) — going from many posteriors to a
  population posterior.
- [`../stack/autofit`](../stack/autofit.md) — the library that owns `Samples`.
