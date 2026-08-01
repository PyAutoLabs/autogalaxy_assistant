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

**Delivered.** `dataset/imaging/cosj100020+015344/` ships a real four-band JWST/NIRCam cutout
reduced through `PyAutoReduce` from COSMOS-Web (program 1727) exposures: `F115W` and `F150W` at
0.03"/pixel, `F277W` and `F444W` at 0.06"/pixel, each with `{data,noise_map,psf}.fits` and its
own `info.json`, plus a dataset-level `info.json`, a `reduction_manifest.json` and a
full-provenance `README.md`. Every `info.json` number is measured from the delivered cutouts;
the redshift and catalogue identifiers are cited rather than measured, and the sky pedestal and
model-PSF caveats are stated rather than smoothed over.
`wiki/core/operations/dataset.md` documents the layout, the schema and those caveats, and is
listed in `wiki/core/index.md`. `docs/make_readme_figures.py` rebuilds the README hero
(`docs/images/cosj100020+015344_dataset.png`) offline from the shipped FITS alone — no
third-party asset is vendored, which `docs/images/sources/README.md` records explicitly.
`README.md` v2 is the real front door, and `benchmarks/prompts/easy_cosj100020_imaging.md`
freezes its second starter prompt with a 100-point rubric — which un-skips the two repo-level
tests in `autoassistant/tests/test_benchmark.py`.

The card shipped as `easy_cosj100020_imaging.md`, not the planned
`easy_<bundled-dataset>_sersic.md`: its prompt fits an MGE bulge with a free sky level and adds
a single Sersic only as a comparison, so naming it for one profile would have described less
than it measures.

### Still open

- [ ] `dataset/imaging/cosj100020+015344/mask_extra_galaxies.fits` — the bundled cutout *does*
      have a real neighbour, so this line stays live: a faint source **2.6" from the centre**,
      inside any mask wide enough to reach the galaxy's outer isophotes. (A brighter one 8.0"
      out is already excluded by a <~4" mask.) No mask ships today, so that source has to be
      masked or modelled per session — the dataset README and the README hero figure both flag
      it. Grounding: `imaging/data_preparation/gui/mask_extra_galaxies.py`.
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

**Delivered.** All nine core-loop skills are on disk with `.claude/skills/` symlinks, rows in
`wiki/core/external/skill_citation_map.md` and entries in the `skills/README.md` Index:
`ag_setup_environment`, `ag_prepare_imaging_data`, `ag_simulate_dataset`,
`ag_build_imaging_model`, `ag_configure_search`, `ag_run_search`, `ag_plot_fit`,
`ag_load_results`, `ag_debug_fit_failure`. Two `AGENTS.md` hand-offs closed with them: the
session-start environment repair now routes to `ag_setup_environment`, and the real-data
inspection gate's procedure is owned by `ag_prepare_imaging_data` rather than pointing at the
workspace scripts directly.

## Phase 4b — features beyond a single smooth profile (8 skills)

**Delivered.** All eight feature skills are on disk with `.claude/skills/` symlinks, rows in
`wiki/core/external/skill_citation_map.md` and entries in the `skills/README.md` Index:
`ag_basis_profiles`, `ag_pixelization`, `ag_light_model_extras`, `ag_ellipse_fitting`,
`ag_multi_dataset`, `ag_build_interferometer_model`, `ag_multi_galaxy_and_cluster`,
`ag_chain_searches`. Each was written from the grounding scripts named above rather than from
memory, and every symbol resolves against released `2026.7.29.2`. That brings the repo to
twenty-four live skills, seventeen of them galaxy-modelling.

Three grounding notes, recorded so nobody re-derives them:

- `ellipse/` really has no `start_here.py`, so `ag_ellipse_fitting` routes to `modeling.py` and
  says so in its own `## Further reading` block.
- The lecture series has no chapter on ellipse fitting, interferometry or multi-wavelength
  fitting. Rather than invent a citation, `ag_ellipse_fitting` omits its student bullet and
  points at `wiki/core/concepts/ellipse_fitting_and_multipoles.md` instead, while
  `ag_multi_dataset` and `ag_build_interferometer_model` cite the HowToGalaxy tutorial that
  teaches the idea each fit leans on hardest (linear profiles; the likelihood) and say plainly
  that it is not a chapter on their own subject.
- Grounding `ag_chain_searches` against the wheel exposed a **stale claim** that had spread from
  the workspace script into two merged wiki pages: `result.model` returns the fitted model with
  its **original priors unchanged** (`samples_summary.model.mapper_via_defaults_from`, which maps
  every prior to itself), *not* narrowed `TruncatedGaussianPrior`s. The narrowing lives on
  `result.model_centred` and its `model_centred_absolute(a=)` / `model_centred_relative(r=)` /
  `model_centred_max_lh_bounded(b=)` variants. `wiki/core/concepts/non_linear_search.md` and
  `wiki/core/api/configuration.md` were corrected in this phase and re-stamped.

### Still open

- [ ] Upstream fix for the same claim in
      `autogalaxy_workspace:scripts/guides/modeling/chaining.py`, whose prose still describes
      `result.model` as producing narrowed Gaussians. A `contribute-upstream` candidate; until it
      lands, `skills/ag_chain_searches.md` warns the reader that the script's description is out
      of date.

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
