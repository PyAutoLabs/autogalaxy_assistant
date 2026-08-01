---
title: The PSF in structural fitting
type: concept
topics: [psf, systematics, structural-fitting]
sources:
  - Trujillo 2001 — the effects of seeing on Sersic profiles
  - Anderson 2000 — an accurate WFPC2 point-spread function
  - Krist 2011 — Tiny Tim
  - Perrin 2014 — WebbPSF
  - Bertin 2011 — PSFEx
  - Sandin 2014 — the influence of diffuse scattered light
status: drafted
---

# The PSF in structural fitting

## TL;DR

The point spread function is not a nuisance to be deconvolved away — it is part of
the forward model. A structural fit convolves the model with the PSF and compares
in the data frame, which is the only statistically correct way to handle it. What
makes the PSF the dominant systematic in structural work is that its errors do not
average out: an over-broad PSF makes galaxies look intrinsically smaller and lower
`n`, an under-broad one the reverse, and the bias grows as the galaxy size
approaches the PSF width. Two failure modes recur — a PSF model that is wrong in
the **core** (biasing `n` and `R_e` for compact objects) and one that is wrong in
the **wings** (redistributing flux to large radii and corrupting outer profiles and
sky estimates).

## What it is

Sources of a PSF model, roughly in order of increasing reliability for a given
dataset:

- **Analytic** (Gaussian, Moffat). Adequate only for ground-based work where the
  seeing disc genuinely dominates, and even then the Moffat wings matter.
- **Optical models** — Tiny Tim for HST, WebbPSF/STPSF for JWST. Physically derived
  from the optical prescription, sampled arbitrarily finely, but blind to the
  as-built and time-varying state of the telescope.
- **Empirical from stars in the frame** — stack unsaturated, unblended stars,
  handling sub-pixel dithering (effective-PSF methods) and spatial variation across
  the field (PSFEx-style polynomial fits). Reflects the real optics but is limited
  by the number and brightness of usable stars.
- **Hybrid** — an optical model with empirically fitted perturbations. Standard for
  JWST work, where the PSF varies with wavelength, field position and time.

Properties a structural fit is sensitive to:

- **Sampling.** A PSF stored at the detector pixel scale is already a
  pixel-integrated quantity. Convolving an over-sampled model with an
  under-sampled PSF double-counts the pixel response. Match the sampling, or use a
  PSF supplied on the over-sampled grid.
- **Core width.** Sets the bias on `R_e` and `n` for objects near the resolution
  limit. This is the dominant error term for compact high-redshift galaxies
  ([[high-z-galaxy-structure]]).
- **Wings and scattered light.** Real PSFs have extended power-law wings that carry
  a non-trivial flux fraction out to many arcseconds. Truncating the PSF model
  moves that flux into the galaxy's outer profile or into the sky estimate,
  producing spurious haloes, spurious antitruncation and biased low-surface-
  brightness photometry ([[sky-subtraction-and-photometry]]).
- **Chromatic variation.** The PSF is wavelength-dependent, so in multi-band
  fitting each band needs its own PSF. Fitting bands with a single PSF manufactures
  colour gradients.
- **Astrometric registration.** A PSF centroid offset of a fraction of a pixel
  relative to the model grid biases central surface brightness.

## Why it matters for PyAutoGalaxy

- The PSF is supplied with the dataset and convolved into the model automatically;
  the mechanics and the over-sampling interaction are in
  [`wiki/core/api/datasets.md`](../../core/api/datasets.md) and
  [`wiki/core/concepts/grids_and_masks.md`](../../core/concepts/grids_and_masks.md).
- **The bundled dataset ships with a model PSF, not an empirical one**, and its
  README says so explicitly. That is a real limit on what its Sersic index means,
  and it is the reason its benchmark prompt prefers an
  [[multi-gaussian-expansion|MGE]] bulge — a basis whose parameters do not have to
  carry a physical interpretation — over a single Sersic. See
  [`wiki/core/operations/dataset.md`](../../core/operations/dataset.md).
- If a fit leaves a bright, symmetric central residual, suspect the PSF before
  adding a component. A PSF-shaped residual is a PSF problem.
- Some profiles are defined as already-convolved ("operated") quantities; the
  distinction matters when combining them with ordinary profiles — see
  [`wiki/core/concepts/sky_background_and_operated_profiles.md`](../../core/concepts/sky_background_and_operated_profiles.md).

## Key results from the literature

- Trujillo and others (2001) quantified how seeing biases Sersic parameters, and
  the companion paper did the same for a Moffat PSF — the standard reference for
  why the PSF must be convolved into the model rather than corrected for afterwards
  ([[sources-light-profile-fitting]]).
- Anderson & King (2000) developed the effective-PSF formalism for WFPC2,
  separating the instrumental PSF from the pixel response and enabling sub-pixel
  accurate empirical PSFs from dithered data
  ([[sources-light-profile-fitting]]).
- Krist, Hook & Stoehr (2011) reviewed two decades of Tiny Tim HST optical
  modelling, including its known limitations — which are precisely the
  time-variable and as-built effects an empirical PSF captures and a model PSF does
  not ([[sources-light-profile-fitting]]).
- Perrin and others (2014) described WebbPSF, the JWST optical PSF simulator that
  underpins most JWST structural work ([[jwst]]).
- Bertin (2011) described PSFEx, which models a spatially varying PSF from the
  stars in the frame and feeds it to automated morphometry — the workhorse for
  ground-based surveys ([[sources-light-profile-fitting]]).
- Häussler and others (2007) showed, by fitting the same GEMS galaxies with two
  codes, that PSF handling is a significant part of the difference between
  structural catalogues ([[photometric-structural-fitting]]).
- Sandin (2014, 2015) demonstrated that the extended PSF wings and diffuse
  scattered light dominate the outermost surface brightness of galaxies, and that
  ignoring them produces spurious faint haloes and thick-disc components
  ([[sky-subtraction-and-photometry]], [[sources-stellar-halos]]).
- Karabal and others (2017) developed a deconvolution technique to remove
  instrumental scattered light from deep galaxy images, quantifying how much of the
  apparent outer structure was instrumental ([[sources-stellar-halos]]).
- Berman and others (2024) benchmarked PSF modelling approaches specifically on
  JWST NIRCam imaging, which is the instrument configuration of this repo's bundled
  dataset ([[jwst]]).

## See also

- [[photometric-structural-fitting]]
- [[sersic-profile]]
- [[multi-gaussian-expansion]]
- [[high-z-galaxy-structure]]
- [[sky-subtraction-and-photometry]]
- [[sources-light-profile-fitting]]
