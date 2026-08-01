---
title: HPC and cluster runs
sources:
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/hpc/README.md
      - scripts/guides/hpc/example_cpu_and_gpu.py
      - scripts/guides/using_jax.py
    pinned_commit: 18245a81097e7cfd6cc27b313c9b2f9c6c4315b2
  - project: autogalaxy_assistant
    paths:
      - hpc/batch_cpu/template
      - hpc/batch_gpu/template
      - skills/ag_pixelization.md
      - skills/ag_run_search.md
    pinned_commit: a083753c217e6d9c07f3c9cc40cb7133b478a439
last_updated: 2026-08-01
content_sha256: 63f54059086daa7fb771ae0e3de4ae8a3355eb980a0694141226c8a1dc671a82
---

# HPC and cluster runs

Galaxy structure work is **sample-shaped**. One galaxy is rarely the point: the science
question is usually a distribution — how the effective radius runs with stellar mass, how the
Sersic index changes with wavelength, how bulge fractions evolve with redshift — and answering
it means fitting tens to hundreds of objects with the same model. Each individual fit is
comparatively cheap. What a cluster buys you is not a faster fit; it is **all of them at once**.

That shapes everything on this page. The default parallelism is one galaxy per SLURM array
task, each task fully independent, nothing to chain and nothing to order. Parallelising a
*single* fit across cores is the exception, reached for when there is one galaxy that matters
or when a pixelised reconstruction has become the bottleneck.

The canonical worked example is
`autogalaxy_workspace:scripts/guides/hpc/example_cpu_and_gpu.py`, with the full setup guide
(virtual environment, filesystem layout, transfers, monitoring) in `scripts/guides/hpc/README.md`
beside it. The concrete templates this repo ships are documented in
[`operations/hpc_infrastructure`](./hpc_infrastructure.md).

## Two kinds of parallelism, and which one you want

| | Many single-core jobs | One parallelised fit |
|---|---|---|
| SLURM shape | `--array=0-N`, `--cpus-per-task=1..4` | `--array=0-0`, `--cpus-per-task=16` |
| Python side | nothing to configure | `number_of_cores` into the search |
| Efficient when | you have a sample | you have one expensive galaxy |
| Cost | none — tasks never talk to each other | inter-process communication overhead |

The workspace guide is blunt about the trade: parallelising one fit across CPUs carries
communication overhead, so *N* single-core jobs finish a sample of *N* galaxies faster than
*N* sequential multi-core fits. Reach for the second column only when the sample has already
been dealt with, or when there is only one object.

For the second column, the core count is read from the SLURM environment rather than hard-coded,
so changing `--cpus-per-task` in the batch script changes the fit without touching Python:

```python
import os

number_of_cores = int(os.environ.get("SLURM_CPUS_PER_TASK", 1))

search = af.Nautilus(
    path_prefix="hpc",
    name="example",
    unique_tag=dataset_name,
    n_live=100,
    number_of_cores=number_of_cores,
)
```

`number_of_cores` also reaches the search through `af.SettingsSearch`, which is what the
shipped `hpc/template.py` uses.

## JAX, CPUs and GPUs

Imaging analyses run through JAX by default when it is installed
(`ag.AnalysisImaging(dataset=dataset, use_jax=True)`), and **the modeling code is identical on
a GPU** — only the batch script changes, because JAX auto-detects the device. That is the single
most useful fact on this page: there is no GPU port to write.

Two consequences for how you request resources.

**JAX disables Python multiprocessing.** A JAX-backed fit gains nothing from
`number_of_cores`, so a GPU job asks for one CPU core and lets the device do the work. The CPU
batch template does the opposite — it forces `JAX_PLATFORM_NAME=cpu` / `JAX_PLATFORMS=cpu` and
pins the linear-algebra thread counts to `$SLURM_CPUS_PER_TASK`, so many array tasks sharing a
node cannot oversubscribe it.

**The GPU is not always the right answer.** For smooth profiles and bases — a Sersic pair, a
Multi-Gaussian Expansion, shapelets — it nearly always is: roughly ten minutes on a GPU against
an hour on a CPU for the workspace's own example. For a **pixelised reconstruction** the trade
inverts with pixel scale, because the inversion's linear algebra is sparse and JAX must work
densely:

- `pixel_scales > 0.05` (Euclid-like) — modest sparsity, GPU with JAX usually wins.
- `pixel_scales <= 0.03` (HST/JWST-like) — sparsity-dominated; a many-core CPU run through
  `numba` can beat a powerful GPU.

The reasoning and the measured scalings are in
[`../../../skills/ag_pixelization.md`](../../../skills/ag_pixelization.md) "run time, VRAM, and
the GPU-versus-CPU choice"; benchmark both paths on your own data rather than trusting either
default.

**Check VRAM before committing a long GPU run.** A JAX fit must fit in device memory, and a
pixelization needs far more than a profile model. `analysis.print_vram_use(model=model,
batch_size=search.batch_size)` takes half a minute and tells you whether the run is feasible;
exceeding VRAM does not degrade gracefully. Set `XLA_PYTHON_CLIENT_PREALLOCATE=false` if you
deliberately place several JAX processes on one GPU node — otherwise each pre-allocates the
whole device.

## Sizing an array job

The five things to set per submission, all of them in the batch script rather than in Python:

1. `#SBATCH -J <job_name>` — how the job appears in `squeue`.
2. `#SBATCH --array=0-N` — N = number of galaxies minus one.
3. `SCRIPT=<filename>.py` — the pipeline in `scripts/` to run.
4. `sample=<sample_name>` — the subdirectory under `dataset/`.
5. `datasets=(...)` — one galaxy name per line, in array-index order.

Scaling from one galaxy to a sample is exactly two of those edits: add names to `datasets=(...)`
and widen `--array`. Wall-clock (`-t`) and memory (`--mem`) should be sized for the *slowest*
galaxy in the list — array tasks that finish early cost nothing, and a task killed at the wall
loses everything it had not yet written.

Rough shapes to start from: a linear bulge-plus-disk or MGE fit on a masked cutout is minutes on
a GPU and tens of minutes on four CPU cores; a pixelised reconstruction is hours, and is the
case that wants both the memory and the wall-clock headroom.

## Cache directories, one per job

Numba and matplotlib both write caches, and two jobs sharing a cache directory corrupt each
other. Point them at per-job scratch:

```bash
export NUMBA_CACHE_DIR=$TMPDIR/numba_cache
export MPLCONFIGDIR=$TMPDIR/matplotlib
```

JAX has a third cache — the persistent compilation cache at `~/.cache/pyauto_jax` — which is
usually a *benefit* on a cluster, since every array task fitting the same model and data shape
pays the compile once between them. Redirect it with `JAX_COMPILATION_CACHE_DIR` if the home
filesystem is unwritable or quota-limited, and see
[`operations/sandbox`](./sandbox.md) for the full set.

## Filesystems, output and resuming

Home directories on most clusters are small and are for code, the virtual environment and
config. Datasets and `output/` belong on the large filesystem (`/scratch`, `/work`, `/data`,
`/gpfs`, `/lustre` — the name varies). **Never point `output/` at `$TMPDIR`**, which is purged
when the job ends.

`output/` is written incrementally as the search runs, so a job killed at the wall can be
resubmitted and will resume from the same path: PyAutoFit recognises the existing
`<unique_id>` directory and continues.

That resume behaviour is also the trap most likely to bite a sample run. **The identifier is
built from the model and the search settings, not from the data.** Two array tasks fitting the
same model to different galaxies would land in the same output directory and silently resume
each other. Separate them by `path_prefix` (per galaxy) or by `unique_tag` — the shipped
`hpc/template.py` uses a per-galaxy prefix for exactly this reason, and
[`../../../skills/ag_debug_fit_failure.md`](../../../skills/ag_debug_fit_failure.md) covers the
symptom when it happens anyway.

## Monitoring

Standard SLURM, plus the log layout the batch templates set up:

```bash
squeue -u YOUR_USERNAME          # running and pending jobs
scancel JOB_ID                   # cancel
sacct -j JOB_ID                  # completed-job accounting and exit codes
```

Stdout and stderr land in `batch_cpu/output/` and `batch_cpu/error/` (or `batch_gpu/`), named
with the job ID and array index, so a single failing galaxy is traceable to a single file. The
`hpc/sync` CLI wraps all of the above so you never have to SSH in by hand — see
[`operations/hpc_infrastructure`](./hpc_infrastructure.md).

## See also

- [`operations/hpc_infrastructure`](./hpc_infrastructure.md) — the `hpc/` templates and the
  `sync` CLI this repo ships.
- [`operations/sandbox`](./sandbox.md) — cache environment variables and the test-mode flags to
  prove a script before submitting it.
- [`operations/installation`](./installation.md) — the virtual-environment and JAX-with-GPU
  install routes.
- [`../concepts/non_linear_search`](../concepts/non_linear_search.md) — why a fit costs what it
  costs, and how run time scales with the model.
