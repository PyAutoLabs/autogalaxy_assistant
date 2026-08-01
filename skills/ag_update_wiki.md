---
name: ag_update_wiki
description: Refresh wiki/core/ pages whose pinned source commits have moved, by re-reading the relevant files from the PyAuto* repos (and the workspace / HowToGalaxy catalogues) and rewriting only the sections that actually drifted, then bumping pinned_commit + last_updated and re-stamping content_sha256. Also surfaces newly exported public APIs so the user can decide whether they warrant a new page or a new row. This is the one workflow permitted to write inside the otherwise read-only wiki/core/. Use after pulling fresh source, when a user reports that a page describes something the library no longer does, or on a deliberate refresh cadence. Do NOT run it opportunistically inside unrelated work — the diff has to stay reviewable. For a symbol that simply no longer resolves, use ag_audit_skill_apis instead.
---

# Refreshing `wiki/core/` from the source repos

The wiki is the content layer of this workspace: the skills are *how to do X*, and
`wiki/core/` is *what X is* — what a Sersic index measures, which searches exist, how a
pixelised reconstruction is regularised, what the config tree overrides. Every page
records the source files it was written from and the commit it was written against, which
is what makes staleness detectable at all rather than a thing someone notices years later.

This skill is that detection loop plus the rewrite: for each page in scope, diff its
pinned sources against current `HEAD`, rewrite the sections whose source genuinely moved,
re-pin, and re-stamp.

It is a **curated task, not a converter.** Wiki prose is hand-written and judged against
the diff; auto-generated docstring dumps belong in each library's own `docs/` folder, which
is where PyAutoGalaxy already puts them (see
[`../wiki/core/external/rtd.md`](../wiki/core/external/rtd.md)). The reason matters: this
wiki exists to say *which thing to use and why*, and no generator can write that.

`wiki/core/` is read-only under [`../AGENTS.md`](../AGENTS.md)'s safety invariants, and
**this skill is the named exception**. Session notes and per-clone findings go to
`wiki/project/` instead — if what you want to record is "what I found today", you are in
the wrong place.

Before starting, confirm with the user:

- **Which sources** — all four libraries, or the one whose API moved?
- **Which pages** — a targeted set, or a sweep?
- **`main` or a tag** as the refresh target?
- **Commit cadence** — one page per commit, or one batch at the end?

A targeted refresh ("PyAutoFit only, they moved the samples API") beats a sweep every time.
Sweeps are for seeding a section; narrow is for maintenance.

## Orient — what a page commits to

Every page under `wiki/core/` opens with frontmatter of this shape (the schema is owned by
[`../wiki/core/README.md`](../wiki/core/README.md)):

```yaml
---
title: Non-linear searches
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/search/nest/nautilus/
      - autofit/non_linear/search/mle/bfgs/
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/modeling/searches.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: <sha256 of everything after the closing --->
---
```

Four fields carry weight:

- **`sources[].paths`** — every file or directory the page's content derives from. If none
  of them changed, the page cannot be stale. If one did, the page *may* be. Listing a path
  the page does not actually depend on creates false refresh work; omitting one it does
  depend on is how drift ships.
- **`pinned_commit`** — a **real 40-character SHA**, never a moving ref. The claim is "this
  prose was validated against *this* revision". `main` is not a claim, and
  `--check-provenance` flags it as unpinned.
- **`last_updated`** — the date of the last validation, not of the last typo fix.
- **`content_sha256`** — binds the prose to that claim. Stamped, never hand-written.

Which project a page pins is not always a library. Pages that map this repo's own content —
`index.md`, the `external/` routing pages, anything documenting `config/` — pin
`autogalaxy_assistant` at this repo's own commit, because that is the revision whose tree
they describe. Pages about the workspace or the lecture series pin
`autogalaxy_workspace` / `HowToGalaxy`. All of them resolve through
[`../sources.yaml`](../sources.yaml).

## Ask — scope the refresh

Ask once, before doing work:

- *"Refresh against `main` of all four libraries, or just the one whose API moved?"*
- *"Bump pins only for pages whose sources really changed, or for every page I open —
  including the ones whose diff turns out to be cosmetic?"*

The second question matters more than it looks. Bumping a pin on a page you did not
re-read makes a validation claim you did not earn, and `--check-provenance` cannot tell the
difference — only you can. The honest answer is almost always "only pages whose content I
actually re-validated".

## Branch — the per-page loop

### 1. Resolve the source repos

Read the page's `sources`. For each project, find a tree, in this order (the same order
`--check-citations` uses):

```bash
# Installed and importable? Read from where it actually loaded.
python -c "import autogalaxy, pathlib; print(pathlib.Path(autogalaxy.__file__).parent)"
```

Otherwise a `sources/<project>/` clone, otherwise a sibling clone, otherwise clone the URL
from `sources.yaml` into the gitignored `sources/<project>/`. Never read a fifth place, and
never substitute a rendered docs page for the source it was generated from.

### 2. Diff each pinned path

```bash
git -C sources/<project> log --oneline <pinned_commit>..HEAD -- <path>
git -C sources/<project> diff <pinned_commit>..HEAD -- <path>
```

Three outcomes:

- **Both empty** — unchanged. Leave the page alone entirely, including its pin.
- **Log non-empty, diff cosmetic** (import shuffles, formatting, comment edits) — treat as
  unchanged. Say so to the user rather than churning the page.
- **Diff has semantic content** — the page is stale in the sections that depend on it.

Read the full diff of every listed path before deciding. A partial read is how a refresh
concludes "no change" on a page whose second source file was rewritten.

### 3. Rewrite only the affected sections

Open the source at current `HEAD` and identify which sections of the page depend on it —
usually obvious from the headings. Rewrite those. **Do not rewrite unaffected prose just
because you have the file open**; a small diff is reviewable and a large one is not.

While rewriting:

- Cite code as `<Project>:<path>`, per [`_style.md`](./_style.md) "Source citations".
- Update class / function / parameter tables to match what is actually exported now.
- Add rows for genuinely new public items; delete rows for removed ones rather than
  annotating them as removed. The wiki documents the current API only.
- Keep the page's framing: an `api/` page answers *which one and when*, a `concepts/` page
  answers *what and why*. A diff that turns one into the other is a rewrite, not a refresh.

### 4. Re-pin, then stamp

```bash
git -C sources/PyAutoFit rev-parse HEAD
```

Set `pinned_commit` to that SHA and `last_updated` to today. Then stamp the page — this is
what records that the prose you just wrote was validated against that commit, and it is
what CI verifies (see
[`ag_audit_skill_apis.md`](./ag_audit_skill_apis.md) "Provenance"):

```bash
python autoassistant/audit_skill_apis.py --write-provenance --page wiki/core/<section>/<page>.md
```

Always pass `--page`. Without it every deliberately-pinned page in the repo is re-stamped,
which silently claims you validated all of them. Stamp **last**, after the body is final —
any later edit invalidates the hash, which is the mechanism working.

Then prove it:

```bash
python autoassistant/audit_skill_apis.py --check-provenance
python autoassistant/audit_skill_apis.py --check-citations
```

The second matters because a rewrite is exactly when a citation path gets fat-fingered or
left pointing at a file the diff you just read had moved.

### 5. Surface new public APIs — and stop there

Compare each source package's top-level exports between the old pin and `HEAD`:

```bash
git -C sources/PyAutoGalaxy diff <pinned_commit>..HEAD -- autogalaxy/__init__.py
```

For each newly exported class or function: if it belongs on an existing page, add it there
as part of this refresh. If it needs a page of its own, **list it to the user and stop**:

> "PyAutoGalaxy now exports two profiles that no page covers. The first fits the light
> profile catalogue as a row; the second probably wants its own concepts page. Draft
> either?"

Do not write new pages unilaterally. A page nobody asked for and no skill cites is exactly
what [`_style.md`](./_style.md) warns against — the wiki exists to back the skills.

## Combine — after the refresh

1. `git diff wiki/` and walk the user through it, page by page.
2. Run the full currency set — `--check-version`, `--scope all`, `--lint-idioms`,
   `--check-provenance`, `--check-citations` — because a refresh pulls in upstream text and
   is a normal way for a symbol or a dead construction to get *introduced*. This is the same
   five-leg set the `wiki-currency` workflow runs, so running it locally is running CI early.
3. Update [`../PENDING.md`](../PENDING.md) if the refresh delivered something it lists, and
   `wiki/core/index.md` if a page was added, renamed or removed. An index entry pointing at
   a page that is not there is worse than an admitted gap.
4. Commit on the chosen cadence — one page per commit, or
   `git commit -m "wiki: refresh against <project>@<short-sha>"` for a batch.

If any page you touched is cited by a skill, re-read that skill's cross-links. A refresh
that renames a section heading breaks every anchor pointing at it.

## When NOT to invoke this skill

- **Inside an unrelated user task.** Never sneak a wiki refresh into a feature change.
- **When you have read only part of a diff.** Read every listed path in full first.
- **When the source was refactored into a shape you do not yet understand.** Ask the user
  rather than writing confidently vague prose — vague prose in a reference wiki is worse
  than an out-of-date paragraph, because it reads as current.
- **When the only problem is one symbol that no longer resolves** → that is
  [`ag_audit_skill_apis.md`](./ag_audit_skill_apis.md).
- **When the user wants the whole maintenance sweep** →
  [`ag_refresh_api_docs.md`](./ag_refresh_api_docs.md).

## Agent procedural checklist

1. Confirm scope: which projects, which pages, `main` or a tag, commit cadence.
2. For each page in scope:
   a. Read its frontmatter `sources` and `pinned_commit`.
   b. Resolve each project's tree (installed → `sources/` → sibling → clone).
   c. `git log` + `git diff <pin>..HEAD` for **every** listed path.
   d. Semantic diff only: read the source at `HEAD`, rewrite the affected sections.
   e. Bump `pinned_commit` and `last_updated`; then
      `--write-provenance --page <page>`.
3. Diff `__init__.py` exports across the pin range; fold new APIs into existing pages, and
   list anything needing a new page to the user without writing it.
4. Run the five currency checks; fix what they surface.
5. Reconcile `wiki/core/index.md` and `PENDING.md` with what actually changed.
6. Show `git diff wiki/`; commit on the user's cadence.
