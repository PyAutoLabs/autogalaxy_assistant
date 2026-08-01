---
title: JWST
type: entity
topics: [instrument, space-telescope, infrared]
sources:
  - arXiv:2304.04869
  - arXiv:2207.05632
  - arXiv:2212.12069
status: drafted
---

# JWST — the James Webb Space Telescope

## What it is

A 6.5 m segmented, passively cooled infrared space telescope
([[sources-collaborations-and-surveys#gardner-2023-the-jwst-mission]]). For galaxy structure the relevant
instrument is usually **NIRCam**, whose imaging is split into a short-wavelength channel and
a long-wavelength channel observed simultaneously through a dichroic
([[sources-collaborations-and-surveys#rieke-2023-nircam-in-flight]]).

## Key facts

- **Two NIRCam channels, two pixel scales.** The short-wavelength channel is finer-sampled
  than the long-wavelength channel; in delivered COSMOS-Web mosaics this is 0.03″/pixel
  versus 0.06″/pixel. A multi-band fit therefore spans two different grids *and* two very
  different PSFs.
- **The PSF is wavelength-dependent and structured.** Diffraction from the segmented primary
  and the secondary supports produces a six-pointed pattern that varies strongly with
  filter — it is not approximable by a Gaussian
  ([[point-spread-function]]).
- **On-orbit performance exceeded requirements** in image quality and sensitivity, as
  characterised during commissioning
  ([[sources-collaborations-and-surveys#rigby-2023-jwst-science-performance-in-commissioning]]).

## Why it matters for galaxy structure

The decisive change is *rest-frame wavelength*. HST-era structural measurements beyond
z ~ 1.5 were made in the rest-frame ultraviolet, which traces recent star formation and
patchy dust rather than the bulk of the stellar mass. NIRCam's long-wavelength channel moves
those measurements into the rest-frame optical and near-infrared, and the answers changed:
sizes measured in the rest-frame near-infrared came out systematically smaller than their
HST-era counterparts, and disk morphologies turned out to be far more common at z > 3 than
rest-frame-UV imaging suggested ([[high-z-galaxy-structure]],
[[morphology-classification]]).

For this assistant it also matters concretely: the bundled dataset is four-band JWST/NIRCam
imaging ([[cosmos-web]]), so its two pixel scales and per-band PSFs are a modelling
consideration on the very first fit a user runs.

## Key papers

- **Gardner and others 2023** — the JWST mission (arXiv:2304.04869, PASP 135, 068001).
- **Rigby and others 2023** — science performance in commissioning (arXiv:2207.05632,
  PASP 135, 048001).
- **Rieke and others 2023** — NIRCam performance in flight (arXiv:2212.12069,
  PASP 135, 028001).

Full entries in [[sources-collaborations-and-surveys]].

## See also

- [[hst]], [[cosmos-web]], [[euclid]]
- [[point-spread-function]], [[high-z-galaxy-structure]]
- [[sources-collaborations-and-surveys]], [[sources-high-redshift]]
