---
title: Sources — bulge/disk decomposition
type: sources
topics: [galaxy-structure, decomposition]
status: drafted
---

# Sources: bulge/disk decomposition

Papers on fitting a galaxy with two (or more) components rather than one. The recurring
theme is that a two-component fit is easy to *run* and hard to *trust*: the bulge and disk
parameters are correlated, the answer depends on the model family allowed, and independent
catalogues of the same galaxies disagree in ways that matter.

## Allen 2006 — Millennium Galaxy Catalogue decompositions

**Canonical BibTeX key:** `Allen2006`
**Reference:** arXiv:astro-ph/0605699, MNRAS 371, 2 — "Millennium Galaxy Catalogue:
bulge-disc decomposition of 10 095 nearby galaxies"
**Concepts:** [[bulge-disk-decomposition]], [[photometric-structural-fitting]]

**Supports:**
- Automated bulge+disk decomposition applied uniformly to a complete magnitude-limited
  sample of ~10,000 nearby galaxies.
- Bulge-to-total ratios and component luminosity functions derived from those fits.

**Use when:**
- Citing an early large-sample, uniformly fitted two-component catalogue.

**Do not use for:**
- SDSS-scale sample statistics — later catalogues are two orders of magnitude larger.

## Simard 2011 — 1.12 million SDSS decompositions

**Canonical BibTeX key:** `Simard2011`
**Reference:** arXiv:1107.1518, ApJS 196, 11 — "A Catalog of Bulge+Disk Decompositions and
Updated Photometry for 1.12 Million Galaxies in the Sloan Digital Sky Survey"
**Concepts:** [[bulge-disk-decomposition]], [[sdss]], [[sky-subtraction-and-photometry]]

**Supports:**
- Bulge+disk decompositions for 1.12 million SDSS galaxies, fitted with more than one model
  family so that model choice can be assessed rather than assumed.
- Updated photometry relative to the SDSS pipeline, including a re-derived sky background.

**Use when:**
- You need a reference local distribution of bulge-to-total ratio, disk scale length or
  bulge Sersic index.

**Do not use for:**
- A claim that the fitted bulge is dynamically a bulge — the catalogue is photometric.

## Meert 2015 — SDSS-DR7 2D decompositions and systematics

**Canonical BibTeX key:** `Meert2015`
**Reference:** arXiv:1406.4179, doi:10.1093/mnras/stu2333 — "A catalogue of 2D photometric
decompositions in the SDSS-DR7 spectroscopic main galaxy sample: preferred models and
systematics"
**Concepts:** [[bulge-disk-decomposition]], [[sdss]], [[photometric-structural-fitting]]

**Supports:**
- An independent 2D decomposition catalogue of the SDSS-DR7 spectroscopic main sample.
- An explicit preferred-model selection between one- and two-component fits, plus a
  systematics analysis of the resulting parameters.

**Use when:**
- Comparing two independent structural catalogues of the same galaxies, or citing model
  selection between a single Sersic and a bulge+disk fit.

**Do not use for:**
- High-redshift decompositions.

## Lackner 2012 — astrophysically motivated decompositions

**Canonical BibTeX key:** `Lackner2012`
**Reference:** arXiv:1201.0763, MNRAS 421, 2277 — "Astrophysically motivated bulge-disc
decompositions of Sloan Digital Sky Survey galaxies"
**Concepts:** [[bulge-disk-decomposition]], [[morphology-classification]]

**Supports:**
- Decompositions in which the allowed component models are restricted on astrophysical
  grounds rather than left maximally free.
- Comparison of the resulting classifications against morphological type.

**Use when:**
- Arguing that constraining the model family is a legitimate — sometimes necessary — choice.

**Do not use for:**
- A claim that unconstrained fits are always wrong.

## Gadotti 2009 — pseudo-bulges, classical bulges and ellipticals

**Canonical BibTeX key:** `Gadotti2009`
**Reference:** arXiv:0810.1953, MNRAS 393, 1531 — "Structural properties of pseudo-bulges,
classical bulges and elliptical galaxies: a Sloan Digital Sky Survey perspective"
**Concepts:** [[bulge-disk-decomposition]], [[disk-galaxy-structure]],
[[galaxy-scaling-relations]]

**Supports:**
- Structural separation of pseudo-bulges from classical bulges in a large SDSS sample,
  including bars as an explicit third component.
- Classical bulges follow the scaling relations of ellipticals more closely than
  pseudo-bulges do.

**Use when:**
- Justifying a three-component (bulge + disk + bar) model, or interpreting a low-Sersic-index
  bulge.

**Do not use for:**
- A kinematic classification of bulge type.

## Weinzirl 2009 — bulge n and B/T in high-mass disks

**Canonical BibTeX key:** `Weinzirl2009`
**Reference:** arXiv:0807.0040, ApJ 696, 411 — "Bulge n and B/T in High Mass Galaxies:
Constraints on the Origin of Bulges in Hierarchical Models"
**Concepts:** [[bulge-disk-decomposition]], [[disk-galaxy-structure]]

**Supports:**
- Measured distributions of bulge Sersic index and bulge-to-total ratio in high-mass disk
  galaxies, used to confront hierarchical bulge-formation predictions.

**Use when:**
- Comparing a measured B/T against the local high-mass disk population.

**Do not use for:**
- Low-mass or dwarf systems.

## Mendez-Abreu 2017 — multi-component CALIFA decompositions

**Canonical BibTeX key:** `MendezAbreu2017`
**Reference:** arXiv:1610.05324, A&A 598, A32 — "Two-dimensional multi-component photometric
decomposition of CALIFA galaxies"
**Concepts:** [[bulge-disk-decomposition]], [[multi-gaussian-expansion]]

**Supports:**
- Two-dimensional decompositions allowing more than two components (bulge, disk, bar) for a
  sample with matched integral-field spectroscopy.

**Use when:**
- Pairing a photometric decomposition with resolved kinematics of the same galaxies.

**Do not use for:**
- Statistically complete population statistics — the sample is survey-sized, not
  million-galaxy-sized.

## Bruce 2014 — decomposed evolution of massive galaxies at 1 < z < 3

**Canonical BibTeX key:** `Bruce2014`
**Reference:** arXiv:1405.1736, MNRAS 444, 1001 — "The Bulge-Disk Decomposed Evolution of
Massive Galaxies at 1<z<3 in CANDELS"
**Concepts:** [[bulge-disk-decomposition]], [[high-z-galaxy-structure]], [[candels]]

**Supports:**
- Bulge+disk decomposition applied to massive galaxies at 1 < z < 3 in CANDELS imaging.
- Separate evolution of the bulge and disk components rather than of a single-Sersic
  summary.

**Use when:**
- Arguing that a single Sersic index hides component-level evolution at high redshift.

**Do not use for:**
- Low-mass galaxies, or redshifts beyond the CANDELS regime.

## Dimauro 2018 — polychromatic CANDELS decompositions

**Canonical BibTeX key:** `Dimauro2018`
**Reference:** arXiv:1803.10234, MNRAS 478, 5410 — "A catalog of polychromatic bulge-disc
decompositions of ~17.600 galaxies in CANDELS"
**Concepts:** [[bulge-disk-decomposition]], [[candels]], [[high-z-galaxy-structure]]

**Supports:**
- A public catalogue of multi-band ("polychromatic") bulge/disk decompositions for ~17,600
  CANDELS galaxies.
- Component-level structural parameters measured consistently across bands rather than band
  by band.

**Use when:**
- You need a high-redshift decomposition catalogue, or a precedent for fitting several bands
  jointly.

**Do not use for:**
- Local-universe comparisons.

## Kruk 2018 — multi-band structural decomposition of barred galaxies

**Canonical BibTeX key:** `Kruk2018`
**Reference:** arXiv:1710.00093, MNRAS 473, 4731 — "Galaxy Zoo: Secular evolution of barred
galaxies from structural decomposition of multi-band images"
**Concepts:** [[bulge-disk-decomposition]], [[disk-galaxy-structure]],
[[morphology-classification]]

**Supports:**
- Multi-band structural decomposition of visually classified barred galaxies, separating
  bar, bulge and disk.

**Use when:**
- A bar is present and you need a precedent for including it as a fitted component.

**Do not use for:**
- Claims about bar dynamics.

## Bottrell 2017 — decomposition of simulated galaxies

**Canonical BibTeX key:** `Bottrell2017`
**Reference:** arXiv:1701.01451, MNRAS 467, 1033 — "Galaxies in the Illustris simulation as
seen by the Sloan Digital Sky Survey - I: Bulge+disc decompositions, methods, and biases"
**Concepts:** [[bulge-disk-decomposition]], [[photometric-structural-fitting]]

**Supports:**
- Simulated galaxies processed into realistic SDSS-like images and then fitted with the same
  decomposition machinery used on real data, so the recovered parameters can be compared to
  a known truth.
- Identification of the biases that decomposition introduces under realistic observing
  conditions.

**Use when:**
- Justifying an end-to-end simulation test of a fitting pipeline before trusting it on data.

**Do not use for:**
- A statement about how real galaxies are structured — the input is a simulation.

## Head 2014 — bulge and disk colours in Coma

**Canonical BibTeX key:** `Head2014`
**Reference:** arXiv:1402.4135, MNRAS 440, 1690 — "Dissecting the Red Sequence: The Bulge and
Disc Colours of Early-Type Galaxies in the Coma Cluster"
**Concepts:** [[bulge-disk-decomposition]], [[early-type-galaxy-structure]]

**Supports:**
- Decomposition of cluster early-type galaxies into bulge and disk components with separate
  colours measured per component.

**Use when:**
- Arguing that component-level colours carry information a global colour does not.

**Do not use for:**
- Field-galaxy conclusions.

## de Jong 1996 — the two-dimensional decomposition method

**Canonical BibTeX key:** `deJong1996`
**Reference:** arXiv:astro-ph/9601002, A&AS 118, 557 — "Near-infrared and optical broadband
surface photometry of 86 face-on disk dominated galaxies. II. A two-dimensional method to
determine bulge and disk parameters"
**Concepts:** [[bulge-disk-decomposition]], [[photometric-structural-fitting]]

**Supports:**
- The two-dimensional (rather than one-dimensional profile) approach to determining bulge and
  disk parameters, and why the 2D formulation is preferable.

**Use when:**
- Citing the methodological origin of 2D decomposition.

**Do not use for:**
- Modern PSF or sky treatments.

## See also

- [[bulge-disk-decomposition]] — the concept page.
- [[sources-light-profile-fitting]] — the fitting codes these catalogues were built with.
- [[sources-disk-galaxy-structure]], [[sources-elliptical-galaxies]] — what the components
  look like in isolation.
