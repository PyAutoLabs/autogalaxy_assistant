---
title: Multi-wavelength and multi-dataset fitting
sources:
  - project: PyAutoFit
    paths:
      - autofit/graphical/declarative/factor/analysis.py
      - autofit/graphical/declarative/collection.py
      - autofit/graphical/declarative/abstract.py
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/imaging/model/analysis.py
      - autogalaxy/interferometer/model/analysis.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/multi_dataset/start_here.py
      - scripts/multi_dataset/modeling.py
      - scripts/multi_dataset/features/wavelength_dependence/modeling.py
      - scripts/multi_dataset/features/dataset_offsets/modeling.py
      - scripts/multi_dataset/features/same_wavelength/modeling.py
      - scripts/multi_dataset/features/one_by_one/modeling.py
      - scripts/multi_dataset/features/imaging_and_interferometer/modeling.py
      - scripts/multi_dataset/features/pixelization/modeling.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 06736390540ad6c5d38ecdd38b7b833ef4e1781be247d5c21cb8975ef87208ef
---

# Multi-wavelength and multi-dataset fitting

A galaxy observed in five filters is one object seen five ways. Fitting the bands
simultaneously with a model that states explicitly what is shared and what is not gives you
more than five independent fits do: the geometry is constrained by all the data at once, while
the wavelength-dependent quantities — brightness, colour gradients, the size of a stellar
population versus a star-forming one — become measurements rather than nuisances.

The same machinery covers datasets that are not different wavelengths at all: undithered
exposures of the same band, joint imaging plus interferometry, multi-epoch follow-up.

Sources: `PyAutoFit:autofit/graphical/declarative/`. Worked example:
`autogalaxy_workspace:scripts/multi_dataset/start_here.py`.

## Shared or per-dataset?

This is the whole design decision, and it is scientific before it is technical.

**Usually shared** — the galaxy's centre, its ellipticity and position angle, its structural
scale (effective radius, Sersic index), and the mesh and regularisation of a pixelised
component. These describe the object.

**Usually per-dataset** — the PSF and pixel scale (properties of the data, not the model), the
mask, the sky background level, and any astrometric offset between frames.

**In between, and the interesting part** — the light's amplitude and, sometimes, its radial
scale. Amplitude *must* be free per band: that is colour. Whether the effective radius may
vary is a real question about the galaxy (a redder, more centrally concentrated old population
inside a bluer disc), and the answer determines whether you free it, tie it to a relation, or
fix it.

Give a band too much freedom and it will absorb a modelling failure that a shared parameter
would have exposed. Give it too little and you will attribute a genuine colour gradient to
noise. Neither error announces itself.

Note that **linear** light profiles handle the amplitude question for free: `intensity` is not
a model parameter at all, so each band's inversion solves its own amplitude with no extra
dimensions and no explicit per-band prior. That is why the multi-wavelength examples use an
MGE — the same basis with the same shared geometry infers a different amplitude set per band,
and colour gradients come out correctly. See
[`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md).

## The factor graph

Each dataset gets its own analysis. Each analysis is paired with a model in an
`af.AnalysisFactor`. The factors are combined in an `af.FactorGraphModel`, whose
log-likelihood is the sum over factors, and it is the factor graph that is passed to the
search:

```python
import autofit as af
import autogalaxy as ag

analysis_list = [
    ag.AnalysisImaging(dataset=dataset, use_jax=True)
    for dataset in dataset_masked_list
]

analysis_factor_list = []

for analysis in analysis_list:
    model_analysis = model.copy()
    analysis_factor_list.append(
        af.AnalysisFactor(prior_model=model_analysis, analysis=analysis)
    )

factor_graph = af.FactorGraphModel(*analysis_factor_list, use_jax=True)

result_list = search.fit(model=factor_graph.global_prior_model, analysis=factor_graph)
```

`autogalaxy_workspace:scripts/multi_dataset/start_here.py`. **This is the current and only
idiom for combining datasets.** Note the two things that change relative to a single-dataset
fit: the search is given `factor_graph.global_prior_model` rather than `model`, and it returns
a **list** of results, one per factor.

Sharing is expressed through the *model*, never by special-casing the datasets. With a bare
`model.copy()` and no overrides the graph identifies (deduplicates) every prior across the
factors, so the entire model is shared. To free something per dataset, override that prior on
the copy before wrapping it:

```python
for i, analysis in enumerate(analysis_list):
    model_analysis = model.copy()

    if i > 0:
        model_analysis.dataset_model.grid_offset.grid_offset_0 = af.UniformPrior(
            lower_limit=-1.0, upper_limit=1.0
        )
        model_analysis.dataset_model.grid_offset.grid_offset_1 = af.UniformPrior(
            lower_limit=-1.0, upper_limit=1.0
        )

    analysis_factor_list.append(
        af.AnalysisFactor(prior_model=model_analysis, analysis=analysis)
    )
```

Inspect what you built with `print(factor_graph.global_prior_model.info)` before launching —
it is the only way to confirm which priors were identified and which were freed.

`af.FactorGraphModel(use_jax=True)` stitches the per-band likelihoods into one JAX-traceable
joint likelihood with JAX-aware broadcasting, so batched GPU evaluation applies to the whole
graph.

## Astrometric offsets

Real datasets are rarely co-registered perfectly. Reduction pipelines align frames, but
sub-pixel residuals remain, and telescope pointing precision itself leaves an uncertainty that
matters for a detailed structural model. Left unmodelled, that misalignment leaks into the
galaxy parameters — commonly seen as a fit that degrades when a model inferred from one band is
applied to another.

`ag.DatasetModel` carries `grid_offset` (two parameters) and `grid_rotation_angle`. The offset
is applied by shifting the *image-pixel grid*, not the profile centres, so the galaxy model's
geometry is untouched. Convention: the first dataset defines the reference frame and each
subsequent one gets its own offset, so N datasets cost `2 × (N − 1)` parameters.
`autogalaxy_workspace:scripts/multi_dataset/features/dataset_offsets/modeling.py`. For most
multi-wavelength work this is the difference between an accurate model and a subtly wrong one,
and the dimensionality is the price.

## Wavelength-dependent parameters without wavelength-many parameters

Freeing a parameter per band scales badly: five bands means five free effective radii. If you
expect the parameter to vary *smoothly* with wavelength, parameterise the **relation** instead
and fit its coefficients. A linear relation costs two parameters no matter how many bands you
have:

```python
wavelength_list = [464, 658, 806]

bulge_m = af.UniformPrior(lower_limit=-0.1, upper_limit=0.1)
bulge_c = af.UniformPrior(lower_limit=-10.0, upper_limit=10.0)

analysis_factor_list = []

for wavelength, analysis in zip(wavelength_list, analysis_list):
    model_analysis = model.copy()
    model_analysis.galaxies.galaxy.bulge.effective_radius = (
        wavelength * bulge_m
    ) + bulge_c

    analysis_factor_list.append(
        af.AnalysisFactor(prior_model=model_analysis, analysis=analysis)
    )

factor_graph = af.FactorGraphModel(*analysis_factor_list, use_jax=True)
```

`autogalaxy_workspace:scripts/multi_dataset/features/wavelength_dependence/modeling.py`. The
arithmetic on priors is real: `(wavelength * bulge_m) + bulge_c` builds a derived prior, so
`m` and `c` are the sampled parameters and each band's `effective_radius` is determined by
them. `m` is then directly the *gradient* of size with wavelength — often the quantity the
science actually wants, measured with an error bar, rather than five loosely constrained radii
you have to regress afterwards.

The same construction works for any parameter and any functional form you can write with prior
arithmetic. Its cost is the assumption: if the true variation is not the shape you imposed, the
fit will distort other parameters to compensate. Fitting a small number of bands with free
per-band values first is a sensible check.

## Variants

`autogalaxy_workspace:scripts/multi_dataset/features/` covers the recurring cases:

- **`same_wavelength/`** — several exposures in one band, for example undithered HST frames
  fitted before drizzling so that correlated noise is not baked in. Combine with
  `dataset_offsets/`, since dithered frames are deliberately shifted.
- **`imaging_and_interferometer/`** — a joint fit to CCD imaging and visibilities. The galaxy
  can look completely different in the optical and the sub-millimetre, so the two datasets are
  complementary rather than redundant: imaging constrains the smooth stellar light, the
  interferometer the compact star-forming structure, and one model must satisfy both. See
  [`interferometer_theory`](./interferometer_theory.md).
- **`pixelization/`** — a pixelised reconstruction across bands. Watch the dimensionality and
  the VRAM; see [`inversions_and_pixelizations`](./inversions_and_pixelizations.md).
- **`one_by_one/`** — the deliberate *alternative* to a simultaneous fit. Fit the highest
  quality dataset first, then chain into the others using its inferred model. Preferable when
  one dataset is much better than the rest (a poor band can otherwise degrade a joint fit),
  often faster in total, and a useful robustness test: a feature that vanishes when bands are
  fitted individually was probably not real. How much to fix versus free at each step is a
  judgement call the script walks through. See
  [`non_linear_search`](./non_linear_search.md) on chaining.

## Practical notes

- **Use the same mask geometry across datasets where you can.** The wavelength-dependence
  example builds one mask radius for every band. It is not required — pixel scales differ — but
  it makes the comparison between bands cleaner and the analysis more reliable.
- **Multi-wavelength fits stay on `Nautilus`.** Each band may have its own pixel scale, so the
  bands do not share a grid shape and JAX must compile a separate gradient kernel per band;
  that compile cost currently makes `MultiStartProdigy` impractical here, even though it is the
  default for single-dataset `start_here.py` scripts.
- **Results are a list.** `result_list[i]` corresponds to `analysis_factor_list[i]` and hence
  to dataset `i`. The `Samples` object, however, is the *global* one — it has the
  dimensionality of the whole graph and is identical in every result.
- **Read `result_list[i].max_log_likelihood_instance`** to confirm the sharing worked: shared
  parameters must be identical across results, freed ones must differ.

## See also

- [`../api/analysis_objects`](../api/analysis_objects.md) — `AnalysisFactor` and
  `FactorGraphModel` in full.
- [`../api/datasets`](../api/datasets.md) — the per-dataset classes.
- [`linear_light_profiles_and_mge`](./linear_light_profiles_and_mge.md) — why per-band
  amplitudes are free of charge.
- [`sky_background_and_operated_profiles`](./sky_background_and_operated_profiles.md) —
  `ag.DatasetModel`'s other parameters.
- [`interferometer_theory`](./interferometer_theory.md) — the visibility side of a joint fit.
- [`hierarchical_models`](./hierarchical_models.md) — many *different* galaxies, rather than
  many views of one.
- [`../stack/autofit`](../stack/autofit.md) — the graphical-model layer.
