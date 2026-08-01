---
title: zCOSMOS (VLT/VIMOS redshift survey)
type: entity
topics: [survey, spectroscopy, redshifts]
sources:
  - arXiv:astro-ph/0612291
  - Lilly and others 2009 — The zCOSMOS 10k-Bright Spectroscopic Sample (ApJS 184, 218)
  - arXiv:1207.0002
status: drafted
---

# zCOSMOS

## What it is

The large VLT/VIMOS spectroscopic redshift survey of the [[cosmos-survey|COSMOS]] field
([[sources-cosmos-survey#lilly-2007-zcosmos]]). It has two tiers:

- **zCOSMOS-bright** — a magnitude-limited survey (I_AB < 22.5) over ~1.7 deg², targeting
  0 < z < ~1.2.
- **zCOSMOS-deep** — a colour-selected sample in the central deg², reaching 1.4 < z < 3.

The bright tier's first public sample, the "10k-bright" release, delivered redshifts for
~10,000 objects with a calibrated per-object confidence class
([[sources-cosmos-survey#lilly-2009-zcosmos-10k-bright-sample]]); the completed survey reached ~16,500
high-quality redshifts and supported an optical group catalogue over 0.1 < z < 1
([[sources-cosmos-survey#knobel-2012-zcosmos-20k-group-catalogue]]).

## Key facts

- **Instrument:** VIMOS on the VLT.
- **Bright tier:** I_AB < 22.5, ~1.7 deg², typical redshift accuracy ~110 km/s.
- **Confidence classes:** each redshift carries an empirically calibrated reliability class,
  derived from repeat observations — the reason a zCOSMOS redshift can be *trusted*
  quantitatively rather than just quoted.
- **Group catalogue:** the 20k group catalogue identifies ~1500 groups between z = 0.1 and
  z = 1, which is how a COSMOS galaxy gets an environment label.

## Why it matters for galaxy structure

A structural fit measures light, in angular units. Converting an effective radius in arcsec
to a physical radius in kpc — and a flux to a stellar mass — needs a redshift, and a
*spectroscopic* redshift removes the dominant systematic from that conversion. For galaxies
in the COSMOS field, zCOSMOS is usually where that number comes from.

It also supplies environment. Whether a galaxy's structure depends on its group membership
is a question you can only ask in a field with a spectroscopic group catalogue
([[galaxy-scaling-relations]], [[early-type-galaxy-structure]]).

## Relation to the dataset bundled with this assistant

The bundled JWST cutout's galaxy takes its spectroscopic redshift, z = 0.3422, from
zCOSMOS-bright DR3, and its group membership from the zCOSMOS 20k group catalogue. The
dataset's own `README.md` records the survey identifiers and confidence class; this page
gives the survey context behind them.

## Key papers

- **Lilly and others 2007** — the zCOSMOS survey definition (arXiv:astro-ph/0612291).
- **Lilly and others 2009** — the 10k-bright spectroscopic sample (ApJS 184, 218).
- **Knobel and others 2012** — the zCOSMOS 20k group catalogue (arXiv:1207.0002,
  ApJ 753, 121).

Full entries in [[sources-cosmos-survey]].

## See also

- [[cosmos-survey]], [[cosmos-web]]
- [[stellar-mass-estimates]], [[galaxy-scaling-relations]]
- [[sources-cosmos-survey]]
