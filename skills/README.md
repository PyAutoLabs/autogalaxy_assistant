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

Twenty-five skills are written: nine for the core modelling loop, eight for the features beyond
a single smooth profile, two meta, two project-workflow, one literature, three maintenance. **Everything else in
this file is a plan, not a file** — the "Pending" section below is a catalogue of what has not
been authored yet, and deliberately does not link to anything. Every entry here that is a link
resolves; if you find a link that doesn't, that is a bug worth fixing rather than a file worth
waiting for.

The core modelling loop and the feature set are both live. For a request that falls outside the
seventeen galaxy-modelling skills below, answer from the installed source and the grounding
scripts named in the Pending tables, say that is what you did, and offer to author the skill via
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

### Features beyond a single smooth profile

Reach for one of these once the core loop is running and a single Sersic — or a plain
bulge-plus-disk on one CCD image — is no longer the right model. Each assumes the core loop's
composition, search and plotting conventions and changes one thing about them.

- [`ag_basis_profiles.md`](./ag_basis_profiles.md) — fit morphology with a *basis* rather than one
  or two smooth profiles: linear light profiles (`ag.lp_linear`), a Multi-Gaussian Expansion or a
  shapelet expansion, where every component's `intensity` is solved analytically by a linear
  inversion instead of sampled by the search — with the positive-only versus signed solver, the
  compact nuclear basis, and how to read solved intensities back out of a fit.
- [`ag_pixelization.md`](./ag_pixelization.md) — reconstruct clumpy or irregular light directly on
  a regularized pixel mesh, using `ag.Pixelization` alongside a parametric `ag.lp_linear` bulge:
  choosing an `ag.mesh` and an `ag.reg` scheme and what each costs, why `mesh_shape` must be fixed
  before the fit, `over_sample_size_pixelization`, noise scaling instead of hard masking, and
  reading the reconstruction and its evidence terms out of the `Inversion`.
- [`ag_light_model_extras.md`](./ag_light_model_extras.md) — the three components that sit beside a
  galaxy's own light profiles: contaminating extra galaxies, a residual background sky via
  `ag.DatasetModel`, and operated (already-PSF-convolved) profiles for compact nuclear emission —
  worked against the bundled real dataset, which has both an un-subtracted sky and a faint
  neighbour 2.6" out.
- [`ag_ellipse_fitting.md`](./ag_ellipse_fitting.md) — measure morphology non-parametrically by
  fitting isophotes with `ag.Ellipse` / `ag.FitEllipse` / `ag.AnalysisEllipse`, one ellipse at a
  time at fixed `major_axis`, producing radial axis-ratio and position-angle profiles instead of a
  light-profile model — plus `ag.EllipseMultipole`, `af.Drawer` and the `ag.agg` classes that read
  many fits back.
- [`ag_multi_dataset.md`](./ag_multi_dataset.md) — fit several datasets of the same galaxy jointly
  (multi-wavelength bands, repeated exposures, imaging together with visibilities) through the
  `af.AnalysisFactor` + `af.FactorGraphModel` construction that is the only way to combine them:
  what is shared versus freed per dataset, a wavelength relation via prior arithmetic, and
  astrometric offsets.
- [`ag_build_interferometer_model.md`](./ag_build_interferometer_model.md) — model a galaxy
  observed with a radio or millimetre interferometer by fitting its complex visibilities in the
  uv-plane: loading an `ag.Interferometer` against a real-space mask, choosing the transformer by
  visibility count, why there is no PSF and no over-sampling, and reading dirty images as
  diagnostics rather than data.
- [`ag_multi_galaxy_and_cluster.md`](./ag_multi_galaxy_and_cluster.md) — model several galaxies
  whose light blends on the sky: an interacting or projected pair, a compact multiple, or a cluster
  field with a brightest cluster galaxy plus a catalogue-driven member tier
  (`ag.galaxy_table_from_csv`) whose intensities tie to one shared normalization, so population
  size costs no dimensions — plus per-galaxy decomposed photometry.
- [`ag_chain_searches.md`](./ag_chain_searches.md) — break one hard fit into a sequence of easier
  searches, each initialized from the last: `result.model_centred` and its absolute / relative /
  bounded variants to narrow priors, `result.model` to keep the original ones, `result.instance` to
  fix a component outright, and the output-path convention that keeps a chain's searches together.

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

### Literature

- [`ag_ingest_paper.md`](./ag_ingest_paper.md) — add a galaxy-structure paper to the
  literature record: project-local `wiki/project/bibliography.md` by default inside a science
  project, or the shared `wiki/literature/` wiki plus its canonical BibTeX layer in the
  assistant clone. Verifies the metadata against a public record *before* recording it,
  writes a compact claim-oriented source entry, and closes with
  `make validate-literature-citations`.

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
