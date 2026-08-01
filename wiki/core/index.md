---
title: Core wiki — PyAuto* reference
sources:
  - project: autogalaxy_assistant
    paths:
      - wiki/core/
      - skills/
      - ROADMAP.md
    pinned_commit: a083753c217e6d9c07f3c9cc40cb7133b478a439
last_updated: 2026-08-01
content_sha256: 02c4f0d6bedb06af5c8528fcdf8261bff6a621f86ed900f7f8f16350cc81b8e0
---

# Core wiki — PyAuto\* reference

The reference layer for everything an agent needs to know about the PyAuto\* stack when
helping a user model galaxy structure. Skills in [`../../skills/`](../../skills/) link in
here for the *what* / *which* / *why*; they own the *how*.

Five sections, each with a different job:

| Section | Answers | Pages |
|---|---|---|
| [`stack/`](#stack) | Which library owns this, and what does it depend on? | 5 |
| [`api/`](#api) | Which one exists, and when would I pick it? | 9 |
| [`concepts/`](#concepts) | What is this, physically and statistically, and why? | 15 |
| [`operations/`](#operations) | How do I install, configure and run it? | 5 |
| [`external/`](#external-resources) | Where do I send the user to read more? | 5 |

Every link on this page resolves to a file that exists, and as of Phase 6 nothing this
sub-wiki planned is still unwritten — see "Nothing is missing" at the foot of the page for
what that does and does not claim.

## Stack

One page per library, plus how they compose.

- [The stack at a glance](./stack/overview.md) — the dependency chain and who imports whom.
- [PyAutoNerves](./stack/autonerves.md) — layered YAML config loading, JSON/FITS I/O, the
  JAX and test-mode utilities every other library imports.
- [PyAutoArray](./stack/autoarray.md) — arrays, grids, masks, datasets, convolution and the
  inversion machinery.
- [PyAutoFit](./stack/autofit.md) — model composition, non-linear search, samples, the
  aggregator.
- [PyAutoGalaxy](./stack/autogalaxy.md) — light and mass profiles, galaxies, ellipse
  fitting, pixelised reconstruction, the analysis objects.

## API

Task-oriented catalogues: what is available, with a "when to use which" note on each entry.

- [Non-linear search catalogue](./api/searches.md) — every search and gradient optimizer,
  their settings, and how to choose.
- [Light profile catalogue](./api/light_profile_catalog.md) — the standard, linear, operated
  and basis variants, and which module each lives in.
- [Mass profile catalogue](./api/mass_profile_catalog.md) — the mass profiles PyAutoGalaxy
  ships, framed for stellar-mass and dynamical work.
- [Datasets](./api/datasets.md) — `Imaging` and `Interferometer`, their settings objects,
  masking and over-sampling.
- [Analysis objects and model composition](./api/analysis_objects.md) — the analyses, and
  the factor graph that combines several datasets.
- [Plotting](./api/plotting.md) — the functional `aplt` entry points. There are no
  object-oriented plotters; this page is the authoritative surface.
- [Ellipse fitting](./api/ellipse.md) — the isophote-fitting API and its multipoles.
- [Aggregator](./api/aggregator.md) — loading and querying many completed fits.
- [Configuration](./api/configuration.md) — the `config/` tree, prior defaults, visualisation
  and output settings, and how the layers override each other.

## Concepts

The physics and the inference behind the API.

- [Light profiles](./concepts/light_profiles.md) — Sersic and its relatives; what the
  effective radius and Sersic index actually measure.
- [Galaxy and Galaxies](./concepts/galaxies.md) — how profiles, redshifts and several
  galaxies compose into what gets fitted.
- [Grids, masks and over-sampling](./concepts/grids_and_masks.md) — slim vs. native, and why
  the over-sampling scheme changes your answer.
- [Linear light profiles and the Multi-Gaussian Expansion](./concepts/linear_light_profiles_and_mge.md)
  — solving intensities by linear inversion, and why fewer free parameters wins.
- [Shapelets](./concepts/shapelets.md) — an orthonormal basis for morphology no smooth
  profile fits.
- [Inversions and pixelisations](./concepts/inversions_and_pixelizations.md) — pixelised
  reconstruction, meshes and regularisation.
- [Sky background and operated light profiles](./concepts/sky_background_and_operated_profiles.md)
  — modelling the background, and components that are already PSF-convolved.
- [Extra galaxies and noise scaling](./concepts/extra_galaxies_and_noise_scaling.md) —
  contaminating neighbours: model them, mask them, or scale their noise.
- [Ellipse fitting and multipoles](./concepts/ellipse_fitting_and_multipoles.md) — isophote
  analysis, twists, and boxy/discy deviations.
- [The non-linear search](./concepts/non_linear_search.md) — what each sampler does, and how
  run time scales with the model.
- [Samples and posteriors](./concepts/samples_and_posteriors.md) — the `Samples` API, errors,
  latent and derived quantities.
- [Multi-wavelength and multi-dataset fitting](./concepts/multi_wavelength.md) — joint fits
  across bands and instruments via the factor graph.
- [Interferometer fitting](./concepts/interferometer_theory.md) — visibilities, the uv-plane,
  FFT/NUFFT and dirty images.
- [Cosmology and units](./concepts/cosmology_and_units.md) — angular ↔ physical conversions,
  fluxes, magnitudes and luminosities.
- [Hierarchical and graphical models](./concepts/hierarchical_models.md) — population-level
  inference over samples of galaxies.

## Operations

- [Dataset layout and `info.json`](./operations/dataset.md) — the `wavebands/<BAND>/` on-disk
  convention, every `info.json` field and where it comes from, how to load one waveband, the
  bundled dataset's sky and PSF caveats, and the workspace auto-simulation pattern for data
  that is not bundled.
- [Installation](./operations/installation.md) — the pip route and its extras, the
  editable-clone route, version floors and caps, `activate.sh`, and how to prove the install
  works.
- [Sandbox / restricted environments](./operations/sandbox.md) — writable caches
  (`NUMBA_CACHE_DIR`, `MPLCONFIGDIR`, the JAX compilation cache), `PYAUTO_TEST_MODE` and the
  other short-circuit flags, and where this repo is allowed to write.
- [HPC and cluster runs](./operations/hpc.md) — why galaxy work is sample-shaped, the two
  kinds of parallelism, JAX on CPU versus GPU (and when the GPU is the wrong answer), sizing
  an array job, per-job caches, and the resume trap on a sample run.
- [HPC infrastructure shipped here](./operations/hpc_infrastructure.md) — the `hpc/` tree:
  `template.py` and its interface contract, the CPU and GPU submit templates, and the `sync`
  CLI for transfer and job control.

## External resources

Routing into the three resources outside this repo, by audience.

- [External routing index](./external/index.md) — the audience matrix; read this first.
- [HowToGalaxy](./external/howtogalaxy.md) — the five-chapter lecture series for newcomers.
- [PyAutoGalaxy RTD](./external/rtd.md) — verified page map of the overview series, general
  docs, installation guides and API reference.
- [`autogalaxy_workspace`](./external/workspace.md) — the seven production script groups and
  how to route from the repo's own generated catalogue.
- [Skill citation map](./external/skill_citation_map.md) — one row per skill; load-bearing
  for each skill's `## Further reading` block.

## Nothing is missing

This section used to list the pages that had not been written. As of Phase 6 there are none:
the two HPC operations pages were the last of them, and they landed with the `hpc/` tree they
document. Every section above is complete, and every link on this page resolves to a file that
exists.

That is a statement about *coverage of this sub-wiki's plan*, not a claim of omniscience. When
a question falls outside these pages — a corner of the API nobody has needed yet, a workspace
feature with no page here — ground the answer in installed source or the `autogalaxy_workspace`
scripts and **say that is what you did**, rather than answering as though a page covered it.
If the gap is real and recurring, `../../ROADMAP.md` is where it gets recorded and
[`../../skills/ag_update_wiki.md`](../../skills/ag_update_wiki.md) is the workflow that fills
it. (The galaxy-structure science reference lives in `../literature/` — see its own index.)

## How this sub-wiki is maintained

`wiki/core/` is **read-only** in ordinary sessions. Every page pins the source commits it
was validated against and carries a `content_sha256` binding its prose to that claim, so a
hand edit breaks the provenance check by design. The schema and the rules are in
[`README.md`](./README.md); the two workflows allowed to rewrite pages are
[`ag_update_wiki`](../../skills/ag_update_wiki.md) (page refresh) and
[`ag_refresh_api_docs`](../../skills/ag_refresh_api_docs.md) (the full sweep), with
[`ag_audit_skill_apis`](../../skills/ag_audit_skill_apis.md) owning the five mechanical
currency checks. `api_audit_baseline.json` records the API surface all of this was validated
against.
