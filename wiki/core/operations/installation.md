---
title: Installation
sources:
  - project: PyAutoGalaxy
    paths:
      - pyproject.toml
      - docs/installation/overview.md
      - docs/installation/pip.md
      - docs/installation/conda.md
      - docs/installation/source.md
      - docs/installation/numba.md
      - docs/installation/troubleshooting.md
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: PyAutoNerves
    paths:
      - pyproject.toml
      - autonerves/setup_colab.py
    pinned_commit: e82c17fd6c8966f6b3a2f6ffbcb655db7035fdb1
  - project: PyAutoArray
    paths:
      - pyproject.toml
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: PyAutoFit
    paths:
      - pyproject.toml
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: autogalaxy_workspace
    paths:
      - requirements.txt
      - runtime.txt
      - welcome.py
    pinned_commit: d6db2643b9f2cd418efc9473f560dc2a2d459c73
  - project: autogalaxy_assistant
    paths:
      - activate.sh
      - autoassistant/audit_skill_apis.py
    pinned_commit: ed72fabb33e14a9a701a4d280e8775dd3a20e98c
last_updated: 2026-08-01
content_sha256: 8999fa2a4700ae1fe2db2782fe66bdb222eadf78d35db474b6043da47155167c
---

# Installation

The galaxy-modelling stack is four packages published to PyPI —
`autonerves`, `autoarray`, `autofit`, `autogalaxy` — and one command installs all of
them, because `autogalaxy` declares the other three transitively
(`PyAutoGalaxy:pyproject.toml` requires `autofit` and `autoarray`; both require
`autonerves`).

```bash
pip install autogalaxy
```

That is the whole install for most users. Everything below is detail: which extras to
add, what the version floors mean, and how to prove the install works before you fit a
galaxy with it.

This page is the *rationale*; [`../../../skills/ag_setup_environment.md`](../../../skills/ag_setup_environment.md)
is the procedure that drives install and repair in code, and it cites this page. The checks in
"Verifying the install" below are the mechanical part either way.

## Python version

`requires-python = ">=3.12"` across all four packages. The classifiers in
`PyAutoGalaxy:pyproject.toml` name 3.12, 3.13 and 3.14; `autogalaxy_workspace`'s
`runtime.txt` targets `python-3.12.1`, which is the best-tested baseline.

Two things worth knowing before you debug a failing install:

- **3.11 and below cannot install it.** Support was dropped in release
  `2026.7.29.2` — the first one published declaring `Requires-Python >=3.12`. The
  back catalogue was *not* yanked and could not be (396 of 421 `autolens` releases
  are live), so until 2026-08-19 `pip install autogalaxy` on 3.9/3.10/3.11 did
  exactly what you would not want: it walked back to `2026.7.29.1` and silently
  installed a months-old, JAX-less stack. The fix is release
  `2026.7.29.1.post1` — no code, `Requires-Python <3.12`, raises on build — so
  those Pythons now get an explanation instead. An explicit pin
  (`pip install autogalaxy==2025.10.6.1`) still resolves if an old project needs
  it, and `--only-binary=:all:` still steps past the tombstone to the old wheel.
- **The RTD installation overview still says "Python 3.12 - 3.13"**
  (`PyAutoGalaxy:docs/installation/overview.md`). `pyproject.toml` is the authority and it
  is the looser of the two; treat 3.14 as supported and 3.12 as the safe default.

## Pip install (most users)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install "autogalaxy[jax]" numba
```

`pip install --upgrade pip` first is not superstition — several of the scientific wheels
below need a modern resolver.

### What the extras contain

`PyAutoGalaxy:pyproject.toml` defines these `[project.optional-dependencies]`:

| Extra | Pulls in | Install it when |
|---|---|---|
| `jax` | `autofit[jax]` (→ `autonerves[jax]`: `jax`/`jaxlib` `>=0.7.0,<0.11.0`, `jaxnnls`; plus `optax`) and `jax_zero_contour` | Almost always — JAX is the accelerated evaluation path, on CPU and GPU |
| `optional` | `autogalaxy[jax]`, `numba`, `zeus-mcmc`, `getdist` | You want the full set in one command |
| `test` | `pytest`, `colossus` | You are running PyAutoGalaxy's own test suite |
| `docs` | Sphinx + theme packages | You are building the RTD site |

**JAX is not installed by default.** A plain `pip install autogalaxy` gives a fully
working NumPy install; the `[jax]` extra adds just-in-time compilation and the GPU path.
The extra installs *CPU* JAX — for GPU, follow the official JAX installation guide and
install the CUDA build **before** installing `autogalaxy[jax]`, so pip does not resolve
the CPU wheel over it.

**`numba` is separate and optional.** It is not in the `jax` extra; add it explicitly
(as the command above does) or via the `optional` extra. It accelerates the
JIT-compiled geometry kernels in PyAutoArray. If it will not build on your platform,
PyAutoGalaxy runs without it — see `PyAutoGalaxy:docs/installation/numba.md`.

**`nufftax` is only for interferometer work.** It is not in PyAutoGalaxy's `optional`
extra — install it explicitly with `pip install nufftax`. Skip it unless you fit
visibilities; if you do run interferometer code without it, the library prints a message
telling you exactly what to install.

### Conda

`PyAutoGalaxy:docs/installation/conda.md` documents the conda route (create the env with
conda, then `pip install` into it). Windows users are pointed at Anaconda specifically.
The dependency set is identical; only the environment manager differs.

## Editable-clone install (developers / contributors)

Needed when you want to *read or modify* the libraries — adding a light profile,
debugging an internal, preparing an upstream contribution.

```bash
mkdir -p sources && cd sources
git clone https://github.com/PyAutoLabs/PyAutoNerves.git
git clone https://github.com/PyAutoLabs/PyAutoArray.git
git clone https://github.com/PyAutoLabs/PyAutoFit.git
git clone https://github.com/PyAutoLabs/PyAutoGalaxy.git
cd ..

for repo in PyAutoNerves PyAutoArray PyAutoFit PyAutoGalaxy; do
    pip install -e "sources/$repo"
done
```

Install **bottom-up** — that is the dependency order in
[`../../../sources.yaml`](../../../sources.yaml) (`dependency_chain`), and each `pip
install -e` needs the layer below it already resolvable. Resolve the git URLs from
`sources.yaml` rather than the literal URLs above; the YAML is the source of truth and
survives a repository move.

`PyAutoGalaxy:docs/installation/source.md` is the upstream equivalent of this section.

## The assistant's `activate.sh`

This repo ships [`../../../activate.sh`](../../../activate.sh), which resolves the
environment **relative to the script's own location**, so it behaves the same whether you
`source activate.sh` from the repo root or a batch script sources it by absolute path. It
tries two locations in order:

1. `<repo>/.venv/bin/activate` — a virtualenv created inside this clone. This is the
   default and the one the pip route above produces if you make `.venv` here.
2. `$PYAUTO_HPC_BASE/PyAuto/bin/activate` — a shared or cluster checkout. Set
   `PYAUTO_HPC_BASE` to a directory holding a `PyAuto/` virtualenv alongside source
   checkouts of the four libraries; the script activates the venv and prepends those
   checkouts to `PYTHONPATH` in dependency order.

If neither exists it prints a one-line diagnostic rather than failing silently. The
commented block at the foot of the file shows the developer variant: skip the venv and
put local source checkouts on `PYTHONPATH` directly.

## Version floors and caps worth knowing

The stack pins several dependencies to keep numerical results reproducible. From each
project's `pyproject.toml`:

- **PyAutoNerves** — `numpy>=1.24.0,<3.0.0`, `PyYAML>=6.0.1`.
- **PyAutoArray** — `scipy<=1.17.1`, `scikit-image<=0.26.0`, `scikit-learn<=1.8.0`,
  `matplotlib>=3.7.0`, `astropy>=5.0,<=7.2.0`.
- **PyAutoFit** — `dynesty==2.1.5`, `emcee>=3.1.6`, `corner==2.2.2`, `networkx==3.1`,
  `SQLAlchemy>=2.0.32,<2.1.0`, `scipy<=1.17.1`.
- **PyAutoGalaxy** — `astropy>=5.0,<=7.2.0`, `nautilus-sampler==1.0.5`.
- **JAX** (via `autonerves[jax]`) — `jax`/`jaxlib` `>=0.7.0,<0.11.0`.

The upper bounds are the ones that bite: forcing a newer `scipy` or `numpy` past its cap
tends to break in non-obvious places (a mesh routine, a sampler's internals) rather than
at import. Stay inside the ranges unless you have a specific need and have checked the
stack supports it.

## The workspace

The library is the engine; `autogalaxy_workspace` is the example catalogue you actually
run. It is a separate clone, not a pip package:

```bash
git clone https://github.com/PyAutoLabs/autogalaxy_workspace --depth 1
cd autogalaxy_workspace
python3 welcome.py
```

Its `requirements.txt` is exactly `autogalaxy[jax]` and `numba`, so an environment built
by the pip section above already satisfies it. Scripts are run **from the workspace root**
(`python scripts/imaging/start_here.py`) — a wrong working directory is the single most
common "it worked yesterday" install problem, and
`PyAutoGalaxy:docs/installation/troubleshooting.md` lists it first. Routing into the
catalogue is [`../external/workspace.md`](../external/workspace.md).

## Google Colab

`PyAutoNerves:autonerves/setup_colab.py` exposes a per-project entry point,
`for_autogalaxy`, which installs the stack, clones the workspace and checks whether JAX
actually found a GPU. Use it instead of hand-writing install cells in a notebook.

## Verifying the install

The blunt check:

```bash
python -c "import autonerves, autoarray, autofit, autogalaxy; print(autogalaxy.__version__)"
```

The useful check — it reports the interpreter, the environment prefix, every resolved
version, where `autogalaxy` was imported from, and whether the install is a wheel or an
editable source checkout:

```bash
python autoassistant/audit_skill_apis.py --check-install
```

Exit `0` = ready. Exit `2` = the packages are absent from *this* interpreter (usually the
wrong `python` on `PATH` — activate the venv). Exit `3` = the packages were found but an
import raised, which is a broken environment rather than a missing one; the output groups
identical errors so a single multi-paragraph failure is printed once. It also sets
writable `NUMBA_CACHE_DIR` / `MPLCONFIGDIR` defaults if they are unset, which is what
lets it run in the restricted environments described in [`sandbox`](./sandbox.md).

Once the stack imports, the second question is whether the *documented* API still matches
it:

```bash
python autoassistant/audit_skill_apis.py --check-version
```

That compares the installed public API surface against the committed baseline. Exit 1
there is API drift, not a broken install — see
[`../../../skills/ag_audit_skill_apis.md`](../../../skills/ag_audit_skill_apis.md).

## See also

- [`sandbox`](./sandbox.md) — cache directories, `PYAUTO_TEST_MODE` and the other
  environment variables restricted environments need.
- [`../stack/overview`](../stack/overview.md) — what each of the four packages does and
  why the install order is what it is.
- [`../api/configuration`](../api/configuration.md) — the `config/` tree the workspace
  and this repo ship, and how it overrides library defaults.
- [`../external/rtd`](../external/rtd.md) — the upstream installation pages, per audience.
