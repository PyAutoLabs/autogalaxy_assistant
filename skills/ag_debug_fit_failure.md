---
name: ag_debug_fit_failure
description: Triage a galaxy fit that crashed, stalled, or finished with residuals and parameters you do not believe. Works through a failure taxonomy — bad environment, bad data, bad model, bad priors, bad search settings, or a stale result that was never re-run — and gives the probes that separate them: hand-evaluating the likelihood at prior medians, checking the mask extent and over-sampling scheme, reading the normalised-residual and chi-squared maps, walking the likelihood step by step, forcing the NumPy path to get a readable stack trace, and the `PYAUTO_TEST_MODE` short-circuit loop for fast iteration. Also covers the two silent failures: a resumed fit whose identifier ignored the data, and a cached result mistaken for a new one. Use when a fit raises, hangs, returns nonsense, or converges somewhere unphysical. Not for the first composition of a model (`ag_build_imaging_model`), not for routine result inspection (`ag_load_results`), and not for an environment that will not import at all (`ag_setup_environment`).
---

# When the fit goes wrong

A galaxy fit fails in a small number of characteristic ways, and the debugging cost is
dominated by mis-attribution: hours spent widening priors when the mask was truncating the
outer isophotes, or rebuilding a model when the script was quietly resuming a cached result
from last week. So the first move is never a fix — it is to establish *which kind* of failure
this is.

The discipline that makes that possible is cheap probes before expensive ones. A single
likelihood evaluation costs a fraction of a second and tells you whether the model and data
can talk to each other at all. A `PYAUTO_TEST_MODE=2` run costs seconds and proves the whole
script executes. Only after those pass is it worth spending an hour of sampling to find out
whether the *inference* is the problem.

## Ask

Get the symptom precisely, because the taxonomy branches on it:

- *"Did it raise, hang, or complete?"* A raise has a traceback to read. A hang is usually
  parallelisation, a JIT compile you mistook for a stall, or an update cadence writing output
  constantly. A completed fit that looks wrong is the hardest case and needs the residuals.
- *"What makes you say it is wrong?"* Coherent residuals, an unphysical parameter, an error
  bar that is implausibly tight or implausibly wide, or the number simply disagreeing with the
  literature — each points somewhere different.
- *"Simulated data or real observations?"* On simulated data you know the truth, which makes
  everything below faster. If the user has real data and no simulated control, running one is
  often the fastest path to an answer ([`ag_simulate_dataset`](./ag_simulate_dataset.md)).
- *"Has this exact script run before?"* This decides whether the stale-result trap is in play.

## The taxonomy

Six categories, ordered by how cheap they are to rule out:

| Category | Tell | First probe |
|---|---|---|
| **Stale output** | The fit "finished" implausibly fast, or the result is identical after you changed something | Delete the `<unique_hash>` folder and re-run |
| **Environment** | An import error, a numba or matplotlib cache error, a parallelisation error the moment the search starts | `--check-install`, the cache variables, the main guard |
| **Bad data** | Residuals dominated by one blob, or a suspiciously large chi-squared everywhere | Plot the dataset; check the noise-map and the mask |
| **Bad model** | Coherent, structured residuals with a physical shape | Read the residual pattern; add or change a component |
| **Bad priors** | The best fit sits on a prior boundary, or the search never moves off its start | `model.info`; hand-evaluate the likelihood |
| **Bad search settings** | Wide posteriors, a low log evidence, different runs disagreeing, no errors at all | `search.summary`; raise `n_live`, or change search |

The rest of this skill is one branch per category.

## Branch — stale output, the silent one

Rule this out first, every time, because it is invisible and it invalidates everything else you
would conclude.

A fit's output folder is `output/<path_prefix>/<name>/<unique_tag>/<unique_hash>/`, and
`<unique_hash>` is derived from the model, the search settings and the dataset identifier. An
identical configuration therefore **resumes** rather than restarting
(`autogalaxy_workspace:scripts/imaging/modeling.py` `__Unique Identifier__`). That is a
feature for an interrupted overnight run and a trap the rest of the time, because **the
identifier does not hash the pixel values of your data**. Swap `data.fits` for a different
galaxy while keeping the model, search and `unique_tag` the same, and the next run finds a
completed fit at the same path and hands it back — in seconds, with the previous galaxy's
parameters, and no warning that anything is wrong.

The symptoms: a fit that completes far faster than it should; a result that does not change
after you deliberately changed the data; `model.results` timestamps older than the run you
just launched.

```bash
# Prove it rather than reasoning about it.
rm -rf output/<path_prefix>/<name>/<unique_tag>/<unique_hash>
```

Then re-run. If the answer changes, that was the bug. Going forward, change the `unique_tag`
whenever the data changes — that is what it is for.

The related trap: test-mode output. Any active `PYAUTO_TEST_MODE` level inserts a `test_mode`
segment straight after the output root, precisely so a smoke run cannot short-circuit a later
real fit ([`wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md)). If you
find yourself inspecting a result whose path contains `test_mode`, stop: every parameter in it
is a wiring check. Also delete any simulated `dataset/` when you toggle
`PYAUTO_SMALL_DATASETS`, or a full-resolution dataset on disk gets reused against capped grids
and produces shape errors that look like library bugs.

## Branch — environment and the errors that fire at launch

If the stack itself is the problem, nothing downstream is diagnostic. Confirm the install
first:

```bash
python autoassistant/audit_skill_apis.py --check-install
```

Exit `0` is ready; `2` means the packages are absent from *this* interpreter; `3` means they
were found but an import raised. Repairing it is
[`ag_setup_environment`](./ag_setup_environment.md), with the routes in
[`wiki/core/operations/installation.md`](../wiki/core/operations/installation.md).

Three failures that are environment, not science:

- **A numba or matplotlib cache error** buried in a long trace — the libraries cannot write
  their caches. Fix with `NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib`
  ([`wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md)).
- **An error the instant the search starts**, from Python's process spawning rather than from
  your model. Wrap the fit in a function under a main guard, exactly as
  `autogalaxy_workspace:scripts/guides/modeling/bug_fix.py` does — it is the same
  `modeling.py` fit with this one structural change:

  ```python
  def fit():
      from autogalaxy import jax_wrapper  # Sets the JAX environment before other imports

      import autofit as af
      import autogalaxy as ag

      # ... dataset, mask, over-sampling, model, search, analysis ...
      result = search.fit(model=model, analysis=analysis)


  if __name__ == "__main__":
      fit()
  ```

  It applies to every dataset type, so adopt it for any modeling script that hits the error.
  That script also names the project's support channel if the fix is not enough.
- **A stale API symbol** — an `AttributeError` on a PyAuto\* name recalled from an older
  release. Do not guess a replacement; check it:

  ```bash
  python autoassistant/audit_skill_apis.py --file scripts/run_fit.py
  ```

  [`ag_audit_skill_apis`](./ag_audit_skill_apis.md) owns that check and its bypass.

### Is it a JAX problem?

The single most useful lever, because it splits the space in two:

```python
analysis = ag.AnalysisImaging(dataset=dataset, use_jax=False)
```

or, without editing code, `PYAUTO_DISABLE_JAX=1` to force the NumPy path on every analysis
(`autogalaxy_workspace:scripts/guides/using_jax.py` `__Disabling JAX__`). NumPy stack traces
are far easier to read than compiled ones, and you can drop a debugger or a `print` into code
JAX would otherwise compile away. If the failure disappears on NumPy, it is a JAX problem; if
it survives, JAX was never involved and you have halved the search space.

Two JAX-specific failure shapes worth recognising:

- **An out-of-memory error at compile time or on the first likelihood call** on a GPU. Check
  the footprint before a long run:
  `analysis.print_vram_use(model=model, batch_size=search.batch_size)`
  (`autogalaxy_workspace:scripts/imaging/modeling.py` `__VRAM Use__`), and lower the batch
  size if it is close to the card's limit.
- **A long pause at the start that looks like a hang.** The first evaluation compiles the
  likelihood and its gradient; every step after that re-uses the compiled result. The log
  line announcing the compile is the tell
  (`autogalaxy_workspace:scripts/imaging/start_here.py` `__JAX__`). A persistent compilation
  cache means this is paid once per machine, not once per process
  ([`wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md)).

## Branch — bad data

Plot the dataset before you plot anything else. On real observations this is not optional —
the inspection gate in [`../AGENTS.md`](../AGENTS.md) requires it before a fit is even
composed, and a fit that skipped it is a prime suspect.

```python
aplt.subplot_imaging_dataset(
    dataset=dataset,
    output_path=PLOT_DIR,
    output_filename="dataset",
    output_format="png",
)
```

Four things to check, in order:

1. **Contaminants.** A neighbouring galaxy, a foreground star or a reduction artefact inside
   the mask contributes to the likelihood and biases every parameter. The fix is to scale its
   noise rather than cut the pixels out — `dataset.apply_noise_scaling(mask=mask_extra_galaxies)`
   keeps the pixels in the fit but makes them contribute negligibly, which avoids the
   discontinuities that removing pixels creates
   (`autogalaxy_workspace:scripts/imaging/modeling.py` `__Extra Galaxies Noise Scaling__`).
   Alternatively shrink the circular mask so the contaminant falls outside it. Concept:
   [`wiki/core/concepts/extra_galaxies_and_noise_scaling.md`](../wiki/core/concepts/extra_galaxies_and_noise_scaling.md);
   the tooling is [`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md).
2. **The mask extent.** Too small and it truncates the outer isophotes, which biases the
   effective radius and the Sersic index directly — the classic cause of a "wrong" Sersic
   index. Too large and it drags sky and neighbours in, slowing the fit for no information.
   [`wiki/core/concepts/grids_and_masks.md`](../wiki/core/concepts/grids_and_masks.md)
   "Choosing the radius is a science decision".
3. **The noise-map.** If it is underestimated, chi-squared is uniformly too large and the
   posterior is spuriously tight; if overestimated, the reverse. A residual map that is
   featureless but scaled wrong across the whole image points here rather than at the model.
4. **`pixel_scales`.** Wrong by a factor and every angular quantity is wrong by that factor,
   while the fit looks perfectly healthy. Check it against the instrument.

## Branch — bad model

This is what coherent residuals mean. Rebuild the fit and read the maps:

```python
fit = result.max_log_likelihood_fit   # or ag.FitImaging(dataset=dataset, galaxies=galaxies)

print(f"chi_squared     = {fit.chi_squared}")
print(f"log_likelihood  = {fit.log_likelihood}")
print(f"figure_of_merit = {fit.figure_of_merit}")

aplt.plot_array(
    array=fit.normalized_residual_map,
    title="Normalized Residual Map",
    symmetric=True,
    output_path=PLOT_DIR,
    output_filename="normalized_residual_map",
    output_format="png",
)
aplt.plot_array(
    array=fit.chi_squared_map,
    title="Chi-Squared Map",
    output_path=PLOT_DIR,
    output_filename="chi_squared_map",
    output_format="png",
)
```

Adapted from `autogalaxy_workspace:scripts/imaging/plot.py` `__Fit Figures__`. Read the
**normalised** residuals first: they are the only map calibrated against the noise, so they
answer *significance* rather than *magnitude*. Scatter within roughly ±3 is consistent with
noise; coherent structure outside that is a model failure however faint it looks.

Two quick numerical summaries worth printing alongside the figures — chi-squared per unmasked
pixel (order unity for a good fit), and the fraction of pixels beyond 3σ (a few per cent for a
good fit, tens of per cent for a badly wrong model).

The residual patterns and what each implies are tabulated in
[`ag_plot_fit`](./ag_plot_fit.md) "The inspection discipline". The model responses:

- **Ring at one radius** → the radial profile is too rigid. One Sersic where a bulge plus a
  disk is needed, or a Sersic index that was fixed. Free it, or add the second component.
- **Four-lobed alternating pattern** → the ellipticity or position angle is wrong, or the
  isophotes twist with radius. [`wiki/core/concepts/ellipse_fitting_and_multipoles.md`](../wiki/core/concepts/ellipse_fitting_and_multipoles.md).
- **Central excess** → coarse over-sampling, or a nuclear component the model lacks. Check the
  over-sampling scheme before adding physics (below).
- **Clumpy, asymmetric structure no smooth profile can absorb** → this is where a
  many-component basis or a pixelised reconstruction earns its keep:
  [`wiki/core/concepts/linear_light_profiles_and_mge.md`](../wiki/core/concepts/linear_light_profiles_and_mge.md),
  [`wiki/core/concepts/shapelets.md`](../wiki/core/concepts/shapelets.md),
  [`wiki/core/concepts/inversions_and_pixelizations.md`](../wiki/core/concepts/inversions_and_pixelizations.md).
- **A uniform offset across the whole image** → an unmodelled sky background:
  [`wiki/core/concepts/sky_background_and_operated_profiles.md`](../wiki/core/concepts/sky_background_and_operated_profiles.md).

**Check the over-sampling before blaming the physics.** A steep central profile evaluated once
per pixel is systematically wrong at the centre, and the symptom is exactly the residual a
missing nuclear component would leave:

```python
over_sample_size = ag.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[8, 4, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)
```

Adapted from `autogalaxy_workspace:scripts/imaging/modeling.py` `__Over Sampling__`. Re-plot
the dataset subplot afterwards — its lower panels show the scheme that was actually applied,
so you can confirm it rather than assume it. The full treatment, including why the outer bins
never drop to a single sub-pixel, is
[`wiki/core/concepts/grids_and_masks.md`](../wiki/core/concepts/grids_and_masks.md)
"Over-sampling", with the runnable guide at
`autogalaxy_workspace:scripts/guides/advanced/over_sampling.py`.

Adding complexity is [`ag_build_imaging_model`](./ag_build_imaging_model.md). Do it one
component at a time and re-fit: a model that gained three components at once tells you nothing
about which one mattered.

## Branch — bad priors, and hand-evaluating the likelihood

The most direct probe in the whole stack. A model and an analysis are enough — no search, no
waiting:

```python
instance = model.instance_from_prior_medians()
log_likelihood = analysis.log_likelihood_function(instance=instance)

print(f"log likelihood at prior medians = {log_likelihood}")
```

From [`wiki/core/api/analysis_objects.md`](../wiki/core/api/analysis_objects.md) "Evaluating
the likelihood by hand". `log_likelihood_function(instance)` is the single contract between a
model and data, so what it returns is diagnostic on its own:

- **It raises.** The failure is in the forward model or the data shapes, not in the inference.
  Force `use_jax=False` first for a readable trace, then walk the likelihood step by step
  (next branch).
- **It returns `nan` or `-inf`.** Something in the model is degenerate at those parameter
  values — a zero or negative size, a profile whose centre sits outside the mask, a noise-map
  with zeros.
- **It returns a finite but wildly bad value, and the fit's best likelihood is barely better.**
  The search never found anything, which usually means the priors do not contain the answer.
- **It returns something close to the fit's best value.** The priors are fine and the search
  is doing its job; look elsewhere.

Then compare against a known-good instance. On simulated data you have the truth, so evaluate
the likelihood there: if the true model scores much better than anything the search found, the
priors or the search settings are at fault, not the model. This is the cleanest experiment
available, and it is the reason to keep a simulated control alongside real data
([`ag_simulate_dataset`](./ag_simulate_dataset.md)).

Read the priors themselves rather than recalling them:

```python
print(model.info)
```

Three specific things to look for. **A best-fit parameter sitting on a prior boundary** means
the prior is truncating the posterior — the answer may be outside it entirely. **A prior far
wider than physically sensible** wastes the search's effort and invites multi-modality. And
**a prior narrowed to make a search behave** is a scientific choice, not a convenience: it
changes the posterior and therefore the answer. If you want to steer where a search *starts*
without changing the posterior, that is a start point, and only the MCMC and optimisation
searches accept one — nested samplers draw from the prior by construction
([`wiki/core/concepts/non_linear_search.md`](../wiki/core/concepts/non_linear_search.md)
"Priors and start points"). Defaults come from configuration
([`wiki/core/api/configuration.md`](../wiki/core/api/configuration.md)), and overriding them
per parameter is [`ag_build_imaging_model`](./ag_build_imaging_model.md).

Also confirm the galaxy is near the coordinate origin. The default priors assume a centre near
(0.0", 0.0"); a galaxy several arcseconds off-centre needs either re-centred data or
explicitly overridden centre priors (`autogalaxy_workspace:scripts/imaging/modeling.py`
`__Coordinates__`).

## Branch — walking the likelihood step by step

When the hand evaluation raises or returns something inexplicable, the step-by-step
walkthrough is the ground truth. `autogalaxy_workspace:scripts/imaging/likelihood_function.py`
computes a galaxy model's log likelihood one NumPy operation at a time — the elliptical
coordinate transform, each light profile's image, the sum into a galaxy image, the blurring
grid and PSF convolution, then:

```
model_data              = convolved_image_2d
residual_map            = data - model_data
normalized_residual_map = residual_map / noise_map
chi_squared_map         = normalized_residual_map ** 2
chi_squared             = sum(chi_squared_map)
noise_normalization     = sum(log(2 * pi * noise_map ** 2))
figure_of_merit         = -0.5 * (chi_squared + noise_normalization)
```

and finishes by showing that `ag.FitImaging(dataset=dataset, galaxies=galaxies).figure_of_merit`
reproduces the same number. Running it against your own dataset localises the failure to one
step, which is far faster than reading a compiled trace.

There are matching walkthroughs for the features whose likelihood is genuinely different, and
the difference is where their failures live:
`autogalaxy_workspace:scripts/imaging/features/linear_light_profiles/likelihood_function.py`
(the mapping matrix, data vector, curvature matrix and the positive-only reconstruction),
`.../multi_gaussian_expansion/likelihood_function.py` (the same for a Gaussian basis), and
`.../pixelization/likelihood_function.py` (the regularisation matrix and the Bayesian
complexity terms). If a fit with linear profiles or a pixelisation fails where a standard
profile fit succeeds, the extra linear-algebra steps in those scripts are the place to look.

A real fit does not run that NumPy code — it runs the same calculation compiled. To probe the
compiled path exactly as a search drives it, `autogalaxy_workspace:scripts/guides/using_jax.py`
`__Custom Likelihood Functions__` shows the `Fitness` route, and explains why batching a vector
of parameters is a stricter test than one concrete call: a single call can quietly succeed on
code where NumPy is leaking through, and then break as soon as the search batches.

## Branch — bad search settings

The model and data are fine; the sampler did not do its job. Read the search's own report
first: `search.summary` in the output folder, plus `result.samples.log_evidence` and the
posterior widths.

- **Posteriors far wider than the data should allow, or a low log evidence** → too few live
  points for the model's dimensionality. `n_live=200` covers most galaxy models; raise it for
  a complex one ([`wiki/core/api/searches.md`](../wiki/core/api/searches.md)).
- **No errors at all** → the fit used a gradient optimiser, which is maximum-a-posteriori and
  returns one model. Re-run with `Nautilus` if the science needs uncertainties
  (`autogalaxy_workspace:scripts/imaging/start_here.py` `__Posterior__`).
- **Two runs of the same configuration disagreeing** → a multi-modal parameter space with a
  search that is finding different modes. Either raise `n_live`, or start simple and chain into
  the complex model with the simple fit's posterior as priors
  ([`wiki/core/concepts/non_linear_search.md`](../wiki/core/concepts/non_linear_search.md)
  "Search chaining"; the runnable version is
  `autogalaxy_workspace:scripts/guides/modeling/chaining.py`).
- **Run time far longer than expected** → total cost is (likelihood evaluation time) ×
  (number of evaluations), and dimensionality dominates. A many-Gaussian expansion with six
  free parameters routinely beats a multi-component decomposition with thirteen, despite the
  slower per-evaluation cost. [`wiki/core/concepts/non_linear_search.md`](../wiki/core/concepts/non_linear_search.md)
  "Run-time estimation".
- **The log constantly reporting that it is outputting results** → `iterations_per_quick_update`
  is too low and visualisation is eating the run. Raise it
  ([`ag_run_search`](./ag_run_search.md)).

Choosing and tuning the search is [`ag_configure_search`](./ag_configure_search.md).

## Branch — the fast iteration loop

While you are changing a script's structure, do not pay for inference. `PYAUTO_TEST_MODE` has
four levels ([`wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md)):

```bash
# Level 2 — sampler bypassed, likelihood called exactly once. The fastest proof that the
# model composes, the shapes agree and the likelihood evaluates.
PYAUTO_TEST_MODE=2 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/run_fit.py

# Level 1 — a real but minimal search. Slower, and the only level that writes model.results,
# image/fit.png and a loadable samples.csv.
PYAUTO_TEST_MODE=1 NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/run_fit.py
```

Level 2 does **not** write the fit products, which is worth knowing before you go looking for
`image/fit.png` after a level-2 run. Level 3 skips the likelihood as well, so it only checks
the non-fitting scaffolding. `PYAUTO_SKIP_CHECKS=1` is available when a smoke run trips a
runtime validation on data too small to be sane — never set it for a real fit, since those
checks are what stop a silently degenerate inversion. And **never quote a parameter measured
in test mode**: the sampler was truncated or mocked, so the numbers are wiring evidence, not
measurements.

The loop that works: level 2 until the script runs clean → level 1 until the products look
sane → one full run on a small mask or a simulated dataset → the production fit.

## Branch — when nothing above explains it

Two escalations, in order.

**Reduce to a control.** Simulate a dataset from a model you choose, fit it with that same
model, and confirm you recover the truth
([`ag_simulate_dataset`](./ag_simulate_dataset.md)). If the control fails, the problem is in
the code or the setup. If the control succeeds, the problem is in the real data or its
preparation — and you have narrowed it to a half of the space you could not distinguish
before. This is the single highest-value move in this skill and it is under-used.

**Check the library, not yourself.** If a symbol does not resolve or an idiom that reads
correctly does not work, run the audit — a construction can be retired while every token in it
still imports:

```bash
python autoassistant/audit_skill_apis.py --scope scripts
python autoassistant/audit_skill_apis.py --lint-idioms
```

[`ag_audit_skill_apis`](./ag_audit_skill_apis.md) owns both. Only after those come back clean
is "this might be a library bug" a reasonable hypothesis — at which point
[`contribute-upstream`](./contribute-upstream.md) is the route to filing it with a minimal
reproduction.

## Combine

- [`ag_plot_fit`](./ag_plot_fit.md) — the residual-pattern table this skill's model branch
  routes through, and the figures that make a diagnosis visible.
- [`ag_build_imaging_model`](./ag_build_imaging_model.md) — acting on a "bad model" or "bad
  priors" verdict.
- [`ag_configure_search`](./ag_configure_search.md) — acting on a "bad search settings"
  verdict.
- [`ag_prepare_imaging_data`](./ag_prepare_imaging_data.md) — acting on a "bad data" verdict:
  masks, noise scaling, contaminant handling.
- [`ag_simulate_dataset`](./ag_simulate_dataset.md) — the control experiment.
- [`ag_setup_environment`](./ag_setup_environment.md) — the install will not import at all.
- [`ag_run_search`](./ag_run_search.md) — re-launching once the cause is fixed.

Record the diagnosis, not just the fix. Offer (default-yes) a dated
`wiki/project/YYYY-MM-DD-<slug>.md` entry naming the symptom, the probe that localised it, and
what changed — per [`_style.md`](./_style.md) property #5. A debugging session that is not
written down gets repeated.

## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: Dealing with failure](https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/chapter_2_modeling/tutorial_4_dealing_with_failure.ipynb):
  why searches fail on galaxy models, what a local maximum looks like in practice, and how
  model complexity and prior choice interact.
- **General reference** — [RTD: Likelihood function](https://pyautogalaxy.readthedocs.io/en/latest/general/likelihood_function.html):
  the likelihood the library evaluates, and pointers into the step-by-step walkthroughs.
- **Experienced PyAutoGalaxy user** — [workspace: guides/modeling/bug_fix.py](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/guides/modeling/bug_fix.py):
  the main-guard fix for the parallelisation error, as a complete runnable fit.

## Agent procedural checklist

1. Get the symptom: raised, hung, or completed-but-wrong; and what makes it wrong.
2. Rule out stale output first — check timestamps, then `rm -rf` the `<unique_hash>` folder and
   re-run. Check for a `test_mode` path segment.
3. Confirm the environment with `--check-install`; apply the cache variables and the main guard
   if either applies.
4. Toggle `use_jax=False` (or `PYAUTO_DISABLE_JAX=1`) to split JAX from non-JAX failures and
   get a readable trace.
5. Plot the dataset: contaminants, mask extent, noise-map, `pixel_scales`.
6. Hand-evaluate `analysis.log_likelihood_function(instance=model.instance_from_prior_medians())`
   before running any search.
7. Read `model.info` for boundary-hugging and over-wide priors; confirm the galaxy is near the
   origin.
8. Rebuild the fit and read the **normalised residual** map, then the chi-squared map; check
   the over-sampling scheme before adding physics.
9. Read `search.summary` and the log evidence for search-settings failures.
10. Iterate with `PYAUTO_TEST_MODE=2`, then `=1`; never quote a test-mode parameter.
11. If unresolved, build a simulated control and fit it; run the symbol and idiom audits before
    suspecting a library bug.
12. Offer the `wiki/project/` entry recording symptom, probe and fix.
