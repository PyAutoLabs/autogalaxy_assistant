# Compilation log

Append-only record of what was done to this wiki, by whom, and when.

---

## 2026-08-01 — Initial build (Phase 5)

**By:** Claude (Opus 5, `autogalaxy_assistant` Phase 5 literature build, branch
`feature/phase-5-literature`).

**Scope of build:** the galaxy-structure literature an assistant needs in order to interpret
a light-profile fit — how galaxy light is parameterised and fitted, what the resulting
structural parameters mean, and which surveys and instruments produced the measurements the
field compares against.

**What was created**

- `AGENTS.md` — the sub-wiki's own contract: page types, naming, frontmatter, the
  `[[wiki-link]]` convention, the source-entry schema, the `SurnameYYYY` bibliography key
  convention, and the verification rule.
- `CLAUDE.md` — one-line `@AGENTS.md` import stub.
- `README.md` — orientation and layout for a human reader.
- `index.md` — top-level navigation, sectioned by galaxy-structure topic.
- `concepts/` — topical concept hubs (built in the same phase).
- `entities/` — surveys, catalogues, missions and instruments: COSMOS-Web, COSMOS, zCOSMOS,
  CANDELS, SDSS, MaNGA, SAMI, Euclid, JWST, HST.
- `sources/` — per-topic bibliography pages, one H2 section per paper, each carrying a
  canonical BibTeX key, the claims the paper supports, and when not to cite it.
- `bibliography/` — `autogalaxy_literature.bib`, `bibkey_aliases.yaml` (no aliases yet — none
  are in actual use) and a README covering the key convention, ingestion and validation.
- `skills/ag_ingest_paper.md` (+ `.claude/skills/` symlink) — the procedure for adding a new
  paper, grounded on `autoassistant/literature.py` and the `validate-literature-citations`
  Make target.

**Citation policy applied in this build**

Every citation was verified against a public record — the arXiv API (`export.arxiv.org`,
which returns title, authors, dates, `journal_ref` and DOI) or NASA ADS via search for
pre-arXiv papers — before it was written. Titles, lead authors, years and identifiers were
each checked individually. This was not ceremonial: several arXiv IDs recalled at the
drafting stage turned out to belong to entirely unrelated papers (one to a protoplanetary-disc
paper, one to a natural-language-processing paper, one to a quantum-optics paper), which is
exactly the failure mode the policy exists to prevent.

Author lists were **not** verified in full. Every bibliography entry therefore records the
verified lead author followed by `and others`, rather than a reconstructed author list.
Volume and page numbers appear only where a `journal_ref`, DOI or ADS bibcode showed them;
where they were not seen, the entry carries the arXiv identifier and DOI alone.

**Known gaps / explicit TODOs**

- Journal volume/page numbers are missing from some entries where only an arXiv record and
  DOI were available. These are safe to cite but incomplete; fill them from ADS when a
  downstream manuscript needs a full reference.
- The bibliography holds only papers the source pages actually cite. `validate-citations`
  reports unreferenced keys as informational, so metadata may be staged ahead of a claim.
- Coverage is deliberately structural. Stellar populations, gas content, star-formation
  histories and galaxy-formation theory appear only where they bear directly on interpreting
  a light-profile fit. Extend through `ag_ingest_paper` rather than by bulk import.

**Provenance note**

The format follows Karpathy's LLM Wiki pattern: the source literature is immutable, the wiki
layer is compiled and cross-linked, and the schema lives in `AGENTS.md` so the maintaining
LLM has a stable contract.
