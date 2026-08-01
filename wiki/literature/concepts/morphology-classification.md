---
title: Morphology classification
type: concept
topics: [morphology, classification, machine-learning]
sources:
  - Hubble 1926 — extragalactic nebulae
  - de Vaucouleurs 1959 — classification and morphology of external galaxies
  - Conselice 2003 — the CAS system
  - Lotz 2004 — Gini and M20
  - Lintott 2008 — Galaxy Zoo
  - Huertas-Company 2015 — deep-learning morphologies in CANDELS
status: drafted
---

# Morphology classification

## TL;DR

Morphological classification runs on three tracks that answer different questions.
**Visual** schemes — Hubble's tuning fork and its de Vaucouleurs revision — encode
a trained human's pattern recognition and remain the vocabulary the field speaks in.
**Non-parametric** statistics — concentration, asymmetry, clumpiness, Gini, `M20` —
reduce an image to numbers without assuming a model, and so extend to irregular and
high-redshift galaxies where parametric fits fail. **Parametric** structure —
Sersic index, `B/T`, isophote shape — is the most physically interpretable but
assumes the model is right. Machine learning has largely replaced human eyes at
survey scale, but it is trained on human labels, so it inherits their conventions
and their biases rather than transcending them. None of the three is "the"
morphology: they correlate strongly but not perfectly, and which one you use
changes which galaxies land in which bin.

## What it is

**Visual schemes.** Hubble's sequence orders galaxies E - S0 - S/SB - Irr, with
spirals split by bulge prominence and arm winding. De Vaucouleurs added the family
(barred/unbarred/intermediate), the variety (ringed/spiral) and stage axes, giving
the `SAB(rs)bc`-style notation still in use. Two later revisions matter
structurally: reordering ellipticals by isophote shape rather than apparent
flattening, and placing S0 galaxies on a sequence parallel to the spirals rather
than between E and Sa.

**Non-parametric statistics.**

- **CAS** — Concentration (ratio of radii enclosing fixed light fractions),
  Asymmetry (residual after 180° rotation), Clumpiness/Smoothness (residual after
  smoothing). Concentration tracks bulge prominence, asymmetry tracks interaction,
  clumpiness tracks star formation.
- **Gini** — the inequality of the light distribution among pixels; unlike
  concentration it does not assume the brightest pixels are central.
- **`M20`** — the second-order moment of the brightest 20% of the light, sensitive
  to multiple bright nuclei.
- **MID** and related statistics (multimode, intensity, deviation) were designed
  specifically to catch disturbed high-redshift morphologies that CAS misses.

All of these depend on the segmentation map, the depth and the resolution, so
comparing values across surveys without degrading to a common depth is unsafe.

**Machine classification.** Convolutional networks trained on Galaxy Zoo labels
reproduce human classifications with high fidelity and now supply morphologies for
hundreds of thousands to millions of galaxies. What they predict is *the
distribution of human votes*, which is a different (and better-defined) quantity
than "the true morphology".

## Why it matters for PyAutoGalaxy

- Morphology is usually the *selection* step upstream of a structural fit — "fit
  the early types" — so the classification method determines the sample. Say which
  one was used.
- Non-parametric statistics are a useful **residual** diagnostic: computing
  asymmetry or clumpiness on the residual map after a smooth model is subtracted is
  a quantitative version of "does this fit leave structure behind"
  ([[clumpy-and-irregular-structure]]).
- Sersic index is a poor proxy for visual type at the individual-galaxy level even
  though the distributions separate in aggregate. Do not use `n > 2.5` as a synonym
  for "elliptical" in anything but a statistical statement.
- For the galaxy-composition machinery a classification feeds into, see
  [`wiki/core/concepts/galaxies.md`](../../core/concepts/galaxies.md).

## Key results from the literature

- Hubble (1926) introduced the classification of extragalactic nebulae that became
  the tuning fork; de Vaucouleurs (1959) added the family/variety/stage axes that
  make up the revised system ([[sources-galaxy-formation-misc]]).
- van den Bergh (1976) proposed the parallel-sequence (DDO) alternative, in which
  S0 and anaemic spirals form their own sequences — an idea revived by
  Kormendy & Bender (2011) with a structural justification
  ([[sources-galaxy-formation-misc]]).
- Kormendy & Bender (1996) argued the elliptical sequence should be ordered by
  isophote shape, because `a_4` tracks rotational support while `E0-E7` tracks only
  projection ([[isophote-analysis]], [[sources-isophotes-and-multipoles]]).
- Conselice (2003) established the CAS system and its links to formation history;
  Abraham, van den Bergh & Nair (2003) introduced the Gini coefficient for galaxy
  images; Lotz, Primack & Madau (2004) combined Gini with `M20` into the
  now-standard non-parametric pair ([[sources-galaxy-formation-misc]]).
- Freeman and others (2013) introduced the MID statistics specifically for
  disturbed high-redshift morphologies where CAS and Gini-`M20` lose sensitivity
  ([[clumpy-and-irregular-structure]]).
- Nair & Abraham (2010) published detailed visual classifications for 14,034 SDSS
  galaxies — the training and calibration set much of the later work rests on
  ([[sources-galaxy-formation-misc]]).
- Lintott and others (2008) launched Galaxy Zoo, giving ~10^5 galaxies
  crowd-sourced morphologies; Willett and others (2013) released the far more
  detailed Galaxy Zoo 2 classifications for 304,122 galaxies
  ([[sources-galaxy-formation-misc]]).
- Dieleman, Willett & Dambre (2015) showed rotation-invariant convolutional
  networks reproduce Galaxy Zoo votes at near-human accuracy;
  Huertas-Company and others (2015) applied deep learning to the five CANDELS
  fields to produce visual-like morphologies at high redshift; Walmsley and others
  (2022) combined volunteers and deep learning for 314,000 DECaLS galaxies
  ([[sources-galaxy-formation-misc]]).
- Rodriguez-Gomez and others (2019) measured the same non-parametric morphologies
  on mock images from a cosmological simulation and on real survey data, which is
  the standard way to test whether a morphology statistic means what it is assumed
  to mean ([[sources-galaxy-formation-misc]]).
- Buta and others (2015) applied the classical de Vaucouleurs system to S4G
  mid-infrared imaging, showing how much of the visual classification survives when
  dust and young stars are removed ([[disk-galaxy-structure]]).

## See also

- [[isophote-analysis]]
- [[bulge-disk-decomposition]]
- [[disk-galaxy-structure]]
- [[high-z-galaxy-structure]]
- [[clumpy-and-irregular-structure]]
- [[sersic-profile]]
