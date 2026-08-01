---
name: ag_audit_skill_apis
description: Verify that every PyAuto* API symbol cited in skills/, wiki/core/api+stack/ and generated scripts/ still resolves in the installed stack, and report the ones that don't with suggested replacements. Also owns the four other mechanical currency checks in autoassistant/audit_skill_apis.py — the version baseline (wiki/core/api_audit_baseline.json, written with --write-baseline and checked cheaply at session start with --check-version), the idiom deny-list (--lint-idioms) that catches removed constructions whose symbols still import, page provenance (--check-provenance / --write-provenance) that binds a wiki page's prose to the commit it was validated against, and citation paths (--check-citations) that resolve every `Project:path` reference against a real checkout. Use when a user hits an API error, after a PyAutoGalaxy upgrade, when a wiki-currency CI run goes red, or on a maintenance cadence. Pairs with ag_update_wiki (prose drift from moved source pins) and ag_refresh_api_docs (the umbrella sweep). Not for feature work, and not for rewriting whole wiki sections.
---

# Auditing the skills and wiki against the installed stack

Every skill in this folder cites PyAutoGalaxy symbols — profile classes, analysis objects,
searches, plot functions — and the wiki cites many more, in API tables and in prose. All of
it drifts silently when a library renames, moves or removes something. Worse, the failure is
invisible until a user runs the code: a skill that reads perfectly can emit a call that
raised `AttributeError` three releases ago.

`autoassistant/audit_skill_apis.py` is the mechanical half of the answer: it imports the
libraries, walks every cited symbol attribute by attribute with `getattr`, and reports what
does not resolve. This skill is the curated half. The philosophy is **curate, don't
auto-rewrite** — the script answers *what is broken*, you and the user answer *what is
right*. A blind find-and-replace across the skill tree would lose the nuance that matters:
a removed helper sometimes maps onto a different class entirely, or onto a different
*paradigm*, and the script's suggestions are string-similarity heuristics that cannot know
that.

There are five independent checks, and it is worth knowing why five rather than one — each
sees a kind of drift the others are structurally blind to:

| Check | Catches | Blind to |
|---|---|---|
| `--scope <s>` | A cited symbol that no longer resolves | Live symbols in a dead construction; stale file paths |
| `--check-version` | The installed public API surface moving away from the pinned baseline | Which page it broke |
| `--lint-idioms` | A removed *construction* whose every token still imports | Renamed symbols |
| `--check-provenance` | A page whose body changed after it was validated, or a forged/unreachable pin | Whether the prose is *correct* |
| `--check-citations` | A `Project:path` citation pointing at a pre-refactor file layout | Symbols |

Before starting, settle three things with the user:

- **Scope** — skills only, wiki only (`api/` + `stack/`), `scripts/`, or all.
- **Fix now, or report only** for a later pass?
- **Is the project environment active?** Everything except the idiom, provenance and
  citation checks needs the libraries importable.

## Orient — the pipeline

### 1. Activate the environment and confirm what you are auditing

The `python` on `PATH` is usually not the one with the stack installed, so source the
project's activation script first (see
[`../wiki/core/operations/installation.md`](../wiki/core/operations/installation.md) for
what it resolves):

```bash
source activate.sh
python autoassistant/audit_skill_apis.py --check-install
```

That prints the interpreter, the environment prefix, every resolved version, the file
`autogalaxy` was imported from, and whether the install is a wheel or an editable source
checkout. Exit `0` = ready. Exit `2` = the packages are absent from *this* interpreter.
Exit `3` = they were found but an import raised.

**Do not audit against a half-installed stack.** Every symbol under a root that failed to
import comes back `import_failed`, which is a flood of false positives, not a report. Repair
the environment first — [`ag_setup_environment`](./ag_setup_environment.md) owns that
procedure, working from the `--check-install` output and the cache/environment variables in
[`../wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md). Only a *later*
`--check-version` exit 1 is genuine API drift.

### 2. Run the symbol audit

```bash
python autoassistant/audit_skill_apis.py --scope all
```

`--scope` takes four values:

- **`skills`** — every `skills/*.md`.
- **`wiki`** — `wiki/core/api/*.md` and `wiki/core/stack/*.md`. Deliberately not the whole
  wiki: `concepts/`, `operations/` and `external/` are prose about physics, environments and
  routing rather than API catalogues.
- **`scripts`** — every `.py` under `scripts/` (recursively, since it mirrors the workspace's
  nested layout) plus `autoassistant/mcp/*.py`. **This is the scope that matters most**: it is
  where a stale symbol actually executes rather than merely reading wrong. The repo's own
  tooling files are excluded, because they contain alias-shaped text (regexes, module-name
  strings) that is not real API usage.
- **`all`** (default) — the union.

In Markdown the extractor splits code fences from prose and scans inline `` `code` `` spans
inside prose too, so a symbol named in a sentence is checked exactly like one in a recipe. A
`.py` file is treated as code throughout.

The report lands at `autoassistant/audit/skill_api_audit_<YYYY-MM-DD>.md` and is
**gitignored** — only the script is committed, because a report is a snapshot of one
environment. `--out` overrides the path, `--root` audits a different checkout. Exit is
non-zero when the report contains misses, so `... --scope all && echo clean || echo drift`
works in a loop. `make audit` is the no-argument shorthand.

A file that *documents* the API surface (intentional fixtures, meta-docs) can opt out
entirely by carrying the skip marker defined as `IDIOM_SKIP_MARKER` in the script — the same
escape hatch the code gate honours. **Use it as close to never as possible, and never in a
skill.** An opted-out file is dropped from the symbol scan, the idiom lint *and* the citation
check at once, so a skill carrying it stops being graded on the API it teaches — which is
precisely the state this audit exists to prevent. Note the second-order trap: the marker is
matched as a plain substring anywhere in the file, so even *quoting* it in prose silently
opts the page out. Refer to it by its constant name, as this paragraph does.

### 3. The version baseline and the session-start drift check

This repo is pinned to a PyAutoGalaxy API surface by
`wiki/core/api_audit_baseline.json`: per-module `__version__` plus a SHA-256 of each
module's sorted public `dir()` names, for the four library roots and the plot module
imported as `aplt`.

```bash
# Cheap drift check — no Markdown scan. Safe at session start (see ../AGENTS.md).
python autoassistant/audit_skill_apis.py --check-version

# Re-pin, only after a deliberate and audited upgrade.
python autoassistant/audit_skill_apis.py --write-baseline
```

`--check-version` **gates on the API-surface hash alone**. A differing `__version__` stamp
is printed for context but does not fail the check: a release no longer commits its version
stamp back to the library's `main`, so a source checkout reports a frozen stamp against a
wheel-derived baseline — a permanent false positive that the identical surface hash already
proves spurious. It runs `--check-install` first and returns that exit code (2 or 3) if the
stack is not ready, so a red result is never ambiguous between "drift" and "broken env".

The workflow is: `--check-version` goes red → run `--scope all` to find *what* broke → fix
the references → `--write-baseline` to re-pin. **Only re-pin after fixing.** Re-pinning to
silence a red check on a stack you have not audited is precisely the drift this file exists
to prevent, and `--write-baseline` refuses to write at all if any library is missing, so it
cannot bake `import_failed` placeholders into the baseline.

The wiki documents only the **current** API. Fix stale references in place; do not add
`old → new` migration tables. They grow without bound and are themselves a drift surface,
because every row names a symbol that no longer exists.

### 4. The idiom deny-list — drift the symbol resolver cannot see

The resolver only checks alias-rooted dotted symbols such as `ag.AnalysisImaging`. It is
structurally blind to a **retired construction**, where every named token still imports but
the operation between them was removed. The seeded case is the old multi-dataset combine,
which joined analyses with an arithmetic operator (and folded lists of them with a builtin)
to sum their log-likelihoods. Every token resolves, so `--scope all` and the code gate both
report clean — yet the operator overload is gone, and datasets are now combined through the
factor graph: wrap each dataset's analysis in `af.AnalysisFactor`, combine the list with
`af.FactorGraphModel`, and fit
`search.fit(model=factor_graph.global_prior_model, analysis=factor_graph)` (see
[`../wiki/core/concepts/multi_wavelength.md`](../wiki/core/concepts/multi_wavelength.md)).

```bash
python autoassistant/audit_skill_apis.py --lint-idioms   # 0 clean, 1 on any hit
```

Each deny-list entry is `{name, regex, why_defunct, replacement, citation}`, and a hit
prints all four so the fix is unambiguous. The lint scans `skills/*.md`, **the whole of
`wiki/`** (not just the API pages — a dead idiom in a concepts page is just as wrong) and
every `scripts/` `.py`. It is self-contained: no installed stack, no `sources.yaml`, which is
why it also runs inside the code gate on snippets about to execute.

**Add an entry whenever the fix is "rewrite the construction", not "rename the symbol".**
That is the boundary between this check and the resolver.

### 5. Provenance — bind a page's prose to the commit it was validated against

The baseline hashes the API *surface*; the idiom lint catches dead *constructions*. Neither
verifies that a `wiki/core/` page's `pinned_commit` is honest — and pins bumped without
re-validating the prose is the original way this repo's ancestors shipped drift. Two
independent signals close it:

```bash
python autoassistant/audit_skill_apis.py --check-provenance          # 0 ok, 1 on error
python autoassistant/audit_skill_apis.py --check-provenance --strict # warnings fail too
```

- **Commit reachability (git mode).** When a git checkout of a cited project resolves, each
  SHA-shaped `pinned_commit` must be a real commit object *and* an ancestor of (or equal to)
  `HEAD`. A forged SHA, or one rewritten out of history, is an **ERROR**. A pin to a moving
  ref (`main`) is a **warning** — "unpinned" is a nudge to re-pin, not a forgery. A named
  tag is accepted if it resolves.
- **Content binding (git-free).** `content_sha256` in the frontmatter is a SHA-256 of the
  page body, stamped at validation time. A page that declares it and no longer matches was
  edited after stamping without re-validation: **ERROR**. A page with no stamp is a
  **warning**. This arm needs no checkout, so it is the one that runs in a packaged-install
  CI job where the git-mode checks are skipped.

Stamp a page **only after validating its content against its pinned commit** — this is the
honest re-pin, and the partner of step 4 in [`ag_update_wiki.md`](./ag_update_wiki.md):

```bash
python autoassistant/audit_skill_apis.py --write-provenance --page wiki/core/api/<page>.md
```

`--page` is repeatable and is the honest default: stamp only what you re-validated. With no
`--page`, **every deliberately-pinned page is re-stamped**, which is a legitimate move only
after a validated full sweep. Pages with no SHA-shaped pin are always skipped — they make no
validation claim, so there is nothing to bind.

Note the asymmetry that makes this check useful: the stamp is written by a command you have
to choose to run, and verified by one that runs in CI.

### 6. Citation paths — the file-layout axis

A page can cite only live symbols while its `` `Project:relative/path` `` source citations
point at a pre-refactor layout: a module that became a package, a deleted file, a renamed
README. Symbols and paths are independent failure axes, and a tree can be clean on one and
badly stale on the other.

```bash
python autoassistant/audit_skill_apis.py --check-citations   # 0 ok, 1 on missing path
```

It scans `skills/*.md`, all of `wiki/core/`, the `benchmarks/` protocol docs and prompt
cards, plus `AGENTS.md` and `llms.txt`, and resolves both forms of claim: inline
`` `<project>:<path>` `` citations (project names from
[`../sources.yaml`](../sources.yaml)) and each wiki page's frontmatter `sources[].paths[]`.
A path containing `...` is a deliberate abbreviation — only its concrete prefix must exist.

Resolution order per project: a full checkout first (the installed package's enclosing git
repo → `sources/<project>/` → a sibling clone), which can check every repo-relative path;
otherwise the site-packages directory of the installed package, which can only check
package-internal paths and **skips** repo-level ones (`README.md`, `docs/`) rather than
false-flagging them. Missing paths are errors; a project with no resolvable tree at all
downgrades to a warning. Citations to this repo itself resolve against the repo root.

**Ground truth here is the ref the docs pin, not the released wheel.** The wiki tracks
`main`, so a post-release file move would false-fail against a pip install. The
`wiki-currency` CI workflow therefore shallow-clones the cited repos into `sources/` before
running this as its fifth leg, while the release install stays ground truth for the symbol,
version and idiom checks — the things a user actually runs.

### 7. The code gate — running it by hand, and bypassing it

The always-on gate (see [`../AGENTS.md`](../AGENTS.md) "Safety invariants") is the
`PreToolUse` hook `.claude/hooks/validate_pyauto_code.py`, which blocks any Bash command
running Python that references a PyAuto\* symbol absent from the installed stack. It exists
because a stale symbol recalled from training data is the single most likely error in
generated PyAutoGalaxy code. The hook only fires on harnesses that support hooks; **on any
other harness, run the same validator by hand** before executing generated code:

```bash
python autoassistant/audit_skill_apis.py --code "import autogalaxy as ag; ag.lp.Sersic"
python autoassistant/audit_skill_apis.py --file scripts/my_script.py
```

Exit `0` = every symbol and idiom resolves. Exit `2` = at least one stale symbol or idiom —
the deny case; each is printed as a `STALE` / `STALE-IDIOM` line with the deepest object
that did resolve and the closest live names as *unverified hints*. Exit `3` = the stack
itself failed to import, reported once as an environment problem rather than as drift (the
hook fails open on it, since the command would raise the same import error anyway). Both
modes are self-contained — no `sources.yaml`, no baseline, just the installed library.

When the gate blocks you, **do not guess a replacement.** Grep `skills/` for the task, or
introspect `dir()` of the live module, then re-run. For deliberate pre-refactor work where
you *mean* to name a symbol the install does not have, bypass with `PYAUTO_SKIP_API_GATE=1`,
exported or prefixed on the single command.

### 8. What CI runs

The `wiki-currency` workflow runs five legs in order — `--check-version`, `--scope all`,
`--lint-idioms`, `--check-provenance`, `--check-citations` — against the *released* stack,
and fails on any non-zero. It is also invoked at stack-release time with the new version, so
a release that moves the API is graded against this wiki immediately. If it goes red, the leg
name in the job summary tells you which section above to start from.

One red result is **not** a defect in the docs, and it is worth recognising before you start
deleting rows: the wiki pins library `main`, while the symbol leg grades against the released
wheel. A symbol that has landed on `main` but is not yet released therefore resolves locally
(against a source checkout) and fails in CI. The page is correct for its pin; the fix is a
release, not an edit. Confirm the direction before acting — a symbol missing because it was
*removed* looks identical in the report to one missing because it is *new*.

## Ask — narrow the work before fixing

A first audit of a drifted tree can surface a dozen or more misses. Don't try to land them
in one push; ask how the user wants it sliced:

- *"Fix the page that triggered this first, then sweep the rest?"*
- *"Group by library — all the PyAutoArray drift in one pass, all the PyAutoFit drift in
  another?"*
- *"One file per commit, or one batch?"*

Re-run the audit after each fix and watch the count shrink. That is the only proof an edit
landed where you thought it did.

## Branch — fixing one row

### Read the row in context

The report gives the symbol, the deepest object that resolved, the suggested replacements,
and whether it was seen in `code` or `prose`. Open the file and find the occurrence — there
may be several, and the surrounding sentences decide which replacement is right.

### Confirm the replacement against source, never against the suggestion

Suggestions come from string similarity plus a cross-module search. They are hints:

```bash
python -c "import autogalaxy as ag; help(ag.Galaxy)" | head -40
python -c "import autogalaxy as ag; print([n for n in dir(ag) if 'Sersic' in n])"
```

If nothing plausible turns up, search the installed libraries for what actually carries the
behaviour you need, then cite the defining file in `<Project>:<path>` form (look it up with
`inspect.getfile`) per [`_style.md`](./_style.md) "Source citations". Reading the source is
the point: this repo's whole discipline is that installed source and `dir()` outrank memory,
changelogs and release notes.

### Edit deliberately

A cosmetic rename is one edit. An API *shape* change — different argument order, one class
split into two, an object-oriented surface replaced by functions — means the surrounding
recipe needs rewriting too, so read the new signature before you touch the prose. For a
`wiki/core/api/` page, a single-symbol rename can be patched in place; a whole-section
rewrite belongs to [`ag_update_wiki.md`](./ag_update_wiki.md).

If you touched a `wiki/core/` page, finish the job: re-validate against its pinned commit,
then `--write-provenance --page <that page>`. An unstamped edit fails
`--check-provenance` in CI, which is the mechanism working, not a nuisance.

### Re-run and expect the row to be gone

```bash
python autoassistant/audit_skill_apis.py --scope all
```

Still there → the edit did not land where you thought. New rows → the fix introduced fresh
drift, which is common when the replacement has a different shape than the original.

## Combine — where to hand off

- **A whole wiki section needs rewriting** → [`ag_update_wiki.md`](./ag_update_wiki.md),
  which diffs pinned source commits and rewrites prose against them.
- **The full maintenance sweep across skills, wiki and pins** →
  [`ag_refresh_api_docs.md`](./ag_refresh_api_docs.md).
- **The new API needs a workflow no existing skill covers** →
  [`_bootstrap_skill.md`](./_bootstrap_skill.md).

After the audit reaches zero misses, smoke-test any script whose recipe you materially
rewrote — a clean symbol audit proves the names exist, not that the code runs:

```bash
PYAUTO_TEST_MODE=2 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/<the_script>.py
```

Zero misses plus a passing smoke run is the signal the audit is complete. The flags are
explained in [`../wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md).

## When NOT to invoke this skill

- **During an unrelated user task.** The audit's value is its reviewable diff; folded into a
  feature commit it loses that entirely.
- **When the libraries are not importable.** The report is all `import_failed` rows and tells
  you nothing about the docs.
- **When the user wants prose improved** — rewording, restructuring, a clearer explanation.
  That is a wiki refresh, not a symbol audit.

## Agent procedural checklist

1. Confirm scope, and whether to fix now or report only.
2. `source activate.sh`; `--check-install` → expect exit 0.
3. `--check-version` — if it is red, that is probably why you are here.
4. `--scope <scope>`; read `autoassistant/audit/skill_api_audit_<date>.md`.
5. `--lint-idioms`, `--check-provenance`, `--check-citations` — the three axes the symbol
   scan cannot see.
6. Per miss: read the file, confirm the replacement against installed source, edit, re-run.
7. Re-stamp any edited `wiki/core/` page with `--write-provenance --page <page>`.
8. Hand whole-section rewrites to `ag_update_wiki`.
9. Once clean against a deliberately upgraded stack, `--write-baseline` and commit the
   updated `wiki/core/api_audit_baseline.json`.
10. Smoke-test materially changed recipes; commit on the user's chosen cadence.
