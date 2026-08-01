# Canonical literature bibliography

`autogalaxy_literature.bib` is the metadata layer paired with the literature wiki. Its
BibTeX keys are canonical inside `autogalaxy_assistant`; `sources/*.md` explains the claims
each cited paper supports. Keep abstracts, paper summaries, PDFs, and local PDF paths out of
the bibliography and keep long summaries out of the wiki.

## Key convention

Keys are `SurnameYYYY` — the lead author's surname plus the publication year
(`Sersic1968`, `Peng2002`, `Casey2023`). Add a trailing lowercase letter only to break a
genuine collision between two papers with the same lead author and year (`Bernardi2013`,
`Bernardi2013a`). Collaboration papers with no individual lead author use the collaboration
name (`EuclidCollaboration2025`). Keys are stable — renaming one breaks every source entry
that cites it.

## Adding a paper

1. **Verify the paper from a public source** (arXiv, ADS, the publisher) or the paper
   itself. Check the title, lead author, year and arXiv ID/DOI individually — do not record
   metadata from memory, and do not invent an author list you have not seen. An unverified
   author list is recorded as the lead author plus `and others`.
2. Add one complete entry to `autogalaxy_literature.bib`. Reuse an existing key when the
   paper is already present; otherwise choose a stable author-year key and check it is unique.
3. Add or update a compact section in the relevant `sources/*.md` file using the schema in
   [`../AGENTS.md`](../AGENTS.md). Include the canonical key and only claims directly
   supported by the paper.
4. Update concept/entity links only where the paper materially supports the page.
5. Run `python -m autoassistant.literature validate-citations`.

The [`ag_ingest_paper`](../../../skills/ag_ingest_paper.md) skill follows this sequence for
future users. A supplied PDF may be read during ingestion, but its path is never recorded.

## Aliases and downstream projects

`bibkey_aliases.yaml` is a flat YAML mapping from a common or historical key to the
canonical key:

```yaml
Sersic68: Sersic1968
```

Add an alias only for a key that is actually in use; do not create aliases speculatively.
Aliases do not rewrite a paper project's bibliography.

Before patching downstream LaTeX, inspect the target project's `.bib`: a canonical key may
not exist there, or the same paper may use a local key. Match papers by trusted metadata
(prefer DOI, then arXiv ID, then title/authors), use the project's existing key when found,
and add the canonical metadata under a conflict-free local key only when necessary. Record a
reusable local/common key here as an alias to the canonical key.

## Validation

```bash
python -m autoassistant.literature validate-citations
# or, equivalently:
make validate-literature-citations
```

Missing source keys, duplicate canonical keys, claim sections with no
`**Canonical BibTeX key:**` line, and aliases with missing targets all fail. Canonical
entries not yet represented by a source entry are reported but do not fail; this allows
metadata to exist before the wiki has a claim that needs it. Use `--show-all` to print the
complete unreferenced-key list.
