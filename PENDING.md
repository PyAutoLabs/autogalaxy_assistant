# PENDING — what this assistant does not have yet

`autogalaxy_assistant` is public from birth and built in phases. This file is the
authoritative ledger of everything still missing: one line per deliverable, grouped by the
phase that authors it, and — where the deliverable is a skill or a reference page — naming the
`autogalaxy_workspace` script(s) that ground its API.

**Why it exists.** A public assistant that lists capabilities it does not have is worse than
one that admits a gap: an agent reads the index, trusts it, activates a skill that was never
written, and emits a recipe grounded in nothing. Every other file in this repo is allowed to
describe a pending item in prose, but **no file may link to one**, and no agent may answer as
though it had read one. When something here is needed before its phase, author it properly —
from the named grounding scripts, never from memory, because older PyAutoGalaxy releases are
heavily represented in model training data.

**Lifecycle.** This file shrinks as each phase lands: the phase that authors a deliverable
deletes its line in the same PR. At Phase 6 the file is retired and replaced by `ROADMAP.md`
(forward-looking wishes, not admissions of absence).

**Tracker.** Epic: [PyAutoLabs/PyAutoBrain#188](https://github.com/PyAutoLabs/PyAutoBrain/issues/188).

Paths under "grounding" are relative to `autogalaxy_workspace/scripts/` unless another repo is
named.

---

## Phase 2 — dataset, README front door, external signposts

- [ ] `dataset/imaging/<galaxy>/` — a real multi-band JWST COSMOS-Web NIRCam cutout of a
      non-lens galaxy: `wavebands/<BAND>/{data,noise_map,psf}.fits` + `info.json`, plus a
      per-dataset provenance README. Every `info.json` number measured by a committed script
      or cited — never invented. Gated on the user approving the cutout + archive identifiers.
- [ ] `dataset/imaging/<galaxy>/mask_extra_galaxies.fits` — only if the cutout has real
      neighbours. Grounding: `imaging/data_preparation/gui/mask_extra_galaxies.py`.
- [ ] `docs/make_readme_figures.py` + the hero PNG it renders + a vendored-sources README.
      `docs/` is outside the audit scan set, so it is validated by execution from a fresh venv.
- [ ] `README.md` v2 — science framing, three anchored example prompts, and an explicit "what
      works today / what's coming" section.
- [ ] `benchmarks/prompts/easy_<bundled-dataset>_sersic.md` — the easy assistant card, whose
      prompt text must match the README verbatim (enforced by
      `autoassistant/tests/test_benchmark.py::test_repo_readme_prompts_match_cards`, currently
      skipped). Grounding: `imaging/start_here.py`.
- [ ] External signpost PRs (shipped from their own repos, merged after this phase):
      `autogalaxy_workspace` llms.txt + README, `PyAutoGalaxy/llms.txt`, `HowToGalaxy/llms.txt`,
      and the org profile README — four places that currently advertise this assistant.

## Phase 3 — `wiki/core` reference + tooling skills

`wiki/core/stack/` (5 pages) and `index.md` are live. Everything below is not, and
`wiki/core/index.md` says so.

### `wiki/core/api/` — task-oriented catalogues

- [ ] `searches.md` — every non-linear search and gradient optimizer, and when to pick each.
      Grounding: `guides/modeling/searches.py`, `guides/modeling/customize.py`.
- [ ] `light_profile_catalog.md` — every light profile, standard / linear / operated / snr
      variants. Grounding: `guides/profiles/light.py`, `PyAutoGalaxy:autogalaxy/profiles/light/`.
- [ ] `mass_profile_catalog.md` — **keep this page**: PyAutoGalaxy owns mass profiles, framed
      for dynamical and stellar-mass work rather than lensing. Grounding:
      `PyAutoGalaxy:autogalaxy/profiles/mass/`.
- [ ] `basis.md` — linear light profiles, Multi-Gaussian Expansion, shapelets. Grounding:
      `imaging/features/linear_light_profiles/`, `imaging/features/multi_gaussian_expansion/`,
      `imaging/features/shapelets/`.
- [ ] `datasets.md` — imaging, interferometer and their settings objects. Grounding:
      `imaging/start_here.py`, `interferometer/start_here.py`.
- [ ] `plotting.md` — the functional plot entry points (`dir()` of the plot module is the
      authoritative list; there are no object-oriented plotters). Grounding:
      `guides/plot/start_here.py`, `guides/plot/plotters.py`, `guides/plot/visuals.py`.
- [ ] `analysis.md` — the analysis objects and the factor graph that combines them. Grounding:
      `imaging/modeling.py`, `multi_dataset/start_here.py`.
- [ ] `ellipse.md` — **new page, no sibling equivalent**: the ellipse/isophote fitting API.
      Grounding: `ellipse/modeling.py`, `ellipse/multipoles.py`.
- [ ] `aggregator.md` — loading and querying many completed fits. Grounding:
      `guides/results/aggregator/`, `guides/results/database/start_here.py`.

### `wiki/core/concepts/` — the physics and inference

- [ ] `light_profiles.md`, `galaxies.md` (replaces a lensing assistant's galaxy-and-plane
      page), `grids_and_masks.md`, `over_sampling.md`, `basis_expansions_and_mge.md`,
      `ellipse_fitting.md`, `inversions_and_pixelizations.md`, `regularisation.md`,
      `non_linear_search.md`, `samples_and_posteriors.md`, `linear_light_profiles.md`,
      `multi_wavelength.md`, `cosmology_and_units.md`, `jax_acceleration.md`.
      Grounding: `guides/galaxies.py`, `guides/data_structures.py`,
      `guides/advanced/over_sampling.py`, `guides/units/{cosmology,flux}.py`,
      `guides/using_jax.py`, `imaging/likelihood_function.py`, `ellipse/`,
      `imaging/features/pixelization/`. Scope the set to what PyAutoGalaxy actually models:
      single-plane galaxy light and mass. Do not import concept pages from a sibling
      assistant whose domain is different.

### `wiki/core/operations/`

- [ ] `installation.md` — grounding: the PyAutoGalaxy RTD installation pages.
- [ ] `dataset.md` — dataset layout + `info.json`. Grounding:
      `imaging/data_preparation/start_here.py` and the workspace `dataset/` trees.
- [ ] `sandbox.md` — cache env vars, `PYAUTO_TEST_MODE`, restricted environments.
- [ ] `hpc.md` — cores, JAX/GPU, SLURM concepts. Grounding:
      `guides/hpc/example_cpu_and_gpu.py`, `guides/using_jax.py`.
- [ ] `hpc_infrastructure.md` — the `hpc/` templates and `sync` CLI. Blocked until Phase 6
      actually ships `hpc/`; `scripts/AGENTS.md` documents the interface contract meanwhile.

### `wiki/core/external/`

- [ ] `index.md`, `howtogalaxy.md`, `workspace.md`, `rtd.md`, `skill_citation_map.md` — the
      per-skill audience routing table that `skills/_style.md` currently expands by hand.

### Phase 3 skills

- [ ] `skills/ag_audit_skill_apis.md` — grounding: `autoassistant/audit_skill_apis.py`.
- [ ] `skills/ag_update_wiki.md` — grounding: `wiki/core/`, `sources.yaml`.
- [ ] `skills/ag_refresh_api_docs.md` — grounding: `autoassistant/refresh_api_docs.py`.

### Also in Phase 3

- [ ] Re-pin `wiki/core/api_audit_baseline.json` after the new pages land.

## Phase 4a — the core modelling loop (9 skills)

- [ ] `skills/ag_setup_environment.md` — grounding: `guides/modeling/bug_fix.py` + the RTD
      installation pages.
- [ ] `skills/ag_prepare_imaging_data.md` — grounding:
      `imaging/data_preparation/start_here.py`, `imaging/data_preparation/examples/`,
      `imaging/data_preparation/gui/`. **This skill owns the real-data inspection gate's
      procedure**, which `AGENTS.md` currently points at the workspace scripts for.
- [ ] `skills/ag_simulate_dataset.md` — grounding: `imaging/simulator.py`,
      `imaging/simulator_sersic.py`, `imaging/simulator_sample.py`.
- [ ] `skills/ag_build_imaging_model.md` — grounding: `imaging/start_here.py`,
      `imaging/modeling.py`, `guides/modeling/cookbook.py`.
- [ ] `skills/ag_configure_search.md` — grounding: `guides/modeling/searches.py`,
      `guides/modeling/customize.py`.
- [ ] `skills/ag_run_search.md` — grounding: `imaging/modeling.py`,
      `guides/modeling/bug_fix.py`.
- [ ] `skills/ag_plot_fit.md` — grounding: `imaging/plot.py`, `guides/plot/start_here.py`,
      `guides/plot/plotters.py`.
- [ ] `skills/ag_load_results.md` — grounding: `guides/results/start_here.py`,
      `guides/results/aggregator/`, `guides/results/latent_variables.py`.
- [ ] `skills/ag_debug_fit_failure.md` — grounding: `guides/modeling/bug_fix.py`,
      HowToGalaxy `chapter_2_modeling/tutorial_4_dealing_with_failure`.

## Phase 4b — features beyond a single smooth profile (8 skills)

- [ ] `skills/ag_basis_profiles.md` — grounding: `imaging/features/linear_light_profiles/`,
      `imaging/features/multi_gaussian_expansion/`, `imaging/features/shapelets/`.
- [ ] `skills/ag_pixelization.md` — grounding: `imaging/features/pixelization/` (including
      `galaxy_reconstruction.py` and `likelihood_function.py`).
- [ ] `skills/ag_light_model_extras.md` — grounding: `imaging/features/extra_galaxies/`,
      `imaging/features/sky_background/`, `imaging/features/operated_light_profile/`.
- [ ] `skills/ag_ellipse_fitting.md` — grounding: `ellipse/modeling.py`,
      `ellipse/multipoles.py`, `ellipse/database.py`. **Route to `modeling.py`: `ellipse/` has
      no `start_here.py`.**
- [ ] `skills/ag_multi_dataset.md` — grounding: `multi_dataset/start_here.py`,
      `multi_dataset/features/`. The idiom deny-list genuinely bites here: datasets combine
      via the factor graph, never by summing analyses.
- [ ] `skills/ag_build_interferometer_model.md` — grounding: `interferometer/start_here.py`,
      `interferometer/modeling.py`, `interferometer/features/`.
- [ ] `skills/ag_multi_galaxy_and_cluster.md` — grounding: `multi_galaxy/start_here.py`,
      `cluster/start_here.py`. The subject is member **light**, not lensing — the phase where
      lensing language most wants to creep back in.
- [ ] `skills/ag_chain_searches.md` — grounding: `guides/modeling/chaining.py`, HowToGalaxy
      `chapter_3_search_chaining`.

## Phase 5 — `wiki/literature` corpus

- [ ] `wiki/literature/` — `AGENTS.md` schema, `index.md`, `README.md`, `log.md`, plus
      `concepts/`, `entities/`, `sources/` and `autogalaxy_literature.bib`. Topics: Sersic and
      bulge-disk decomposition, isophotes and multipoles, MGE, early-type structure, scaling
      relations, high-z morphology. Entities: surveys (COSMOS-Web, CANDELS, MaNGA/SAMI, Euclid
      morphology).
- [ ] `skills/ag_ingest_paper.md` — grounding: the `wiki/literature/` schema authored in the
      same phase.
- [ ] Every citation verified by web search against ADS/arXiv before it is recorded. A
      fabricated citation is the worst possible artifact for a public repo, and prior
      experience is that a memory-sourced paper's metadata is wrong often enough to matter.

## Phase 6 — benchmarks, HPC, ledger retirement

- [ ] `benchmarks/prompts/medium_mge_bulge_disk.md`,
      `benchmarks/prompts/hard_multi_galaxy_cluster.md`,
      `benchmarks/prompts/teacher_workflow.md` — with rubric rows in the format
      `autoassistant/benchmark.py` parses.
- [ ] `benchmarks/RESULTS.md` — regenerated only from cards that were actually run. Never ship
      unrun scores.
- [ ] `hpc/` — `template.py`, `batch_cpu/`, `batch_gpu/`, the `sync` CLI, with galaxy-tuned
      prose (sample-scale batches; `template.py` imports autogalaxy). `hpc/` is outside the
      audit scan set and CI-ungated, so it is validated by hand execution. The interface
      contract it must satisfy is already documented in `scripts/AGENTS.md`.
- [ ] `skills/ag_to_notebook.md` — grounding: `autoassistant/to_notebook.py`.
- [ ] `skills/ag_inspect_results_mcp.md` — grounding: `autoassistant/mcp/galaxy_tools.py`.
- [ ] Retire this file: replace with `ROADMAP.md` and close out the epic's deferral list.

## Backlog — catalogued, may never ship

Neither has an `autogalaxy_workspace` script that grounds it, and neither may be authored by
porting the equivalent skill from a sibling assistant — a recipe with no grounding script is
precisely the failure this ledger exists to prevent. Write one only when the workspace grows an
example, or when a real user need supplies the missing ground truth.

- [ ] `skills/ag_custom_profile.md` — subclassing a light profile. Closest existing material:
      `guides/profiles/light.py`, which uses the built-in profiles without subclassing.
- [ ] `skills/ag_custom_analysis.md` — subclassing an analysis to add likelihood terms.

## Deferred by decision (not pending work)

Recorded on the epic; listed here so nobody files them as gaps.

- `paper/` + a JOSS `draft-pdf.yml` workflow — considered only after the assistant is complete.
- A `REFERENCE_PROFILES` entry in PyAutoBrain's clone tooling — owned by whoever first clones
  *from* this repo. `modes/maintainer.md`'s "Assistant-as-template" section is the partition
  seed that entry would pair with, and its four bold markers are read literally, so keep them.
- A second HST / PyAutoReduce dataset.
