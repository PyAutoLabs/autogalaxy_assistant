---
title: HowToGalaxy — lecture catalogue routing
sources:
  - project: HowToGalaxy
    paths:
      - llms.txt
      - llms-full.txt
      - workspace_index.json
      - start_here.py
      - scripts/chapter_1_introduction/
      - scripts/chapter_2_modeling/
      - scripts/chapter_3_pixelizations/
      - scripts/chapter_4_scaling_up_galaxies/
      - scripts/chapter_optional/
      - scripts/simulators/
    pinned_commit: ee283c9d18d40b9365c9194292f427bcaed797f3
last_updated: 2026-08-07
content_sha256: 9e34da30c7e7c22ed747398b4f51d4939dcc86e17780bc0a690118f33c79ae11
---

# HowToGalaxy

HowToGalaxy teaches galaxy morphology and the PyAutoGalaxy API **from first principles**,
assuming no prior knowledge of galaxy structure or Bayesian inference. It is the on-ramp:
five chapters of tutorials shipped as parallel Python scripts (`scripts/`) and Jupyter
notebooks (`notebooks/`), one notebook per script. Primary audience: students, and
scientists new to model-fitting.

It is a **separate repository** from `autogalaxy_workspace`. HowToGalaxy teaches; the
workspace is what you use afterwards on your own data. Sending a newcomer straight to a
workspace `modeling.py` is the most common routing mistake.

## Route from HowToGalaxy's own generated catalogue

Do **not** recite per-tutorial titles or paths from this page or from memory. The repo
ships a catalogue at its **root**, regenerated to stay in sync with the tutorials:

- **`llms.txt`** — the compact routing layer: "Start here", the learning path by chapter,
  "I want to understand…", and the same answer shape the workspace navigator uses. Small
  enough to paste whole into a chat that cannot browse GitHub.
- **`llms-full.txt`** — the full per-tutorial catalogue with titles and one-line summaries.
- **`workspace_index.json`** — the same listing, machine-readable.

Resolve `HowToGalaxy` the normal way (sibling clone → clone-on-demand from
[`../../../sources.yaml`](../../../sources.yaml); see
[Source-of-truth resolution](../../../AGENTS.md)) and read those files for the current
tutorial rather than trusting a hand-written list.

## The five chapters

The series is **26 tutorial scripts across five chapters**, plus
**six simulator scripts** under `scripts/simulators/` that generate the teaching datasets
(32 `.py` files in total, each tutorial with a matching notebook). Route by what the learner
is stuck on:

| Chapter | Scripts | Teaches | Route here when the user… |
|---|---|---|---|
| `chapter_1_introduction` | 6 (`tutorial_0_visualization` … `tutorial_5_summary`) | Grids and galaxies, light profiles, simulated data, fitting, methods | …has never fitted a light profile, or asks what a Sersic index / chi-squared / PSF convolution *is* |
| `chapter_2_modeling` | 10 (`tutorial_1_non_linear_search` … `tutorial_10_prior_passing`) | The non-linear search, practicalities, realism vs. complexity, dealing with failure, linear profiles, masking, results, speed, search chaining, prior passing | …can fit but the search fails, stalls, or returns something unphysical — or has a model too complex for one search |
| `chapter_3_pixelizations` | 6 (`tutorial_1_pixelizations` … `tutorial_6_model_fit`) | Pixelisations, mappers, inversions, Bayesian regularisation | …has an irregular or clumpy galaxy no smooth profile fits |
| `chapter_4_scaling_up_galaxies` | 3 (`tutorial_1_extra_galaxies`, `tutorial_2_multi_galaxy`, `tutorial_3_cluster`) | Extra galaxies, multi-galaxy blends, cluster fields | …has blended neighbours or a crowded field |
| `chapter_optional` | 1 (`tutorial_searches`) | The non-linear search zoo | …is choosing between samplers |

Two caveats about chapter 1, both checked at the pinned commit:

- `tutorial_0_visualization` is a **setup** tutorial (working directory, matplotlib
  options, subplots, overlays), not a physics lecture. The first real lecture is
  `tutorial_1_grids_and_galaxies`, which is where `llms.txt` sends a complete beginner.
- `tutorial_4_methods` is a **placeholder** — its docstring says the tutorial is not
  written yet and is not needed to use the library. Don't route anyone there; if the user
  wants the methodology, the RTD `general/likelihood_function` page and
  `autogalaxy_workspace:scripts/imaging/likelihood_function.py` are the real material.

Two chapters also carry an **extensionless prose file** — `chapter_2_modeling/tutorial_11_summary`
and `chapter_3_pixelizations/introduction`. These are chapter narrative (what you just learnt /
what is coming), not runnable tutorials: no `.py`, no notebook, and deliberately excluded from
the counts above. Listing the directory makes `tutorial_11_summary` look like an eleventh
tutorial; it is not, and the URL-building rules below do not apply to it — appending `.py`
yields a 404. Chapter 1's summary is different: `tutorial_5_summary.py` *is* a real script and
*is* counted in that chapter's 6.

## When to cite HowToGalaxy

- The user is new to galaxy structure, or new to Bayesian non-linear inference.
- The user wants the conceptual grounding behind something a skill is already using
  (a Sersic profile, regularisation, search chaining, inversions).
- **Lead with the notebook URL**, before the code block rather than after — see
  [`../../../skills/_style.md`](../../../skills/_style.md) "Newcomer mode". Offer the
  script if they would rather read than run.
- Once the learner wants to model their *own* galaxy, hand off to
  [`workspace.md`](./workspace.md).

Mention once per session that running the notebook alongside the script the assistant
produces makes the concepts land much faster. Once, not repeatedly.

## URL-building

**URL base** (derived from `sources.yaml`): `https://github.com/PyAutoLabs/HowToGalaxy`.

- Notebook: `blob/main/notebooks/<chapter>/<tutorial>.ipynb`
- Script: `blob/main/scripts/<chapter>/<tutorial>.py`
- Catalogue files: repo root.

Default to `.ipynb` for student-leaning users and `.py` for returning PyAutoGalaxy users.
Get `<chapter>/<tutorial>` from the catalogue; never guess it. The chapter pages rendered
on RTD (`howtogalaxy/chapter_1_introduction` and siblings) are descriptions of these
chapters, not the runnable tutorials — see [`rtd.md`](./rtd.md).

## See also

- [`index`](./index.md) — audience routing across all three external resources.
- [`workspace`](./workspace.md) — where a learner goes next.
- [`skill_citation_map`](./skill_citation_map.md) — the per-skill routing table.
