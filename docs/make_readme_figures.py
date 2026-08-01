"""
COSJ100020+015344 README Figure
===============================

Builds the hero figure shown at the top of the README's "Getting Started" section,
which introduces the bundled JWST/NIRCam dataset that both starter prompts point at.

Everything the figure draws comes from the shipped dataset itself — the four
`data.fits` cutouts and their `info.json` measurements under
`dataset/imaging/cosj100020+015344/`. There are no vendored third-party inputs and no
network access, so the figure rebuilds from a fresh clone of this repository alone.

The layout is two rows over the same four wavebands, so a feature seen in one column's
top panel reappears in its bottom panel:

- **Top row** — each band at a 9" field of view with the 4" circular mask a fit of this
  galaxy would plausibly use, plus the annotations a first modelling session will ask
  about: which blob is the target, the faint neighbour that sits *inside* that mask, and
  the un-subtracted sky pedestal.
- **Bottom row** — a 2.5" zoom on the same four bands with each band's own measured
  isophote ellipse drawn on it. Priming the reader here means the "how elliptical is it,
  and does its size change with wavelength?" beat in a modelling session lands as a
  recognition rather than a surprise.

__Contents__

- **Paths**: the shipped dataset inputs and the output figure.
- **Framing**: the two fields of view, the mask radius, and the display stretch.
- **Load**: read each band's cutout and its measurements, and locate the galaxy.
- **Plot**: render the two rows, the mask overlay, the isophote ellipses and the labels.
"""

import json
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse
from astropy.io import fits

"""__Paths__

Inputs are the bundled dataset's own products: one `data.fits` plus one `info.json` per
waveband. `info.json` is what makes the annotations measurements rather than guesses —
its `axis_ratio`, `position_angle` and `effective_radius_arcsec_rough` are second-moment
measurements of these same cutouts, and its `background_sky_level` is the sigma-clipped
sky the display stretch subtracts. The dataset README documents where each number comes
from.
"""

DOCS_PATH = Path(__file__).parent
REPO_PATH = DOCS_PATH.parent

DATASET_PATH = REPO_PATH / "dataset" / "imaging" / "cosj100020+015344" / "wavebands"
OUTPUT_PATH = DOCS_PATH / "images" / "cosj100020+015344_dataset.png"

BANDS = ["F115W", "F150W", "F277W", "F444W"]

"""__Framing__

Two fields of view, quoted in arcseconds rather than pixels so the short-wave bands
(0.03"/pixel) and long-wave bands (0.06"/pixel) frame the *same* patch of sky despite
their factor-of-two difference in sampling.

The 10" top-row field contains the 8"-diameter mask circle with an arcsecond of margin on
each side — enough that the in-panel labels clear the circle rather than colliding with
it. The delivered cutouts are 12.5" on a side, so the crop also trims the outer frame
where the short-wave depth steps across a NIRCam detector-gap boundary. The 2.5"
bottom-row field is roughly three times the galaxy's rough half-light radius — enough to
show the isophote shape without the surrounding sky dominating the panel.
"""

FIELD_ARCSEC_WIDE = 10.0
FIELD_ARCSEC_ZOOM = 2.5

"""The mask radius the README's second starter prompt would plausibly settle on. The
dataset README's §5c recommends a modelling mask of radius <~ 4": that keeps the fit
inside the uniformly-covered part of the short-wave cutouts and excludes the 8.0"
neighbour, while still reaching well beyond the galaxy's ~0.37" half-light radius. It
does *not* exclude the faint source 2.6" from the centre, which is exactly why that
source is annotated below."""

MASK_RADIUS_ARCSEC = 4.0

NEIGHBOUR_OFFSET_ARCSEC = 2.6

"""The display stretch. `arcsinh` brings the faint outer isophotes and the bright core
into one range without saturating either; scaling the argument by each band's own sky RMS
(rather than a fixed surface brightness) makes the four panels comparable even though
their absolute brightness differs by a factor of several. The sky pedestal is subtracted
for *display only* — the shipped `data.fits` still carries it, which is the point of the
annotation on the F444W panel."""

STRETCH_IN_SKY_RMS = 12.0

"""__Load__

Each band contributes its cutout, its measurements, and a centre. The centre is
recomputed here as a flux-weighted centroid inside a central 2" box rather than assumed
to be the middle pixel: the reduction centred the cutout on the catalogue position, but
the measured centroid sits a fraction of an arcsecond away from the exact centre, and the
mask circle and isophote ellipse should both sit on the galaxy rather than on the grid.
"""

CENTROID_BOX_ARCSEC = 2.0


def load_band(band):
    """The band's sky-subtracted cutout, its `info.json`, and the galaxy's pixel centre."""

    directory = DATASET_PATH / band

    info = json.loads((directory / "info.json").read_text())
    data = fits.getdata(directory / "data.fits").astype(float)

    data = data - info["background_sky_level"]

    half = int(round(0.5 * CENTROID_BOX_ARCSEC / info["pixel_scale"]))

    centre_y, centre_x = (dimension // 2 for dimension in data.shape)

    box = data[
        centre_y - half : centre_y + half + 1, centre_x - half : centre_x + half + 1
    ]

    """Weighting by the positive flux only keeps sky noise in the corners of the box from
    dragging the centroid; the box is small enough that the galaxy dominates regardless."""

    weights = np.clip(box, 0.0, None)

    rows, columns = np.mgrid[0 : box.shape[0], 0 : box.shape[1]]

    offset_y = float((weights * rows).sum() / weights.sum()) - half
    offset_x = float((weights * columns).sum() / weights.sum()) - half

    return {
        "info": info,
        "data": data,
        "centre": (centre_y + offset_y, centre_x + offset_x),
        "pixel_scale": info["pixel_scale"],
    }


bands = {band: load_band(band) for band in BANDS}

"""__Plot__

Four columns (one per waveband) by two rows (wide field, then zoom). Every panel is
square and crops to a field quoted in arcseconds, so the columns stay registered to each
other and the rows stay registered within a column.

Panels are labelled *inside* their own frame rather than with axis titles, which lets the
grid butt right up against the figure edges — no bands of white space between rows — and
leaves room for the labels to be set large enough to stay readable at the width the README
displays the figure at. `origin="lower"` keeps the FITS row order, which for these
`rotation = 0` mosaics puts north up and east left in every panel.
"""

"""The panels abut with no gap: any spacing shows through as a white line, since the
figure background is what sits behind the axes. Panels are square, so the figure height is
derived rather than guessed — four panel widths fill the figure width, and two panel
widths give the height."""

FIGURE_WIDTH = 14.0

PANEL_WIDTH = FIGURE_WIDTH / 4.0

figure, axes = plt.subplots(2, 4, figsize=(FIGURE_WIDTH, 2.0 * PANEL_WIDTH))

"""Amber for the panel titles reads clearly against the magma colour map and stays
distinct from the two annotation colours already in play — white for the arrows and scale
bar, cyan for the mask and the isophote ellipses. The dark stroke keeps every label
legible where it happens to fall across the bright core."""

LABEL_COLOR = "#ffc400"
MASK_COLOR = "#22d3ee"
LABEL_STROKE = [path_effects.withStroke(linewidth=3.0, foreground="black")]

ARROW_STYLE = dict(arrowstyle="-|>", color="white", lw=1.7, shrinkA=0, shrinkB=3)


def crop(band, field_arcsec):
    """The band's cutout trimmed to a square field centred on the galaxy, and the pixel
    coordinates the galaxy sits at within that crop."""

    entry = bands[band]

    half = int(round(0.5 * field_arcsec / entry["pixel_scale"]))

    centre_y, centre_x = (int(round(value)) for value in entry["centre"])

    data = entry["data"][
        centre_y - half : centre_y + half + 1, centre_x - half : centre_x + half + 1
    ]

    """The galaxy's sub-pixel position is preserved relative to the crop so the overlays
    land on the galaxy rather than on the nearest whole pixel."""

    offset_y = entry["centre"][0] - centre_y
    offset_x = entry["centre"][1] - centre_x

    return data, (half + offset_y, half + offset_x)


def render(ax, band, field_arcsec):
    """Draw one band's cropped, arcsinh-stretched image and return its centre in pixels."""

    entry = bands[band]

    data, centre = crop(band, field_arcsec)

    stretch = STRETCH_IN_SKY_RMS * entry["info"]["background_sky_rms"]

    ax.imshow(
        np.arcsinh(data / stretch),
        origin="lower",
        cmap="magma",
        interpolation="bicubic",
    )

    return centre


def panel_label(ax, text, color=LABEL_COLOR, fontsize=15):
    ax.text(
        0.035,
        0.965,
        text,
        transform=ax.transAxes,
        color=color,
        fontsize=fontsize,
        fontweight="bold",
        ha="left",
        va="top",
        path_effects=LABEL_STROKE,
    )


def footer_label(ax, text, color="white", fontsize=11.5):
    ax.text(
        0.035,
        0.035,
        text,
        transform=ax.transAxes,
        color=color,
        fontsize=fontsize,
        fontweight="bold",
        ha="left",
        va="bottom",
        path_effects=LABEL_STROKE,
    )


"""The wide row. Each panel carries its band, its pixel scale and the 4" mask; the four
annotations are spread across the row rather than repeated, so no single panel is
cluttered and the reader collects the whole brief by reading left to right."""

for column, band in enumerate(BANDS):

    ax = axes[0, column]

    entry = bands[band]
    centre = render(ax, band, FIELD_ARCSEC_WIDE)

    panel_label(ax, f'JWST {band}\n{entry["pixel_scale"]}"/pix')

    ax.add_patch(
        Circle(
            (centre[1], centre[0]),
            radius=MASK_RADIUS_ARCSEC / entry["pixel_scale"],
            fill=False,
            color=MASK_COLOR,
            lw=1.6,
            ls="--",
        )
    )

"""Panel 1 names the target and puts a scale bar on the row. The arrow comes in from the
south-west, away from the annotations on the other panels."""

ax = axes[0, 0]
entry = bands["F115W"]
centre_y, centre_x = crop("F115W", FIELD_ARCSEC_WIDE)[1]
span = crop("F115W", FIELD_ARCSEC_WIDE)[0].shape[0]

ax.annotate(
    "COSJ100020+015344\nearly type, z = 0.3422",
    xy=(centre_x - 0.35 / entry["pixel_scale"], centre_y - 0.35 / entry["pixel_scale"]),
    xytext=(0.10 * span, 0.30 * span),
    color="white",
    fontsize=12,
    fontweight="bold",
    ha="left",
    va="top",
    path_effects=LABEL_STROKE,
    arrowprops=ARROW_STYLE,
)

scale_bar_pixels = 1.0 / entry["pixel_scale"]

ax.plot(
    [0.06 * span, 0.06 * span + scale_bar_pixels],
    [0.09 * span, 0.09 * span],
    color="white",
    lw=2.6,
    solid_capstyle="butt",
)
ax.text(
    0.06 * span + scale_bar_pixels / 2.0,
    0.115 * span,
    '1"',
    color="white",
    fontsize=12,
    fontweight="bold",
    ha="center",
    path_effects=LABEL_STROKE,
)

"""Panel 2 labels the mask, and panel 3 the faint neighbour that sits inside it. The
neighbour is the contaminant question a real-data session has to settle: at 2.6" from the
centre it falls well within any mask wide enough to reach the galaxy's outer isophotes, so
it has to be masked or modelled rather than ignored. Its position angle on the sky is
taken from the data — the brightest pixel in an annulus at that radius."""

"""The mask label is anchored in axes fractions at the foot of the panel, below the
circle's lowest arc, so it cannot spill into the neighbouring panel however the crop is
framed."""

axes[0, 1].text(
    0.5,
    0.025,
    f'{MASK_RADIUS_ARCSEC}" mask — your choice to make',
    transform=axes[0, 1].transAxes,
    color=MASK_COLOR,
    fontsize=11.5,
    fontweight="bold",
    ha="center",
    va="bottom",
    path_effects=LABEL_STROKE,
)


def brightest_in_annulus(band, radius_arcsec, tolerance_arcsec=0.5):
    """Pixel offset (dy, dx) of the brightest pixel in an annulus about the galaxy — used
    to point the neighbour arrow at the neighbour actually present in the data."""

    entry = bands[band]
    data, centre = crop(band, FIELD_ARCSEC_WIDE)

    rows, columns = np.mgrid[0 : data.shape[0], 0 : data.shape[1]]

    radius = (
        np.hypot(rows - centre[0], columns - centre[1]) * entry["pixel_scale"]
    )

    annulus = np.abs(radius - radius_arcsec) < tolerance_arcsec

    masked = np.where(annulus, data, -np.inf)

    index = np.unravel_index(np.argmax(masked), masked.shape)

    return index[0] - centre[0], index[1] - centre[1]


ax = axes[0, 2]
centre_y, centre_x = crop("F277W", FIELD_ARCSEC_WIDE)[1]

offset_y, offset_x = brightest_in_annulus("F277W", NEIGHBOUR_OFFSET_ARCSEC)

"""The arrow tip is in data coordinates (wherever the neighbour actually is) but the label
is anchored in axes fractions at the foot of the panel, so the text stays inside the frame
regardless of which way the neighbour lies. Anchoring it below the source also keeps the
arrow over open sky rather than across the galaxy it is drawing attention away from."""

ax.annotate(
    f'faint neighbour {NEIGHBOUR_OFFSET_ARCSEC}"\ninside the mask',
    xy=(centre_x + offset_x, centre_y + offset_y),
    xycoords="data",
    xytext=(0.72 if offset_x > 0 else 0.28, 0.035),
    textcoords="axes fraction",
    color="white",
    fontsize=11.5,
    fontweight="bold",
    ha="center",
    va="bottom",
    path_effects=LABEL_STROKE,
    arrowprops=ARROW_STYLE,
)

"""Panel 4 carries the sky caveat. It is the one property of this dataset that will
silently bias a light-profile fit without ever looking like an error: the pedestal is real
JWST sky that `calwebb_image3` matched between exposures but never subtracted, and a
Sersic fit that ignores it absorbs it into the profile wings."""

"""Kept to two short lines: at this panel width a longer line would run off the frame. The
API for actually freeing the pedestal is in the README and the dataset's own README."""

footer_label(
    axes[0, 3],
    f'sky NOT subtracted: {bands["F444W"]["info"]["background_sky_level"]:.2f} MJy/sr\n'
    "model it, don't ignore it",
)

"""The zoom row. Each panel gets its own band's measured isophote ellipse, drawn at twice
the rough half-light radius so it traces the outer isophotes rather than the core. The
rough radius steps from ~0.29" short-ward to ~0.37" long-ward — a genuine wavelength
dependence mixed with the changing PSF width, and the thing the multi-band starter prompt
asks the assistant to explain."""

for column, band in enumerate(BANDS):

    ax = axes[1, column]

    entry = bands[band]
    info = entry["info"]

    centre = render(ax, band, FIELD_ARCSEC_ZOOM)

    semi_major = 2.0 * info["effective_radius_arcsec_rough"] / entry["pixel_scale"]

    ax.add_patch(
        Ellipse(
            (centre[1], centre[0]),
            width=2.0 * semi_major,
            height=2.0 * semi_major * info["axis_ratio"],
            angle=info["position_angle"],
            fill=False,
            color=MASK_COLOR,
            lw=1.6,
            ls="--",
        )
    )

    panel_label(ax, f"{band} zoom", fontsize=14)

    footer_label(
        ax,
        f'q = {info["axis_ratio"]:.2f}   PA = {info["position_angle"]:.0f}°\n'
        f'R½ ~ {info["effective_radius_arcsec_rough"]:.2f}"   S/N = {info["peak_snr"]:.0f}',
        color=MASK_COLOR,
    )

for ax in axes.flatten():
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

"""With every label moved inside its panel there is nothing left to reserve margin for, so
the axes run to the figure edge and butt against each other."""

figure.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0, wspace=0.0, hspace=0.0)

"""110 dpi gives a ~1540 pixel wide figure — comfortably sharp at the 900 pixel width the
README displays it at, without the noise-dominated outer regions bloating the committed
PNG."""

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

figure.savefig(OUTPUT_PATH, dpi=110, facecolor="white")

print(f"Figure written to: {OUTPUT_PATH.resolve()}")
