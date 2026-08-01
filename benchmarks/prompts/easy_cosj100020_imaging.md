---
id: assistant-easy-cosj100020-imaging
version: 1
mode: assistant
difficulty: easy
datasets:
  - dataset/imaging/cosj100020+015344
workspace_packages:
  - imaging
added: 2026-08-01
---

# Benchmark: measure the bundled JWST galaxy's structure (assistant · easy)

Almost everything this prompt asks for is directly available in the assistant: the dataset
ships with the repository, and data preparation, model composition, search configuration,
running the fit, plotting it and reading the result are all covered by existing core-loop
`ag_*` skills. A capable agent should complete it without inventing anything — the benchmark
measures whether it *finds and follows* the built-in workflow rather than writing
PyAutoGalaxy from memory.

One deliberate exception makes this card worth running even though it is the easy one: the
**dedicated MGE skill is still pending** (Phase 4b in [`../../PENDING.md`](../../PENDING.md)).
The feature itself exists in the library and is documented in the reference wiki
(`concepts/linear_light_profiles_and_mge.md`, `api/light_profile_catalog.md`) and in
`autogalaxy_workspace:scripts/imaging/features/multi_gaussian_expansion/`. So the card also
measures whether the agent grounds a feature that has no procedural skill in the wiki and the
workspace examples — and says that is what it did — instead of reconstructing an MGE from
training data.

## Prompt

Paste verbatim as the first message of a fresh session (see
[`../AGENTS.md`](../AGENTS.md) for the run protocol):

```
Assistant mode.

Fit the JWST F277W imaging in dataset/imaging/cosj100020+015344 with a multi-Gaussian
expansion (MGE) bulge, freeing the background sky level — the sky is not subtracted in
this data. Report the effective radius, axis ratio and position angle, add a single-Sersic
fit so I get a Sersic index to compare against, and then tell me how the recovered
structure changes across the other three wavebands.
```

This is Starter Prompt 2 of the top-level [`README.md`](../../README.md); the two texts must
stay identical (a divergence is a bug — fix the README or bump this card's `version`).
`autoassistant/tests/test_benchmark.py::test_repo_readme_prompts_match_cards` enforces it.

## What this measures

- **Routing**: does the agent use the assistant's skills, bundled dataset and reference wiki
  rather than writing PyAutoGalaxy from memory?
- **The real-data safety gate**: plotting and inspecting the data, and settling both the
  contaminant question and the mask extent, *before* composing any fit.
- **Reading the dataset's own caveats**: the un-subtracted sky is stated in the prompt, but
  the faint 2.6" neighbour and the model-PSF systematic are not — they are in the dataset
  README, and a good run finds them.
- **A complete run**: preparation → model → search → fit → the requested numbers, across
  four wavebands.

## Success rubric (100 points)

### Machine-checkable (40)

| # | Check | Pts |
|---|-------|-----|
| M1 | A script (or scripts) saved under `scripts/` that performs the fit | 5 |
| M2 | A completed non-linear search result exists under `output/` (not test-mode) | 10 |
| M3 | The model includes an MGE basis for the bulge **and** a free background sky level, both verifiable in the script | 10 |
| M4 | A single-Sersic comparison fit exists, with its own result under `output/` | 5 |
| M5 | A fit subplot figure was produced and its path shown to the user | 5 |
| M6 | The other three wavebands were fitted or measured, with per-band numbers reported | 5 |

### Judged (60)

| # | Criterion | Pts |
|---|-----------|-----|
| J1 | Real-data gate honoured: dataset plotted and inspected, and **both** questions settled before any fit — contaminants (the faint 2.6" neighbour) and the mask extent, with the chosen radius justified rather than left as a default | 15 |
| J2 | The sky pedestal is handled as the prompt asks and the agent explains the consequence of not doing so (it inflates the effective radius and Sersic index); the recovered level is sane against the dataset's measured value | 10 |
| J3 | Sensible model and priors for this galaxy; the MGE is grounded in the reference wiki or a workspace example and the agent says so, rather than recalled from memory | 10 |
| J4 | The requested quantities are all reported, and the agent is honest that `info.json`'s `effective_radius_arcsec_rough` is a prior-scale measurement rather than ground truth to be matched | 10 |
| J5 | The multi-band comparison is scientifically framed — the size trend with wavelength separated from the changing PSF width — and the shipped model PSF is acknowledged as the dominant systematic | 10 |
| J6 | Conduct: concise assistant-mode communication, no fabricated numbers, API-gate discipline (no invented symbols, functional `aplt` plotting) | 5 |

## Operator notes

- Expected wall-clock: roughly 15–60 minutes depending on hardware and the search chosen;
  the non-linear searches dominate. Five fits are implied by the prompt (MGE + Sersic on
  F277W, then three further bands), so an agent that proposes a cheaper route — a maximum
  likelihood optimiser, or reusing priors across bands — is being sensible, not lazy.
- The galaxy is bright (peak S/N 180 at F277W) and smooth, so a poor fit is a modelling
  problem rather than a data problem. A run that ends with the agent honestly reporting a
  poor fit scores what the rubric gives it — record it; failures are data.
- Do not coach the agent toward the neighbour or the PSF caveat. Finding them is J1 and J5.
