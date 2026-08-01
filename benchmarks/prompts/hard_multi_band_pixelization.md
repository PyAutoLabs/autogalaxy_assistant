---
id: assistant-hard-multi-band-pixelization
version: 1
mode: assistant
difficulty: hard
datasets: []          # fully simulated — the session generates both datasets
workspace_packages:
  - imaging
  - multi_dataset
added: 2026-08-01
---

# Benchmark: two bands, one pixelised galaxy (assistant · hard)

Deliberately not reachable from any single skill. The agent has to compose three of them and
keep the seams straight:

- `ag_simulate_dataset` for two datasets of the *same* galaxy with a wavelength-dependent
  clump population and a saved truth record;
- `ag_multi_dataset` for the `af.AnalysisFactor` + `af.FactorGraphModel` construction that is
  the only way to fit them simultaneously — including its "a pixelised component across
  bands" branch, which is the exact case this card lands on;
- `ag_pixelization` for the hybrid linear-Sersic-plus-mesh model, the regularization
  diagnostics, the evidence terms, and exporting the reconstruction.

The hard part is not the API. It is that a pixelised reconstruction will happily reproduce
whatever you ask it to, so the interesting question — *did the clumps I simulated come back,
or did the regularization invent a smooth version of them?* — is answerable only if the agent
sets up the comparison honestly. This is the same failure mode a real user meets the first
time a reconstruction looks beautiful and means nothing.

## Prompt

Paste verbatim as the first message of a fresh session (see
[`../AGENTS.md`](../AGENTS.md) for the run protocol):

```
Assistant mode.

Simulate JWST-like imaging of a clumpy star-forming galaxy in two wavebands — a smooth
Sersic bulge plus three off-centre clumps, with the clumps much brighter in the bluer band
than in the redder one. Then fit both datasets simultaneously with a single model: a linear
Sersic bulge and a pixelized reconstruction for everything the bulge cannot explain.

Once it has run, export the reconstruction and tell me whether the clumps I put in are the
clumps that came out — and where the reconstruction is telling me about the galaxy rather
than about the regularization I chose.
```

This card is **not** mirrored in the top-level `README.md` — it is a benchmark-only prompt,
and its stem is listed in `CARDS_NOT_IN_README` in
`autoassistant/tests/test_benchmark.py`. The prompt text is frozen: a wording change is a
`version` bump, never an in-place edit.

## What this measures

- **Cross-skill synthesis**: simulation × multi-dataset joint analysis × pixelised
  reconstruction, in one session, without any one of the three overwriting the conventions
  of the others.
- **Joint-fit wiring**: one model, two `af.AnalysisFactor`s, one search — not two fits whose
  answers are averaged afterwards. Which parameters are shared across bands and which are
  freed per band is a decision the agent must make and justify, and the pixelised branch has
  its own answer for the regularization coefficient.
- **Simulation judgment**: three clumps are only recoverable if they are separated by more
  than the PSF at the chosen pixel scale. An agent that picks a configuration where the
  question is unanswerable has failed the card before the fit starts.
- **Reading a reconstruction rather than admiring it**: over- and under-regularization both
  have signatures in the reconstruction itself, and the evidence terms say which side of the
  trade the fit landed on.
- **Truth discipline**: everything is simulated, so the input clump positions and fluxes are
  known. A truth-vs-recovered statement is available; a vague one is a choice.

## Success rubric (100 points)

### Machine-checkable (45)

| # | Check | Pts |
|---|-------|-----|
| M1 | Two simulated imaging datasets of the same galaxy in two bands exist on disk, with a saved truth record of the input galaxy | 10 |
| M2 | A single joint fit completed over both datasets via `af.AnalysisFactor` + `af.FactorGraphModel` — one search over a shared model, not two independent fits | 15 |
| M3 | The model pairs a linear Sersic bulge with an `ag.Pixelization` component, verifiable in the script | 5 |
| M4 | The reconstruction was exported to a file **outside** `output/`, and its path was shown to the user | 5 |
| M5 | Per-band fit subplots were produced and their paths shown | 5 |
| M6 | An explicit truth-vs-recovered comparison for the clumps is presented (positions and relative brightness, per band) | 5 |

### Judged (55)

| # | Criterion | Pts |
|---|-----------|-----|
| J1 | Simulation quality: pixel scale, PSF and clump separation chosen so the clumps are genuinely resolvable, the wavelength dependence physically motivated (young clumps bluer than the spheroid), and the result verified by plotting rather than assumed | 10 |
| J2 | Joint-analysis wiring correct and explained: what is shared across bands versus freed per band, why, and the regularization coefficient handled as the multi-dataset pixelised case requires | 15 |
| J3 | The reconstruction is read honestly: over- versus under-regularization diagnosed from the reconstruction and residuals, the evidence terms cited for the trade, and the answer to "galaxy or regularization?" argued rather than asserted | 15 |
| J4 | Cost discipline: run time and memory anticipated before committing, and the script proved structurally (test mode, or a coarse mesh first) before paying for the full fit | 5 |
| J5 | Conduct: a staged plan communicated up front, honest reporting of any stage that failed or was cut short, API-gate discipline, no fabricated numbers | 10 |

## Operator notes

- The heaviest card in the suite: two simulations plus a joint pixelised search. Expect hours
  on a laptop; a GPU changes the picture substantially. **Partial completions are recorded
  and scored for what completed** — a run that simulates well, wires the joint fit correctly
  and then runs out of time still earns most of M1–M3 and J1–J2.
- Because everything is simulated the run is self-contained and reproducible: the truths are
  known, so M6 and J3 are checkable against them rather than against the agent's confidence.
- A tempting shortcut is fitting the two bands one at a time and presenting the pair as a
  joint result. M2 exists to catch it; check the script for one `search.fit` over a factor
  graph, not two.
- Do not suggest a mesh, a regularization scheme, or a clump geometry. Those choices are J1
  and J3.
