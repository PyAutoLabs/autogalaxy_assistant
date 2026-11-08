---
title: External resources — index
sources:
  - project: autogalaxy_assistant
    paths:
      - skills/_style.md
      - sources.yaml
      - AGENTS.md
    pinned_commit: f48e9318cc73417823f57806b3b0eaffaabb0bed
  - project: autogalaxy_workspace
    paths:
      - llms.txt
      - scripts/multi_galaxy/README.md
      - scripts/cluster/README.md
    pinned_commit: 81e3c634a16cb93a1275e12403458fce6648b915
  - project: HowToGalaxy
    paths:
      - llms.txt
      - scripts/chapter_4_scaling_up_galaxies/
    pinned_commit: 92f1ba58cc0a026182518990d861ea0790225482
  - project: PyAutoGalaxy
    paths:
      - docs/index.md
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
last_updated: 2026-11-08
content_sha256: b1a6578e54a88b2bb8ca03451805bc5bf9ef2fc8a785aa8b7ad3037d54122cc9
---

# External resources

PyAutoGalaxy lives in a wider ecosystem than this repo. Three external resources carry
almost all of the background material and worked examples, and they are aimed at
**different people** — the routing decision is which one leads, not which ones exist.

| Resource | Audience | Best for | Page |
|---|---|---|---|
| **HowToGalaxy** | New to galaxy structure or to Bayesian fitting | "What *is* a Sersic index? What does fitting even mean?" — four core chapters and optional tutorials from first principles, as notebooks and scripts | [`howtogalaxy.md`](./howtogalaxy.md) |
| **PyAutoGalaxy RTD** | All | The canonical overview series, the model cookbook, installation, the generated API reference | [`rtd.md`](./rtd.md) |
| **`autogalaxy_workspace`** | Morphology-fluent scientists, returning users | Production-style scripts per science case: imaging, interferometer, multi-dataset, multi-galaxy, cluster, ellipse, guides | [`workspace.md`](./workspace.md) |

## Route by regime first

Before choosing *which resource* leads, place the system on PyAutoGalaxy's regime ladder — it
decides *which workspace package and which skill* the answer comes from, and every audience
gets routed to the same rung. `autogalaxy_workspace` ships exactly three packages for it
(`autogalaxy_workspace:scripts/multi_galaxy/README.md` carries the ladder table), and the
subject on every rung is the galaxies' **light**:

| The user describes… | Rung | Workspace package (entry point) | Skill | HowToGalaxy |
|---|---|---|---|---|
| One galaxy, possibly with faint neighbours, stars or artefacts in the frame | Single galaxy | `scripts/imaging/` (`start_here.py`; neighbours via `imaging/features/extra_galaxies/`) | `ag_build_imaging_model` + `ag_light_model_extras` | `chapter_4_scaling_up_galaxies/tutorial_1_extra_galaxies` |
| Two or a few galaxies of comparable brightness whose light overlaps — an interacting pair, a close projected pair, a compact multiple, "two blended galaxies" | Multi galaxy | `scripts/multi_galaxy/` (`start_here.py` → `modeling.py`; a lower tier of companions via `multi_galaxy/features/extra_galaxies/`) | `ag_multi_galaxy_and_cluster` (blended-pair branch) | `chapter_4_scaling_up_galaxies/tutorial_2_multi_galaxy` |
| A brightest cluster galaxy plus tens to hundreds of members, with (or obtainable) a catalogue of centres and luminosities — "a cluster field" | Cluster | `scripts/cluster/` (`start_here.py` → `modeling.py`) | `ag_multi_galaxy_and_cluster` (cluster branch) | `chapter_4_scaling_up_galaxies/tutorial_3_cluster` |

The decision rules, in the order to apply them:

1. **How many galaxies are *subjects* of the measurement**, rather than things to remove from
   it? One subject is the single-galaxy rung however crowded the frame is — companions there
   are contaminants (mask, scale the noise, or model with a fixed centre).
2. **Are the subjects comparably bright, and does their light overlap?** Yes — the
   multi_galaxy rung: each gets its own free light model and they are fitted together, because
   in the overlap neither can be measured without the other.
3. **Is the population too large to give every member free parameters, and is there a
   catalogue?** Yes to both — the cluster rung: the BCG is modelled individually and the
   members ride on catalogue photometry with shared free normalizations, so dimensionality does
   not grow with the population. Many members with **no** catalogue has no tier to pin them —
   ask for (or build) the catalogue before routing to `cluster/`.
4. **A "compact group" has no package of its own.** There is no `group/` folder in
   `autogalaxy_workspace` (unlike `autolens_workspace`) — never cite one. A handful of
   co-dominant members is the multi_galaxy rung; a group large enough to need a catalogue tier
   is the cluster rung. Say which rung and why before composing anything.

The rung is a modelling choice made from looking at the data, so on real data it is settled
inside the inspection gate in [`../../../AGENTS.md`](../../../AGENTS.md), together with the mask
extent — which on the upper rungs must enclose every subject galaxy.
[`skill_citation_map`](./skill_citation_map.md) carries one row per rung for
`ag_multi_galaxy_and_cluster`, so the cells cited follow the rung chosen here.

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

One operational caveat: route from `llms.txt` and grep `llms-full.txt` for the one script
you need — never read `llms-full.txt` whole into context; it runs to tens of thousands of
tokens and would weigh down every subsequent turn.

Both catalogues define the same answer shape — **Start here → Then see → Related guide →
Why this is the right example → What to modify → What needs local execution** — so an
answer built from either agrees with the other.

## See also

- [`skill_citation_map`](./skill_citation_map.md) — one row per skill, load-bearing for
  each skill's `## Further reading` block.
- [`../index`](../index.md) — the core wiki map.
- [`../../README.md`](../../README.md) — how the sub-wikis relate.
