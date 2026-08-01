---
title: autogalaxy_workspace — example catalogue routing
sources:
  - project: autogalaxy_workspace
    paths:
      - llms.txt
      - llms-full.txt
      - workspace_index.json
      - start_here.py
      - scripts/README.md
      - scripts/imaging/
      - scripts/interferometer/
      - scripts/multi_dataset/
      - scripts/multi_galaxy/
      - scripts/cluster/
      - scripts/ellipse/
      - scripts/guides/
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 91aa2b6462ef73af9a04308a11601467a2eab67c07ffe20e79bc0f6127cc9158
---

# autogalaxy_workspace

`PyAutoLabs/autogalaxy_workspace` is the production-style example library: runnable
scripts (with generated notebooks alongside them) organised by science case and, inside
each case, by depth — `start_here.py` → `modeling.py` → `features/` → `plot.py` /
`simulator.py`. Audience: galaxy-structure scientists and returning PyAutoGalaxy users who
want a working example to fork rather than an explanation.

Its scope is galaxy **light and mass profiles in a single plane**. Where a group covers
more than one galaxy — `multi_galaxy/` (blended pairs) and `cluster/` (a brightest cluster
galaxy plus a catalogue-driven member population) — the subject is still those galaxies'
**light**: one free light model per galaxy, fitted simultaneously.

## Route from the workspace's own generated catalogue

Do **not** recite per-script paths from this page or from memory — they drift. The repo
ships a catalogue at its **root**, regenerated to stay in sync with the actual files:

- **`llms.txt`** — the compact routing layer: "Start here", "I want to…", the answer
  shape, and a capability boundary for chat-only harnesses. Small enough to paste whole
  into a chat that cannot browse GitHub.
- **`llms-full.txt`** — the full per-script catalogue, one entry per example. **Do not
  fetch this in a connector chat**: it is tens of thousands of tokens and weighs down every
  later turn. Grep it on a local harness; route from `llms.txt` in chat.
- **`workspace_index.json`** — the same listing, machine-readable.

Resolve `autogalaxy_workspace` the normal way (installed copy → sibling clone →
clone-on-demand from [`../../../sources.yaml`](../../../sources.yaml); see
[Source-of-truth resolution](../../../AGENTS.md)) and read those files to find the current
path. `llms.txt` also defines the canonical answer shape — **Start here → Then see →
Related guide → Why this is the right example → What to modify → What needs local
execution** — so follow it and this assistant and the workspace navigator give the same
answer.

## The seven script groups

Enough of a map to choose *which* group to route into before you read the catalogue. Every
group has a `README.md`, a `modeling.py`, a `plot.py` and a `simulator.py`; the table lists
what is distinctive.

| Group | Subject | Entry point |
|---|---|---|
| `scripts/imaging/` | One galaxy in CCD imaging (HST, JWST, ground-based). The largest group: `features/`, `data_preparation/`, `likelihood_function.py`, three simulators | `start_here.py` |
| `scripts/interferometer/` | Visibilities in the uv-plane (e.g. ALMA), plus `casa_reduction.py` and its own `data_preparation/` | `start_here.py` |
| `scripts/multi_dataset/` | One galaxy, several datasets fitted simultaneously — wavelengths, instruments, offsets | `start_here.py` |
| `scripts/multi_galaxy/` | Two or more blended galaxies, each with a free light model | `start_here.py` |
| `scripts/cluster/` | A cluster field: the brightest cluster galaxy modelled individually plus a member population driven by a catalogue CSV | `start_here.py` |
| `scripts/ellipse/` | Non-parametric isophote fitting and multipoles — no light-profile model at all | **`modeling.py`** (see below) |
| `scripts/guides/` | Reference guides rather than science cases: `profiles/`, `plot/`, `modeling/`, `results/`, `units/`, `advanced/`, `hpc/`, `data_structures.py`, `galaxies.py`, `using_jax.py` | `README.md`, then the sub-folder |

**`scripts/ellipse/` has no `start_here.py`.** It is the one group that breaks the
pattern: the entry point is `modeling.py`, with `multipoles.py`, `fit.py`, `database.py`,
`plot.py` and `simulator.py` beside it. Route there directly — a citation to
`ellipse/start_here.py` is a path that does not exist, and inventing it is exactly the
failure this page is here to prevent.

The top-level `start_here.py` at the repo root is a different thing again: a single-page
tour of the whole API (galaxies, profiles, fitting, JAX), and the best first read for
someone new to the library rather than to a science case.

## When to cite the workspace

- The user knows galaxy structure and wants a working example to fork.
- The user is mid-project and needs a concrete recipe for a feature — MGE, shapelets, a
  pixelisation, sky background, a multi-band fit.
- A skill produces a script that is a direct adaptation of a workspace example. Cite the
  example; still produce the user-specific script (see
  [`../../../skills/_style.md`](../../../skills/_style.md) "Python-first").

## Running and URL-building

Scripts run **from the workspace root**: `python scripts/imaging/start_here.py`. A wrong
working directory is the most common failure and produces confusing config errors rather
than a clean message.

**URL base** (derived from `sources.yaml`):
`https://github.com/PyAutoLabs/autogalaxy_workspace`. Scripts are at
`blob/main/scripts/<relative-path>`, notebooks at
`blob/main/notebooks/<relative-path>.ipynb`, and the catalogue files sit at the repo root.
Get `<relative-path>` from the catalogue, then build the URL — never guess it.

## See also

- [`index`](./index.md) — audience routing across all three external resources.
- [`howtogalaxy`](./howtogalaxy.md) — where to send someone who is not ready for these
  examples yet.
- [`skill_citation_map`](./skill_citation_map.md) — the per-skill routing table.
- [`../operations/installation`](../operations/installation.md) — cloning the workspace and
  what its `requirements.txt` asks for.
