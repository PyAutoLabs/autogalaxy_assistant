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
- [ ] `wiki/core/operations/dataset.md` — on-disk dataset layout and `info.json`. **Moved here
      from Phase 3**: the page describes the bundled dataset's tree, so it cannot be written
      honestly before that dataset exists. Grounding:
      `imaging/data_preparation/start_here.py` and the workspace `dataset/` trees. Until it
      lands, `wiki/core/index.md` names it as pending and routes to those two sources.
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

**Delivered.** `wiki/core/` now holds `stack/` (5), `api/` (9), `concepts/` (15),
`operations/` (2) and `external/` (5), plus a rebuilt `index.md` that lists every one and
names what is still missing; `skills/` gained the three maintenance skills
(`ag_audit_skill_apis`, `ag_update_wiki`, `ag_refresh_api_docs`) with matching
`.claude/skills/` symlinks. Two Phase-3 items were **moved rather than done** — see Phase 2
(`operations/dataset.md`) and Phase 6 (the two HPC pages) — and one is still open, below.

Three planned page names shipped under different names, recorded here so nobody hunts for a
file that was never written:

- planned `api/basis.md` → shipped as two concepts pages,
  `concepts/linear_light_profiles_and_mge.md` and `concepts/shapelets.md`, with the profile
  variants themselves tabulated in `api/light_profile_catalog.md`. A "basis" page would have
  had to explain the physics and list the API in one breath; the split follows the
  `api/` = *which one* vs `concepts/` = *what and why* boundary.
- planned `api/analysis.md` → shipped as `api/analysis_objects.md`, which also covers model
  composition and the factor graph.
- planned `concepts/over_sampling.md` and `concepts/regularisation.md` → folded into
  `concepts/grids_and_masks.md` and `concepts/inversions_and_pixelizations.md`, where neither
  concept can be explained apart from its host anyway.

`api/configuration.md` was added beyond the plan (the `config/` tree needed a map), and
`concepts/jax_acceleration.md` was **not** written as a standalone page: JAX guidance lives
where it is acted on — the run-time and GPU sections of `concepts/non_linear_search.md`,
`api/searches.md`, `api/analysis_objects.md`, and the caches and `PYAUTO_DISABLE_JAX` in
`operations/sandbox.md`. Revisit only if a user question shows the split leaves a real gap.

### Still open

- [ ] Re-pin `wiki/core/api_audit_baseline.json`. **Do not re-pin from a local source
      checkout.** The committed baseline is wheel-derived (generated against released
      `2026.7.29.2`), which is what the `wiki-currency` job installs; a checkout of library
      `main` carries a frozen version stamp and a newer public surface, so
      `--check-version` reports drift locally that is not drift in CI. Re-pin only from an
      environment on the *released* stack, and only after `--scope all` is clean there — the
      procedure is in `skills/ag_audit_skill_apis.md` "The version baseline".

## Phase 4a — the core modelling loop (9 skills)

- [ ] `skills/ag_setup_environment.md` — grounding: `guides/modeling/bug_fix.py`, plus
      `wiki/core/operations/installation.md` and `wiki/core/operations/sandbox.md` (both live
      since Phase 3) and the RTD installation pages they were written from. `AGENTS.md`'s
      session-start step and `skills/ag_audit_skill_apis.md` route environment failures here;
      until it exists they route to `--check-install` and those two pages.
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
- [ ] `wiki/core/operations/hpc.md` — cluster concepts: cores, JAX/GPU, SLURM. **Moved here
      from Phase 3.** Grounding: `guides/hpc/example_cpu_and_gpu.py`, `guides/using_jax.py`.
- [ ] `wiki/core/operations/hpc_infrastructure.md` — the `hpc/` templates and `sync` CLI.
      **Moved here from Phase 3**, where it was already blocked: the page documents files that
      only exist once the `hpc/` item above ships, so the two land together.
      `wiki/core/index.md` names both as pending and routes to the two workspace guides
      meanwhile.
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
