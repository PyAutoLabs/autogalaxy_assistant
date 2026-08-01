# Figure sources

Provenance of the images under `docs/images/`. The rule this directory exists to record:
**every committed figure must be rebuildable offline from material already in this
repository.**

## Vendored third-party inputs

**None.** This directory holds no image assets, and that is deliberate rather than an
oversight: the only README figure is built from the bundled dataset's own FITS files, so
there is no survey cutout, colour composite or externally-published image to vendor. If a
future figure does need a third-party asset, vendor it here and add a row to the table
below — never fetch it at build time, because the figure scripts must run without network
access.

| File | Source | Notes |
|------|--------|-------|
| _(none)_ | | |

## Generated figures

| File | Built by | Inputs |
|------|----------|--------|
| `../cosj100020+015344_dataset.png` | [`../../make_readme_figures.py`](../../make_readme_figures.py) | `dataset/imaging/cosj100020+015344/wavebands/<BAND>/{data.fits,info.json}` for `F115W`, `F150W`, `F277W`, `F444W` — all shipped in this repository |

The figure is the README's "Getting Started" hero: two rows over the four wavebands, the
top row at a 10" field of view with the 4" mask circle overlaid, the bottom row a 2.5" zoom
carrying each band's measured isophote ellipse. Every annotated number — axis ratio,
position angle, rough half-light radius, peak signal-to-noise, the un-subtracted sky
pedestal — is read at runtime from the per-band `info.json` rather than hard-coded, so the
figure cannot drift out of agreement with the dataset it describes. Where those numbers come
from, and which are measured versus cited, is documented in
[the dataset's own README](../../../dataset/imaging/cosj100020+015344/README.md) and in
[`wiki/core/operations/dataset.md`](../../../wiki/core/operations/dataset.md).

Rebuild it with:

```bash
python docs/make_readme_figures.py
```

No PyAuto\* import is involved — the script reads the FITS files with `astropy.io.fits` and
draws with `matplotlib` on the `Agg` backend — so it runs in a bare environment with only
`numpy`, `astropy` and `matplotlib` installed. `docs/` is outside the
`autoassistant/audit_skill_apis.py` scan set, so execution from a clean checkout is what
validates it.
