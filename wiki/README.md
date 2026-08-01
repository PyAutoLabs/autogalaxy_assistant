# wiki/

Independently maintained sub-wikis. Each one answers a different question. **Two exist
today**; the third arrives in a later phase and is listed here so its role is clear, not
because you can read it yet.

| Sub-wiki | Question | Provenance | Edited by |
|---|---|---|---|
| [`core/`](./core/) | *What is X / which X / why X* in the PyAuto\* stack? | Curated from source repos listed in [`../sources.yaml`](../sources.yaml) | `ag_update_wiki` skill, against pinned source commits |
| [`project/`](./project/) | *What did we do in this fork, and why?* | Dated journal entries | Agent + user, every meaningful session |
| `literature/` — **planned** | *What does the galaxy-structure literature say about X?* | Compiled syntheses of papers (PDFs typically kept outside the repo), with its own `concepts/` / `entities/` / `sources/` schema and `[[wiki-link]]` cross-references | The user, when extending the literature wiki from new papers |

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
  bulge-disk decomposition literature"** → this is `literature/` territory. It does not exist
  yet: answer from what the user supplies or from a source you can cite and verify, and never
  imply you read a page here.
- A user asks **"what fits have we already tried on this galaxy?"** → `project/`, grep for the
  dataset name.

## When to write which

- **`core/`** is treated as read-only outside of `ag_update_wiki` runs. Don't edit pages
  ad-hoc as part of unrelated work — every page carries a provenance claim that a hand edit
  silently breaks.
- **`project/`** is append-only. After any session where the agent helps with a real
  modeling decision, dataset change, pipeline tweak, or interpretation, ask the user
  whether to add a journal entry. Use [`project/_template.md`](./project/_template.md).
- **`literature/`** will have its own schema when it lands. Do not create it ad-hoc as part
  of unrelated work; it is authored as a phase, so that its citations can all be verified
  against ADS/arXiv in one pass. A fabricated citation is the worst artifact this repo could
  publish.

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
└── literature/          # planned — galaxy-structure scientific reference
```
