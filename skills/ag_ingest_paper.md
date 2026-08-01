---
name: ag_ingest_paper
description: Add a verified galaxy-structure paper to the literature record — project-local (`wiki/project/bibliography.md`) by default when working inside a science project, or the shared literature wiki + canonical BibTeX layer when in the assistant clone or on explicit promotion. Accepts an arXiv ID, a public paper URL, or a local PDF; verifies the metadata against a public record before recording it, resolves or adds the canonical BibTeX key, writes a compact claim-oriented source entry, updates relevant concept/entity links, runs citation validation, and never records local PDF paths. Use when a user wants a paper added so future assistants can cite its supported claims reliably.
---

# Ingesting a paper into the literature wiki

A galaxy-structure result is only useful to a future session if it can be cited *precisely*:
the right paper, the right claim, and a BibTeX key that resolves in whatever manuscript the
user is writing. This skill is how a paper becomes part of that record.

Read [`wiki/literature/AGENTS.md`](../wiki/literature/AGENTS.md) and
[`wiki/literature/bibliography/README.md`](../wiki/literature/bibliography/README.md) before
editing. The wiki and bibliography are paired but distinct:

- `sources/*.md` says which claims a paper supports.
- `bibliography/autogalaxy_literature.bib` holds canonical metadata and keys.
- `bibliography/bibkey_aliases.yaml` records known alternate keys.

Do not save PDFs, local PDF paths, abstracts, or long paper summaries.

## Orient

Ingestion makes a paper discoverable from a scientific concept — "what sets the Sersic index
of a bulge?", "what does the size–mass relation look like at z ~ 2?" — while preserving a
reliable citation key. A normal addition changes the canonical `.bib`, one compact source
section, relevant concept/entity links, and `log.md`.

The scientific point is claim scope. A source entry is not a summary; it records what the
paper *licenses you to say*. "Simard et al. measured bulge+disk decompositions for 1.12
million SDSS galaxies" is a claim that paper supports. "Bulge+disk decomposition recovers the
true bulge mass" is not — and the difference is exactly what a future session needs from you.

## Target — project-local or shared?

Two destinations; pick before editing anything (the hybrid rule: general concepts stay
shared, analysis-specific papers stay in the project):

- **Inside a science project** (the working repo has `project.yaml` and a thin refer-back
  `AGENTS.md`): the default target is the **project's** `wiki/project/bibliography.md` — one
  `##` section per paper, exactly the "record claim support" shape below. Reuse the
  assistant's canonical BibTeX key when the paper is already in `autogalaxy_literature.bib`
  (read-only lookup via refer-back); otherwise use a stable author-year key, aligned with the
  project's own paper `.bib` if one exists. Do **not** edit the assistant clone's
  `bibliography/` or `sources/` from a project session — that is promotion, below. The shared
  quality gate does not run against a project page; keep it consistent by inspection.
- **In the assistant clone, or on explicit promotion** of a generally-useful paper out of a
  project: the shared `wiki/literature/` flow below — canonical `.bib`, `sources/<topic>.md`,
  concept/entity links, `log.md`, `validate-citations`. Promotion is a deliberate act, never
  the default, and is a verbatim copy of the project section into the right
  `sources/<topic>.md` plus the canonical-metadata steps.

## Ask

Establish only what is not already supplied:

- the arXiv ID, public URL, or local PDF;
- the relevant `sources/<topic>.md` page — show the existing filenames and ask one focused
  question if the topic is unclear;
- whether the user needs specific claims extracted, or metadata-only staging.

## Branch — verify the metadata before recording anything

**This step is not skippable, and it is not satisfied by recall.** Paper metadata recalled
from a model's memory is wrong often enough to matter — a plausible-looking arXiv ID
routinely belongs to a completely different paper in a different field. Verify against a
public record:

```
http://export.arxiv.org/api/query?id_list=2211.07865&max_results=1
```

The arXiv API accepts a comma-separated `id_list` (roughly 15 IDs per call), and returns the
title, author list, publication date and `journal_ref` for each. When you do not know the ID,
search by title phrase:

```
http://export.arxiv.org/api/query?search_query=ti:%22COSMOS-Web%22&max_results=10
```

For pre-arXiv papers (before ~1992) there is no arXiv record: verify through NASA ADS and
record the bibcode (e.g. `1968adga.book.....S`), which encodes year, journal, volume and page.
Space the calls out — the endpoint rate-limits, and a throttled call returns nothing rather
than wrong data.

Check four things individually: **title, lead author, year, identifier**. If the author list
cannot be seen in full, record the lead author and `and others` rather than reconstructing
co-authors. Never invent a DOI, a volume, or a page number.

Then resolve the key:

1. Search `autogalaxy_literature.bib` by DOI, arXiv ID, and normalized title before minting
   a key.
2. If present, reuse its canonical key. If absent, add verified BibTeX metadata under a
   stable, unique `SurnameYYYY` key (see the bibliography README for the convention). Do not
   fabricate missing fields or rename unrelated keys.
3. Add an alias only when a common or project-local alternate key is actually known.

For a downstream paper project, inspect its `.bib` separately. Match by DOI, arXiv ID, then
title/authors; use the project's existing key when present. Never assume this repository's
canonical key exists in the target project.

## Branch — record claim support

Add one H2 section to the relevant `sources/*.md` file:

```markdown
## Author Year — short tag

**Canonical BibTeX key:** `KeyYYYY`
**Reference:** arXiv ID, DOI or journal reference
**Concepts:** [[concept-1]], [[entity-1]]

**Supports:**
- Claim this paper directly supports.
- Another claim this paper directly supports.

**Use when:**
- Situation where the citation is appropriate.

**Do not use for:**
- Similar but unsupported claim.
```

Use 2–5 support bullets. Each must be directly supported by the paper. Keep prose short;
paraphrase rather than copying the abstract. If only metadata was verified, add an explicit
TODO for claim extraction instead of inferring claims.

The `**Canonical BibTeX key:**` line is machine-read — a claim section without one fails
validation, and so does a key with no matching `.bib` entry.

Update concept/entity pages only where this paper materially supports existing text, using
`[[wiki-link]]` slugs. Create a new page only when the paper introduces a genuinely missing
concept or named entity.

## Quality gate

Append a concise dated row to `wiki/literature/log.md` naming what was added and where the
metadata came from, then run:

```bash
python -m autoassistant.literature validate-citations
```

or equivalently `make validate-literature-citations`. The checker
(`autoassistant/literature.py`) reads
`wiki/literature/bibliography/autogalaxy_literature.bib`, every `wiki/literature/sources/*.md`
and `bibkey_aliases.yaml`, and fails on: a canonical key cited by a source entry but absent
from the bibliography, a duplicate key in the bibliography, a `**Supports:**` section with no
canonical-key declaration, and an alias whose target does not exist. Bibliography entries not
yet cited by any source entry are reported but do **not** fail — metadata may legitimately
land before the claim that needs it.

A successful ingestion leaves no local path in tracked files and no unsupported claim in the
source entry.

## Combine

- Use [`ag_update_wiki`](./ag_update_wiki.md) only if the paper changes curated `wiki/core/`
  API documentation — the literature wiki and the API reference are separate surfaces.
- Project notes may link the source section, but LaTeX citations must use the target
  project's resolved local BibTeX key.
- When the paper motivated an actual fit, the script and its `wiki/project/` entry are the
  other half of the record — see [`_style.md`](./_style.md) "Records work to the project
  wiki".

## Further reading

- **General reference** — [`wiki/literature/AGENTS.md`](../wiki/literature/AGENTS.md): the
  page types, frontmatter, `[[wiki-link]]` convention and key convention this skill writes
  against.
