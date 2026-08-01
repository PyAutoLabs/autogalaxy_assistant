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
      - scripts/chapter_3_search_chaining/
      - scripts/chapter_4_pixelizations/
      - scripts/chapter_optional/
      - scripts/simulators/
    pinned_commit: b1815e9df8ea2c247f4596fa45614e38e0bf86ff
last_updated: 2026-08-01
content_sha256: f6443e77f49a27d946247838df516a95b77bbffdd8191684be634ad8649d1394
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

At the pinned commit the series is **23 tutorial scripts across five chapters**, plus
**three simulator scripts** under `scripts/simulators/` that generate the teaching datasets
(26 `.py` files in total, each with a matching notebook). Route by what the learner is
stuck on:

| Chapter | Scripts | Teaches | Route here when the user… |
|---|---|---|---|
| `chapter_1_introduction` | 6 (`tutorial_0_visualization` … `tutorial_5_summary`) | Grids and galaxies, light profiles, simulated data, fitting, methods | …has never fitted a light profile, or asks what a Sersic index / chi-squared / PSF convolution *is* |
| `chapter_2_modeling` | 8 (`tutorial_1_non_linear_search` … `tutorial_8_need_for_speed`) | The non-linear search, practicalities, realism vs. complexity, dealing with failure, linear profiles, masking, results, speed | …can fit but the search fails, stalls, or returns something unphysical |
| `chapter_3_search_chaining` | 3 (`tutorial_1_search_chaining`, `tutorial_2_prior_passing`, `tutorial_3_x2_galaxies`) | Chaining searches, passing priors, two-galaxy fits | …has a model too complex for one search, or blended neighbours |
| `chapter_4_pixelizations` | 5 (`tutorial_1_pixelizations` … `tutorial_5_model_fit`) | Pixelisations, mappers, inversions, Bayesian regularisation | …has an irregular or clumpy galaxy no smooth profile fits |
| `chapter_optional` | 1 (`tutorial_searches`) | The non-linear search zoo | …is choosing between samplers |

Two caveats about chapter 1, both checked at the pinned commit:

- `tutorial_0_visualization` is a **setup** tutorial (working directory, matplotlib
  options, subplots, overlays), not a physics lecture. The first real lecture is
  `tutorial_1_grids_and_galaxies`, which is where `llms.txt` sends a complete beginner.
- `tutorial_4_methods` is a **placeholder** — its docstring says the tutorial is not
  written yet and is not needed to use the library. Don't route anyone there; if the user
  wants the methodology, the RTD `general/likelihood_function` page and
  `autogalaxy_workspace:scripts/imaging/likelihood_function.py` are the real material.

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
