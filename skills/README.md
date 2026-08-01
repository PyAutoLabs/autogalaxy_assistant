# skills/

Procedural how-to-do-X skills for the PyAuto\* galaxy-modelling stack. Each skill is a
single Markdown file with YAML frontmatter; the body teaches an agent (and through them, the
user) how to write Python that accomplishes one galaxy-structure task.

Skills are also exposed at `.claude/skills/` (Claude Code) and `~/.codex/skills/` (when
configured) via symlinks; the canonical files live here.

## Conventions

- File names use the `ag_<task>` convention for library-API skills, e.g. `ag_run_search.md`.
- Project-workflow skills (repo-level operations, template manipulation) use a plain
  kebab-case name, e.g. `start-new-project.md`.
- Meta-skills (writing guide, bootstrap protocol) start with `_`.
- Every library-API skill is **python-first**: the deliverable is a runnable `.py` script
  + the understanding to evolve it. Project-workflow skills may instead drive `rsync`,
  `cp`, or other repo-level operations.
- Source citations use the project-name + repo-relative-path form,
  e.g. `PyAutoFit:autofit/non_linear/search/nest/nautilus/`, resolved via
  [`../sources.yaml`](../sources.yaml).
- Wiki references use workspace-relative paths, e.g. `wiki/core/stack/overview.md`.
- Every skill that cites an external resource takes its `## Further reading` block from its
  row in [`../wiki/core/external/skill_citation_map.md`](../wiki/core/external/skill_citation_map.md).
  Add the row in the same change as the skill; a skill whose row is entirely `_` (every
  maintenance and workflow skill today) omits the block.

## Index — what exists today

Seven skills are written: two meta, two project-workflow, three maintenance. **Everything
else in this file is a plan, not a file** — the "Pending" section below is a catalogue of what
has not been authored yet, and deliberately does not link to anything. Every entry here that
is a link resolves; if you find a link that doesn't, that is a bug worth fixing rather than a
file worth waiting for.

No skill for *doing* galaxy science exists yet: the modelling loop arrives in Phase 4a and the
feature skills in Phase 4b. Until then, answer a science request from the installed source and
the grounding scripts named in the Pending tables, say that is what you did, and offer to
author the skill via [`_bootstrap_skill.md`](./_bootstrap_skill.md).

### Meta

- [`_style.md`](./_style.md) — writing guide every skill is authored against. Read first
  before adding or editing any skill.
- [`_bootstrap_skill.md`](./_bootstrap_skill.md) — protocol for authoring a new skill on
  demand when a user requests a capability not yet covered.

### Project workflow

- [`start-new-project.md`](./start-new-project.md) — the single bridge to a standalone
  **science project** and its full lifecycle (Create → Work → Collaborate → Publish):
  scaffold a lean repo that copies the reproducible science and refers back to the assistant
  for skills/wiki, run modelling with reproducibility manifests + the `wiki/project/` journal,
  build collaborator summaries, and harden for an open-science release (CITATION/license/Zenodo).
  Optional HPC folder.
- [`contribute-upstream.md`](./contribute-upstream.md) — prepare a scoped change,
  push it either to your collaborator branch on `PyAutoLabs/autogalaxy_assistant`
  or to your fork, and open a draft PR into `PyAutoLabs/autogalaxy_assistant`.

### Maintenance

These three keep this repo's own content honest against the installed stack. They are
maintainer workflows, not science workflows — don't surface them when answering a galaxy
question, and don't fold them into an unrelated change, because their whole value is a
reviewable diff.

- [`ag_audit_skill_apis.md`](./ag_audit_skill_apis.md) — the five mechanical currency checks
  in `autoassistant/audit_skill_apis.py`: symbol resolution across `skills/`,
  `wiki/core/api+stack/` and `scripts/`; the API-surface version baseline
  (`--check-version` / `--write-baseline`); the idiom deny-list that catches removed
  constructions whose tokens still import; page provenance (`content_sha256` + pinned
  commits); and `Project:path` citation resolution. Also documents running the code gate by
  hand and its bypass.
- [`ag_update_wiki.md`](./ag_update_wiki.md) — refresh `wiki/core/` pages whose pinned source
  commits have moved: diff the pins, rewrite only the drifted sections, re-pin, re-stamp, and
  surface newly exported APIs for the user to decide on. **The one workflow permitted to write
  inside the otherwise read-only `wiki/core/`.**
- [`ag_refresh_api_docs.md`](./ag_refresh_api_docs.md) — the umbrella sweep after a stack
  upgrade, orchestrating the two above across all four drift surfaces (skills, wiki, source
  pins, generated scripts), with `autoassistant/refresh_api_docs.py` as its preflight.

## Pending — the `ag_*` skill roadmap

Not yet written. Grouped by the phase that will author them, each with the
`autogalaxy_workspace` script(s) that ground its API — a skill is written *from* those
scripts, never from memory, because older PyAutoGalaxy releases are heavily represented in
model training data. The repo-root [`PENDING.md`](../PENDING.md) is the authoritative ledger
and shrinks as each phase lands.

**Until a skill exists, do not pretend it does.** Answer from the installed source and the
named grounding scripts, say that is what you did, and offer to author the skill via
[`_bootstrap_skill.md`](./_bootstrap_skill.md).

### Phase 4a — the core modelling loop

| Skill | Purpose | Grounding (`autogalaxy_workspace/scripts/`) |
|-------|---------|--------------------------------------------|
| `ag_setup_environment` | detect absent or broken PyAuto\* environments, install via pip or editable clones, configure caches, verify imports | `guides/modeling/bug_fix.py` + the RTD installation pages |
| `ag_prepare_imaging_data` | load and preprocess FITS imaging, decide masking for real data, measure noise, prepare the PSF | `imaging/data_preparation/start_here.py`, `imaging/data_preparation/examples/`, `imaging/data_preparation/gui/` |
| `ag_simulate_dataset` | synthesise a galaxy dataset from a ground-truth light model, including population samples | `imaging/simulator.py`, `imaging/simulator_sersic.py`, `imaging/simulator_sample.py` |
| `ag_build_imaging_model` | compose a galaxy's light model (bulge, disk, single Sersic) and wrap it in an imaging analysis | `imaging/start_here.py`, `imaging/modeling.py`, `guides/modeling/cookbook.py` |
| `ag_configure_search` | pick and tune a non-linear search or gradient optimizer for the problem at hand | `guides/modeling/searches.py`, `guides/modeling/customize.py` |
| `ag_run_search` | execute `search.fit(model=..., analysis=...)`, monitor convergence, read the live output folder | `imaging/modeling.py`, `guides/modeling/bug_fix.py` |
| `ag_plot_fit` | plot the model image, residuals, normalised residuals and chi-squared map | `imaging/plot.py`, `guides/plot/start_here.py`, `guides/plot/plotters.py` |
| `ag_load_results` | load a completed fit's galaxies, samples, dataset and FITS products from its output folder | `guides/results/start_here.py`, `guides/results/aggregator/` |
| `ag_debug_fit_failure` | diagnose a fit that didn't converge or produced unphysical structural parameters | `guides/modeling/bug_fix.py`, HowToGalaxy `chapter_2_modeling/tutorial_4_dealing_with_failure` |

### Phase 4b — features beyond a single smooth profile

| Skill | Purpose | Grounding (`autogalaxy_workspace/scripts/`) |
|-------|---------|--------------------------------------------|
| `ag_basis_profiles` | linear light profiles, Multi-Gaussian Expansion and shapelets — flexible bases that solve for intensity by linear inversion | `imaging/features/linear_light_profiles/`, `imaging/features/multi_gaussian_expansion/`, `imaging/features/shapelets/` |
| `ag_pixelization` | pixelised reconstruction of an irregular or clumpy galaxy, with regularisation | `imaging/features/pixelization/` |
| `ag_light_model_extras` | blended neighbours, sky background, and already-PSF-convolved (operated) components | `imaging/features/extra_galaxies/`, `imaging/features/sky_background/`, `imaging/features/operated_light_profile/` |
| `ag_ellipse_fitting` | non-parametric isophote fitting and multipole perturbations | `ellipse/modeling.py`, `ellipse/multipoles.py`, `ellipse/database.py` (note: `ellipse/` has no `start_here.py`) |
| `ag_multi_dataset` | simultaneous fits across wavebands or instruments via the factor graph | `multi_dataset/start_here.py`, `multi_dataset/features/` |
| `ag_build_interferometer_model` | uv-plane modelling of ALMA / JVLA observations | `interferometer/start_here.py`, `interferometer/modeling.py` |
| `ag_multi_galaxy_and_cluster` | 2+ blended galaxies each with a free light model; BCG + catalogue-driven member population in a cluster field | `multi_galaxy/start_here.py`, `cluster/start_here.py` |
| `ag_chain_searches` | sequence searches so a later fit inherits priors from an earlier one | `guides/modeling/chaining.py`, HowToGalaxy `chapter_3_search_chaining` |

### Phase 5 — literature

| Skill | Purpose | Grounding |
|-------|---------|-----------|
| `ag_ingest_paper` | add a galaxy-structure paper (local PDF or arXiv URL): project-local `wiki/project/bibliography.md` by default inside a science project; shared `wiki/literature/` in the assistant clone or on explicit promotion | `wiki/literature/` schema (arrives in the same phase) |

### Phase 6 — output surfaces

| Skill | Purpose | Grounding |
|-------|---------|-----------|
| `ag_to_notebook` | convert a generated narrative-docstring script to a Jupyter notebook (docstrings → markdown cells, code → code cells) | `autoassistant/to_notebook.py` |
| `ag_inspect_results_mcp` | the read-only results-inspector MCP server: browse fits, summaries and result images from chat harnesses without code execution | `autoassistant/mcp/galaxy_tools.py` |

### Backlog — may never ship

Catalogued so the gap is visible, but with **no `autogalaxy_workspace` script that grounds
them**. Neither may be authored by porting the equivalent skill from a sibling assistant: a
recipe with no grounding script is exactly the failure mode the API discipline exists to
prevent. Write one only when the workspace grows an example, or when a user's real need
supplies the missing ground truth.

- `ag_custom_profile` — write a new light profile subclass and register it for use in
  models. Closest existing material: `guides/profiles/light.py` (uses the built-in
  profiles; does not subclass).
- `ag_custom_analysis` — subclass an analysis object to add custom likelihood terms.

## Stub-tracking discipline

If a skill is ever committed as a scaffold rather than a complete recipe — frontmatter and
the Orient/Ask/Branch/Combine skeleton in place, but `Branch` recipes left as TODO markers —
it **must** be marked `(stub)` in this index on the same commit, and it must appear in
`PENDING.md` with the grounding script that will complete it.

The rule exists because an unmarked stub is worse than a missing file: an agent that reads
this index trusts it, activates the skill, and emits a recipe that was never grounded. A
sibling assistant once shipped an index listing 45 skills of which 13 existed. Prefer an
honest gap in the Pending tables above over a hollow entry in the Index.

The same rule governs links. An entry under "Index — what exists today" carries a relative
link; an entry anywhere in "Pending" carries none, so a broken link is always a real defect
and never an expected placeholder.
