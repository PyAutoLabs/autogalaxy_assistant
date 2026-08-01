# wiki/literature/

The literature sub-wiki holds compiled syntheses of the galaxy-structure scientific
literature: concepts (light profiles, decompositions, isophotes, scaling relations), named
entities (surveys, instruments, catalogues), and per-topic bibliography pages.

> **Authoritative schema:** [`AGENTS.md`](./AGENTS.md) describes the page types,
> frontmatter, cross-reference convention (`[[page-slug]]`), the bibliography key convention,
> and how an assistant should use this wiki. Read it before adding or editing pages.

This is a **self-contained base literature wiki** that ships with the assistant. It is not
tied to any external paper repository — every page stands on its own and papers are cited by
arXiv/DOI reference and/or author-year citation, never by a local file path. Users extend it
with the papers their own project needs.

## Layout

| Folder | Page type | Scope |
|---|---|---|
| `concepts/` | concept | one scientific concept per page (e.g. `sersic-profile.md`) |
| `entities/` | entity | one named thing per page (survey, instrument, catalogue, mission) |
| `sources/` | sources | compact claim support, one paper section per topic |
| `bibliography/` | metadata | canonical BibTeX, key aliases, and citation workflow |
| `index.md` | meta | top-level navigation |
| `log.md` | meta | append-only compilation log |

## How papers are referenced

Each source entry records a verified public reference, a canonical BibTeX key, and only the
claims the paper directly supports. Citation metadata lives separately in
[`bibliography/autogalaxy_literature.bib`](./bibliography/autogalaxy_literature.bib). See
[`bibliography/README.md`](./bibliography/README.md) for adding papers, aliases, downstream
key resolution, and validation.

Every reference in this wiki was verified against a public record (arXiv, ADS, the
publisher) at the time it was written. Keep it that way: an unverified citation is worse than
a missing one.

## When you, the agent, should write here

- A user asks about a specific galaxy-structure paper or result and you can find the topic
  in the wiki — quote and cite from the existing page.
- A new paper has been read and the user explicitly asks for the wiki to be
  updated. Use [`ag_ingest_paper`](../../skills/ag_ingest_paper.md), which updates canonical
  metadata and compact claim support together and runs citation validation.

Do **not** treat this folder as scratch space, and do **not** invent citations:
the schema demands that any cited result trace back to an actual paper stub.
