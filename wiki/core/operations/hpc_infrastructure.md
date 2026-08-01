---
title: HPC infrastructure shipped with the assistant
sources:
  - project: autogalaxy_assistant
    paths:
      - hpc/template.py
      - hpc/batch_cpu/template
      - hpc/batch_gpu/template
      - hpc/sync
      - hpc/sync.conf.example
      - scripts/AGENTS.md
    pinned_commit: a083753c217e6d9c07f3c9cc40cb7133b478a439
  - project: autogalaxy_workspace
    paths:
      - scripts/guides/hpc/README.md
    pinned_commit: 18245a81097e7cfd6cc27b313c9b2f9c6c4315b2
  - project: PyAutoFit
    paths:
      - autofit/non_linear/paths/directory.py
    pinned_commit: 67c4090f05fa19f10b028fe2dee2e9d8adfbcbf0
last_updated: 2026-08-01
content_sha256: 1146b9f5f332c8edb9ef701af6ab6c160ccb2598116ee17ff63801e6a6c3ea17
---

# HPC infrastructure shipped with the assistant

This page documents the concrete machinery in `autogalaxy_assistant:hpc/`: the pipeline
template, the SLURM batch submit templates, and the bidirectional `sync` script. For the
*science* of cluster runs — the two kinds of parallelism, JAX on CPU versus GPU, sizing an
array job — see [`operations/hpc`](./hpc.md). For dataset layout and `info.json`, see
[`operations/dataset`](./dataset.md).

`hpc/` sits outside the symbol audit's scan set (it is a template folder, not documentation),
so it is validated by **running it**, not by a checker. `python hpc/template.py --sample=…
--dataset=…` against a real dataset directory should parse its arguments, load the FITS, apply
the mask and then stop at the `NotImplementedError` that marks where your science goes — that
round trip is the test.

## Directory structure

```
hpc/
├── template.py            # Python pipeline template (HPC arg-parsing interface)
├── batch_gpu/             # GPU submit template + SLURM log dirs (output/, error/)
│   └── template
├── batch_cpu/             # CPU submit template + SLURM log dirs (output/, error/)
│   └── template
├── sync                   # bidirectional sync + job-control script (local ↔ HPC)
├── sync.conf.example      # template config for sync (copy to sync.conf, gitignored)
├── sync_jump.conf.example # example two-hop / relay-host config
└── .gitignore             # ignores sync.conf and sync_jump.conf
```

The four `batch_*/output/` and `batch_*/error/` directories exist in a fresh clone by way of a
tracked `.gitignore` keeper in each. That is not cosmetic: `sbatch` fails outright if the
`-o` / `-e` paths it is given do not exist.

## Pipeline template — `hpc/template.py`

The interface between the batch scripts and PyAutoGalaxy modeling code. Copy it into
`scripts/` (e.g. `scripts/imaging.py`) and fill in the `Model, Analysis & Search` section of
`fit()`; there is deliberately no skill that scaffolds this, because galaxy work has no single
default pipeline worth scaffolding — compose the `ag_*` skills for the science and adapt the
closest `autogalaxy_workspace` script, as
[`../../../scripts/AGENTS.md`](../../../scripts/AGENTS.md) sets out.

It parses `--sample`, `--dataset`, `--iterations_per_quick_update`, `--number_of_cores` and
`--use_cpu`; pushes the project's `config/` and `output/` paths through `autonerves`; and reads
every dataset-specific value from the dataset's `info.json` via `info.get(key, default)` —
`pixel_scale`, `mask_radius`, `redshift` — so one script serves a whole sample. The mask radius
is read per galaxy rather than shared, because a mask that truncates the outer isophotes biases
the effective radius and Sersic index directly.

For a multi-waveband dataset laid out as `dataset/<galaxy>/wavebands/<BAND>/`
([`operations/dataset`](./dataset.md)), pass the two arguments one level deeper —
`--sample=<galaxy>/wavebands --dataset=F277W` — and each band becomes its own array task with
its own `info.json`. No change to the template is needed.

**The HPC interface must be preserved.** `parse_fit_args`, `__main__`, `--use_cpu` and
`--number_of_cores` are the contract the batch templates depend on; `scripts/AGENTS.md`
documents it as the shape every pipeline in `scripts/` conforms to. `scripts/imaging.py` and
`scripts/interferometer.py` are gitignored precisely because they are per-clone copies of this
generic mechanism rather than tracked content.

## Submit templates — GPU vs CPU

Each batch folder ships one generic `template`. Both run one galaxy per SLURM array task and
call `python3 $PROJECT_PATH/scripts/$SCRIPT` (set `SCRIPT` to your pipeline filename).
Differences:

| | GPU (`batch_gpu/template`) | CPU (`batch_cpu/template`) |
|---|---|---|
| Partition | `--partition=gpu` | `--partition=cpu` |
| GPU | `--gres=gpu:1` | none |
| CPUs | `--cpus-per-task=1` | `--cpus-per-task=4` |
| Memory | `--mem=32gb` | `--mem=64gb` |
| Wall time | `--time=08:00:00` | `-t 18:00:00` |
| JAX | uses the GPU by default | forces `JAX_PLATFORM_NAME=cpu` |
| Thread pinning | none | `OPENBLAS/MKL/OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK` |
| Echo block | includes `nvidia-smi` | no `nvidia-smi` |
| Python args | `--sample --dataset` | adds `--use_cpu --number_of_cores=$THREADS` |

The CPU template also exports `JAX_PLATFORMS=cpu`, `VECLIB_MAXIMUM_THREADS`,
`NUMEXPR_NUM_THREADS` and `NPROC`, all pinned to `$SLURM_CPUS_PER_TASK`. The GPU template pins
nothing, because a GPU job holds one CPU core and JAX supplies the parallelism.

### Checklist after copying (edit both `batch_gpu/template` and `batch_cpu/template`)

1. `#SBATCH -J <job_name>` — SLURM queue name.
2. `#SBATCH --array=0-N` — N = number of galaxies minus 1.
3. `SCRIPT=<filename>.py` — the pipeline in `scripts/` to run.
4. `sample=<sample_name>` — matches the subdirectory under `dataset/`.
5. `datasets=(...)` — one galaxy name per line, in array-index order.

To test a single galaxy first, set `--array=0-0` and put just that name in `datasets=(...)`.
Scaling to the full sample afterwards is two edits: widen the array and extend the list.

Before submitting either, `export PROJECT_PATH=/path/to/your/project` so the template can find
`activate.sh` and `scripts/`.

## `hpc/sync` — bidirectional project sync

One script for all transfer and job management between local and HPC, so no step of the loop
requires an interactive SSH session. Set it up with `cp hpc/sync.conf.example hpc/sync.conf`
and edit `HPC_HOST`, `HPC_BASE` and `PROJECT_NAME`; the remote path is
`$HPC_HOST:$HPC_BASE/$PROJECT_NAME`, which is the same location the batch scripts call
`$PROJECT_PATH`. `sync.conf` is gitignored and never leaves your machine; the same values can
be exported as environment variables instead.

**Transfer:** `push` (code + config + data), `push --no-data`, `pull` (logs then results),
`logs` (logs only — small and fast, use it mid-run), `sync` (push then pull), `push-data-init`
(first dataset upload via a tar pipe), `pull-full` (whole output download via a tar pipe),
`status` (dry run).

**Jobs:** `submit [gpu|cpu] <script>`, `push-submit [gpu|cpu] <script>`, `jobs` (squeue),
`sacct`, `cancel <job_id>`, `wait-and-pull [secs]`.

**Inspect:** `tail [gpu|cpu]` (stream live logs), `du`, `check` (verify SSH, the remote project
directory and `sbatch`), `clear-logs [gpu|cpu]`.

**What syncs:** push code = `config/`, `hpc/`, `scripts/`, `simulators/` plus the root files;
push data = `dataset/` with `--ignore-existing`, so FITS already on the HPC are never re-sent
(they are written once and never modified, and re-checksumming a large archive on every sync is
the thing that makes syncing painful); pull = the SLURM logs and then `output/`, excluding
`search_internal/`. Always excluded: `__pycache__/`, `*.pyc`, `.git/`, `*.egg-info/` and
`sync.conf` itself.

A typical sample run is three commands:

```bash
hpc/sync push-submit cpu template   # push code+data, then sbatch
hpc/sync jobs                       # ...check on it
hpc/sync wait-and-pull              # poll until the array drains, then download
```

> **Concurrency caution.** `remove_search_internal()` in PyAutoFit is an unguarded
> `shutil.rmtree` (`PyAutoFit:autofit/non_linear/paths/directory.py`). Two array tasks that
> chain off the *same* cached earlier result — the pattern in
> [`../../../skills/ag_chain_searches.md`](../../../skills/ag_chain_searches.md) — can race on
> that cleanup, and one dies with `FileNotFoundError`. Sample runs where every task is
> independent are unaffected; run chained jobs serially, or give each task its own base result.

## See also

- [`operations/hpc`](./hpc.md) — the science of cluster runs and how to size a job.
- [`operations/dataset`](./dataset.md) — dataset layout and the `info.json` fields the template
  reads.
- [`../../../scripts/AGENTS.md`](../../../scripts/AGENTS.md) — the pipeline-script contract and
  the workspace catalogue to adapt from.
- [`../../../skills/start-new-project.md`](../../../skills/start-new-project.md) — the full
  new-project workflow, including its optional HPC folder.
