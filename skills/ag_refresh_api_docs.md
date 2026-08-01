---
name: ag_refresh_api_docs
description: The umbrella maintenance sweep that brings the whole documentation layer — skill recipes, wiki/core/ pages, source pins and generated scripts — back into line with the currently installed PyAutoGalaxy stack. Use it when the user says "make the docs current again" after a stack upgrade, after pulling fresh source repos, or on a deliberate maintenance cadence; it orchestrates ag_audit_skill_apis (symbol / idiom / provenance / citation drift) and ag_update_wiki (prose drift from moved source pins) in a reviewable order, with autoassistant/refresh_api_docs.py as the preflight. Hand off to the narrower skill instead when the user wants only one symbol checked or only one known-stale wiki page rewritten. Never run it inside unrelated feature work.
---

# Refreshing the whole documentation layer

Documentation drift shows up in four places in this repo, and a refresh that checks only one
of them leaves the others quietly wrong:

1. **`skills/*.md`** — symbol references and code recipes. No pinned commits at all, so
   nothing detects their staleness except an audit.
2. **`wiki/core/`** — curated prose, each page pinned to the source commits it was written
   from.
3. **The source repos themselves**, which move past those pins.
4. **`scripts/`** — the generated pipelines, where a stale symbol does not merely read wrong
   but actually raises.

This skill strings the checks together so the user can ask once. It is deliberately broader
than [`ag_audit_skill_apis.md`](./ag_audit_skill_apis.md) (the mechanical "does this symbol
still resolve?" pass, plus the four other currency checks) and
[`ag_update_wiki.md`](./ag_update_wiki.md) (the curated "did the source move enough to
rewrite this page?" pass), and replaces neither.

Background on how the three layers relate:
[`../wiki/core/stack/overview.md`](../wiki/core/stack/overview.md) for what each library
owns, and [`../wiki/core/operations/installation.md`](../wiki/core/operations/installation.md)
for what "the installed stack" means in practice.

## Ask

Three boundaries, settled before any work:

- **Scope** — skills only, wiki only, `scripts/` only, or every surface.
- **Reference point** — audit against the **installed environment** only, or also against
  local source checkouts (which is what a pin diff needs)?
- **Cadence** — a report the user reads later, or fixes applied and committed in this
  session?

If they want one narrow slice, hand off directly to the narrower skill. This skill earns its
keep only on the full sweep.

## Orient — preflight

Start from an environment where the stack imports cleanly:

```bash
source activate.sh
python autoassistant/refresh_api_docs.py --scope all
```

That helper does exactly three things, and knowing its limits saves confusion:

1. Imports the four-module chain — `autonerves`, `autoarray`, `autofit`, `autogalaxy` — in
   dependency order, which is the order a broken install fails in. If any import raises it
   prints the exception and exits `2` without auditing anything.
2. Prints the resolved version of each of the four.
3. Runs `autoassistant/audit_skill_apis.py --scope <scope>` from the repo root and returns
   its exit code, telling you whether to read the report.

It does **not** run the version, idiom, provenance or citation checks, and it rewrites
nothing. It is a repeatable starting point, not the job. If the preflight fails, stop and fix
the environment first — a refresh against a broken env produces noise, not signal
(`--check-install` in [`ag_audit_skill_apis.md`](./ag_audit_skill_apis.md) is the structured
diagnosis, and the environment skill that will own repair is still pending; see
[`../PENDING.md`](../PENDING.md)).

Then take the baseline reading, because it tells you whether the *stack* moved or only the
*docs*:

```bash
python autoassistant/audit_skill_apis.py --check-version
```

Green means the installed public API surface still matches
`wiki/core/api_audit_baseline.json`, so anything you find is docs-side drift. Red means the
stack moved, and the sweep below is how you find out what it broke.

## Branch — pass 1: symbol drift

```bash
python autoassistant/audit_skill_apis.py --scope all
```

Read `autoassistant/audit/skill_api_audit_<YYYY-MM-DD>.md`. Per miss: open the cited file,
confirm the replacement against installed source (never against the report's fuzzy
suggestion), patch deliberately. Don't bulk-rewrite every occurrence of a name to the same
string — the same old symbol can map to two different new ones in two different contexts.

If every miss is inside `skills/*.md`, you may be able to finish without touching the wiki
at all. If any miss lands in `wiki/core/api/` or `wiki/core/stack/`, keep the report open for
pass 2. The detailed fix loop is in
[`ag_audit_skill_apis.md`](./ag_audit_skill_apis.md) "Branch".

## Branch — pass 2: the three axes the symbol scan cannot see

Run all three before touching the wiki, because each finds a different class of stale page
and you want the full picture before you start rewriting:

```bash
python autoassistant/audit_skill_apis.py --lint-idioms
python autoassistant/audit_skill_apis.py --check-provenance
python autoassistant/audit_skill_apis.py --check-citations
```

- **Idioms** — a retired construction whose every token still imports. Fix by rewriting the
  construction, in every page and script that shows it.
- **Provenance** — errors mean a page's body changed after stamping, or a pin is forged or
  unreachable. Both are content problems: re-validate the page against its pin, then
  re-stamp. Warnings (a `main` pin, an unstamped page) are a to-do list, not a failure.
- **Citations** — a `Project:path` pointing at a layout that no longer exists. Fix the path
  from the source tree, not from what the sentence around it implies.

## Branch — pass 3: refresh the wiki pages whose pins moved

Now that you know which pages are implicated, run the pin-diff loop from
[`ag_update_wiki.md`](./ag_update_wiki.md) over them (or over everything in scope, if the
user asked for a sweep):

```bash
git -C sources/<project> log --oneline <pinned_commit>..HEAD -- <path>
git -C sources/<project> diff <pinned_commit>..HEAD -- <path>
```

Rewrite only the sections whose source actually changed; leave a cosmetic diff alone and say
so. Then, per page: bump `pinned_commit`, bump `last_updated`, and
`--write-provenance --page <page>` **last**. Note any newly exported API that needs a row or
a page, and list it rather than inventing coverage.

This skill is about accuracy, not churn. A refresh whose diff is mostly reworded paragraphs
has failed at its job.

## Branch — pass 4: skill recipes and generated scripts

The wiki refresh does not fix procedure drift inside `skills/*.md`, and nothing at all fixes
`scripts/`. Sweep them once the changed surface is known:

- Update code snippets whose constructor names or arguments moved.
- Update `<Project>:<path>` citations for files that moved.
- Update cross-links if a wiki page was renamed or split, and check that a section anchor
  you point at still exists.
- Re-check each skill's `## Further reading` block against
  [`../wiki/core/external/skill_citation_map.md`](../wiki/core/external/skill_citation_map.md)
  — those URLs are external and rot independently of the API.

Then re-run the audit until the count reaches zero:

```bash
NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python autoassistant/refresh_api_docs.py --scope all
```

For any skill whose recipe changed materially, smoke-test the script that skill actually
produces — that is a separate run, and the one that needs test mode:

```bash
PYAUTO_TEST_MODE=2 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/<the_script>.py
```

A clean symbol audit proves the names exist; only running the thing proves the recipe works.
The environment variables are explained in
[`../wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md).

## Combine — what "complete" looks like

Six conditions, all of them:

- the stack imports in the target environment (`--check-install` exit 0);
- `--scope all` reports zero misses;
- `--lint-idioms` is clean;
- `--check-provenance` has zero errors, and every page you rewrote is re-stamped;
- `--check-citations` reports zero missing paths;
- every wiki page you touched has either a bumped pin *or* an explicit recorded decision that
  its source diff was cosmetic.

The five checks are exactly the five legs the `wiki-currency` workflow runs, so a locally
clean sweep predicts a green CI run — with one caveat: CI grades symbols against the
*released* wheel while the wiki pins library `main`, so a page documenting a symbol that has
landed on `main` but is not yet released will pass locally and fail there. If that is the
cause, the fix is a release, not an edit; say so rather than deleting the row.

Then show the diff grouped by surface — skills, wiki pages, scripts, tooling — and commit on
the user's cadence. If the sweep followed a deliberate stack upgrade and everything is now
clean, re-pin the baseline as the final step:

```bash
python autoassistant/audit_skill_apis.py --write-baseline
```

Commit `wiki/core/api_audit_baseline.json` with the sweep. Re-pinning *before* the sweep is
clean would silence the very signal that told you to run it.

Finally, reconcile the ledgers: delete anything from [`../PENDING.md`](../PENDING.md) the
sweep actually delivered, and update `wiki/core/index.md` and
[`README.md`](./README.md) if the page or skill set changed.

## When NOT to invoke this skill

- **During unrelated feature work.** Maintenance diffs have to stay separately reviewable.
- **When one known symbol is broken** → [`ag_audit_skill_apis.md`](./ag_audit_skill_apis.md).
- **When one known wiki page's pin moved** → [`ag_update_wiki.md`](./ag_update_wiki.md).
- **When the environment cannot import the stack.** Fix that first; there is nothing to
  refresh against.
- **When the user wants a capability the docs never had.** That is a new skill —
  [`_bootstrap_skill.md`](./_bootstrap_skill.md).

## Agent procedural checklist

1. Confirm scope, reference point, and report-only vs. fix-and-commit.
2. `source activate.sh`; `python autoassistant/refresh_api_docs.py --scope <scope>` —
   preflight plus the symbol audit.
3. `--check-version` to learn whether the stack or only the docs moved.
4. Fix symbol drift from the report first.
5. Run `--lint-idioms`, `--check-provenance`, `--check-citations`; fix each axis.
6. Pin-diff the implicated wiki pages; rewrite only changed sections; bump pin +
   `last_updated`; `--write-provenance --page <page>`.
7. Sweep `skills/*.md` recipes, citations, cross-links and `## Further reading` blocks.
8. Re-run until all five checks are clean; smoke-test materially changed recipes.
9. `--write-baseline` only if this followed a deliberate upgrade and the sweep is clean.
10. Reconcile `PENDING.md`, `wiki/core/index.md` and `skills/README.md`; show the grouped
    diff; commit.
