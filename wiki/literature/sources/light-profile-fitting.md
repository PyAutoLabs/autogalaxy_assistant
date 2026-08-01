---
title: Sources — light-profile fitting
type: sources
topics: [light-profiles, structural-fitting, software]
status: drafted
---

# Sources: light-profile fitting

The formalism behind the profiles a galaxy's light is fitted with, the codes that do the
fitting, and the papers that measure how much the answer depends on how you fit.

## de Vaucouleurs 1948 — the R^(1/4) law

**Canonical BibTeX key:** `deVaucouleurs1948`
**Reference:** de Vaucouleurs 1948, Annales d'Astrophysique 11, 247 — "Recherches sur les
Nébuleuses Extragalactiques" (ADS: 1948AnAp...11..247D)
**Concepts:** [[sersic-profile]], [[early-type-galaxy-structure]]

**Supports:**
- Elliptical galaxy surface-brightness profiles follow an R^(1/4) law.

**Use when:**
- Citing the origin of the de Vaucouleurs profile, i.e. the Sersic profile with n = 4.

**Do not use for:**
- The generalised R^(1/n) law — that is Sersic.

## Sersic 1968 — the R^(1/n) law

**Canonical BibTeX key:** `Sersic1968`
**Reference:** Sersic 1968, "Atlas de Galaxias Australes", Observatorio Astronomico,
Universidad Nacional de Cordoba (ADS: 1968adga.book.....S)
**Concepts:** [[sersic-profile]], [[photometric-structural-fitting]]

**Supports:**
- The generalisation of the R^(1/4) law to a free index n — the profile essentially all
  parametric galaxy fitting is built on.

**Use when:**
- Citing the Sersic profile itself. This is the canonical citation.

**Do not use for:**
- Analytical relations between n, the effective radius and the total flux — cite Ciotti &
  Bertin or Graham & Driver.

## Ciotti 1999 — analytical properties of the R^(1/m) law

**Canonical BibTeX key:** `Ciotti1999`
**Reference:** arXiv:astro-ph/9911078, A&A 352, 447 — "Analytical properties of the R^(1/m)
luminosity law"
**Concepts:** [[sersic-profile]]

**Supports:**
- Analytical results for the Sersic law, including accurate expressions for the b(n)
  normalisation that relates the effective radius to the half-light condition.

**Use when:**
- You need the mathematics of the profile — total luminosity, b(n), asymptotic behaviour.

**Do not use for:**
- Observational claims about galaxies.

## Graham 2005 — a concise reference to Sersic quantities

**Canonical BibTeX key:** `Graham2005`
**Reference:** arXiv:astro-ph/0503176, PASA 22, 118 — "A concise reference to (projected)
Sersic R^{1/n} quantities, including Concentration, Profile Slopes, Petrosian indices, and
Kron Magnitudes"
**Concepts:** [[sersic-profile]], [[photometric-structural-fitting]]

**Supports:**
- Conversions between Sersic parameters and the derived quantities people actually quote:
  concentration, profile slope, Petrosian index, Kron magnitude.

**Use when:**
- Translating a fitted Sersic model into a catalogue-style measurement, or vice versa.

**Do not use for:**
- The fitting procedure itself.

## Trujillo 2001 — the effects of seeing on Sersic profiles

**Canonical BibTeX key:** `Trujillo2001`
**Reference:** arXiv:astro-ph/0009097, MNRAS 321, 269 — "The effects of seeing on Sérsic
profiles"
**Concepts:** [[point-spread-function]], [[sersic-profile]]

**Supports:**
- Seeing systematically biases the recovered Sersic index and effective radius when it is
  not modelled.
- The size of that bias as a function of the ratio of the PSF width to the effective radius.

**Use when:**
- Explaining why the PSF must be convolved into the model rather than corrected for
  afterwards, or judging whether a galaxy is resolved enough to fit.

**Do not use for:**
- A Moffat PSF specifically — that is the Part II paper (arXiv:astro-ph/0109067).

## Emsellem 1994 — the multi-Gaussian expansion method

**Canonical BibTeX key:** `Emsellem1994`
**Reference:** Emsellem, Monnet & Bacon 1994, A&A 285, 723 — "The multi-Gaussian expansion
method: a tool for building realistic photometric and kinematical models of stellar systems
I. The formalism" (ADS: 1994A&A...285..723E)
**Concepts:** [[multi-gaussian-expansion]], [[photometric-structural-fitting]]

**Supports:**
- Representing a galaxy's surface brightness as a sum of Gaussians, which makes both the
  PSF convolution and the deprojection analytic.
- The formalism linking the photometric model to a kinematic one.

**Use when:**
- Citing the origin of MGE, or justifying MGE as a flexible alternative to a fixed
  parametric profile.

**Do not use for:**
- The fitting algorithm that determines the Gaussians — cite Cappellari 2002.

## Cappellari 2002 — efficient MGE fitting

**Canonical BibTeX key:** `Cappellari2002`
**Reference:** arXiv:astro-ph/0201430, MNRAS 333, 400 — "Efficient Multi-Gaussian Expansion
of galaxies"
**Concepts:** [[multi-gaussian-expansion]]

**Supports:**
- A practical algorithm for fitting an MGE to a galaxy image, including how the Gaussian
  widths are chosen.

**Use when:**
- Describing how an MGE model is actually constructed in practice.

**Do not use for:**
- Claims that MGE components are physically distinct structures — they are basis functions.

## Peng 2002 — GALFIT

**Canonical BibTeX key:** `Peng2002`
**Reference:** arXiv:astro-ph/0204182, AJ 124, 266 — "Detailed Structural Decomposition of
Galaxy Images"
**Concepts:** [[photometric-structural-fitting]], [[bulge-disk-decomposition]]

**Supports:**
- Two-dimensional, PSF-convolved, multi-component parametric fitting of galaxy images
  (GALFIT), minimising chi-squared over the image pixels.

**Use when:**
- Citing the standard forward-modelling approach to structural fitting, or the code most
  published structural catalogues were made with.

**Do not use for:**
- Bayesian posteriors — GALFIT is an optimiser, not a sampler.

## Peng 2010 — GALFIT beyond axisymmetric models

**Canonical BibTeX key:** `Peng2010`
**Reference:** arXiv:0912.0731, AJ 139, 2097, doi:10.1088/0004-6256/139/6/2097 — "Detailed
Decomposition of Galaxy Images. II. Beyond Axisymmetric Models"
**Concepts:** [[photometric-structural-fitting]], [[isophote-analysis]]

**Supports:**
- Extending parametric fitting beyond pure ellipses: Fourier (multipole) modes, bending
  modes, coordinate rotations and truncation functions.

**Use when:**
- Motivating multipole or boxy/discy terms in a parametric model rather than in an isophote
  analysis.

**Do not use for:**
- The original GALFIT formulation — cite Peng 2002.

## Erwin 2015 — Imfit

**Canonical BibTeX key:** `Erwin2015`
**Reference:** arXiv:1408.1097, ApJ 799, 226, doi:10.1088/0004-637X/799/2/226 — "Imfit: A
Fast, Flexible New Program for Astronomical Image Fitting"
**Concepts:** [[photometric-structural-fitting]]

**Supports:**
- An open-source 2D image-fitting program with a modular component library, supporting
  different minimisation algorithms and Poisson-appropriate statistics.

**Use when:**
- Comparing fitting codes, or citing a non-GALFIT alternative.

**Do not use for:**
- Claims about a specific published catalogue.

## Robotham 2017 — ProFit

**Canonical BibTeX key:** `Robotham2017`
**Reference:** arXiv:1611.08586, MNRAS 466, 1513, doi:10.1093/mnras/stw3039 — "ProFit:
Bayesian Profile Fitting of Galaxy Images"
**Concepts:** [[photometric-structural-fitting]]

**Supports:**
- Bayesian profile fitting of galaxy images with MCMC posterior sampling rather than
  point-estimate optimisation.

**Use when:**
- Arguing that structural parameters need uncertainties and covariances, not just best-fit
  values — the same argument PyAutoGalaxy's sampler-based approach rests on.

**Do not use for:**
- Large legacy catalogues, which predate it.

## Haeussler 2007 — testing parametric fitting codes

**Canonical BibTeX key:** `Haussler2007`
**Reference:** arXiv:0704.2601, ApJS 172, 615, doi:10.1086/518836 — "GEMS: Galaxy Fitting
Catalogs and Testing Parametric Galaxy Fitting Codes: GALFIT and GIM2D"
**Concepts:** [[photometric-structural-fitting]], [[sky-subtraction-and-photometry]]

**Supports:**
- A controlled comparison of two independent fitting codes on the same simulated and real
  data, quantifying where each is reliable.
- Sensitivity of recovered parameters to the treatment of neighbouring sources and the sky.

**Use when:**
- Justifying a simulation-based test of your own fitting setup before trusting it.

**Do not use for:**
- Modern Bayesian codes, which are not covered.

## Haeussler 2013 — multi-wavelength structural fitting

**Canonical BibTeX key:** `Haussler2013`
**Reference:** arXiv:1212.3332, MNRAS 430, 330 — "MegaMorph – multiwavelength measurement of
galaxy structure: Complete Sérsic profile information from modern surveys"
**Concepts:** [[photometric-structural-fitting]], [[point-spread-function]]

**Supports:**
- Fitting all available bands simultaneously, with structural parameters allowed to vary
  smoothly with wavelength, improves the precision and stability of the fit relative to
  independent per-band fits.

**Use when:**
- Justifying a joint multi-band fit — directly relevant to any four-band NIRCam dataset.

**Do not use for:**
- A claim about which wavelength dependence is physically correct.

## Bernardi 2013 — the fitted profile changes the mass function

**Canonical BibTeX key:** `Bernardi2013`
**Reference:** arXiv:1304.7778, doi:10.1093/mnras/stt1607 — "The massive end of the
luminosity and stellar mass functions: Dependence on the fit to the light profile"
**Concepts:** [[photometric-structural-fitting]], [[stellar-mass-estimates]],
[[galaxy-scaling-relations]]

**Supports:**
- The high-mass end of the luminosity and stellar-mass functions depends significantly on
  which light profile is fitted to the galaxies.

**Use when:**
- Making the case that a structural-fitting choice has downstream astrophysical consequences.

**Do not use for:**
- A claim that one profile family is definitively correct.

## Fischer 2017 — sky background and model fitting effects

**Canonical BibTeX key:** `Fischer2017`
**Reference:** arXiv:1702.08526, doi:10.1093/mnras/stx136 — "Comparing PyMorph and SDSS
photometry. I. Background sky and model fitting effects"
**Concepts:** [[sky-subtraction-and-photometry]], [[photometric-structural-fitting]]

**Supports:**
- Differences between independent photometric pipelines for the same galaxies trace largely
  to background-sky estimation and to the fitted model.

**Use when:**
- Explaining why two catalogues disagree about the same galaxy, or why the sky must be
  fitted rather than assumed.

**Do not use for:**
- Concluding which pipeline is right — that is the companion paper's argument.

## Bernardi 2017 — two pipelines, two answers

**Canonical BibTeX key:** `Bernardi2017`
**Reference:** arXiv:1702.08527, doi:10.1093/mnras/stx677 — "Comparing PyMorph and SDSS
photometry. II. The differences are more than semantics and are not dominated by intracluster
light"
**Concepts:** [[photometric-structural-fitting]], [[sky-subtraction-and-photometry]],
[[sdss]]

**Supports:**
- The disagreement between two independent photometric pipelines applied to the same SDSS
  galaxies is real and systematic, not a matter of definitions.
- It is not explained by intracluster light contaminating the outer profile.

**Use when:**
- Arguing that "which catalogue did you use?" is a scientific question, not a bookkeeping one.

**Do not use for:**
- The background-sky mechanism specifically — that is Paper I (Fischer 2017).

## Nightingale 2023 — PyAutoGalaxy

**Canonical BibTeX key:** `Nightingale2023`
**Reference:** Nightingale and others 2023, JOSS 8(81), 4475, doi:10.21105/joss.04475 —
"PyAutoGalaxy: Open-Source Multiwavelength Galaxy Structure & Morphology"
**Concepts:** [[photometric-structural-fitting]], [[multi-gaussian-expansion]]

**Supports:**
- The software citation for PyAutoGalaxy itself: open-source, multi-wavelength galaxy
  structure and morphology modelling.

**Use when:**
- A user publishes work done with this assistant's stack. This is the citation to give them.

**Do not use for:**
- A methodological claim about a specific algorithm; cite the underlying method paper.

## See also

- [[sersic-profile]], [[photometric-structural-fitting]], [[multi-gaussian-expansion]],
  [[point-spread-function]] — the concept pages.
- [[sources-bulge-disk-decomposition]] — what these codes are used to fit.
- [[sources-isophotes-and-multipoles]] — the non-parametric alternative.
