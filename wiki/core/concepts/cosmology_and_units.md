---
title: Cosmology and units
sources:
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/cosmology/
      - autogalaxy/analysis/analysis/analysis.py
      - autogalaxy/imaging/model/latent.py
      - autogalaxy/profiles/light/standard/sersic.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/units/cosmology.py
      - scripts/guides/units/flux.py
      - scripts/guides/results/start_here.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
last_updated: 2026-08-01
content_sha256: 8ec0ab59fba5d7850bb44280ccd5e7cb1d9232dc3181ac9aab23d81e85a22f29
---

# Cosmology and units

PyAutoGalaxy works internally in **angular** and **instrumental** units: positions and radii in
arcseconds, surface brightness in the units of the data being fitted (conventionally electrons
per second per pixel), and mass quantities such as convergence dimensionless. That choice is
deliberate — angular quantities need no redshift, so a fit is possible for a galaxy whose
distance you do not know.

Converting to physical units — kiloparsecs, luminosities, magnitudes — requires a redshift and a
cosmology. Sources: `PyAutoGalaxy:autogalaxy/cosmology/`. Worked guides:
`autogalaxy_workspace:scripts/guides/units/cosmology.py` and `.../units/flux.py`.

## The cosmology object

```python
import autogalaxy as ag

cosmology = ag.cosmo.Planck15()
print(cosmology.H0)
```

`ag.cosmo.Planck15` is the default: an analysis constructed without an explicit `cosmology`
falls back to it (`PyAutoGalaxy:autogalaxy/analysis/analysis/analysis.py`). It and
`ag.cosmo.FlatLambdaCDM` are astropy cosmologies with extra conversion methods bolted on. For a
non-standard cosmology, construct one and pass it through:

```python
cosmology = ag.cosmo.FlatLambdaCDM(H0=70.0, Om0=0.3)

analysis = ag.AnalysisImaging(dataset=dataset, cosmology=cosmology)
```

The cosmology actually used by a fit is recorded in `files/cosmology.json` in the output folder,
so a result is self-documenting — check it rather than assuming.

For galaxy *structure* specifically, the cosmology matters much less than it does for
distance-sensitive measurements: it enters only through the angular-diameter distance to a
single redshift. Swapping Planck15 for a mildly different flat cosmology changes a size in kpc
by a percent or two, not by a factor. Say which one you used all the same.

## Arcseconds to kiloparsecs

One redshift, one conversion factor:

```python
import autogalaxy as ag

galaxy = ag.Galaxy(
    redshift=0.5,
    bulge=ag.lp.Sersic(intensity=1.0, effective_radius=1.0, sersic_index=4.0),
)

cosmology = ag.cosmo.Planck15()

kpc_per_arcsec = cosmology.kpc_per_arcsec_from(redshift=galaxy.redshift)
effective_radius_kpc = galaxy.bulge.effective_radius * kpc_per_arcsec
```

`autogalaxy_workspace:scripts/guides/units/cosmology.py`. `cosmology.arcsec_per_kpc_from` goes
the other way, which is what you want when a prior is naturally expressed as a physical size.
Any angular length converts the same way: effective radius, half-light radius, a Gaussian
`sigma`, an ellipse `major_axis`.

Two cautions specific to galaxy structure:

- **`effective_radius` is the *circular* half-light radius**, not the major-axis one. The
  major-axis value is `elliptical_effective_radius = effective_radius / sqrt(axis_ratio)`
  (`PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py`). For a flattened disc the two
  differ substantially, and catalogues are inconsistent about which they report. Convert
  whichever one your comparison uses, and say so.
- **The conversion is exact but the *measurement* is not.** Propagating an uncertainty on
  `effective_radius` through a fixed `kpc_per_arcsec` is a simple multiplication; if the
  redshift is itself uncertain, that uncertainty has to be propagated too, which the fit does
  not do for you.

## Luminosities

The `intensity` of a light profile is in the units of the data, so a total flux is an integral
over the profile:

```python
import numpy as np

luminosity = galaxy.luminosity_within_circle_from(radius=np.inf)
```

`autogalaxy_workspace:scripts/guides/units/cosmology.py`. Use this rather than summing pixels
inside the mask: a mask always truncates the profile's wings, and for a high-Sersic-index
component the missing fraction is not negligible. `radius` can be finite when you want an
aperture luminosity — which is the honest way to compare with an aperture-photometry catalogue.

The result is still in instrumental units. Getting to a physical luminosity or magnitude
requires a photometric **zero point**, which is a property of the instrument and filter, not of
the model.

## Flux calibration

`autogalaxy_workspace:scripts/guides/units/flux.py` works the conversion through for JWST
NIRCam data delivered in MJy/sr, following the STScI prescription:

```
ZP_AB   = -6.10 - 2.5 * log10(PIXAR_SR)
mag_AB  = ZP_AB - 2.5 * log10(total_flux)
```

```python
import numpy as np

pixar_sr = 2.29e-14              # F444W; from the instrument documentation
zero_point = -6.10 - 2.5 * np.log10(pixar_sr)

grid = ag.Grid2D.uniform(shape_native=(500, 500), pixel_scales=0.02)
total_flux = np.sum(light.image_2d_from(grid=grid))

magnitude_ab = zero_point - 2.5 * np.log10(total_flux)
```

Note the grid in that snippet: `500 × 500` at `0.02″` extends to 5″, chosen so that essentially
all of the profile's light is inside it. Summing an image over too small a grid quietly
under-reports the flux and therefore over-reports the magnitude — the same truncation problem as
using a mask, and the reason `luminosity_within_circle_from(radius=np.inf)` is preferable when
you have a profile rather than an array.

The library ships the two conversion helpers it uses internally:

```python
from autogalaxy.imaging.model.latent import (
    ab_mag_via_flux_from,
    flux_mujy_via_ab_mag_from,
)

ab_mag = ab_mag_via_flux_from(flux=total_galaxy_0_flux, magzero=zero_point)
flux_mujy = flux_mujy_via_ab_mag_from(ab_mag=ab_mag)
```

Beyond AB magnitudes and microjanskies — solar luminosities, `erg s⁻¹` — the conversions are not
implemented; the guide points you at astropy and flags it as a good first contribution.

### Total flux for free, with errors

You rarely need the manual recipe. Every fit computes the integrated flux of each galaxy and
records it as a **latent variable**, written per sample to `latent/samples.csv` beside the search
output:

- **`total_galaxy_0_flux`** — the integrated flux of the first galaxy in the fit's *raw* image
  units (MJy/sr for JWST, e⁻ s⁻¹ for HST). Default-on: it needs no instrument input.
- **`total_galaxy_0_flux_mujy`** — the microjansky conversion. Default-off, because it needs a
  zero point: enable it in `config/latent.yaml` and pass `magzero=` to the analysis
  (`ag.AnalysisImaging(dataset=dataset, magzero=zero_point)`). Enable it without supplying
  `magzero` and the column is filled with NaN plus one warning — the fit itself is unaffected.

`autogalaxy_workspace:scripts/guides/units/flux.py`. Because latents are recorded per sample,
their **uncertainties come for free** — this is the cheapest correct route to an error bar on a
total flux or magnitude, and it avoids the derived-quantity loop entirely. See
[`samples_and_posteriors`](./samples_and_posteriors.md).

## Errors on converted quantities

A unit conversion is a function of the model parameters, so its uncertainty must be built from
the posterior, not from the median plus a converted error bar. For a multiplication by a fixed
factor the two agree; for anything non-linear — a magnitude, an axis ratio, a luminosity — they
do not.

The pattern is: loop over samples (or posterior draws), compute the converted quantity for each,
and marginalise with the sample weights via `af.marginalize`. Worked out in
[`samples_and_posteriors`](./samples_and_posteriors.md); a latent variable, where one exists,
does this for you during the fit.

## Reporting

- **Always state the unit.** `effective_radius = 1.23` is not a result: arcseconds and
  kiloparsecs differ by a redshift-dependent factor, and a reader cannot recover which you meant.
- **State the redshift and the cosmology** alongside any physical size, mass or luminosity.
- **State which effective radius** — circular or major-axis — and which aperture a flux was
  measured in.
- **Do not convert to physical units unnecessarily.** Ellipticity, Sersic index and
  bulge-to-total ratio are dimensionless; an angular size is often the more directly comparable
  quantity when contrasting fits of the same data. Convert when the answer *is* a physical size,
  mass or luminosity.

## See also

- [`light_profiles`](./light_profiles.md) — what `intensity` and `effective_radius` mean.
- [`galaxies`](./galaxies.md) — where the redshift lives, and `luminosity_within_circle_from`.
- [`samples_and_posteriors`](./samples_and_posteriors.md) — propagating a posterior through a
  conversion, and latent variables.
- [`../api/configuration`](../api/configuration.md) — `latent.yaml` and the other configuration
  files.
- [`../stack/autogalaxy`](../stack/autogalaxy.md) — the cosmology module in context.
