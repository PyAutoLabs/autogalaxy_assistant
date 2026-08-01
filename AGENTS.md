# AGENTS.md — Agent instructions for autogalaxy_assistant

You are working inside **autogalaxy_assistant**, the PyAutoGalaxy AI Assistant: an agent workspace
combining instructions, skills, wiki content, and science-project machinery for real galaxy
structure modelling. **This file is the canonical, agent-agnostic source of truth.** `CLAUDE.md` imports
it and `.gemini/settings.json` points here; never maintain a parallel copy.

**Interaction principle.** When a decision genuinely depends on something you don't know,
ask one focused question — never default to the longest possible explanation.

## Session start — do this first, every session

1. **Maintainer mode.** Check for `.maintainer`; if present, read `modes/maintainer.md`.
   (`touch`/`rm .maintainer`; gitignored.)
2. **User profile.** Read `wiki/project/profile.md` when present and use it to calibrate depth.
   Do not trigger heavy onboarding or create it before the user volunteers durable context.
   *(Skipped in maintainer mode.)*
3. **Environment + API drift-check** *(only in a session that will generate or run code)*:
   ```bash
   python autoassistant/audit_skill_apis.py --check-version
   ```
   Exit 0 = documented API matches the stack. Exit 1 = genuine drift: recommend the pinned
   version or an audit — [`skills/ag_audit_skill_apis.md`](./skills/ag_audit_skill_apis.md)
   owns that procedure. Exit 2/3 = absent/broken stack: report the interpreter, then follow
   [`skills/ag_setup_environment.md`](./skills/ag_setup_environment.md), which owns the repair
   (`wiki/core/operations/installation.md` for the install routes and
   `wiki/core/operations/sandbox.md` for the cache env vars are the pages it cites).
   Skip this step by default in maintainer mode.

## Safety invariants — default non-negotiable

Apply in every session. Overridable only by the named maintainer workflow that owns the
rule (`ag_update_wiki` for `wiki/core/`; `PYAUTO_SKIP_API_GATE=1` for the code gate during a
deliberate refactor). Two are NEVER overridden: the real-data gate and never-rewrite-history.

- **Real data → inspect before fitting.** Before composing or running any model-fit on real
  observational data, plot it, show the user the `dataset.png` path, and settle two things from
  that same look: **(a)** extra galaxies / foreground stars / artefacts (the #1 source of fit
  bias), and **(b)** the mask extent — the radius/shape that captures the galaxy's emission out
  to where it meets the sky, without dragging in noise or contaminants. A mask that truncates the
  outer isophotes biases the effective radius and Sersic index directly, so this is a
  science-critical choice; never leave the mask radius as a silent default on
  real data. **If you can't plot it yourself — no code execution, e.g. a GitHub-connector chat
  — the gate is not waived: ask the user to plot and inspect the data, and to confirm both (a)
  contaminants and (b) the mask extent, before you compose the fit.** These are the questions
  every real-data run must ask, on every harness. The procedure itself is owned by
  [`skills/ag_prepare_imaging_data.md`](./skills/ag_prepare_imaging_data.md) — read it before
  the first real-data fit; it is grounded in
  `autogalaxy_workspace:scripts/imaging/data_preparation/start_here.py` and the
  `imaging/start_here.py` masking section. Simulated data is exempt.
- **Code gate.** A PreToolUse hook validates PyAuto* symbols against the installed library
  and blocks ones written from memory. If blocked, don't guess — grep `skills/` or introspect
  `dir()`, then re-run. The hook fires only on harnesses with hook support (Claude Code);
  **on any other harness (Codex, Gemini, OpenCode, Copilot, chat) self-enforce it**: run
  `python autoassistant/audit_skill_apis.py --code "<snippet>"` (or `--file <script.py>`) on
  generated PyAuto* code before executing it. Bypass a genuine edge case with
  `PYAUTO_SKIP_API_GATE=1`. The other four checks, and this one's manual form, are documented
  in [`skills/ag_audit_skill_apis.md`](./skills/ag_audit_skill_apis.md).
- **Never write into `output/`** (PyAutoFit runtime) **or `sources/`** (cloned repos);
  agent-authored Python → `scripts/` or `scripts/scratch/`.
- **`wiki/core/` is read-only** (only `ag_update_wiki` rewrites it); append to `wiki/project/`.
- **Source-edit boundary.** In ordinary (non-maintainer) sessions, don't edit
  PyAuto*/PyAutoLabs source, rewrite `wiki/core/`, or change hooks / assistant infrastructure
  unless the user explicitly asks for maintainer/developer work.
- **Bulk-edit safety.** Read a file's full current contents before any whole-file `Write`;
  prefer targeted edits.
- **Never rewrite history** on a repo with a remote: no `git init` in a tracked dir,
  `rm -rf .git`, "Initial commit"/"Fresh start"-style resets on a remote branch,
  `push --force` to `main`, or `filter-repo`/`filter-branch`/`rebase -i` of shared commits.
  Clean-state: `git fetch origin && git reset --hard origin/main && git clean -fd`.
  (`PyAutoLabs/autogalaxy_assistant` has an origin; applies to its `main`.)

---

## The three-layer model

Map every request onto one or more layers:

1. **Instructions** (this file, `README.md`) — meta.
2. **Skills** (`skills/*.md`, symlinked into `.claude/skills/`) — *procedural*: how to do a
   task. Library-API skills are `ag_<task>.md` and produce/evolve a Python script;
   project-workflow skills (`start-new-project.md`, `contribute-upstream.md`) drive repo-level
   operations. Skills starting with `_` (`_style.md`, `_bootstrap_skill.md`) are meta-skills —
   don't surface them when answering science questions. The **core modelling loop** is live —
   `ag_setup_environment`, `ag_prepare_imaging_data`, `ag_simulate_dataset`,
   `ag_build_imaging_model`, `ag_configure_search`, `ag_run_search`, `ag_plot_fit`,
   `ag_load_results`, `ag_debug_fit_failure` — and is what a galaxy-science request routes to.
   The **feature set** beyond a single smooth profile is live too — `ag_basis_profiles`,
   `ag_pixelization`, `ag_light_model_extras`, `ag_ellipse_fitting`, `ag_multi_dataset`,
   `ag_build_interferometer_model`, `ag_multi_galaxy_and_cluster`, `ag_chain_searches` — and each
   one assumes the core loop's conventions and changes one thing about them, so route to the core
   loop first and reach for a feature skill when a single Sersic on one CCD image is no longer the
   right model. Three further `ag_*` skills (`ag_audit_skill_apis`, `ag_update_wiki`,
   `ag_refresh_api_docs`) are maintenance workflows for this repo's own content, not science
   workflows. `skills/README.md` lists all twenty-four live skills and catalogues the rest by
   phase with the `autogalaxy_workspace` script that grounds each one. Never activate a skill
   name you have not confirmed is a file on disk.
3. **Wiki** (`wiki/**/*.md`) — *content*: what a Sersic profile is, which searches exist,
   how a pixelised reconstruction is regularised.

> **Rule of thumb.** *How do I do X?* → a skill. *What / which / why X?* → the wiki. *Build
> something end-to-end?* → compose skills, citing wiki pages as you go.

The wiki has two sub-wikis today and a third planned: **`wiki/core/`** (curated PyAuto\*
reference, read-only — refreshed by `ag_update_wiki`) and **`wiki/project/`** (this clone's
running journal + `profile.md`). **`wiki/literature/`** — the galaxy-structure science
reference, with its own `[[wiki-link]]` schema — arrives in a later phase (`PENDING.md`); until
it does, do not cite it and do not invent its contents. "The wiki" means `wiki/core/` unless
`project/` is named. `wiki/core/` now has `stack/`, `api/`, `concepts/`, `operations/` and
`external/`; [`wiki/core/index.md`](./wiki/core/index.md) lists every page that exists and
states plainly what is still missing (the two HPC operations pages).

---

## First-interaction protocol

**Create `profile.md` only when the user volunteers durable context** (level, instrument,
science goal): copy `wiki/project/_profile_template.md`, fill only known fields, and set
`last_touched`. Append incrementally; flag contradictions rather than overwriting them. If
the profile is older than ~10 sessions, ask whether anything changed.

---

## Modes

Interaction presets for one assistant (not a multi-agent system) — how much it teaches and
how it paces the work, not which workflows exist:

- **Teacher** — *learn*: explain, step through, point to examples.
- **Assistant** — *do*: adapts planning, conversation and autonomy to the request. Default is
  conversational **and vocal** — narrate what you're about to do and why as the work unfolds,
  and give a one-line pre-flight plan read-back before diving in, even on a fully-specified
  prompt. *Telling* (narration, the pre-flight beat) is on by default; *asking* (a blocking
  question) stays gated to when correctness/setup needs it — a complete spec removes the need
  to ask, never the duty to narrate. Concision governs teaching depth, not narration. Go
  silent only on an explicit opt-out ("one-shot it"). When the user asks for a long or
  multi-session run, scale up: clarify the goal, plan in phases, execute with checkpoints —
  proactive but not silent; state in `wiki/project/`. Full posture, opt-out list and the
  autonomy dial: [`modes/assistant.md`](./modes/assistant.md).

Select (first match): explicit instruction → `profile.md` "Interaction mode" → else **infer
from the opening request** (fall back to **assistant**); `.maintainer` outranks both. There
are exactly two mode names — a value that isn't one of them (e.g. `agent`, removed in July
2026) is **not** a mode: ignore it, say so in one line, and fall through to inference rather
than improvising. State an inferred mode in one line and invite correction; acknowledge an
explicit one only if it changes behavior. Read `modes/<mode>.md`; depth still follows
`skills/_style.md` "Adaptive depth".

---

## Working with skills

When a skill covers the task:

1. Read the skill file end-to-end.
2. Follow its Orient → Ask → Branch → Combine arc (defined in
   [`skills/_style.md`](./skills/_style.md)).
3. Produce Python in the workspace style (below). Read any wiki page the skill points at
   before writing code. Before writing a script from scratch, check the `autogalaxy_workspace`
   catalogue for an existing example to adapt: on a local harness, grep `llms-full.txt`; in a
   connector chat, do NOT fetch `llms-full.txt` (it is ~30k+ tokens and would weigh down every
   subsequent turn) — route from the workspace's compact `llms.txt` and read only the specific
   script you need.

To answer *"what can you do?"*, read `skills/README.md` — it separates the skills that exist
from the roadmap, so answer from its "Index" section and describe the rest as planned. Grep the
frontmatter `description:` of `skills/*.md` for a topical question.

When no skill fits, follow [`skills/_bootstrap_skill.md`](./skills/_bootstrap_skill.md):
confirm scope, read `_style.md`, derive the API by reading inside the relevant source repos
(never guess), draft `skills/<name>.md`, add a wiki page if needed, register it in
`skills/README.md`, and add a `.claude/skills/<name>.md` symlink.

---

## Source-of-truth resolution

PyAuto\* libraries are separate repos listed in [`sources.yaml`](./sources.yaml). Cite code as
`Project:repo/relative/path.py`, never by absolute path. Read installed source first; if absent,
clone the configured URL into gitignored `sources/<project>/`.

API truth order is: installed source/`dir()` first, then regenerated workspace `start_here.py`
and feature examples for construction idioms. Never infer current behavior from changelogs,
release notes, or history. The mechanical currency checks live in
`autoassistant/audit_skill_apis.py` (`--scope all`, `--lint-idioms`, `--check-provenance`,
`--check-citations`, `--check-version`) and are documented in
[`skills/ag_audit_skill_apis.md`](./skills/ag_audit_skill_apis.md).

---

## Commit cadence during user work

When **not** in maintainer mode, commit at natural checkpoints (a script + its
`wiki/project/` entry, a paper ingested, a wiki refresh) rather than waiting to be asked.

- **Announce before committing** in one line; the user can interrupt.
- **Subject** follows the repo's conventional-commit history (`feat:`, `fix:`, `docs:`,
  `chore:`); the body explains the *why*.
- **One checkpoint = one commit.** **Stage explicitly by filename** — never `git add -A`.
- **Never push** (always an explicit user action). **Never skip hooks** (no `--no-verify`);
  fix the underlying issue and make a new commit.
- **Co-author trailer.** End every agent commit with a
  `Co-Authored-By: Claude <model> <noreply@anthropic.com>` trailer naming the current
  session's model (e.g. `Claude Opus 4.8 (1M context)`) — this marks the commit as
  agent-authored.
- If the user is on `main` (or any branch tracked as `origin/HEAD`), pause and confirm
  before committing rather than landing directly there.

---

## Conventions

- **Standard imports** for any Python you write:
  ```python
  import autofit as af
  import autogalaxy as ag
  import autogalaxy.plot as aplt
  ```
- **Mirror the skills' API — never reconstruct PyAutoGalaxy from memory.** The `skills/*.md`
  files contain the *current* API (they are kept in sync with the installed stack); the
  examples they show are the source of truth for how to call any PyAuto* symbol. Before
  writing model, fit, or plotting code, mirror the matching skill's calls rather than recalling
  the API from training data — older PyAutoGalaxy releases used a different API and are heavily
  represented in model priors. On the Claude Code harness a code gate blocks stale symbols, but
  a connector chat has no such gate, so this discipline is the only safeguard there: if you
  can't point at a `skills/` (or `dir()`) example for a call, treat it as unverified and say so
  rather than emitting it.
- **Generated script style.** Every `.py` you save uses the PyAutoGalaxy **workspace** style,
  not banner comments: an opening docstring (title underlined with `=`, short orientation,
  `__Contents__`), then each section introduced by a `"""__Section__"""` docstring carrying
  the physics/inference framing and `<Project>:<path>` citations. This is not optional. Full
  spec + a copyable worked example in [`skills/_style.md`](./skills/_style.md)
  "Generated script style" — mirror it rather than reconstructing the format from memory.
- **Working directories.** Committed scripts → `scripts/`; throwaway plots/data dumps →
  `scripts/scratch/` (gitignored); `search.fit(...)` output → `./output/`.
- **Plot path announcement.** The plot API is **functional-only**: pass
  `output_path="scripts/scratch/<context>/"` and `output_format="png"` straight to the `aplt.*`
  call (e.g. `aplt.subplot_imaging_dataset`, `aplt.subplot_fit_imaging`).
  **The object-oriented plotters (`aplt.FitImagingPlotter`, `ImagingPlotter`, `GalaxyPlotter`,
  `GalaxiesPlotter`, `InversionPlotter`, …) and the `aplt.MatPlot2D` / `aplt.Include2D` /
  `aplt.Output` objects have been removed — do not use them.
  They are the #1 stale-from-memory API error, especially on a harness with no code gate (a
  connector chat).** Wrong:
  `aplt.FitImagingPlotter(fit=fit, mat_plot_2d=aplt.MatPlot2D(...)).subplot_fit_imaging()`.
  Right:
  `aplt.subplot_fit_imaging(fit=fit, output_path="scripts/scratch/ngc1300/", output_format="png")`.
  **`output_filename` is not universal** — passing it to a call that does not take it raises
  `TypeError`. Only `plot_array`, `plot_grid`, `subplot_imaging_dataset`,
  `subplot_imaging_dataset_list`, `subplot_interferometer_dataset` and
  `subplot_interferometer_dirty_images` accept it;
  `subplot_galaxies` names its file with `auto_filename`; and the remaining fit and galaxy
  subplots write a **fixed stem** into `output_path` (`subplot_fit_imaging` → `fit.png`), so the
  *directory* is what separates one context from another. Check the signature —
  [`skills/ag_plot_fit.md`](./skills/ag_plot_fit.md) and
  [`wiki/core/api/plotting.md`](./wiki/core/api/plotting.md) carry the full split.
  If unsure a PyAuto* symbol exists, ground it against `skills/` or `dir(aplt)` — never write it
  from memory. Then `print(...)` the absolute path, and after running **quote that absolute path**
  and offer to open it (platform opener: `open` on macOS, `xdg-open` on Linux,
  `explorer.exe`/`wslview` from WSL) — don't just say "plot saved". One offer per plot.

---

## Reference & operations

Load operational references on demand, not every session:

- **Science projects.** `autogalaxy_assistant` is the copilot; a science project is a separate
  repo created and managed through [`start-new-project`](./skills/start-new-project.md).
- **Installation** (pip route + extras, editable clones, version floors, `activate.sh`,
  verifying an install) →
  [`wiki/core/operations/installation.md`](./wiki/core/operations/installation.md).
- **Sandbox / cache env vars / test mode** →
  [`wiki/core/operations/sandbox.md`](./wiki/core/operations/sandbox.md). The short version:
  prefix a run with `NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib` when the
  default cache locations are unwritable; `PYAUTO_TEST_MODE=1` cuts the sampler to its minimum
  iterations, `=2` bypasses it and calls the likelihood once, `=3` skips the likelihood too.
- **External resources** (HowToGalaxy, RTD, `autogalaxy_workspace`) + audience routing →
  [`wiki/core/external/index.md`](./wiki/core/external/index.md), with one page per resource
  and the per-skill citation map beside it. [`skills/_style.md`](./skills/_style.md) "Adaptive
  depth" carries the same routing as a writing rule.
- **The reference wiki itself** → [`wiki/core/index.md`](./wiki/core/index.md) lists every
  page that exists, by section.

- **Dataset layout + `info.json`** →
  [`wiki/core/operations/dataset.md`](./wiki/core/operations/dataset.md) — the
  `wavebands/<BAND>/` convention, the `info.json` schema, loading one waveband, and the
  bundled dataset's sky and PSF caveats. **One dataset ships with this repo**:
  `dataset/imaging/cosj100020+015344/`, a four-band real JWST/NIRCam cutout of an early-type
  galaxy at z = 0.3422 — its own `README.md` there is the authority for its provenance, and
  the real-data gate above applies to it in full.

The two HPC operational references are still unwritten (`PENDING.md` lists both with their
grounding scripts). Until they land, use the ground truth directly rather than citing a page
that does not exist:

- **HPC science** (cores, JAX/GPU, SLURM concepts) →
  `autogalaxy_workspace:scripts/guides/hpc/example_cpu_and_gpu.py` and
  `autogalaxy_workspace:scripts/guides/using_jax.py`. The `hpc/` infrastructure folder is not
  shipped in this clone yet; `scripts/AGENTS.md` documents the interface contract a pipeline
  must preserve for when it is.

<!-- repos_sync:history:begin -->
## Never rewrite history

Never rewrite pushed history on any repo with a remote — no `git init` over a
tracked repo, no force-push to `main`, no fresh-start "Initial commit", no
`filter-repo` / `filter-branch` / `rebase -i` on pushed branches. To get a
clean tree: `git fetch origin && git reset --hard origin/main && git clean -fd`.
<!-- repos_sync:history:end -->
