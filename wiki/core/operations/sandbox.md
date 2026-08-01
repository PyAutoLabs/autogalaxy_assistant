---
title: Sandbox and restricted-environment configuration
sources:
  - project: PyAutoNerves
    paths:
      - autonerves/test_mode.py
      - autonerves/jax_wrapper.py
      - autonerves/workspace.py
    pinned_commit: e82c17fd6c8966f6b3a2f6ffbcb655db7035fdb1
  - project: PyAutoArray
    paths:
      - autoarray/util/dataset_util.py
      - autoarray/plot/utils.py
      - autoarray/plot/output.py
    pinned_commit: 59b0f198fc7bdf9c91e5a8f734dad796fcc55656
  - project: PyAutoFit
    paths:
      - autofit/non_linear/paths/abstract.py
      - autofit/non_linear/analysis/analysis.py
      - autofit/text/text_util.py
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
  - project: PyAutoGalaxy
    paths:
      - autogalaxy/plot/plot_utils.py
      - autogalaxy/analysis/model_util.py
    pinned_commit: 65b14d7767da194a21bf0f3a4345f0790af86ed4
  - project: autogalaxy_assistant
    paths:
      - AGENTS.md
      - .gitignore
      - autoassistant/audit_skill_apis.py
      - .claude/hooks/validate_pyauto_code.py
    pinned_commit: ed72fabb33e14a9a701a4d280e8775dd3a20e98c
last_updated: 2026-08-01
content_sha256: e594c604f396ad7dac62d4f787b78db19c8b20981cf379ed0a5f8b82e6043b06
---

# Sandbox / restricted-environment configuration

Two separate problems get solved on this page, and it is worth keeping them apart.

The first is **write access**: the libraries cache compiled code and plot configuration
under the user's home directory, and in a sandbox (a coding-agent container, CI, a
read-only home, an install imported from a `/mnt/c/...` Windows mount under WSL) those
paths fail — usually with a confusing message buried inside a numba trace.

The second is **run time**: a real galaxy fit takes minutes to hours, which is far too
slow a loop for "does this script even execute?". The stack ships a set of environment
variables that short-circuit sampling, shrink datasets and skip visualisation, turning a
fit into a fast structural check.

## Writable caches (fix this first)

```bash
export NUMBA_CACHE_DIR=/tmp/numba_cache
export MPLCONFIGDIR=/tmp/matplotlib
```

- **`NUMBA_CACHE_DIR`** — where numba writes its compiled-function cache. The default is
  a `__pycache__/` directory beside the installed module, which fails outright when the
  install sits on a read-only or unwritable filesystem.
- **`MPLCONFIGDIR`** — where matplotlib writes its config and font cache (default
  `~/.config/matplotlib` on Linux).

Set them once per shell, or bake them into the venv activation. This repo's tooling
already does the equivalent for its own imports: `--check-install` creates
`<tempdir>/numba_cache` and `<tempdir>/matplotlib` and points the two variables at them
*only if they are unset* (`autoassistant/audit_skill_apis.py`), so a deliberate choice is
never overridden.

There is a third cache most people meet only once, on the first JAX fit. With JAX
installed, `PyAutoNerves:autonerves/jax_wrapper.py` enables the persistent compilation
cache at `$XDG_CACHE_HOME/pyauto_jax` (or `~/.cache/pyauto_jax`) so that the minutes spent
compiling a model/data shape are paid once per machine rather than once per process. Point
`JAX_COMPILATION_CACHE_DIR` somewhere writable in a sandbox, or set it to the **empty
string** to disable the cache entirely. The same module sets `XLA_FLAGS` and
`JAX_ENABLE_X64=True` before JAX is imported, which is why every workspace script that
uses JAX begins with `from autogalaxy import jax_wrapper` *before* its other imports —
setting them after JAX has loaded has no effect.

### Concurrent agents in one working directory

If two agents (a Claude Code session and a CI job, say) may run in the same checkout at
once, give each its own cache so they cannot race to write the same numba artefact:

```bash
export NUMBA_CACHE_DIR=/tmp/numba_cache_$$
export MPLCONFIGDIR=/tmp/matplotlib_$$
```

`$$` expands to the shell's PID.

## Fast structural checks — `PYAUTO_TEST_MODE`

`PyAutoNerves:autonerves/test_mode.py` defines four levels, read from
`PYAUTO_TEST_MODE`:

| Level | Behaviour |
|---|---|
| `0` (unset) | Normal operation |
| `1` | Reduce the sampler to its minimum number of iterations |
| `2` | Bypass the sampler entirely; call the likelihood **once** |
| `3` | Bypass the sampler entirely and skip the likelihood call too |

```bash
PYAUTO_TEST_MODE=1 python scripts/your_script.py
```

Levels 2 and 3 are the ones to reach for while iterating on a script's *structure*; level
1 still exercises the search. **The returned `Result` is not physically meaningful at any
level** — the parameter values are whatever the truncated or mocked run produced, so never
quote a structural parameter measured in test mode.

Two consequences of test mode are easy to trip over:

- **Output is namespaced.** Any active level inserts a `test_mode` segment directly after
  the output root, so results land in `output/test_mode/<path_prefix>/<name>/` rather than
  beside real runs (`PyAutoFit:autofit/non_linear/paths/abstract.py`). This is deliberate:
  without it, a cached test-mode result short-circuits a later real run at the same paths
  with "Fit Already Completed". Workspace scripts that compose their own output paths use
  `with_test_mode_segment` from `PyAutoNerves:autonerves/test_mode.py` so they agree with
  PyAutoFit's internal rule.
- **Latent variables are skipped automatically.** Test-mode samples are mocked, so
  latent-variable values would be meaningless; `PYAUTO_SKIP_LATENTS` is implied by any
  active level (and can be set on its own to skip the post-fit
  latent pass in a real run).

`PYAUTO_TEST_MODE_SAMPLES` controls how many fake samples a level-2/3 bypass writes.
Default `4`; values below `4` raise. Raise it (10 000+) when you want a `samples.csv`
whose row count and byte size are representative of a production run — the point is honest
resume/load timings against realistic output while the fit itself finishes in seconds.

## The other short-circuit flags

Each is independent of `PYAUTO_TEST_MODE` and each is `=1` to enable:

- **`PYAUTO_SKIP_FIT_OUTPUT`** — skip the pre/post-fit output: the FITS/JSON products,
  VRAM profiling, result info text and likelihood-function checks
  (`PyAutoNerves:autonerves/test_mode.py`, `PyAutoFit:autofit/text/text_util.py`).
- **`PYAUTO_SKIP_VISUALIZATION`** — skip the diagnostic figures rendered during the fit.
- **`PYAUTO_SKIP_CHECKS`** — skip runtime validation: mesh pixel validation, sample-weight
  thresholds and the inversion's guard exceptions. Useful when a smoke run trips a check on
  data too small to be sane; never set it for a real fit, since those checks are what stop
  a silently degenerate inversion.
- **`PYAUTO_SMALL_DATASETS`** — cap every array, mask and grid to **16 × 16 pixels at
  0.6"/pixel** (`PyAutoArray:autoarray/util/dataset_util.py`, and the matching caps in
  `Mask2D.circular`, `Grid2D.uniform`, the convolver and the over-sampling utilities).
  Loaded FITS data larger than the cap is **centre-cropped**, not resampled, so it stays
  shape-consistent with masks and grids built under the same flag. **Delete any previously
  simulated `dataset/` when you toggle this flag**, or a full-resolution dataset on disk
  will be reused and mismatch the capped grids.
- **`PYAUTO_FAST_PLOTS`** — skip `plt.tight_layout()` in the subplot helpers
  (`PyAutoArray:autoarray/plot/utils.py`) and short-circuit the expensive contour
  overlays PyAutoGalaxy can compute for a mass model
  (`PyAutoGalaxy:autogalaxy/plot/plot_utils.py`). Figures are still created and rendered;
  only the layout pass and those overlays are dropped.
- **`PYAUTO_DISABLE_JAX`** — force `use_jax=False` on every analysis regardless of what
  the script asked for (`PyAutoFit:autofit/non_linear/analysis/analysis.py`). The lever for
  isolating "is this a JAX problem?" without editing code.
- **`PYAUTO_OUTPUT_MODE`** — instead of writing each figure to its configured path, save
  numbered snapshots (`0_<name>.png`, `1_<name>.png`, …) into a directory named after the
  running script (`PyAutoArray:autoarray/plot/output.py`). Built for collecting a figure
  sequence from an automated run.

A representative fast-iteration combination:

```bash
PYAUTO_TEST_MODE=2 \
  PYAUTO_SKIP_FIT_OUTPUT=1 \
  PYAUTO_SKIP_VISUALIZATION=1 \
  PYAUTO_SKIP_CHECKS=1 \
  PYAUTO_SMALL_DATASETS=1 \
  PYAUTO_FAST_PLOTS=1 \
  NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
  python scripts/your_script.py
```

Leave every one of them unset for a production fit. They answer "is this script correct?",
never "what is this galaxy's Sersic index?".

One more exists and is deliberately not in the list above:
`PYAUTO_LATENT_NAN_INJECT` is a **test-only** knob the `*_workspace_test` suites use to
poison latent values with NaNs on purpose. It is a no-op when unset; never set it by hand.

## Workspace version handshake

`PyAutoNerves:autonerves/workspace.py` compares the workspace clone's version against the
installed library and warns on a mismatch. That warning is informative locally and pure
noise in CI or on a source checkout where the two intentionally diverge. Two documented
ways to silence it:

```bash
PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1 python scripts/your_script.py
```

or set `version.workspace_version_check: False` in `config/general.yaml` — the recommended
route for anyone tracking the workspace's `main` branch. See
[`../api/configuration`](../api/configuration.md) for how that config layer resolves.

## The API gate's escape hatch

Distinct from all of the above, and specific to this repo: a `PreToolUse` hook
(`.claude/hooks/validate_pyauto_code.py`) blocks agent-written Python that references a
PyAuto\* symbol absent from the installed stack. During a deliberate refactor — where you
*mean* to name a symbol the current install does not have — bypass it with
`PYAUTO_SKIP_API_GATE=1`, either exported or as a prefix on the single command. On
harnesses without hook support the same check is run by hand; see
[`../../../skills/ag_audit_skill_apis.md`](../../../skills/ag_audit_skill_apis.md).

## Where things are allowed to be written

The repo's own boundaries, from [`../../../AGENTS.md`](../../../AGENTS.md) and
`.gitignore` — they matter most in a sandbox, where a stray write is easy and hard to
notice:

- `output/` — PyAutoFit's runtime output. **Never written by hand**; gitignored.
- `sources/` — cloned library source. Never written by hand; gitignored.
- `scripts/` — committed, notebook-convertible Python.
- `scripts/scratch/` — throwaway plots and data dumps; gitignored. This is where a
  sandbox run's figures should go.

## See also

- [`installation`](./installation.md) — getting the stack in place, and
  `--check-install` for diagnosing which interpreter you are actually using.
- [`../concepts/non_linear_search`](../concepts/non_linear_search.md) — why a real fit
  costs what it costs, and how run time scales with the model.
- [`../api/configuration`](../api/configuration.md) — the config layer these environment
  variables sit alongside.
