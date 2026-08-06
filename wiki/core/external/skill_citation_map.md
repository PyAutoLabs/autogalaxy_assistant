---
title: Skill external-citation map
sources:
  - project: autogalaxy_assistant
    paths:
      - skills/
      - skills/_style.md
      - skills/README.md
      - ROADMAP.md
    pinned_commit: a083753c217e6d9c07f3c9cc40cb7133b478a439
last_updated: 2026-08-01
content_sha256: 85756d5daf2dce5003c8c192005da407f4b7f7119eee2983e2feaba897becd21
---

# Skill → external resource map

One row per skill, three audience-tagged cells. **This table is load-bearing**: a skill's
`## Further reading` block is written from its row (see
[`../../../skills/_style.md`](../../../skills/_style.md) "External resource citation"), and
the agent surfaces *one* of the three bullets in conversation based on the audience —
the other two stay in the block as fallbacks.

**The table lists only skills that exist**, and as of Phase 6 that is all twenty-seven of
them. Never add a row for a skill that is only planned — a row here reads as "this skill
exists and cites this page". Anything still wished for lives in `../../../ROADMAP.md`, which
is deliberately not a place rows are drawn from.

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
| `ag_basis_profiles` | `chapter_2_modeling/tutorial_5_linear_profiles` | `api/light` | `imaging/features/multi_gaussian_expansion/modeling.py` |
| `ag_pixelization` | `chapter_3_pixelizations/tutorial_4_bayesian_regularization` | `api/pixelization` | `imaging/features/pixelization/modeling.py` |
| `ag_light_model_extras` | `chapter_4_scaling_up_galaxies/tutorial_2_multi_galaxy` | `overview/overview_3_features` | `imaging/features/extra_galaxies/modeling.py` |
| `ag_ellipse_fitting` | _ | `overview/overview_3_features` | `ellipse/modeling.py` |
| `ag_multi_dataset` | `chapter_2_modeling/tutorial_5_linear_profiles` | `overview/overview_3_features` | `multi_dataset/start_here.py` |
| `ag_build_interferometer_model` | `chapter_1_introduction/tutorial_3_fitting` | `overview/overview_3_features` | `interferometer/start_here.py` |
| `ag_multi_galaxy_and_cluster` | `chapter_4_scaling_up_galaxies/tutorial_2_multi_galaxy` | `overview/overview_2_new_user_guide` | `cluster/start_here.py` |
| `ag_chain_searches` | `chapter_2_modeling/tutorial_9_search_chaining` | `general/configs` | `guides/modeling/chaining.py` |
| `ag_ingest_paper` | _ | _ | _ |
| `ag_to_notebook` | _ | _ | _ |
| `ag_inspect_results_mcp` | _ | _ | _ |

The first seven rows and the last three are entirely `_`, and that is the correct state rather
than an omission: those skills are **internal to the workspace** — two meta-skills, two
repo-workflow skills, the three maintenance skills that audit and refresh this repo's own
content, the literature-ingest workflow, and the two output surfaces (`ag_to_notebook` converts
a script the assistant already wrote; `ag_inspect_results_mcp` configures this repo's own MCP
server). None of them teaches a galaxy-modelling task, so none has an external resource that
would help a user, and per `_style.md` a skill whose row is entirely `_` omits the
three-audience `## Further reading` block. A few of them do carry a short block of *internal*
pointers under the same heading — that is not the external block this table drives.

The nine core-loop rows beneath them are the first with real cells, one per skill in the
modelling loop. Each skill's `## Further reading` block was written from its row here, and
each cell was confirmed to resolve against the target repo's catalogue (or the RTD page map)
before it was recorded. A skill may cite an *extra* tutorial inline within a bullet — the
masking lecture under `ag_prepare_imaging_data`, the optional searches chapter under
`ag_configure_search` — but the row holds the one primary cell per audience.

The eight feature rows after them follow the same rule, with two honest gaps worth reading
before you "fix" a cell that looks wrong:

- **`ag_ellipse_fitting`'s student cell is `_`.** The lecture series teaches light-profile
  modelling and has no ellipse-fitting chapter, so the skill omits that bullet and routes a
  newcomer to [`../concepts/ellipse_fitting_and_multipoles.md`](../concepts/ellipse_fitting_and_multipoles.md)
  instead. A `_` here is the correct state, not a missing lookup.
- **Three rows cite a tutorial that is not about their own subject.** There is no
  multi-wavelength chapter and no interferometer chapter, so `ag_multi_dataset` and
  `ag_build_interferometer_model` cite the tutorial that teaches the idea each fit leans on
  hardest — linear profiles, and the likelihood — and `ag_light_model_extras` shares
  `tutorial_2_multi_galaxy` with `ag_multi_galaxy_and_cluster` because a second galaxy in the
  frame is where the lectures come closest to a contaminant. Each of those bullets says so in
  the skill, rather than implying a chapter exists that does not. Sharing a cell across two
  rows is allowed; inventing one is not.

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
row, register the skill in [`../../../skills/README.md`](../../../skills/README.md), and add
the `.claude/skills/` symlink. When a skill is removed or renamed, its row goes with it
— a row for a file that is not on disk is the same defect as a link to a missing page.

## See also

- [`index`](./index.md) — audience routing across the three resources.
- [`rtd`](./rtd.md) · [`workspace`](./workspace.md) · [`howtogalaxy`](./howtogalaxy.md) —
  the three resources, one page each.
