---
name: ag_setup_environment
description: Install, diagnose and repair the PyAutoGalaxy environment so galaxy-modelling code can actually run — a fresh pip install into a virtualenv, the JAX and numba extras, writable caches for a sandbox or restricted filesystem, the `activate.sh` interpreter resolution, a shared/cluster checkout, and the Google Colab entry point. Use when an import raises, when `--check-install` returns exit 2 or 3, when the user is starting from nothing, when figures fail on a matplotlib backend, or when a run dies inside a numba or cache path. Produces a saved verification script that proves the install works end to end. Not for API drift against a working install (that is `ag_audit_skill_apis` — a `--check-version` exit 1 means the stack imports fine and the *docs* moved), and not for choosing a search or composing a model.
---

# Getting a working PyAutoGalaxy environment

Nothing else in this workspace matters until `import autogalaxy` succeeds in the
interpreter that will run your script. This is worth a skill of its own because the
failure mode is almost never "the package is missing" — it is that the packages are
installed in a *different* interpreter than the one on `PATH`, or that a compiled-code
cache cannot be written, or that JAX resolved a CPU wheel over a CUDA one. Those three
produce three completely different error messages and one identical user experience.

The stack is four PyPI packages — `autonerves`, `autoarray`, `autofit`, `autogalaxy` —
and one command installs all of them, because `autogalaxy` declares the other three
transitively. The rationale, the extras table and every version floor live in
[`../wiki/core/operations/installation.md`](../wiki/core/operations/installation.md);
the cache and short-circuit environment variables live in
[`../wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md). Read whichever
of those two the branch you land in points at — this skill is the procedure, they are the
facts.

## Ask

One question decides the branch, so ask it before typing anything:

- *"Are we installing from scratch, repairing an install that used to work, or setting up
  a hosted/shared environment (Google Colab, an HPC checkout)?"*

And one follow-up when the answer is "repair", because it changes everything:
*"what exactly failed — an `ImportError`, a numba or cache path, a matplotlib backend, or
a JAX/GPU message?"* If they don't know, run the diagnosis branch below and read it off
the output rather than guessing.

## Branch — diagnose before you install anything

Never install over a broken environment; find out which interpreter you are actually in
first. The repo ships a diagnostic that answers that in one call:

```bash
source activate.sh
python autoassistant/audit_skill_apis.py --check-install
```

It prints the interpreter path, the environment prefix, every resolved version, the file
`autogalaxy` was imported from, and whether the install is a wheel or an editable source
checkout (`autogalaxy_assistant:autoassistant/audit_skill_apis.py`). Three exit codes,
three different repairs:

| Exit | Means | Go to |
|---|---|---|
| `0` | Ready — the stack imports in *this* interpreter | "Prove it works" below |
| `2` | The packages are absent from this interpreter | "Fresh install", or just activate the right venv |
| `3` | The packages were found but an import **raised** | "Repair a broken import" |

Exit `2` is far more often the wrong `python` on `PATH` than a genuinely missing install,
which is why the output leads with the interpreter path. Check it against where you
believe you installed before you pip-install anything a second time.

A separate check answers a different question — whether the *documented* API still matches
the installed one:

```bash
python autoassistant/audit_skill_apis.py --check-version
```

Exit `1` there is **not** an environment problem. The stack imports fine and this repo's
prose has drifted from it (or vice versa); that is
[`ag_audit_skill_apis`](./ag_audit_skill_apis.md)'s job, and it owns the baseline. Don't
reinstall anything in response to it. Exit `2`/`3` from `--check-version` are the install
codes above, forwarded, so a red result is never ambiguous between the two causes.

## Branch — a fresh install

Python first: `requires-python = ">=3.12"` across all four packages
(`PyAutoGalaxy:pyproject.toml`), and `autogalaxy_workspace:runtime.txt` targets
`python-3.12.1`, which is the best-tested baseline. On 3.11 and below the install cannot
succeed at all — every earlier wheel on PyPI is yanked, so pip reports "no matching
distribution" rather than silently resolving something ancient.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install "autogalaxy[jax]" numba
```

That is deliberately the exact content of `autogalaxy_workspace:requirements.txt`
(`autogalaxy[jax]` plus `numba`), so an environment built this way already satisfies the
example workspace.

Three things about that command are worth saying out loud, because each is a support
question in disguise:

- **`--upgrade pip` first is not superstition.** Several of the scientific wheels below
  need a modern resolver.
- **The `[jax]` extra is what makes fitting fast**, and it is *not* included by default.
  A plain `pip install autogalaxy` gives a fully working NumPy install; the extra adds
  just-in-time compilation and the GPU path. It installs **CPU** JAX — for a GPU, follow
  the official JAX guide and install the CUDA build **before** `autogalaxy[jax]`, or pip
  will happily resolve the CPU wheel over it.
- **`numba` is separate and optional.** It is not in the `jax` extra, which is why the
  command names it explicitly. It accelerates the compiled geometry kernels in
  PyAutoArray; if it will not build on your platform, the stack runs without it.

`nufftax` only matters if you fit visibilities — skip it otherwise; the library prints
exactly what to install if you reach interferometer code without it. The full extras
table, the conda route and the editable-clone route (for reading or modifying library
source) are in
[`../wiki/core/operations/installation.md`](../wiki/core/operations/installation.md).

### How `activate.sh` resolves the interpreter

This repo ships [`../activate.sh`](../activate.sh), and it resolves the environment
**relative to the script's own location**, so it behaves identically whether you
`source activate.sh` from the repo root or a batch job sources it by absolute path. It
tries two locations in order:

1. `<repo>/.venv/bin/activate` — a virtualenv created inside this clone, which is exactly
   what the `python3.12 -m venv .venv` above produces.
2. `$PYAUTO_HPC_BASE/PyAuto/bin/activate` — a shared or cluster checkout. Point
   `PYAUTO_HPC_BASE` at a directory holding a `PyAuto/` virtualenv alongside source
   checkouts of the four libraries; the script activates the venv and prepends those
   checkouts to `PYTHONPATH` in dependency order.

If neither exists it prints a one-line diagnostic rather than failing silently. If your
venv lives somewhere else entirely (`~/venv/PyAuto`, say), edit `VENV` at the top of the
file rather than working around it every session.

## Branch — repair a broken import (`--check-install` exit 3)

Exit 3 means the packages resolved and then something raised. In practice it is one of
four things, in descending order of frequency.

**1. An unwritable cache.** The libraries cache compiled code and plot configuration under
your home directory, and in a container, in CI, on a read-only home, or on an install
imported from a `/mnt/c/...` Windows mount under WSL, those writes fail — usually with a
confusing message buried inside a numba traceback:

```bash
export NUMBA_CACHE_DIR=/tmp/numba_cache
export MPLCONFIGDIR=/tmp/matplotlib
```

Set them once per shell or bake them into the venv activation. `--check-install` already
sets equivalent temporary defaults for its *own* imports, but only when they are unset, so
a deliberate choice of yours is never overridden.

**2. The JAX compilation cache.** With JAX installed,
`PyAutoNerves:autonerves/jax_wrapper.py` enables a persistent compilation cache under
`$XDG_CACHE_HOME/pyauto_jax` (or `~/.cache/pyauto_jax`) so the minutes spent compiling a
given model/data shape are paid once per machine rather than once per process. In a
sandbox, point `JAX_COMPILATION_CACHE_DIR` somewhere writable, or set it to the **empty
string** to disable the cache outright. The same module sets `XLA_FLAGS` and
`JAX_ENABLE_X64=True` *before* JAX is imported — which is why workspace scripts that use
JAX open with `from autogalaxy import jax_wrapper` ahead of their other imports. Setting
those after JAX has loaded has no effect, so an import you reorder "for tidiness" can
silently change your numerics.

**3. The matplotlib backend.** If a figure call hangs, raises, or kills the process with
no message, the backend is misconfigured for your system. It is read from
`config/visualize/general.yaml` → `general:` → `backend:`, whose default is `default`
(your system's own). `autogalaxy_workspace:welcome.py` exists largely to surface this one
interactively, and suggests `TKAgg`, `Qt5Agg` or `Qt4Agg` as replacements. Since every
plot this workspace produces is written to disk rather than displayed (see
[`_style.md`](./_style.md) "Plot output and path announcement"), an `Agg` backend is
usually the right answer for an agent-driven session.

**4. A dependency pushed past its cap.** The stack pins upper bounds deliberately —
`scipy<=1.17.1`, `astropy>=5.0,<=7.2.0`, `numpy>=1.24.0,<3.0.0`, `jax>=0.7.0,<0.11.0`,
and exact pins on `dynesty` and `nautilus-sampler`. These are the ones that bite, because
forcing a newer version tends to break inside a mesh routine or a sampler's internals
rather than at import. The full list is in the installation page's "Version floors and
caps".

One more failure that looks like a broken install and is not: a **working-directory**
error. PyAutoGalaxy resolves `config/`, `dataset/` and `output/` relative to the current
directory, so running a workspace script from the wrong place produces import-shaped and
file-not-found-shaped errors that have nothing to do with the install.
`PyAutoGalaxy:docs/installation/troubleshooting.md` lists it first for good reason. Run
workspace scripts from the workspace root; run this repo's scripts from this repo's root.
A related, harmless warning: `PyAutoNerves:autonerves/workspace.py` compares a workspace
clone's version to the installed library and warns on a mismatch —
`PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1` silences it when the two intentionally diverge.

## Branch — Google Colab

Don't hand-write install cells. `PyAutoNerves:autonerves/setup_colab.py` exposes a
per-project entry point, `for_autogalaxy(raise_error_if_not_gpu=...)`, which installs the
stack, clones the workspace and checks whether JAX actually found a GPU. The guard that
makes it work both in and out of Colab is the one every workspace `start_here` uses
(`autogalaxy_workspace:start_here.py`):

```python
try:
    import google.colab
except ImportError:
    from autogalaxy import setup_colab as _setup_colab
else:
    import importlib
    import subprocess
    import sys

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "autonerves", "--no-deps"]
    )
    _setup_colab = importlib.import_module("autonerves.setup_colab")

_setup_colab.for_autogalaxy(
    raise_error_if_not_gpu=False  # True to hard-fail when no GPU was found
)
```

Outside Colab the same block is a no-op verification pass, so it is safe to leave at the
top of a script you also run locally. Set `raise_error_if_not_gpu=True` when a GPU is the
whole point of the run and you would rather fail loudly than discover 40 minutes later
that you were on a CPU.

## Prove it works

An install that imports is not yet an install that fits galaxies. Save a verification
script — it takes seconds to run and it exercises the config layer, the array structures,
a light-profile evaluation and the plot path, which between them cover every failure above.

```python
"""
Environment Verification: PyAutoGalaxy
======================================

Prove a PyAutoGalaxy install is usable end to end, not merely importable. Each section
exercises one layer that fails independently: package resolution, the YAML configuration
tree, the array/grid structures, a light-profile evaluation, and writing a figure to disk.
Run this after any install, repair or interpreter change, and read the printed paths — a
wrong interpreter or an unwritable cache shows up here rather than three hours into a fit.

__Contents__

- **Imports:** Import the stack and report which interpreter and files were resolved.
- **Grid:** Build a `Grid2D` and confirm the pixel-to-arcsecond conversion.
- **Light Profile:** Evaluate a Sersic profile on the grid — the first real numerical work.
- **Plot:** Write a figure to disk and print its absolute path.
"""

"""
__Imports__

Importing all four packages separately is deliberate: they form a dependency chain
(`autonerves` → `autoarray` → `autofit` → `autogalaxy`), so a failure names the layer that
broke rather than reporting a generic `autogalaxy` error. `__file__` is printed because the
single most common install problem is not a missing package but a *different interpreter*
than the one you installed into.
"""
import sys
from pathlib import Path

import autonerves
import autoarray
import autofit as af
import autogalaxy as ag
import autogalaxy.plot as aplt

print(f"interpreter: {sys.executable}")
print(f"autonerves={autonerves.__version__}  autoarray={autoarray.__version__}")
print(f"autofit={af.__version__}  autogalaxy={ag.__version__}")
print(f"autogalaxy imported from: {ag.__file__}")

"""
__Grid__

The `Grid2D` is the (y,x) coordinate grid every light profile is evaluated on, and
`pixel_scales` is the arcseconds-per-pixel conversion that ties it to a real detector.
Constructing one touches the configuration tree, so a config-resolution failure surfaces
here (`PyAutoArray:autoarray/structures/grids/uniform_2d.py`).
"""
grid = ag.Grid2D.uniform(shape_native=(50, 50), pixel_scales=0.1)

print(f"grid shape: {grid.shape_native}, pixel scale: {grid.pixel_scales}")

"""
__Light Profile__

An elliptical Sersic is the workhorse profile of galaxy morphology, and evaluating its
image is the first genuinely numerical operation — it is where a numba cache that cannot be
written, or a NumPy pushed past its version cap, actually fails
(`PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py`). `ell_comps` is the
elliptical-components parameterisation used throughout the library in place of an
axis-ratio and position-angle pair.
"""
bulge = ag.lp.Sersic(
    centre=(0.0, 0.0),
    ell_comps=(0.2, 0.1),
    intensity=1.0,
    effective_radius=0.8,
    sersic_index=4.0,
)

image = bulge.image_2d_from(grid=grid)

print(f"image sum: {float(image.sum()):.4f}, peak: {float(image.max()):.4f}")

"""
__Plot__

The final layer is visualisation, which depends on the matplotlib backend and on a writable
`MPLCONFIGDIR`. The plot API is function-based: `output_path`, `output_filename` and
`output_format` are passed straight to the call, and nothing is displayed interactively —
so this works identically in a terminal, a notebook and a headless job.
"""
PLOT_DIR = Path("scripts") / "scratch" / "environment_check"

aplt.plot_array(
    array=image,
    title="Sersic Light Profile",
    output_path=PLOT_DIR,
    output_filename="sersic",
    output_format="png",
)

print(f"Saved to: {PLOT_DIR.resolve()}")
```

Run it, then **quote the printed absolute path back to the user and offer to open it**
(`xdg-open` on Linux, `open` on macOS, `explorer.exe` or `wslview` from WSL). A figure the
user can actually see is the only proof that the last layer works.

For a guided, interactive version of the same idea, `autogalaxy_workspace:welcome.py`
walks a new user through the working-directory rule and the matplotlib backend with
`input()` prompts — worth pointing at rather than reproducing when someone is setting up
their own machine for the first time.

## Fast iteration once it works

While you are still shaping a script rather than measuring a galaxy, the stack ships flags
that turn a fit into a structural check. `PYAUTO_TEST_MODE=1` cuts the sampler to its
minimum iterations, `=2` bypasses the sampler and calls the likelihood **once**, and `=3`
skips the likelihood too (`PyAutoNerves:autonerves/test_mode.py`). A representative
combination, with the cache variables from above:

```bash
PYAUTO_TEST_MODE=2 PYAUTO_SMALL_DATASETS=1 \
  NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/your_script.py
```

Two consequences catch everyone once. Test-mode output is **namespaced** into
`output/test_mode/...`, deliberately, so a cached structural run cannot short-circuit a
later real fit with "Fit Already Completed". And the returned parameter values are **not
physically meaningful at any level** — never quote an effective radius or Sersic index
measured in test mode. `PYAUTO_DISABLE_JAX=1` is the other lever worth knowing: it forces
every analysis onto NumPy, whose tracebacks are far easier to read than JAX's when you are
isolating whether a failure is a JAX problem at all. The full flag list is in
[`../wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md).

## Combine — where to go next

- **The install is clean and you have your own FITS files** → the data-preparation skill
  ([`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md)), which also owns the
  real-data inspection gate.
- **The install is clean and you have no data yet** → simulate one with known truth
  ([`ag_simulate_dataset`](./ag_simulate_dataset.md)); it is the fastest way to confirm the
  whole modelling loop runs before real data is at stake.
- **`--check-version` went red** → [`ag_audit_skill_apis`](./ag_audit_skill_apis.md), which
  owns the baseline and the four other currency checks.
- **A fit ran and then failed or returned nonsense** → the fit-failure debugging skill
  (`ag_debug_fit_failure`), not this one; the environment is no longer the suspect once a
  likelihood has been evaluated.

Ask if you want the editable-clone route instead — it is the setup you need if you intend
to read or modify library source rather than only call it.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Visualization and setup](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_1_introduction/tutorial_0_visualization.ipynb):
  the setup tutorial — working directory, matplotlib options, and how figures are
  configured. The right first stop when plots are the thing misbehaving.
- **General reference** — [RTD: Installation overview](https://pyautogalaxy.readthedocs.io/en/latest/installation/overview.html):
  the upstream installation index, with the pip, conda, source, numba and troubleshooting
  pages beneath it.
- **Experienced PyAutoGalaxy user** — [workspace: start_here.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/imaging/start_here.py):
  the canonical imaging script, including the Colab setup block and the JAX notes — the
  fastest end-to-end proof that a fresh environment really works.

## Agent procedural checklist

1. Ask: fresh install, repair, or hosted/shared environment?
2. `source activate.sh`; `python autoassistant/audit_skill_apis.py --check-install`.
3. Exit 2 → check the printed interpreter *before* reinstalling; then the fresh-install
   branch. Exit 3 → the repair branch, starting with the cache variables.
4. Never install over a broken environment, and never re-pin a baseline to silence a check.
5. Save and run the verification script; print and then **quote** the figure's absolute
   path, and offer to open it once.
6. `--check-version` exit 1 → hand off to `ag_audit_skill_apis`; do not reinstall.
7. Offer (default-yes) a dated `wiki/project/YYYY-MM-DD-<slug>.md` entry only if the
   environment work was non-trivial — a genuine repair worth remembering, not a routine
   install.
