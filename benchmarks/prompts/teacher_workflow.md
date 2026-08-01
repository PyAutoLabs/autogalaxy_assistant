---
id: teacher-basic-workflow
version: 1
mode: teacher
difficulty: easy
datasets: []          # fully simulated — the session generates its own data
workspace_packages:
  - imaging
added: 2026-08-01
---

# Benchmark: end-to-end workflow walkthrough (teacher)

The teacher-mode card: the deliverable is **understanding**, not a measurement. The science
is deliberately the simplest thing the stack does well — a Sersic bulge plus an Exponential
disk on data the session simulates itself — so the score concentrates on pedagogy: pacing,
correctness of explanation, and whether a newcomer would come away able to reconstruct the
workflow rather than having watched commands scroll past.

Simulated data also removes the real-data gate from the picture (simulated data is exempt),
which is deliberate: this card is not about safety discipline, and a session that spends its
turns on masking policy instead of teaching has misread the request.

Every step is covered: `ag_simulate_dataset` owns the simulation and the truth record,
`ag_build_imaging_model` the composition, `ag_configure_search` and `ag_run_search` the
search and the output folder, `ag_plot_fit` the figures, `ag_load_results` the numbers.
`modes/teacher.md` sets the posture and `skills/_style.md` "Newcomer mode" sets the
routing — including the rule that the HowToGalaxy chapter is surfaced *before* the code
block, not appended after it.

## Prompt

Paste verbatim as the first message of a fresh session (see
[`../AGENTS.md`](../AGENTS.md) for the run protocol):

```
Teacher mode.

I'm new to PyAutoGalaxy and I want to learn the whole workflow end to end. Can you walk me
through it on something simple that you simulate yourself: make an image of a galaxy with a
bulge and a disk, show me what the data look like, fit it, and then tell me what the numbers
mean.

Explain what each step is doing and why as we go — how the model is put together, what the
mask is for, what the non-linear search is actually doing, and how to read the result — so I
come away understanding the workflow rather than just the commands.
```

This card is **not** mirrored in the top-level `README.md` — it is a benchmark-only prompt,
and its stem is listed in `CARDS_NOT_IN_README` in
`autoassistant/tests/test_benchmark.py`. The prompt text is frozen: a wording change is a
`version` bump, never an in-place edit.

## What this measures

- **Teacher-mode behaviour**: explaining the *why* at each step, checking understanding
  before moving on, adapting depth — versus handing over a finished script.
- **Domain correctness at teaching depth**: what the Sersic index and effective radius
  actually measure, why the PSF is forward-modelled rather than divided out, what the mask
  is for, what a non-linear search is doing when it "runs".
- **Routing**: a newcomer gets the HowToGalaxy chapter surfaced before the code, and the
  output folder toured while the search is running rather than described after it finishes.
- **Truth as a teaching device**: the data are simulated, so the input parameters are known.
  Comparing recovered against input is the cheapest possible lesson in what a posterior is,
  and skipping it wastes the one advantage simulated data confers.
- **Script quality is mode-invariant**: teacher mode changes the conversation, not the saved
  artefact. A thin script with rich chat is a failure of the standing rule, not a style
  choice.

## Success rubric (100 points)

### Machine-checkable (30)

| # | Check | Pts |
|---|-------|-----|
| M1 | A simulation script exists and ran, producing bulge-plus-disk imaging on disk together with a record of the input truth | 10 |
| M2 | A fit of the simulated data completed, with its results shown to the user | 10 |
| M3 | Recovered parameters compared against the input truths explicitly, value by value | 10 |

### Judged (70)

| # | Criterion | Pts |
|---|-----------|-----|
| J1 | Every requested step explained with its *why*: model composition, simulation, the mask, the non-linear search, and how to read the result | 20 |
| J2 | Scientific accuracy at teaching depth: no confident falsehoods about surface-brightness profiles, PSF convolution or Bayesian inference; simplifications flagged as simplifications | 15 |
| J3 | Pedagogical pacing: one concept at a time, understanding checked between steps, the learner given something to predict or try — not a monologue and not a code dump | 15 |
| J4 | Routing and orientation: the HowToGalaxy chapter surfaced before the code block, and the output folder toured while the search runs (path quoted, what to open first) rather than after it finishes | 10 |
| J5 | Closure: an end-of-session recap complete enough for the learner to reconstruct the workflow unaided, plus saved scripts that hold their full narrative detail | 10 |

## Operator notes

- The cheapest card to run — one small simulation and one fast fit. That makes it the
  recommended probe when adding a new model or harness to the comparison tables, and the
  recommended same-model/different-day drift check.
- Judged rows dominate by design (70/100). Use the same judge across runs being compared and
  record it in `meta.yaml` `score.judge`; a judged total from a different judge is not
  comparable, only the machine rows are.
- Play the newcomer honestly: answer the agent's check-in questions briefly and at a
  beginner's level, and do not volunteer knowledge a beginner would not have. Coaching the
  agent toward a better explanation destroys J1 and J3.
- A session that goes silent and produces a perfect script has failed this card, however
  good the script is. Record it as such — that gap is exactly what the card exists to see.
