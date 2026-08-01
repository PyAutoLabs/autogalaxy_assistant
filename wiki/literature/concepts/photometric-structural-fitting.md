---
title: Photometric structural fitting
type: concept
topics: [structural-fitting, software, inference]
sources:
  - Peng 2002 — GALFIT
  - Simard 2002 — GIM2D structural parameters
  - Erwin 2015 — Imfit
  - Robotham 2017 — ProFit
  - Haussler 2007 — testing GALFIT and GIM2D
  - Nightingale 2023 — PyAutoGalaxy
status: drafted
---

# Photometric structural fitting

## TL;DR

Photometric structural fitting means forward-modelling a galaxy image: build a
parametric surface-brightness model, convolve it with the PSF, compare it to the
data pixel by pixel under a noise model, and infer the parameters. The field's
tooling has moved through three generations — deterministic
`chi^2` minimisers (GIM2D, GALFIT), pipeline wrappers that made them run on whole
surveys (GALAPAGOS, MegaMorph/GALFITM), and Bayesian forward-modelling codes that
return posteriors rather than best-fit points (GALPHAT, ProFit, PyAutoGalaxy,
pysersic, AstroPhot). The generational shift matters because the structural
parameter space is degenerate: `n`, `R_e`, sky and PSF trade against one another,
and a point estimate cannot express that while a posterior can.

## What it is

Every code in the lineage implements the same core loop:

```
model params -> surface brightness on an (over-sampled) grid
             -> convolve with PSF
             -> bin to pixel scale, apply mask
             -> compare to data with a noise map -> likelihood
             -> optimiser or sampler proposes new params
```

The differences that matter in practice:

- **Point estimate vs posterior.** Levenberg-Marquardt returns a best fit and a
  covariance matrix that assumes local Gaussianity. That assumption fails exactly
  where structural fitting is hard: bulge-disc degeneracy, `n`-sky degeneracy,
  multimodality. Nested sampling or MCMC returns the shape of the degeneracy and,
  in the nested case, a Bayesian evidence for comparing models with different
  component counts.
- **Linear vs sampled amplitudes.** Component intensities enter the model
  linearly, so they can be solved exactly at each likelihood evaluation instead of
  sampled. This removes the most strongly covariant parameters from the search.
- **Single-band vs simultaneous multi-band.** Fitting bands independently produces
  structural parameters that scatter unphysically with wavelength; tying them with
  a smooth function of wavelength (the MegaMorph approach) uses all the data at
  once and yields meaningful component colours.
- **Over-sampling and PSF handling.** The model must be evaluated finely enough
  that the pixel-integrated surface brightness is accurate in the steep central
  region, and convolved with a PSF sampled at least as finely.
  [[point-spread-function]] covers the second; over-sampling is documented in
  [`wiki/core/concepts/grids_and_masks.md`](../../core/concepts/grids_and_masks.md).
- **Sky treatment.** Fitting the sky level simultaneously with the profile, versus
  fixing it from a prior measurement, is the single largest fork in the road for
  `n` and `R_e` ([[sky-subtraction-and-photometry]]).

**What a structural catalogue is.** Every large structural catalogue is a set of
fits plus a set of decisions. Two catalogues of the same SDSS galaxies can differ
systematically because one fixed `n = 4` for the bulge and the other did not, or
because one used a global sky and the other a local one. Cross-catalogue comparison
is the field's standard error estimate — it is usually larger than the quoted
statistical errors.

## Why it matters for PyAutoGalaxy

PyAutoGalaxy sits in the Bayesian forward-modelling generation, built on the
PyAutoFit probabilistic programming layer:

- Model composition, priors and the analysis/likelihood objects:
  [`wiki/core/api/analysis_objects.md`](../../core/api/analysis_objects.md).
- Samplers and optimisers, including when nested sampling versus a gradient method
  is appropriate: [`wiki/core/api/searches.md`](../../core/api/searches.md) and
  [`wiki/core/concepts/non_linear_search.md`](../../core/concepts/non_linear_search.md).
- Search chaining — fitting a simple model first and using its result to initialise
  a complex one — which is how multi-component fits are made tractable.
- Linear light profiles, which solve component amplitudes analytically:
  [`wiki/core/concepts/linear_light_profiles_and_mge.md`](../../core/concepts/linear_light_profiles_and_mge.md).
- Model comparison by Bayesian evidence rather than by `chi^2` improvement, which is
  the principled answer to "does this galaxy need a second component?".

## Key results from the literature

- Simard and others (2002) introduced the GIM2D structural parameters for the DEEP
  Groth Strip Survey — one of the first automated two-dimensional bulge+disc fits
  applied to a survey ([[sources-light-profile-fitting]]).
- Peng and others (2002) released GALFIT, which became the field's default fitting
  engine; Peng and others (2010) extended it to non-axisymmetric models — Fourier
  modes, bending modes, coordinate rotation — allowing spiral arms and lopsidedness
  to be fitted parametrically ([[sources-light-profile-fitting]]).
- Häussler and others (2007) tested GALFIT and GIM2D against simulated and real
  GEMS data, quantifying where each biases and how much of the difference between
  catalogues is code rather than data ([[sources-light-profile-fitting]]).
- Barden and others (2012) released GALAPAGOS, the pipeline layer (source
  detection, cutout generation, neighbour handling, batch fitting) that made
  survey-scale GALFIT runs reproducible ([[sources-light-profile-fitting]]).
- Häussler and others (2013) and Vika and others (2013, 2014) built the MegaMorph
  extension: simultaneous multi-band Sersic and bulge-disc fitting with parameters
  tied by wavelength ([[bulge-disk-decomposition]]).
- Yoon, Weinberg & Katz (2011) built GALPHAT, an explicitly Bayesian Sersic fitter,
  and benchmarked how much the posterior differs from a Levenberg-Marquardt
  covariance ([[sources-light-profile-fitting]]).
- Erwin (2015) released Imfit — fast, flexible, with a large library of
  two-dimensional components including bars, rings and truncated discs; Robotham
  and others (2017) released ProFit, a Bayesian profile fitter with MCMC sampling
  ([[sources-light-profile-fitting]]).
- Nightingale, Hayes & Griffiths (2021) described PyAutoFit, the probabilistic
  programming layer; Nightingale and others (2023) described PyAutoGalaxy itself —
  Bayesian multiwavelength galaxy structure and morphology, including hierarchical
  fitting of large samples ([[sources-light-profile-fitting]]).
- Pasha & Miller (2023) released pysersic (Bayesian Sersic fitting accelerated with
  JAX) and Stone and others (2023) released AstroPhot (gradient-based fitting of
  many objects and many images at once) — the current generation, in which
  automatic differentiation rather than sampler cleverness supplies the speed
  ([[sources-light-profile-fitting]]).
- Skilling (2006) introduced nested sampling and Speagle (2020) the widely used
  `dynesty` implementation; these supply the evidence estimates that make component
  counting a model-comparison question ([[sources-light-profile-fitting]]).
- Simard and others (2011), Lackner & Gunn (2012), Meert and others (2015) and
  Kelvin and others (2012) are the large structural catalogues whose mutual
  disagreements calibrate how much model choice matters
  ([[sources-bulge-disk-decomposition]]).

## See also

- [[sersic-profile]]
- [[bulge-disk-decomposition]]
- [[multi-gaussian-expansion]]
- [[point-spread-function]]
- [[sky-subtraction-and-photometry]]
- [[isophote-analysis]]
- [[sources-light-profile-fitting]]
