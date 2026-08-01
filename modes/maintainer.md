# Maintainer mode

Active when `.maintainer` exists at the repo root (gitignored; `touch .maintainer` /
`rm .maintainer`). The session is **assistant-maintenance** — editing the constitution,
skills, wiki schema, hooks, or infrastructure — not user galaxy science. `AGENTS.md`
"Session start" routes here when the sentinel is present.

## What changes

- Skip the `wiki/project/profile.md` read/create and the newcomer-mode defaults.
- Skip the session-start API drift-check by default (run it manually before testing any
  generated script).
- **No auto-commit.** The maintainer drives every commit; stage explicitly, announce, and
  never push.
- Don't offer to add `wiki/project/YYYY-MM-DD-*.md` entries.
- The **source-edit boundary** is lifted: you may edit `wiki/core/`, hooks, and assistant
  infrastructure (that is the point of maintenance work).

## What does NOT change

- Every safety invariant in `AGENTS.md` still applies — in particular the two hard-absolutes
  (the real-data inspection gate and never-rewrite-history), plus bulk-edit safety and the
  `output/` write-ban.
- Commits still end with the `Co-Authored-By: Claude <model> <noreply@anthropic.com>` trailer.

## Maintainer procedures

Use the existing skills, not new docs:

- Authoring or evolving a skill → [`skills/_bootstrap_skill.md`](../skills/_bootstrap_skill.md).
- Regenerating `wiki/core/` against pinned sources → `ag_update_wiki`.
- API gate / version baseline → `autoassistant/audit_skill_apis.py` directly (`--scope all`,
  `--lint-idioms`, `--check-citations`, `--check-version`, `--write-baseline`). The
  `ag_audit_skill_apis` skill that will document this is pending — see `../PENDING.md`.

## Release-time wiki-currency check (two triggers, one check)

The currency rules — symbol audit, idiom deny-list, provenance — live in **exactly one
place**: [`.github/workflows/wiki-currency.yml`](../.github/workflows/wiki-currency.yml) in
this repo, driving `autoassistant/audit_skill_apis.py`. The check versions with the content
it grades, so it must not be reimplemented anywhere else. Two triggers feed that one check:

- **Release (workflow_call).** PyAutoHands's `release.yml` — the same run that regenerates
  the autogalaxy_workspace / HowToGalaxy notebooks and the API baseline — invokes `wiki-currency.yml` via
  `uses:`, passing the new `stack_version` and `assistant_ref: main`. It installs that exact
  stack and runs all four checks. On drift the reusable workflow fails; PyAutoHands's
  dependent `if: failure()` job downloads the `wiki-drift-report` artifact and opens a "wiki
  drift" issue against this repo. **PyAutoHands only orchestrates and reports — it holds no
  copy of the rules.** (If releases ever move off PyAutoHands, the `repository_dispatch`/
  `workflow_call` trigger moves to whatever cuts the release; this workflow is unchanged.)
- **Assistant change (pull_request / schedule).** The same workflow runs on every PR and
  weekly against the *currently-released* stack, catching drift a wiki/skill edit introduces
  before it merges.

Ordering matters at release: PyAutoHands regenerates + commits the API baseline **before**
calling this workflow, so `--check-version` compares the new stack against an already-updated
baseline. When you change the rules, edit them here only; never copy a rule into PyAutoHands.

## Assistant-as-template: generic vs PyAutoGalaxy-specific

This repo was itself seeded from a sibling assistant, and a future PyAuto domain assistant may
in turn be seeded from it. When maintaining it, keep the boundary below in mind — it is the seam
a cloning workflow cuts along, and the four bold markers are read literally by that workflow, so
do not rename or reorder them. Do not generalise anything pre-emptively; just avoid entangling
the two sides.

Several items below do not exist yet. They are listed anyway, because the partition is a
statement about *where a file belongs when it lands*, and a newborn cloned from this repo must
inherit the classification rather than rediscover it. `../PENDING.md` says which are still
missing.

**Generic assistant infrastructure** (clones to any domain assistant near-verbatim):
`AGENTS.md`'s skeleton (session start, safety invariants, three-layer model, mode
selection, source-of-truth resolution, commit cadence), the root `AI_POLICY.md` usage
policy, the Teacher/Assistant mode model and `modes/` machinery (the `.maintainer`
sentinel), the skills framework (`_style.md`, `_bootstrap_skill.md`, the README index
conventions and its stub-tracking discipline), the `core`/`literature`/`project` wiki split
and its read-only/update rules, the science-project lifecycle (`start-new-project`,
`contribute-upstream`), `sources.yaml` + the source registry pattern, the API gate
(`autoassistant/audit_skill_apis.py` + the `wiki-currency` / `clone-boundary` workflows), the
profile template, the benchmark machinery (the `benchmarks/AGENTS.md` contract + the
`autoassistant/benchmark.py` harness), `PENDING.md` as a mechanism (an honest ledger every
newborn needs, though never its contents), and `.mcp.json` (it wires the results-inspector
MCP, which *is* `autoassistant.mcp` — generic tooling, so the wiring carries no domain
either).

**PyAutoGalaxy-specific content** (regenerated per domain, never copied blind): every
`ag_*` skill body, the `wiki/core/` reference pages, the whole `wiki/literature/` sub-wiki
(galaxy-structure science — Sersic and bulge-disk decomposition, isophotes and multipoles,
MGE, early-type structure, scaling relations, high-z morphology; arrives in a later phase),
bundled `dataset/` examples and their provenance READMEs, the root `README.md`'s science
framing and its example prompts, the standard-imports convention, `hpc/` templates tuned to
galaxy-fit runtimes and sample-scale batches, the benchmark prompt cards
(`benchmarks/prompts/` — a new domain writes its own easy/medium/hard assistant + teacher
cards against its own bundled data), the README figure assets in `docs/` (the hero imagery
plus the `make_readme_figures.py` script that renders it — a newborn regrows its own), and
any bundled science scripts in `scripts/` tied to a named galaxy (only `scripts/`'s own
AGENTS/CLAUDE docs are generic, and its workspace pipeline-reference table is domain).

This assistant deliberately has **no survey-specific mode** and no `paper/` directory. A
newborn grows whichever survey modes its own domain needs, if any, and writes its own paper if
one is ever warranted; neither is inherited from here.

**Mixed** (structure generic, values domain-specific): `llms.txt` read-order,
`config/` (the tree derives from `autogalaxy_workspace/config`, but the assistant convention
READMEs inside it are generic), `benchmarks/README.md` (protocol generic, benchmark table
domain), and the maintainer smoke tests below.

**Per-clone data** (never copied to a newborn — each clone accumulates its own):
`wiki/project/` journal entries and `profile.md`, `benchmarks/runs/` and the regenerated
`benchmarks/RESULTS.md`. A newborn starts with empty runs and regenerates `RESULTS.md` via
`python autoassistant/benchmark.py report`.

## Chat-surface compatibility smoke test

Run these checks after documentation changes are available on the public GitHub repository. Do
not claim a surface is tested merely because its documentation says repository access is
supported.

- **ChatGPT with GitHub access:** provide the repository URL and the bootstrap prompt from
  [`llms.txt`](../llms.txt); ask it to name the exact instruction, skill-index, and wiki files
  it read before answering one installation question and one modelling question.
- **ChatGPT without GitHub access:** attach `llms.txt`, `AGENTS.md`, and one selected skill;
  confirm it states the capability boundary and requests missing local evidence rather than
  pretending to inspect files.
- **Codex web:** connect the repository, ask it to summarize the active `AGENTS.md`
  constraints, then request a read-only plan for a small modelling task. Confirm it grounds the
  plan in the relevant skill and does not make an unrequested edit or pull request.
- **Non-agentic CLI/chat:** provide the same bootstrap and either browsing access or attached
  files; confirm it produces commands for the user to run instead of claiming execution.

Record the surface, date, plan/account context, files successfully loaded, and any limitations.
Plan availability changes, so test results should describe observed behavior rather than promise
that a feature is free for every user.
