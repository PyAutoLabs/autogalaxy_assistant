---
id: assistant-medium-mge-bulge-disk
version: 1
mode: assistant
difficulty: medium
datasets:
  - dataset/imaging/cosj100020+015344
workspace_packages:
  - imaging
added: 2026-08-01
---

# Benchmark: is it two components or one? (assistant · medium)

The easy card asks the agent to *run* the built-in workflow. This one asks it to **decide
something with the workflow** — a Bayesian model comparison between a two-component
decomposition and a multi-Gaussian expansion, on the same bundled JWST cutout, in two
wavebands whose pixel scales differ by a factor of two.

Every ingredient is covered by a live skill: `ag_basis_profiles` owns both the linear
bulge-plus-disk decomposition and the MGE, `ag_light_model_extras` owns the free sky,
`ag_configure_search` owns the choice of a search that actually produces a Bayesian evidence,
and `ag_load_results` owns reading `samples.log_evidence` back out. Nothing here needs
inventing. What is *not* handed over is the judgement: which comparison is legitimate, how
much of a ∆log Z gap survives a model PSF, and whether "the data prefer two components"
is a statement about the galaxy or about the fit.

The card also carries a quiet trap the prompt does not mention. The sky in this data is
**not subtracted** (`info.json` `background_sky_level_per_band`, and the dataset README says
so). An agent that leaves it out inflates the effective radius and Sersic index of whichever
model is more extended — which is exactly the axis the comparison runs along, so the trap
does not merely cost accuracy, it corrupts the answer. The easy card states the sky in its
prompt; this one does not.

## Prompt

Paste verbatim as the first message of a fresh session (see
[`../AGENTS.md`](../AGENTS.md) for the run protocol):

```
Assistant mode.

I want to know whether COSJ100020+015344 is genuinely a two-component galaxy or just one
smooth spheroid. Using the bundled dataset in dataset/imaging/cosj100020+015344, fit both
the F150W and the F277W band twice: once with a Sersic bulge plus an Exponential disk, and
once with a multi-Gaussian expansion. Tell me which model the data prefer in each band,
quote the Bayesian evidence you are comparing, and say how much of that difference you
actually believe. If the two-component model wins, give me the bulge-to-total light ratio
in both bands.
```

This card is **not** mirrored in the top-level `README.md` — it is a benchmark-only prompt,
and its stem is listed in `CARDS_NOT_IN_README` in
`autoassistant/tests/test_benchmark.py`. Like every published card the prompt text is
frozen: a wording change is a `version` bump, never an in-place edit.

## What this measures

- **Composing two competing models, not one**: the linear bulge-plus-disk pair and the MGE
  are different constructions of the same `af.Collection` tree, and the agent has to build
  both correctly rather than fitting one and describing the other.
- **Knowing what a Bayesian evidence requires**: a MAP optimiser returns no `log_evidence`.
  Choosing the search that yields one, and saying why, is the inference half of the card.
- **Finding the sky without being told.** The prompt is silent about it; the dataset is not.
- **Two bands, two pixel scales.** F150W is 0.03"/pixel and F277W is 0.06"/pixel. A mask
  radius copied between them changes the physical aperture, and the PSF width changes with
  wavelength independently of anything the galaxy is doing — so a size difference between
  bands is not automatically a colour gradient.
- **Honesty about the ceiling.** The shipped PSFs are models, not empirical stars. A
  decomposition is PSF-limited at exactly the scale that separates a bulge from a disk.

## Success rubric (100 points)

### Machine-checkable (40)

| # | Check | Pts |
|---|-------|-----|
| M1 | A script (or scripts) saved under `scripts/` that performs all four fits | 5 |
| M2 | Four completed non-linear search results exist under `output/` — two models × two bands, none of them test-mode | 10 |
| M3 | The two-component model uses **linear** light profiles (`ag.lp_linear`), verifiable in the script | 5 |
| M4 | The MGE model is composed with the basis idiom from `ag_basis_profiles` (`ag.model_util.mge_model_from` or an explicit `ag.lp_basis.Basis`), not a hand-listed set of free-intensity Gaussians | 5 |
| M5 | Every fit includes a free background sky level, verifiable in the script | 5 |
| M6 | A Bayesian evidence is reported for each of the four fits, sourced from the samples rather than asserted | 5 |
| M7 | Bulge-to-total light ratios reported for both bands, or the ratio explicitly declared inapplicable because the decomposition lost | 5 |

### Judged (60)

| # | Criterion | Pts |
|---|-----------|-----|
| J1 | Real-data gate honoured: both bands plotted and inspected, and **both** questions settled before any fit — contaminants (the faint 2.6" neighbour) and the mask extent, with the radius justified rather than defaulted | 15 |
| J2 | The un-subtracted sky is discovered from the dataset's own metadata without being prompted, and its effect on the comparison — not just on the fit — is explained | 10 |
| J3 | The evidence comparison is legitimate: a search that produces an evidence was chosen and said to be why, the two models are compared over the same data and mask, and the size of ∆log Z is interpreted rather than merely quoted | 15 |
| J4 | The two pixel scales are handled deliberately — one physical aperture across bands rather than one pixel count — and the wavelength-dependent PSF is separated from any recovered size difference | 10 |
| J5 | Conduct: concise assistant-mode communication with the pre-flight read-back, honest reporting if a fit is poor or a model does not converge, API-gate discipline, no fabricated numbers | 10 |

## Operator notes

- Expected wall-clock: hours rather than minutes — four nested-sampling runs. An agent that
  proposes a cheaper staged route (a fast MAP pass to sanity-check the composition, then the
  evidence-bearing runs) is being sensible; the rubric only requires that the *quoted*
  evidences come from runs that can produce one.
- The correct scientific answer is not fixed in advance and the card does not assume one.
  An agent that decomposes the galaxy, finds the disk is marginal, and says so scores J3
  fully; an agent that finds a decisive result it cannot justify does not.
- Do not coach toward the sky, the neighbour, or the pixel-scale difference. Finding them is
  J1, J2 and J4.
