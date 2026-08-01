---
title: COSMOS-Web (JWST Cycle 1 Treasury)
type: entity
topics: [survey, jwst, deep-field]
sources:
  - arXiv:2211.07865
  - arXiv:astro-ph/0612305
status: drafted
---

# COSMOS-Web

## What it is

The largest JWST Cycle 1 General Observer programme (GO 1727, 255 hours): a contiguous
NIRCam imaging survey of ~0.54 deg² of the [[cosmos-survey|COSMOS]] field in four filters —
F115W, F150W, F277W and F444W — with ~0.19 deg² of parallel MIRI F770W coverage
([[sources-cosmos-survey#casey-2023-cosmos-web]]).

Its scientific case is galaxy evolution at scale: identifying and characterising galaxies in
the reionization era, mapping the assembly of massive galaxies from z ~ 2–6, and — because
the area is large enough to contain many environments — measuring how structure and stellar
mass growth depend on where a galaxy lives.

## Key facts

- **Programme:** JWST GO 1727, PIs C. M. Casey and J. S. Kartaltepe.
- **Filters and depths:** NIRCam F115W, F150W, F277W, F444W; MIRI F770W in parallel.
- **Pixel scales in the delivered mosaics:** the short-wavelength channel is sampled at
  0.03″/pixel and the long-wavelength channel at 0.06″/pixel — a factor-two difference that
  any multi-band structural fit has to carry explicitly.
- **Field:** COSMOS, so every galaxy inherits three decades of ancillary photometry,
  spectroscopy and photometric-redshift work ([[cosmos-survey]], [[zcosmos]]).

## Why it matters for galaxy structure

COSMOS-Web is the current best combination of *area* and *rest-frame optical resolution* at
intermediate and high redshift. Before JWST, structural measurements beyond z ~ 1.5 were
made in the rest-frame ultraviolet, where a galaxy's light traces recent star formation
rather than its stellar mass — the "morphological k-correction" problem. NIRCam's long
wavelength channel moves the measurement back into the rest-frame optical, so a Sersic index
or a bulge-to-total ratio measured there means something closer to what the same number
means locally ([[high-z-galaxy-structure]]).

The four-filter design also makes COSMOS-Web a natural multi-band fitting dataset: the same
galaxy is observed at two pixel scales with two very different PSFs, which is exactly the
configuration where fitting bands jointly (rather than independently) changes the answer
([[point-spread-function]], [[photometric-structural-fitting]]).

## Relation to the dataset bundled with this assistant

The imaging shipped in `dataset/imaging/cosj100020+015344/` is a four-band NIRCam cutout
reduced from COSMOS-Web (programme 1727) exposures. Its target is an early-type galaxy at
z = 0.3422, with the redshift coming from [[zcosmos]] and its catalogue identifiers from the
COSMOS2020 photometric catalogue ([[cosmos-survey]]). The dataset's own `README.md` is the
authority on its provenance, depth and PSF caveats; this page is only the survey context.

## Key papers

- **Casey and others 2023** — the COSMOS-Web survey overview: design, area, filters, depths
  and science goals (arXiv:2211.07865). See
  [[sources-cosmos-survey#casey-2023-cosmos-web]].

## See also

- [[cosmos-survey]], [[zcosmos]], [[candels]]
- [[jwst]], [[point-spread-function]]
- [[high-z-galaxy-structure]], [[photometric-structural-fitting]]
- [[sources-cosmos-survey]]
