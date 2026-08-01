---
name: ag_run_search
description: Run the fit — take a composed model, an analysis and a configured search and drive `search.fit(model=model, analysis=analysis)` to completion, then read what it wrote. Covers the output-folder anatomy and the on-the-fly announcement, the unique-identifier resume behaviour and when it silently reuses a stale fit, `iterations_per_quick_update` and `live_visual_update`, JAX/GPU acceleration and when it actually pays, VRAM checks before a long GPU run, the `PYAUTO_TEST_MODE` smoke levels, and the `if __name__ == "__main__"` parallelisation fix. Use once `ag_build_imaging_model` and `ag_configure_search` have produced `model`, `analysis` and `search` objects, or when a fit is running and the user wants to know what to watch. Not for composing the model or choosing the search (those two skills), not for interpreting the finished posterior (`ag_load_results`), and not for diagnosing a fit that ran but converged somewhere unphysical (`ag_debug_fit_failure`).
---

# Running the fit

This is the moment the inference actually happens. Everything before it was preparation:
a `model` says which morphological parameters are free and what priors they carry, an
`analysis` binds that model to one dataset and knows how to turn a parameter vector into a
log likelihood, and a `search` knows how to explore the parameter space. One call joins
them:

```python
result = search.fit(model=model, analysis=analysis)
```

Statistically, that call is sampling (or optimising) the posterior
$P(\theta | d) \propto \mathcal{L}(d | \theta) P(\theta)$, where the likelihood is the
Gaussian-noise chi-squared of the PSF-convolved model image against the data — walked
line by line in `autogalaxy_workspace:scripts/imaging/likelihood_function.py`. Scientifically,
it is where a Sersic index, an effective radius or a bulge-to-total ratio stops being a guess
and becomes a measurement with errors. What this skill adds is everything *around* the call:
how to watch it, how long to expect, how to make it fast, and how to prove the script works
before committing hours to it.

Two wiki pages carry the background this skill assumes. Read
[`wiki/core/concepts/non_linear_search.md`](../wiki/core/concepts/non_linear_search.md) for
what each sampler does and how run time scales with the model, and
[`wiki/core/api/analysis_objects.md`](../wiki/core/api/analysis_objects.md) for what the
returned `Result` contains.

## Ask

Three questions, and the answers change the branch:

- *"Do you already have `model`, `analysis` and `search`?"* If not, route to
  [`ag_build_imaging_model`](./ag_build_imaging_model.md) and
  [`ag_configure_search`](./ag_configure_search.md) first. A fit assembled from a
  half-remembered model is the most expensive mistake available here.
- *"Smoke test first, or straight to the production run?"* Almost always smoke test first —
  it takes seconds and answers "does this script execute end to end?", which is a different
  question from "is this galaxy's Sersic index 3.2?". The smoke branch is below.
- *"How long can this run, and on what?"* A `MultiStartProdigy` fit is minutes; a `Nautilus`
  fit of a smooth model is tens of minutes on a GPU and can be hours on a CPU; a pixelised
  fit can be far longer. That answer decides foreground vs background, laptop vs cluster,
  and whether `live_visual_update` is worth switching on.

If the data is real observational imaging, the inspection gate in
[`../AGENTS.md`](../AGENTS.md) applies before you get here at all — contaminants and mask
extent are settled in [`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md), not
retrospectively.

## Branch — the production run

The deliverable is one script in `scripts/` the user can re-run and edit. Adapted from
`autogalaxy_workspace:scripts/imaging/start_here.py` (the fit and result sections) and
`autogalaxy_workspace:scripts/imaging/modeling.py` (the Nautilus configuration and the VRAM
check):

```python
"""
Galaxy Structure: Run the Fit
=============================

Fit a galaxy's surface-brightness profile to CCD imaging: load and mask the data, compose a
linear Sersic bulge, and sample the posterior with Nautilus so the inferred effective radius
and Sersic index come with errors.

__Contents__

- **Imports:** JAX environment first, then the standard trio.
- **Dataset:** Load imaging, mask it, and apply adaptive over-sampling.
- **Model:** Compose the galaxy's light profile.
- **Search:** Configure Nautilus and its update cadence.
- **Analysis:** Bind the model to the data and choose the JAX backend.
- **Model-Fit:** Run the search and announce the output folder.
- **Result:** Read the best-fit model back.
"""
from autogalaxy import jax_wrapper  # Sets the JAX environment before other imports

from pathlib import Path

import autofit as af
import autogalaxy as ag
import autogalaxy.plot as aplt

"""
__Dataset__

Galaxy modeling needs three ingredients: the image in CCD counts, a per-pixel RMS noise-map,
and the PSF. The PSF is forward-modelled rather than divided out, which is what separates a
genuinely compact bulge from a seeing-broadened one. `pixel_scales` converts pixels to
arcseconds and must match the instrument (`ag.Imaging.from_fits`,
`PyAutoArray:autoarray/dataset/imaging/dataset.py`).

The mask sets which pixels enter the likelihood, and its radius is a science choice, not a
default: truncate the outer isophotes and the effective radius and Sersic index are biased
directly. Over-sampling evaluates the light profile several times per pixel where the
gradient is steep, which matters most in the central few tenths of an arcsecond
(`ag.util.over_sample.over_sample_size_via_radial_bins_from`).
"""
DATASET_PATH = Path("dataset") / "imaging" / "<your_galaxy>"
MASK_RADIUS = 2.5

dataset = ag.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    psf_path=DATASET_PATH / "psf.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    pixel_scales=0.1,
)

mask = ag.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=MASK_RADIUS,
)

dataset = dataset.apply_mask(mask=mask)

over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[8, 4, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)

dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

"""
__Model__

A linear `Sersic` bulge: the `intensity` is solved by linear inversion each iteration rather
than sampled, so the search explores one fewer dimension per component for free
(`autogalaxy_workspace:scripts/imaging/modeling.py` `__Linear Light Profiles__`).
"""
bulge = af.Model(ag.lp_linear.Sersic)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))

print(model.info)

"""
__Search__

`Nautilus` is nested sampling: it returns the full posterior — every parameter's density,
its errors, and the correlations between them. `n_live` trades accuracy against run time and
200 covers the vast majority of galaxy models. `unique_tag` is conventionally the dataset
name, which is what keeps the same model fitted to different data in different folders
(`PyAutoFit:autofit/non_linear/search/nest/nautilus/search.py`).
"""
search = af.Nautilus(
    path_prefix=Path("imaging"),
    name="sersic",
    unique_tag="<your_galaxy>",
    n_live=200,
    iterations_per_quick_update=10000,
    live_visual_update=False,
)

"""
__Analysis__

`ag.AnalysisImaging` defines the `log_likelihood_function` the search calls, and defaults to
`use_jax=True` when JAX is installed (`PyAutoGalaxy:autogalaxy/imaging/model/analysis.py`).
"""
analysis = ag.AnalysisImaging(dataset=dataset, use_jax=True)

"""
__Model-Fit__

Results are written to the output folder on the fly, from the best model found so far, so the
folder is worth opening the moment the search starts.
"""
print(f"Output folder: {search.paths.output_path.resolve()}")

result = search.fit(model=model, analysis=analysis)

"""
__Result__
"""
print(result.info)
print(result.max_log_likelihood_instance)
```

Run it with writable caches if the default locations are not writable — a sandbox, CI, or an
install imported from a Windows mount under WSL
([`wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md)):

```bash
NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib python scripts/run_fit.py
```

`search.fit` itself is `PyAutoFit:autofit/non_linear/search/abstract_search.py`.

## Branch — what the output folder contains, and when to look

**Announce the folder at launch, not at the end.** Quote
`search.paths.output_path.resolve()` once the fit is running and say plainly that
`model.results` and `image/fit.png` refresh as the search goes — there is nothing to wait
for. Users new to the stack sit watching a silent terminal because nobody told them.

The annotated tree of `files/`, `image/`, `model.info`, `model.results`, `search.summary`
and the `<unique_hash>` folder is `__Output Folder Layout__` in
[`autogalaxy_workspace/scripts/imaging/modeling.py`](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/imaging/modeling.py);
the same section appears in the `interferometer`, `multi_dataset`, `multi_galaxy` and
`cluster` `modeling.py` scripts. Link it rather than copying the tree into the conversation,
where it would rot. The condensed version is also in
[`wiki/core/concepts/non_linear_search.md`](../wiki/core/concepts/non_linear_search.md)
"The output folder".

Name what to open first, in this order:

1. `model.results` — the human-readable fit summary, parameters with errors.
2. `image/fit.png` — data, model image, residuals and chi-squared map in one figure.
3. `search.log` — tail it if you want to watch progress from a terminal.

Depth follows [`_style.md`](./_style.md) "Adaptive depth": for a newcomer, or in teacher
mode, walk all three. For a returning user, quoting the path is enough.

## Branch — resuming, and the trap inside it

`<unique_hash>` is derived from the model, the search settings and the dataset identifier, so
re-running an identical configuration **resumes** the existing fit rather than restarting it
(`autogalaxy_workspace:scripts/imaging/modeling.py` `__Unique Identifier__`). That is a
feature — an interrupted overnight run picks up where it stopped.

It is also the sharpest edge in the workflow. **The identifier does not hash the pixel
values of your data.** Swap `data.fits` for a different galaxy, keep the model, the search
and the `unique_tag` identical, and the next run finds a completed fit at the same path and
returns it — silently, in seconds, with the previous galaxy's parameters. If the data
changes, change the `unique_tag`. If you are unsure whether a result is stale, delete the
`<unique_hash>` folder and re-run rather than reasoning about it.

Test mode namespaces its output separately: any active `PYAUTO_TEST_MODE` level inserts a
`test_mode` segment straight after the output root, so a smoke run lands in
`output/test_mode/<path_prefix>/...` and cannot short-circuit a later real fit
([`wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md)).

## Branch — the update cadence and the live view

Two settings control what you see while the fit runs, both on the search
(`PyAutoFit:autofit/non_linear/search/abstract_search.py`):

- **`iterations_per_quick_update`** — how often the current best model is visualised and
  written to disk. The unit depends on the search: likelihood evaluations for `Nautilus`
  (hence the large `10000` in `modeling.py`), gradient steps for `MultiStartProdigy` (hence
  the much smaller `50` in `start_here.py`). Each update costs roughly ten seconds, so too
  low a value and output dominates the run time; too high and you cannot see progress. If
  the log is constantly reporting that it is outputting results, raise it.
- **`live_visual_update`** — additionally push the quick-update image to a live surface: a
  matplotlib window that refreshes in a plain script, or a self-updating cell in Jupyter and
  Colab. The `fit.png` disk write happens either way. Leave it `False` on anything headless
  — an HPC node, a background process, CI.

If the search configuration already records the choice, don't re-ask; that decision belongs
to [`ag_configure_search`](./ag_configure_search.md).

## Branch — JAX, GPUs, and when the acceleration pays

Imaging fits run through JAX by default. Installing the extra (`pip install autogalaxy[jax]`)
is all that is required: `ag.AnalysisImaging` then defaults to `use_jax=True`, and the search
driver wraps the likelihood in `jax.vmap(jax.jit(...))` so a whole batch of parameter vectors
evaluates in one call. You will see a one-time log line as the JIT compile starts; every
evaluation after that re-uses the compiled trace. This is described in
`autogalaxy_workspace:scripts/guides/using_jax.py` `__Auto-Enabled Modeling__`, and if JAX is
absent the analysis warns once and falls back to NumPy.

**When it pays.** The gain scales with how much array work each likelihood evaluation does,
so it is largest for big masks, fine over-sampling, many-component bases and pixelised
reconstructions, and smallest for a tiny mask with one smooth profile. GPU gains dwarf CPU
gains: `autogalaxy_workspace:scripts/imaging/modeling.py` `__JAX__` quotes roughly ten
minutes on a GPU against an hour on a CPU for its example, with a CPU still gaining from
multithreading. Gradient-based searches like `MultiStartProdigy` are not merely faster under
JAX — they are only possible with it, because JAX is what supplies the likelihood's
derivatives and evaluates all the parallel starts in one batched call
(`autogalaxy_workspace:scripts/imaging/start_here.py` `__Multi Start Gradient Optimization__`).

**Check VRAM before a long GPU run.** A JAX fit must fit inside the GPU's memory, and it
fails at JIT-compile time or on the first likelihood call if it does not:

```python
analysis.print_vram_use(model=model, batch_size=search.batch_size)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py` `__VRAM Use__`. It takes
twenty or thirty seconds, so comment it out once you know your model's footprint. Batch size
is the lever: larger batches cut wall-clock time and raise VRAM, smaller batches the reverse.
A smooth-profile fit on a modest dataset is tens of megabytes; a pixelised reconstruction on
high-resolution data can exceed ten gigabytes.

**Turn JAX off to debug.** `ag.AnalysisImaging(dataset=dataset, use_jax=False)`, or
`PYAUTO_DISABLE_JAX=1` to force it globally without editing code. NumPy stack traces are far
easier to read, and you can drop a debugger or a `print` into code JAX would otherwise
compile. That is the first lever to pull when deciding whether a failure is a JAX problem at
all — see [`ag_debug_fit_failure`](./ag_debug_fit_failure.md).

For running on a cluster — SLURM array jobs, one dataset per task, the CPU and GPU batch
scripts, and `number_of_cores` read from `SLURM_CPUS_PER_TASK` — the ground truth is
`autogalaxy_workspace:scripts/guides/hpc/example_cpu_and_gpu.py`. The Python modeling code is
identical for a GPU run; only the batch script changes. This repo has no HPC operations page
yet ([`../PENDING.md`](../PENDING.md)), so cite that script rather than a page that does not
exist.

## Branch — the smoke test, before you spend hours

Every script gets one fast structural run before a real one. `PYAUTO_TEST_MODE` has four
levels ([`wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md)), and the
choice between them matters more than it looks:

```bash
# Level 1 — sampler runs with minimal iterations. A real (tiny) search: writes
# model.results, image/fit.png and a samples.csv you can load back.
PYAUTO_TEST_MODE=1 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/run_fit.py

# Level 2 — sampler bypassed, likelihood called exactly once. The fastest proof that
# the model composes and the likelihood evaluates.
PYAUTO_TEST_MODE=2 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/run_fit.py
```

**Level 2 does not write the fit products.** A level-2 run returns a `Result`, proving the
wiring, but leaves no `model.results` and no `image/fit.png` behind — so if the next thing
you want to do is plot or load the fit, use level 1. Level 3 skips the likelihood call as
well, which is only useful for checking that a script's non-fitting scaffolding runs.

**The parameter values from any test-mode run are meaningless.** The sampler was truncated or
mocked. Never quote a structural parameter measured in test mode; say explicitly that the
number is a wiring check.

For the fastest possible loop, combine test mode with the dataset and output short-circuits:

```bash
PYAUTO_TEST_MODE=2 PYAUTO_SKIP_FIT_OUTPUT=1 PYAUTO_SKIP_VISUALIZATION=1 \
  PYAUTO_SMALL_DATASETS=1 PYAUTO_FAST_PLOTS=1 python scripts/run_fit.py
```

`PYAUTO_SMALL_DATASETS=1` caps every array, mask and grid to 16 × 16 pixels — so delete any
previously simulated `dataset/` when you toggle it, or a full-resolution dataset on disk will
be reused and mismatch the capped grids.

## Branch — the error that appears the moment the search starts

On some combinations of operating system and Python version, a script raises as soon as the
search begins, from Python's process spawning rather than from anything about your model. The
fix is to wrap the whole fit in a function and call it under a main guard:

```python
def fit():
    from autogalaxy import jax_wrapper  # Sets the JAX environment before other imports

    import autofit as af
    import autogalaxy as ag

    # ... dataset, model, search, analysis as above ...
    result = search.fit(model=model, analysis=analysis)


if __name__ == "__main__":
    fit()
```

Adapted from `autogalaxy_workspace:scripts/guides/modeling/bug_fix.py`, which is the same
`modeling.py` fit with this one structural change. It works for every dataset type, so adopt
it for any modeling script that hits the error. If parallelisation still will not work after
the fix, that script points at the project's support channel.

## Combine

- [`ag_plot_fit`](./ag_plot_fit.md) — render the fit yourself, at whatever scaling and
  cropping the science needs, rather than reading the auto-generated `image/fit.png`.
- [`ag_load_results`](./ag_load_results.md) — pull the posterior, the best-fit galaxies and
  the derived quantities back into Python, in-session or from disk later.
- [`ag_debug_fit_failure`](./ag_debug_fit_failure.md) — the fit finished but the residuals or
  the parameters are wrong.
- [`ag_configure_search`](./ag_configure_search.md) — the fit is too slow, or the sampler is
  the wrong one for the model.
- [`ag_simulate_dataset`](./ag_simulate_dataset.md) — build a controlled dataset with known
  truth and fit that first, which is the cleanest way to separate a model problem from a
  data problem.

When the script and its fit are worth keeping, offer (default-yes) to record the run in a
dated `wiki/project/YYYY-MM-DD-<slug>.md` entry: the science question, what was inferred and
with what search, and the output path — per [`_style.md`](./_style.md) property #5.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Practicalities](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_2_modeling/tutorial_2_practicalities.ipynb):
  the practical side of running a fit — output structure, reviewing results as they appear,
  and managing run times.
- **General reference** — [RTD: New user guide](https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_2_new_user_guide.html):
  the decision tree for which fit to run first, by system scale and dataset type.
- **Experienced PyAutoGalaxy user** — [workspace: imaging/start_here.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/imaging/start_here.py):
  the minimal end-to-end imaging fit, with the JAX and quick-update sections this skill
  mirrors.

## Agent procedural checklist

1. Confirm `model`, `analysis` and `search` exist; if not, route to the model-building and
   search-configuration skills.
2. On real observational data, confirm the inspection gate has been satisfied.
3. Write the script to `scripts/` in the generated-script style; never leave it inline only.
4. Validate it with `PYAUTO_TEST_MODE=1` (level 2 if you only need the likelihood proved),
   with the cache variables set if the environment needs them.
5. Launch the production run; **quote the absolute output path immediately** and say results
   refresh on the fly.
6. Name `model.results` and `image/fit.png` as the first two things to open.
7. If the data changed but the model did not, confirm the `unique_tag` changed too.
8. On a GPU, run the VRAM check before a long fit.
9. On completion, hand off to the results-loading or fit-plotting skill rather than
   interpreting the numbers inline.
10. Offer the `wiki/project/` entry.
