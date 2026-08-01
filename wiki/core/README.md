# wiki/core/

Curated reference content for the PyAuto\* galaxy-modelling stack. The core wiki
documents *what* the API contains; the skills in [`../../skills/`](../../skills/) document
*how* to use it. The siblings — `../literature/` (the science-literature reference) and
[`../project/`](../project/) (this clone's journal) — are maintained separately; see
[`../README.md`](../README.md) for the overview.

**This directory is read-only.** Only the `ag_update_wiki` maintainer skill rewrites it,
because every page carries a provenance claim (below) that a hand edit silently breaks.
Session notes and per-clone findings belong in `../project/`.

## Organisation

- [`index.md`](./index.md) — top-level map; the entry point for an agent or human reader.
- [`stack/`](./stack/) — one page per source library, plus an overview of how they fit
  together.
- [`concepts/`](./concepts/), [`api/`](./api/), [`operations/`](./operations/),
  [`external/`](./external/) — physics/framework explanations, task-oriented API catalogues,
  operational guides and external-resource routing. All four are written; `index.md` is the
  page-by-page list.

## Page format

Every wiki page begins with YAML frontmatter:

```yaml
---
title: <Page title>
sources:
  - project: PyAutoFit
    paths:
      - autofit/non_linear/search/nest/nautilus/
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
last_updated: 2026-08-01
content_sha256: <sha256 of the page body>
---
```

- **`sources`** is what `ag_update_wiki` reads to know when a page is stale relative to
  upstream. After a source file changes between `pinned_commit` and current HEAD, the
  relevant section of the page is rewritten and the pin is bumped.
- **`pinned_commit` must be a real 40-character commit SHA**, never a moving ref like
  `main`: the pin is the claim "this page was validated against *this* revision".
- **`content_sha256`** binds the prose to that claim. It is the SHA-256 of everything
  after the closing `---`, stamped by
  `python autoassistant/audit_skill_apis.py --write-provenance`. Edit the body without
  re-stamping and the provenance check fails — which is the point.

Verify both with `python autoassistant/audit_skill_apis.py --check-provenance`, and check
that every cited path still exists with `--check-citations`.

## Source citations inside page bodies

Inside a wiki page, code references use the **project name + path relative to the
project's repo root**, identical to the skill convention:

```
See `PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py` for the implementation.
```

Resolve project names via [`../../sources.yaml`](../../sources.yaml). Never embed
absolute local paths.

## Adding a new page

1. Pick the right subdirectory (`stack/`, and later `concepts/`, `api/`, `operations/`).
2. Add the YAML frontmatter, including every source path the page depends on and a real
   pinned SHA.
3. Hand-write the body against the installed source, not from memory. The wiki is
   curated; auto-generated dumps belong in each library's own `docs/` folder.
4. Link the new page from `index.md` and from any skill that should cite it — and never
   link a page that does not exist yet.
5. Stamp it: `--write-provenance`, then re-run `--check-provenance` and
   `--check-citations`.
