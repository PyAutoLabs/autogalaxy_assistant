---
title: External resources — index
sources:
  - project: autogalaxy_assistant
    paths:
      - skills/_style.md
      - sources.yaml
      - AGENTS.md
    pinned_commit: ed72fabb33e14a9a701a4d280e8775dd3a20e98c
  - project: autogalaxy_workspace
    paths:
      - llms.txt
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
  - project: HowToGalaxy
    paths:
      - llms.txt
    pinned_commit: b1815e9df8ea2c247f4596fa45614e38e0bf86ff
  - project: PyAutoGalaxy
    paths:
      - docs/index.md
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
last_updated: 2026-08-01
content_sha256: 9447557d11fccb86afbba5157709c9e9e5c111f262a069d8206916440b3e0e87
---

# External resources

PyAutoGalaxy lives in a wider ecosystem than this repo. Three external resources carry
almost all of the background material and worked examples, and they are aimed at
**different people** — the routing decision is which one leads, not which ones exist.

| Resource | Audience | Best for | Page |
|---|---|---|---|
| **HowToGalaxy** | New to galaxy structure or to Bayesian fitting | "What *is* a Sersic index? What does fitting even mean?" — five chapters from first principles, as notebooks and scripts | [`howtogalaxy.md`](./howtogalaxy.md) |
| **PyAutoGalaxy RTD** | All | The canonical overview series, the model cookbook, installation, the generated API reference | [`rtd.md`](./rtd.md) |
| **`autogalaxy_workspace`** | Morphology-fluent scientists, returning users | Production-style scripts per science case: imaging, interferometer, multi-dataset, multi-galaxy, cluster, ellipse, guides | [`workspace.md`](./workspace.md) |

## Routing matrix

Match the audience to one lead resource. This mirrors the table in
[`../../../skills/_style.md`](../../../skills/_style.md) "Resource routing by audience" —
that section is the writing rule, this page is the reference behind it.

- **Galaxy-morphology newcomer** → **HowToGalaxy** first (physics from the ground up),
  then RTD `overview/overview_1_start_here` for the bigger picture. Don't lead with a
  workspace script.
- **Morphology-fluent, PyAutoGalaxy-new** → RTD `overview/overview_2_new_user_guide` (it
  routes by scale of system and dataset type) and `overview/overview_3_features`, then the
  workspace script for the chosen science case.
- **Returning PyAutoGalaxy user** → the workspace script, plus the RTD API reference. Skip
  HowToGalaxy unless they ask how a concept is taught.

**Pick one to lead and optionally cite a second. Never dump all three.** A wall of links is
the failure mode this page exists to prevent.

The user's level accumulates in `wiki/project/profile.md`. With no profile yet, infer from
the immediate cues in their question — *"I'm new to this"* versus *"how do I get the
bulge-to-total ratio?"* versus *"load `output/.../abc/`"* are three different audiences.

## Catalogues, not URL lists

Neither [`workspace.md`](./workspace.md) nor [`howtogalaxy.md`](./howtogalaxy.md) lists
per-script URLs, deliberately. Each repo ships its own **generated catalogue** at its root
— `llms.txt` (compact), `llms-full.txt` (full per-script), `workspace_index.json`
(machine-readable) — regenerated with the files, so it cannot go stale the way a
hand-written list does. Resolve the repo per
[`../../../sources.yaml`](../../../sources.yaml) and read the catalogue.

One operational caveat: in a connector chat, route from `llms.txt` only. `llms-full.txt`
runs to tens of thousands of tokens and would weigh down every subsequent turn; grep it on
a local harness instead.

Both catalogues define the same answer shape — **Start here → Then see → Related guide →
Why this is the right example → What to modify → What needs local execution** — so an
answer built from either agrees with the other.

## See also

- [`skill_citation_map`](./skill_citation_map.md) — one row per skill, load-bearing for
  each skill's `## Further reading` block.
- [`../index`](../index.md) — the core wiki map.
- [`../../README.md`](../../README.md) — how the sub-wikis relate.
