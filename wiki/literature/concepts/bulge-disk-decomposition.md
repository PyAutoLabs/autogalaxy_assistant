---
title: Bulge-disc decomposition
type: concept
topics: [light-profiles, structural-fitting, galaxy-components]
sources:
  - Kormendy 1977 — decomposition of observed profiles
  - de Jong 1996 — two-dimensional bulge/disc method
  - Simard 2011 — SDSS bulge+disk catalogue
  - Gadotti 2009 — pseudo-bulges, classical bulges and ellipticals
  - Allen 2006 — Millennium Galaxy Catalogue decompositions
  - Fisher 2008 — pseudobulges and Sersic index
status: drafted
---

# Bulge-disc decomposition

## TL;DR

A bulge-disc decomposition fits a galaxy's light as the sum of a centrally
concentrated component (usually a free-index Sersic) and an exponential disc,
recovering a bulge-to-total ratio `B/T` alongside each component's size and
shape. It is the workhorse measurement of galaxy structure, and also the single
place where structural fitting is least well posed: the two components overlap in
radius, `B/T` trades against bulge `n` and against the disc scale length, and the
"right" number of components is a modelling choice, not a measurement. Published
`B/T` catalogues for the same galaxies disagree at a level that matters, and the
disagreement traces to fitting decisions rather than to data quality.

## What it is

The standard two-component model is

```
I(R) = I_e exp{ -b_n [ (R/R_e)^(1/n) - 1 ] }  +  I_0 exp(-R/h)
```

fitted in two dimensions, so each component carries its own axis ratio and
position angle as well. Variants in wide use:

- **`n` free vs `n = 4` fixed.** Forcing a de Vaucouleurs bulge was standard for
  decades and systematically inflates `B/T` in late-type galaxies, because a
  high-`n` bulge absorbs inner disc light.
- **Three or more components.** Bars, nuclear discs, ovals and haloes are real
  and photometrically distinct; a two-component fit assigns their light to
  whichever of the two components can absorb it — usually the bulge.
- **Simultaneous multi-band fitting.** Fitting all bands at once with the
  structural parameters tied by a smooth function of wavelength stabilises the
  decomposition considerably relative to independent per-band fits.

The two components are only separable when they differ in *shape*, not merely in
scale. Where a galaxy is nearly face-on and the bulge index is low, `B/T` is close
to unconstrained even in excellent data — a fact that shows in the posterior as a
long degenerate ridge, and in maximum-likelihood catalogues as a bimodal or
piled-up `B/T` distribution.

**Classical vs pseudo-bulges.** The photometric distinction is drawn at bulge
`n ≈ 2`: classical bulges are dense, high-`n`, merger-built spheroids; pseudo-bulges
are low-`n`, disc-like, and built by secular processes in the disc. The threshold
is a useful heuristic, not a physical boundary, and should be quoted as such.

## Why it matters for PyAutoGalaxy

- A two-component model is the first place a user meets a genuinely multimodal
  posterior. Chained searches — fit the disc-dominated outskirts first, then add
  the bulge — are the standard remedy; see
  [`wiki/core/concepts/non_linear_search.md`](../../core/concepts/non_linear_search.md).
- **Linear light profiles** matter more here than for a single Sersic: with two
  components there are two intensity normalisations, and solving both analytically
  removes the worst-conditioned directions from the sampled space
  ([`wiki/core/concepts/linear_light_profiles_and_mge.md`](../../core/concepts/linear_light_profiles_and_mge.md)).
- Multi-band decomposition is directly supported and is the recommended route when
  more than one waveband exists — see
  [`wiki/core/concepts/multi_wavelength.md`](../../core/concepts/multi_wavelength.md).
- Report `B/T` with the model that produced it. "`B/T` = 0.4" is not a measurement
  without "from a free-`n` Sersic + exponential fit over this radial range with
  this sky treatment".

## Key results from the literature

- Kormendy (1977) set out the decomposition of an observed profile into spheroid
  and disc components — the origin of the method
  ([[sources-bulge-disk-decomposition]]).
- de Jong (1996) moved the decomposition from one-dimensional profile fitting to a
  two-dimensional method fitted directly to the image, which is how it is done
  today ([[sources-bulge-disk-decomposition]]).
- Andredakis, Peletier & Balcells (1995) showed bulge `n` varies systematically
  along the Hubble sequence, undermining the fixed-`n = 4` bulge
  ([[sources-bulge-disk-decomposition]]).
- Allen and others (2006) decomposed ~10,000 Millennium Galaxy Catalogue galaxies,
  one of the first large homogeneous `B/T` samples
  ([[sources-bulge-disk-decomposition]]).
- Fisher & Drory (2008) tied the `n ≈ 2` photometric threshold to independently
  classified pseudo-bulges, giving the index-based classification an empirical
  basis ([[sources-bulge-disk-decomposition]]).
- Gadotti (2009) fitted bulge + disc + bar to SDSS galaxies and showed that
  omitting the bar biases the recovered bulge — a concrete demonstration that
  component count is a systematic ([[sources-bulge-disk-decomposition]]).
- Simard and others (2011) produced bulge+disc decompositions for 1.12 million SDSS
  galaxies; Lackner & Gunn (2012) and Meert, Vikram & Bernardi (2015) produced
  independent decompositions of overlapping samples with different model choices.
  Comparing the three is the standard way to see how large the model-choice
  systematic really is ([[sources-bulge-disk-decomposition]]).
- Kelvin and others (2012) fitted single-Sersic and multi-component models across
  the GAMA bands, and Lange and others (2015) showed how the resulting size-mass
  relation depends on whether galaxies are split by index, colour or morphology
  ([[galaxy-scaling-relations]]).
- Häussler and others (2013) and Vika and others (2013, 2014) developed
  simultaneous multi-band Sersic and bulge-disc fitting, demonstrating that tying
  parameters across wavelength gives physically meaningful component colours where
  independent per-band fits do not ([[photometric-structural-fitting]]).
- Salo and others (2015) and Méndez-Abreu and others (2017) published
  multi-component decompositions (bulge, disc, bar, nuclear component) for the S4G
  and CALIFA samples respectively — the current standard for what a careful
  decomposition of a nearby galaxy looks like
  ([[sources-bulge-disk-decomposition]]).
- Kormendy & Kennicutt (2004) is the review that frames the whole exercise: what
  secular evolution predicts a pseudo-bulge should look like, and why the
  photometric split is worth making ([[sources-bulge-disk-decomposition]]).

## See also

- [[sersic-profile]]
- [[disk-galaxy-structure]]
- [[morphology-classification]]
- [[photometric-structural-fitting]]
- [[stellar-mass-estimates]]
- [[multi-gaussian-expansion]]
- [[sources-bulge-disk-decomposition]]
