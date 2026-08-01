---
title: Skill external-citation map
sources:
  - project: autogalaxy_assistant
    paths:
      - skills/
      - skills/_style.md
      - skills/README.md
      - PENDING.md
    pinned_commit: ed72fabb33e14a9a701a4d280e8775dd3a20e98c
last_updated: 2026-08-01
content_sha256: 1d29ca6a67048d5e548dd83006597944a348f31ade73b852b625800a64d1f40b
---

# Skill → external resource map

One row per skill, three audience-tagged cells. **This table is load-bearing**: a skill's
`## Further reading` block is written from its row (see
[`../../../skills/_style.md`](../../../skills/_style.md) "External resource citation"), and
the agent surfaces *one* of the three bullets in conversation based on the audience —
the other two stay in the block as fallbacks.

**The table lists only skills that exist.** It grows one row per skill as each phase lands;
`../../../PENDING.md` is the ledger of what has not been authored yet. Never add a row for
a planned skill — a row here reads as "this skill exists and cites this page".

## URL expansion

Cells hold a path *relative to* the resource. Expand with:

- **HowToGalaxy (notebook):** `https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/<cell>.ipynb`
- **HowToGalaxy (script):** `https://github.com/PyAutoLabs/HowToGalaxy/blob/main/scripts/<cell>.py`
- **RTD:** `https://pyautogalaxy.readthedocs.io/en/latest/<cell>.html`
- **workspace script:** `https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/<cell>`

Default to `.ipynb` for student-leaning users and `.py` for returning PyAutoGalaxy users.

> HowToGalaxy and workspace cells are **routing hints**. The authoritative, always-current
> paths are each repo's generated catalogue (`llms.txt` / `llms-full.txt` /
> `workspace_index.json` at the repo root). If a cell no longer resolves, resolve it against
> the catalogue and fix the cell — see [`howtogalaxy.md`](./howtogalaxy.md) and
> [`workspace.md`](./workspace.md). RTD slugs are verified against `PyAutoGalaxy:docs/` in
> [`rtd.md`](./rtd.md).

## Table

| Skill | HowToGalaxy (student) | RTD (general) | workspace (experienced) |
|-------|-----------------------|---------------|-------------------------|
| `_style` | _ | _ | _ |
| `_bootstrap_skill` | _ | _ | _ |
| `start-new-project` | _ | _ | _ |
| `contribute-upstream` | _ | _ | _ |
| `ag_audit_skill_apis` | _ | _ | _ |
| `ag_update_wiki` | _ | _ | _ |
| `ag_refresh_api_docs` | _ | _ | _ |
| `ag_setup_environment` | `chapter_1_introduction/tutorial_0_visualization` | `installation/overview` | `imaging/start_here.py` |
| `ag_prepare_imaging_data` | `chapter_1_introduction/tutorial_2_data` | `overview/overview_2_new_user_guide` | `imaging/data_preparation/start_here.py` |
| `ag_simulate_dataset` | `chapter_1_introduction/tutorial_1_grids_and_galaxies` | `overview/overview_1_start_here` | `imaging/simulator.py` |
| `ag_build_imaging_model` | `chapter_2_modeling/tutorial_3_realism_and_complexity` | `general/model_cookbook` | `imaging/modeling.py` |
| `ag_configure_search` | `chapter_2_modeling/tutorial_1_non_linear_search` | `general/configs` | `guides/modeling/searches.py` |
| `ag_run_search` | `chapter_2_modeling/tutorial_2_practicalities` | `overview/overview_2_new_user_guide` | `imaging/start_here.py` |
| `ag_plot_fit` | `chapter_1_introduction/tutorial_3_fitting` | `api/plot` | `guides/plot/start_here.py` |
| `ag_load_results` | `chapter_2_modeling/tutorial_7_results` | `api/fitting` | `guides/results/start_here.py` |
| `ag_debug_fit_failure` | `chapter_2_modeling/tutorial_4_dealing_with_failure` | `general/likelihood_function` | `guides/modeling/bug_fix.py` |

The first seven rows are entirely `_`, and that is the correct state rather than an omission:
those skills are **internal to the workspace** — two meta-skills, two repo-workflow skills, and
the three maintenance skills that audit and refresh this repo's own content. None of them
teaches a galaxy-modelling task, so none has an external resource that would help a user,
and per `_style.md` a skill whose row is entirely `_` omits the `## Further reading` block
altogether.

The nine core-loop rows beneath them are the first with real cells, one per skill in the
modelling loop. Each skill's `## Further reading` block was written from its row here, and
each cell was confirmed to resolve against the target repo's catalogue (or the RTD page map)
before it was recorded. A skill may cite an *extra* tutorial inline within a bullet — the
masking lecture under `ag_prepare_imaging_data`, the optional searches chapter under
`ag_configure_search` — but the row holds the one primary cell per audience.

Rows for the Phase-4b feature skills arrive with those skills. Author the row and the skill in
the same change, from the grounding script named in
[`../../../PENDING.md`](../../../PENDING.md), never from memory.

## Template for the inserted skill block

```markdown
## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: <tutorial title>](<URL>): one
  line on what the tutorial teaches.
- **General reference** — [RTD: <page title>](<URL>): the canonical PyAutoGalaxy
  documentation page for this feature.
- **Experienced PyAutoGalaxy user** — [workspace: <script name>](<URL>): a
  production-style example to fork from.
```

Rules, from `_style.md`:

- Three bullets maximum, one per audience. A `_` cell means omit that bullet and keep the
  others; all three `_` means omit the block.
- Every URL must be one you have **confirmed resolves** — against the target repo's
  catalogue or the RTD page map, never from memory.
- The block sits above the agent checklist, if the skill has one.

## Maintenance

When a skill is added: append its row here, write its `## Further reading` block from that
row, register the skill in [`../../../skills/README.md`](../../../skills/README.md), and
delete its line from `PENDING.md`. When a skill is removed or renamed, its row goes with it
— a row for a file that is not on disk is the same defect as a link to a missing page.

## See also

- [`index`](./index.md) — audience routing across the three resources.
- [`rtd`](./rtd.md) · [`workspace`](./workspace.md) · [`howtogalaxy`](./howtogalaxy.md) —
  the three resources, one page each.
