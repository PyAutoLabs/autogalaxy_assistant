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

Sixteen skills are written: nine for the core modelling loop, two meta, two project-workflow,
three maintenance. **Everything else in this file is a plan, not a file** — the "Pending"
section below is a catalogue of what has not been authored yet, and deliberately does not link
to anything. Every entry here that is a link resolves; if you find a link that doesn't, that is
a bug worth fixing rather than a file worth waiting for.

The core modelling loop is live; the feature skills (bases, pixelisations, ellipse fitting,
multi-dataset, interferometry, multi-galaxy, search chaining) arrive in Phase 4b. For a request
that falls outside the nine below, answer from the installed source and the grounding scripts
named in the Pending tables, say that is what you did, and offer to author the skill via
[`_bootstrap_skill.md`](./_bootstrap_skill.md).

### Galaxy modelling — the core loop

Read in this order for an end-to-end fit; each is usable on its own. Every one is
**python-first**: the deliverable is a runnable script plus the understanding to evolve it.

- [`ag_setup_environment.md`](./ag_setup_environment.md) — install, diagnose and repair the
  PyAutoGalaxy environment so galaxy-modelling code can actually run: a fresh pip install, the
  JAX and numba extras, writable caches for a sandbox, `activate.sh` interpreter resolution,
  a shared/cluster checkout and the Colab entry point, ending in a saved verification script.
- [`ag_prepare_imaging_data.md`](./ag_prepare_imaging_data.md) — load a user's own CCD imaging
  from FITS into an `ag.Imaging` and get it ready to fit: pixel scale, flux units, RMS
  noise-map, PSF, mask extent, contaminants, over-sampling and the `info.json` sidecars.
  **Owns the real-data inspection gate.**
- [`ag_simulate_dataset.md`](./ag_simulate_dataset.md) — simulate imaging (or visibilities) of a
  galaxy with known truth: grid and over-sampling, PSF, exposure time and background sky, light
  profiles, FITS output plus a `galaxies.json` truth record, S/N targeting, whole samples in a
  loop, and the `should_simulate` convention.
- [`ag_build_imaging_model.md`](./ag_build_imaging_model.md) — compose the model for an imaging
  fit: an `af.Model` / `af.Collection` tree of light profiles on one or more galaxies plus the
  `ag.AnalysisImaging` that scores it — single Sersic, bulge-plus-disk, linear profiles, MGE,
  prior customisation, pairing and assertions, `ag.DatasetModel`, and checking with
  `print(model.info)` before spending a search.
- [`ag_configure_search.md`](./ag_configure_search.md) — choose and configure the non-linear
  search: `af.Nautilus` for a quotable posterior, `af.MultiStartProdigy` for a fast MAP check,
  `af.DynestyStatic` for ellipse fitting and cross-checks, plus `n_live` / `n_batch` /
  `n_starts`, the output cadence, start-point initialisers, grid searches, and the
  `unique_tag` resume semantics that silently reuse a fit across datasets.
- [`ag_run_search.md`](./ag_run_search.md) — drive `search.fit(model=model, analysis=analysis)`
  to completion and read what it wrote: the output-folder anatomy and on-the-fly announcement,
  resume behaviour, quick updates, JAX/GPU acceleration and VRAM checks, the
  `PYAUTO_TEST_MODE` smoke levels, and the `if __name__ == "__main__"` parallelisation fix.
- [`ag_plot_fit.md`](./ag_plot_fit.md) — visualise a dataset, a galaxy or a fit with the
  functional `aplt` API: dataset and fit subplots, individual residual / normalised-residual /
  chi-squared panels, per-galaxy breakdowns, log10 stretch and fixed colour limits, overlays,
  figures and FITS to disk — plus the residual-inspection discipline for judging a fit.
- [`ag_load_results.md`](./ag_load_results.md) — get a completed fit back into Python and turn
  it into science: the in-session `Result`, direct `from_json` / `SamplesNest.from_table`
  loading of one output folder, the `Samples` API for medians and errors, and the aggregator
  for a whole sample with its `ag.agg` generators, queries and CSV/FITS/PNG exports.
- [`ag_debug_fit_failure.md`](./ag_debug_fit_failure.md) — triage a fit that crashed, stalled or
  finished with parameters you do not believe, through a failure taxonomy (environment, data,
  model, priors, search settings, stale result) and the probes that separate them — including
  the two silent failures: a resumed fit whose identifier ignored the data, and a cached result
  mistaken for a new one.

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
