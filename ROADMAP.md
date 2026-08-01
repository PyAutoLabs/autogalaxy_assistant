# ROADMAP — where this assistant goes next

`autogalaxy_assistant` was built in public, in phases, against a construction ledger
(`PENDING.md`) that listed everything not yet written. **That ledger is retired**: every skill,
wiki page, benchmark card and piece of infrastructure it tracked is now on disk. This file
replaces it, and it is a different kind of document — forward-looking wishes and known limits,
not admissions of absence.

The distinction matters because a construction ledger has an expiry date and a roadmap does
not. A public assistant that keeps a stale "under construction" page long after construction
finished tells its next user something false; a sibling assistant did exactly that, and a real
user read it. So the rule that governed `PENDING.md` carries over unchanged and applies to this
file too:

> **No file may link to something on this list**, and no agent may answer as though it had read
> one. If an item here is needed before it ships, author it properly — from a named grounding
> script, never from memory, because older PyAutoGalaxy releases are heavily represented in
> model training data.

What *is* written is indexed in [`skills/README.md`](./skills/README.md) (twenty-seven skills),
[`wiki/core/index.md`](./wiki/core/index.md) (the reference wiki, complete) and
[`wiki/literature/index.md`](./wiki/literature/index.md) (the science reference).

**Tracker.** Epic: [PyAutoLabs/PyAutoBrain#188](https://github.com/PyAutoLabs/PyAutoBrain/issues/188).

---

## 1. Benchmark calibration runs

[`benchmarks/prompts/`](./benchmarks/prompts/) holds four frozen cards — easy, medium, hard and
teacher. **`benchmarks/RESULTS.md` records no scored runs**, because none have been run. That is
the honest state and it is regenerated mechanically
(`python autoassistant/benchmark.py report`); it is never hand-written, and a score is never
recorded for a session that did not happen.

Calibration is the natural first post-birth task: run each card once on a known model and
harness to establish a baseline, starting with the teacher card (cheapest, and the recommended
drift probe). The protocol is [`benchmarks/README.md`](./benchmarks/README.md) "Running a
benchmark" and the agent-side contract is [`benchmarks/AGENTS.md`](./benchmarks/AGENTS.md).

Until at least one run exists, the suite measures nothing — it only *can* measure. Do not cite
benchmark performance.

## 2. A second dataset — HST via PyAutoReduce

One dataset ships: `dataset/imaging/cosj100020+015344/`, a four-band JWST/NIRCam cutout. A
second, reduced from HST imaging through `PyAutoReduce`, would give the assistant a genuinely
different instrument to reason about — a different PSF regime, a different pixel scale, a
different set of reduction artefacts — instead of one instrument seen four times.

Deferred by decision during the build rather than forgotten. Whoever picks it up inherits the
same rule that governed the first: **never invent provenance.** Every `info.json` number is
either measured by a committed script or cited, and the caveats are stated rather than
smoothed over.

### The bundled dataset's own open item

`dataset/imaging/cosj100020+015344/mask_extra_galaxies.fits` does not ship. The cutout has a
real neighbour — a faint source **2.6" from the centre**, inside any mask wide enough to reach
the galaxy's outer isophotes (a brighter one 8.0" out is already excluded by a <~4" mask). Every
session that fits this data has to mask or model it per-session; the dataset README and the
README hero figure both flag it. A committed mask would remove that repeated work. Grounding:
`autogalaxy_workspace:scripts/imaging/data_preparation/gui/mask_extra_galaxies.py`.

## 3. Two skills with no grounding script

Catalogued so the gap is visible, and deliberately not written:

- **`ag_custom_profile`** — subclassing a light profile and registering it for use in models.
  Closest existing material is `autogalaxy_workspace:scripts/guides/profiles/light.py`, which
  uses the built-in profiles without subclassing.
- **`ag_custom_analysis`** — subclassing an analysis object to add custom likelihood terms.

Neither has an `autogalaxy_workspace` script that grounds it, and **neither may be authored by
porting the equivalent skill from a sibling assistant.** A recipe with no grounding script is
precisely the failure this whole discipline exists to prevent. Write one when the workspace
grows an example, or when a real user need supplies the missing ground truth. The authoring
protocol is [`skills/_bootstrap_skill.md`](./skills/_bootstrap_skill.md).

## 4. Upstream fixes to contribute

Things this repo knows are wrong *elsewhere*, found while grounding against them. Each is a
[`skills/contribute-upstream.md`](./skills/contribute-upstream.md) candidate.

- **`autogalaxy_workspace:scripts/guides/modeling/chaining.py`** describes `result.model` as
  returning narrowed `TruncatedGaussianPrior`s. It does not: `result.model` returns the fitted
  model with its **original priors unchanged**
  (`samples_summary.model.mapper_via_defaults_from`, which maps every prior to itself). The
  narrowing lives on `result.model_centred` and its `model_centred_absolute(a=)` /
  `model_centred_relative(r=)` / `model_centred_max_lh_bounded(b=)` variants. The same claim had
  spread into two wiki pages here and was corrected during Phase 4b;
  [`skills/ag_chain_searches.md`](./skills/ag_chain_searches.md) warns the reader that the
  upstream script's description is out of date until the fix lands.

Add to this list rather than fixing silently: the value is that the next person grounding
against the same script is warned before they trust it.

## 5. Newborn-validation leg 4 — the chat-surface smoke record

Three of the four newborn-validation legs are mechanical and run in this repo: the symbol audit
with its version baseline, the full markdown-link crawl, and the `wiki-currency` workflow on a
PR. **Leg 4 is not mechanical**: a formal smoke test of the assistant over a chat surface —
a GitHub-connector session against the live public repository, driven per
[`modes/maintainer.md`](./modes/maintainer.md), where there is no code execution and no API
gate, so the discipline that holds is the one written into the prose.

It has to run against the published URL rather than a local checkout, and its result belongs in
a dated `wiki/project/` entry. Until that record exists, the chat surface is untested by the
gate even though the prose is written for it.

## 6. Deferred by decision — recorded so nobody files them as gaps

- **`paper/` and a JOSS `draft-pdf.yml` workflow.** Considered only once the assistant is
  complete and has benchmark evidence behind it. Shipping the workflow without a `paper.md`
  would mean a permanently red CI badge on a public repo.
- **A `REFERENCE_PROFILES` entry in PyAutoBrain's clone tooling.** Owned by whoever first
  clones *from* this repo, not by this repo.
  [`modes/maintainer.md`](./modes/maintainer.md)'s "Assistant-as-template" section is the
  partition seed that entry would pair with, and its four bold markers are read literally by the
  clone checker — **keep them**.

---

## How to use this file

Add an item when you find a real limit and decide not to fix it now — with enough detail that
the next reader can act on it, and with its grounding named. Remove an item in the same change
that closes it. Do not add a wish with no grounding path; that is how a roadmap decays back into
a list of things nobody can start.
