---
title: COSMOS (Cosmic Evolution Survey)
type: entity
topics: [survey, deep-field, photometric-redshifts]
sources:
  - arXiv:astro-ph/0612305
  - arXiv:astro-ph/0703095
  - arXiv:2110.13923
status: drafted
---

# COSMOS — the Cosmic Evolution Survey

## What it is

A 2 deg² equatorial field observed by essentially every major facility since the mid-2000s,
built around a 640-orbit HST/ACS mosaic — the largest contiguous HST imaging survey of its
era ([[sources-cosmos-survey#scoville-2007-cosmos-overview]],
[[sources-cosmos-survey#koekemoer-2007-cosmos-hstacs-imaging]]). Its purpose was to measure how galaxy
properties depend jointly on redshift and environment over a volume large enough that
large-scale structure is sampled rather than stumbled into.

What makes COSMOS the field it is today is not any single observation but the *stacking* of
them: optical and near-infrared ground-based imaging, Spitzer, Chandra, VLA, and a
spectroscopic backbone ([[zcosmos]]), all on the same sky, feeding successive generations of
photometric-redshift and stellar-mass catalogues.

## Key facts

- **Area:** ~2 deg², centred at RA 10:00:28.6, Dec +02:12:21 (J2000).
- **HST/ACS:** F814W imaging over ~1.8 deg², the backbone for morphology and structural
  measurement in the field.
- **Catalogues:** a sequence of increasingly deep photometric catalogues — COSMOS2015
  (~half a million galaxies, 30+ bands) and COSMOS2020 (two complementary catalogues,
  reaching z ~ 10) are the ones in current use
  ([[sources-cosmos-survey#laigle-2016-cosmos2015]],
  [[sources-cosmos-survey#weaver-2022-cosmos2020]]).
- **Photometric redshifts:** the 30-band photometric-redshift work is what makes COSMOS
  usable for structure-versus-environment studies at all
  ([[sources-cosmos-survey#ilbert-2009-cosmos-photometric-redshifts]]).
- **Multi-wavelength:** Spitzer (S-COSMOS), Chandra COSMOS Legacy, VLA-COSMOS 3 GHz, and
  Subaru optical imaging all cover the same field.

## Why it matters for galaxy structure

Three reasons a structural-fitting user meets COSMOS constantly:

1. **Ancillary data.** A structural fit produces a size, a Sersic index and an axis ratio.
   Interpreting those requires a redshift and a stellar mass, and COSMOS supplies both for
   nearly every source in the field — which is why size–mass relations
   ([[galaxy-scaling-relations]]) are so often measured here.
2. **Environment.** The field is large enough to contain groups and structures, so the
   dependence of galaxy structure on environment can be measured within one homogeneous
   dataset ([[sources-cosmos-survey#scoville-2007-large-structures-in-cosmos]]).
3. **It is the JWST field.** [[cosmos-web]] built its NIRCam mosaic here precisely because
   of the ancillary data described above.

## Key papers

- **Scoville and others 2007** — the COSMOS overview (arXiv:astro-ph/0612305).
- **Koekemoer and others 2007** — the HST/ACS observations and data processing
  (arXiv:astro-ph/0703095).
- **Capak and others 2007** — the first-release optical and near-IR catalogue
  (arXiv:0704.2430).
- **Weaver and others 2022** — COSMOS2020, the current reference catalogue
  (arXiv:2110.13923).

Full entries in [[sources-cosmos-survey]].

## See also

- [[cosmos-web]], [[zcosmos]], [[candels]]
- [[hst]], [[stellar-mass-estimates]], [[galaxy-scaling-relations]]
- [[sources-cosmos-survey]]
