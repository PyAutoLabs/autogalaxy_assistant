---
title: PyAutoGalaxy RTD — page map
sources:
  - project: PyAutoGalaxy
    paths:
      - docs/index.md
      - docs/overview/overview_1_start_here.md
      - docs/overview/overview_2_new_user_guide.md
      - docs/overview/overview_3_features.md
      - docs/installation/
      - docs/general/
      - docs/howtogalaxy/
      - docs/api/
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
last_updated: 2026-08-01
content_sha256: 4a680d62d8a2c77c61276f27b8e19543094274536a38284f565a31a503f0a3ec
---

# PyAutoGalaxy RTD

The Read-The-Docs site is the canonical human-readable PyAutoGalaxy documentation: a
three-page overview series for newcomers, general docs on configuration and methodology,
installation guides, the HowToGalaxy chapter index, and the generated API reference.
Audience varies by section, so pick the section, not the site.

**URL template:** `https://pyautogalaxy.readthedocs.io/en/latest/<path>.html`

Every `<path>` on this page is the RTD slug of a real file under `PyAutoGalaxy:docs/`, so
the map and the site cannot drift apart silently — if a slug 404s, check `docs/` at the
pinned commit before assuming the page moved.

**When to cite RTD:**

- The user wants the canonical "what is this feature and when would I use it?" page.
- The user is fluent in PyAutoGalaxy and needs the API surface.
- The user has worked through HowToGalaxy chapters 1–2 and is ready for the feature tour.

## Overview series (three pages, in order)

### `overview/overview_1_start_here` — Start Here

The core API demonstrated end to end: imports, a `Grid2D`, light profiles, plotting, a
`Galaxy`, several galaxies together, units, extensibility, galaxy modeling, simulations.
The page to hand someone evaluating whether the library does what they need.

- Audience: newcomer
- `https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_1_start_here.html`

### `overview/overview_2_new_user_guide` — New User Guide

A decision-tree guide that routes by **scale of system** (single galaxy, blended pair,
cluster field) and then by **dataset type** (CCD imaging, interferometer, multi-band),
with Google Colab entry points and a pointer into HowToGalaxy for anyone still unsure.
The recommended first page after installing.

- Audience: general
- `https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_2_new_user_guide.html`

### `overview/overview_3_features` — Features

The tour of the nine capabilities beyond a single smooth profile: interferometry,
multi-wavelength, ellipse fitting, Multi-Gaussian Expansion, shapelets, sky background,
operated light profiles, pixelizations, graphical models. Each section links onward to
deeper docs and workspace examples.

- Audience: experienced — choosing features for a specific science case
- `https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_3_features.html`

## General docs

| Slug | What it covers | Audience |
|---|---|---|
| `general/configs` | How the config files customise searches, visualisation and system behaviour, and where they are looked up | general |
| `general/model_cookbook` | Systematic reference for composing models with `af.Model` and `af.Collection`: multiple components, prior customisation, parameter pairing, bases | general |
| `general/likelihood_function` | The likelihood the library evaluates, pointing at the workspace notebooks that walk it line by line | advanced |
| `general/workspace` | Tour of the `autogalaxy_workspace` clone: what each folder is for | general |
| `general/citations` | BibTeX for PyAutoGalaxy and its affiliated packages | general |
| `general/papers` | Published work using PyAutoGalaxy — the prior-art starting point | advanced |
| `general/credits` | Developers and contributors | general |

## Installation

| Slug | What it covers |
|---|---|
| `installation/overview` | Which route to take, supported platforms, the dependency list |
| `installation/pip` | venv + `pip install autogalaxy[jax]`, the workspace clone, legacy-Python pinning |
| `installation/conda` | The conda route (required on Windows) |
| `installation/source` | Cloning and installing the libraries for development |
| `installation/numba` | Why numba is optional, and getting it to build |
| `installation/troubleshooting` | The usual failures — pip/conda conflicts, wrong working directory, matplotlib backends |

The curated, cross-checked version of these pages — including the extras table and the
version floors — is [`../operations/installation.md`](../operations/installation.md).
Cite RTD when the user wants the upstream page; cite the operations page when you need the
facts.

## HowToGalaxy on RTD

`howtogalaxy/howtogalaxy` is the chapter index, with one page per chapter
(`howtogalaxy/chapter_1_introduction` … `chapter_4_pixelizations`, plus
`howtogalaxy/chapter_optional`). These are the *rendered* chapter descriptions; the
runnable tutorials live in the HowToGalaxy repository —
see [`howtogalaxy.md`](./howtogalaxy.md) for routing into them.

## API reference

Generated from docstrings, browsable under the API Reference section. The functional
sections, from `PyAutoGalaxy:docs/api/`:

| Page | Covers |
|---|---|
| `api/data` | 2D data structures — masks, arrays, grids, imaging and interferometer datasets |
| `api/galaxy` | The `Galaxy` object and its redshift |
| `api/light` | Light profiles: standard, linear, operated and basis variants |
| `api/fitting` | Fitting imaging and interferometer data, and the fit objects produced |
| `api/modeling` | Analysis objects, searches and priors — the modeling surface |
| `api/pixelization` | Image meshes, meshes and regularization, and the objects that combine them |
| `api/plot` | The visualisation library |
| `api/source` | "Source Code" — internals not normally used directly (geometry profiles and similar); developer-facing |

Note that `api/light` is where the four light-profile flavours are enumerated by module
(`ag.lp` for standard, and the linear / operated / basis siblings). For a task-oriented
version of the same material — which profile to pick, not just which exists — use
[`../api/light_profile_catalog.md`](../api/light_profile_catalog.md).

Don't enumerate individual classes from RTD in an answer. A deep API question is better
served by reading the source, cited as `<Project>:<path>` and resolved through
[`../../../sources.yaml`](../../../sources.yaml), because that is the only reference
guaranteed to match the *installed* version.

## A caveat on the docs' own currency

`PyAutoGalaxy:docs/index.md` contains one stale code sample (it constructs an
object-oriented plotter, a paradigm the plot API no longer has — see
[`../api/plotting.md`](../api/plotting.md)) and one dead cross-link to an overview slug
that does not exist under `docs/overview/`. The overview and installation pages themselves
are current, and the three overview slugs above were checked at the pinned commit. Prefer the slugs tabulated
above, and never lift a code recipe out of RTD without checking it against the installed
API — that is what the code gate exists for.

## See also

- [`index`](./index.md) — the three external resources and audience routing.
- [`workspace`](./workspace.md) — production example scripts.
- [`howtogalaxy`](./howtogalaxy.md) — the from-first-principles lecture series.
- [`skill_citation_map`](./skill_citation_map.md) — which resource each skill cites.
