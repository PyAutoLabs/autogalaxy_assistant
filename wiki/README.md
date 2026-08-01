# wiki/

Independently maintained sub-wikis. Each one answers a different question. **Two exist
today**; the third arrives in a later phase and is listed here so its role is clear, not
because you can read it yet.

| Sub-wiki | Question | Provenance | Edited by |
|---|---|---|---|
| [`core/`](./core/) | *What is X / which X / why X* in the PyAuto\* stack? | Curated from source repos listed in [`../sources.yaml`](../sources.yaml) | `ag_update_wiki` skill, against pinned source commits |
| [`project/`](./project/) | *What did we do in this fork, and why?* | Dated journal entries | Agent + user, every meaningful session |
| `literature/` | *What does the galaxy-structure literature say about X?* | Compiled syntheses of papers (PDFs typically kept outside the repo), with its own `concepts/` / `entities/` / `sources/` schema, `[[wiki-link]]` cross-references and a verified BibTeX bibliography | The user (via `ag_ingest_paper`), when extending the literature wiki from new papers |

`core/` is itself partially built: only `stack/` (one page per source library) exists so far.
[`core/index.md`](./core/index.md) states exactly which directories are still missing, and the
repo-root [`PENDING.md`](../PENDING.md) is the authoritative ledger of unwritten pages with the
grounding script for each.

## When to read which

- A user asks **"what does PyAutoFit contribute to the stack?"** → `core/stack/autofit.md`.
- A user asks **"what's a Sersic index?"** or **"which searches can I use?"** → `core/`, once
  its `concepts/` and `api/` pages land. Until then, ground the answer in the installed source
  and the `autogalaxy_workspace` scripts, and say that is what you did.
- A user asks **"how does the Kormendy relation constrain this?"** or **"summarise the
  bulge-disk decomposition literature"** → this is `literature/` territory: start from
  [`literature/index.md`](./literature/index.md) and cite the concept or source page you
  actually read.
- A user asks **"what fits have we already tried on this galaxy?"** → `project/`, grep for the
  dataset name.

## When to write which

- **`core/`** is treated as read-only outside of `ag_update_wiki` runs. Don't edit pages
  ad-hoc as part of unrelated work — every page carries a provenance claim that a hand edit
  silently breaks.
- **`project/`** is append-only. After any session where the agent helps with a real
  modeling decision, dataset change, pipeline tweak, or interpretation, ask the user
  whether to add a journal entry. Use [`project/_template.md`](./project/_template.md).
- **`literature/`** grows only through [`ag_ingest_paper`](../skills/ag_ingest_paper.md),
  which verifies every citation against ADS/arXiv/CrossRef before it is recorded and ends by
  running `make validate-literature-citations`. A fabricated citation is the worst artifact
  this repo could publish; its own contract is [`literature/AGENTS.md`](./literature/AGENTS.md).

## Sub-wiki layout

```
wiki/
├── README.md            # this file
├── core/                # PyAuto* reference
│   ├── README.md  index.md
│   ├── stack/           # one page per library — LIVE
│   └── concepts/  api/  operations/  external/     # planned (see PENDING.md)
├── project/             # running journal for this fork
│   ├── README.md
│   ├── _template.md            # dated-entry template
│   └── _profile_template.md    # user-profile template
└── literature/          # galaxy-structure scientific reference (own AGENTS.md schema)
    ├── concepts/               # the science: profiles, decomposition, scaling relations…
    ├── entities/               # surveys and instruments
    ├── sources/                # per-topic annotated bibliographies
    └── bibliography/           # autogalaxy_literature.bib (verified) + aliases
```
