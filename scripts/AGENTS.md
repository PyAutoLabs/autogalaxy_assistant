# Scripts

This folder holds the galaxy modeling pipelines for this project. A fresh clone ships
**no** pipeline scripts here — they are adapted per project from the `autogalaxy_workspace`
catalogue (see below), because a user can do a broad variety of things and there is no
single "default" script. For quick, throwaway exploration scripts, use `scripts/scratch/`
(gitignored) instead.

All scripts here follow the **Generated script style** (title + `__Contents__` header,
`"""__Section__"""` narrative sections, no banner comments) — see the project root
`AGENTS.md` "Conventions" and `skills/_style.md` "Generated script style".

## HPC interface template

The standard interface between the HPC batch templates and Python modeling code lives at
[`../hpc/template.py`](../hpc/template.py), paired with `hpc/batch_cpu/template` and
`hpc/batch_gpu/template`. The whole folder — templates, the `sync` CLI and its config
examples — is documented in
[`../wiki/core/operations/hpc_infrastructure.md`](../wiki/core/operations/hpc_infrastructure.md),
with the science of cluster runs in
[`../wiki/core/operations/hpc.md`](../wiki/core/operations/hpc.md). The contract below is what
a pipeline script in this folder must preserve. It includes:

- **`parse_fit_args()`** — parses `--sample`, `--dataset`, `--iterations_per_quick_update`,
  `--number_of_cores`, and `--use_cpu` from the command line
- **`fit()`** — receives these parameters and sets up config, dataset loading, and
  `SettingsSearch`. The body raises `NotImplementedError` where the science-specific
  model, analysis, and search steps go
- **`__main__`** — wires `parse_fit_args()` into `fit()`

To create a pipeline for HPC array runs, copy `hpc/template.py` into this folder (e.g.
`scripts/imaging.py`) and fill in the `fit()` body with science code adapted from
`autogalaxy_workspace/scripts/`. The HPC interface (`parse_fit_args`, `__main__`, `use_cpu`,
`number_of_cores`) must be preserved — the batch templates run `scripts/$SCRIPT` and depend
on it. `scripts/imaging.py` and `scripts/interferometer.py` are gitignored for exactly this
reason: they are per-clone copies of a generic mechanism, not tracked content.

## Workspace pipeline reference

There is no single canonical galaxy pipeline — the right starting script depends on the data
and the science question — and deliberately no skill that scaffolds one, because there is no
default worth scaffolding. Compose the `ag_*` skills for the science
([`../skills/README.md`](../skills/README.md) indexes them) and adapt the closest script from
the `autogalaxy_workspace` catalogue below.

Every path below is relative to `autogalaxy_workspace/scripts/`. Each group's
`start_here.py` (where one exists) is the always-current reference for that group; read it
before adapting anything else in the group.

### Imaging — the main entry point

| Path | What it gives you |
|------|-------------------|
| `imaging/start_here.py` | the canonical end-to-end run: load FITS → noise-scale blended neighbours → mask + over-sample → MGE galaxy model → multi-start gradient fit → result. Start here. |
| `imaging/modeling.py` | the same fit with `Nautilus` nested sampling instead, returning a full posterior with errors and covariances. The statistically complete version. |
| `imaging/data_preparation/start_here.py` | preparing your own image, noise-map, PSF and masks, with GUI tools under `data_preparation/gui/`. |
| `imaging/simulator.py`, `imaging/simulator_sersic.py`, `imaging/simulator_sample.py` | simulate one galaxy, a plain Sersic galaxy, or a population sample. |
| `imaging/fit.py`, `imaging/plot.py`, `imaging/likelihood_function.py` | fit objects, plotting entry points, and a step-by-step walk through the likelihood. |

### Imaging features — pick by what the data demands

| Path | Use when |
|------|----------|
| `imaging/features/linear_light_profiles/` | you want intensity solved by linear inversion rather than sampled as a free parameter — fewer non-linear dimensions, same model. |
| `imaging/features/multi_gaussian_expansion/` | the default recommendation: a sum of Gaussians flexible enough for most morphologies and fast to fit. |
| `imaging/features/shapelets/` | you need a basis that captures asymmetry and spiral structure a Sersic cannot. |
| `imaging/features/pixelization/` | the galaxy is clumpy or irregular and no smooth analytic profile fits it. |
| `imaging/features/extra_galaxies/` | other galaxies or foreground stars blend with the target and must be masked, noise-scaled, or modelled. |
| `imaging/features/sky_background/` | the background sky level is uncertain and should be a model parameter. |
| `imaging/features/operated_light_profile/` | a component is already PSF-convolved (e.g. an unresolved nuclear point source) and must not be convolved again. |

### Other data types and scales

| Path | Scope |
|------|-------|
| `interferometer/start_here.py` | ALMA / JVLA uv-plane modelling, with the same feature set under `interferometer/features/`. |
| `multi_dataset/start_here.py` | simultaneous fits across wavebands or instruments, including wavelength-dependent parameters and per-dataset offsets. |
| `multi_galaxy/start_here.py` | two or more blended galaxies, each with its own free light model. |
| `cluster/start_here.py` | a cluster field: BCG plus a catalogue-driven member population. The subject is the members' **light**, not lensing. |
| `ellipse/modeling.py` | non-parametric isophote fitting, with `ellipse/multipoles.py` for multipole perturbations. **This group has no `start_here.py`** — route to `modeling.py`. |
| `guides/` | API guides rather than pipelines: `modeling/` (cookbook, chaining, searches, customize, bug_fix), `results/` (+ `aggregator/`, `database/`, `workflow/`), `plot/`, `profiles/light.py`, `units/`, `advanced/over_sampling.py`, `using_jax.py`. |

## After adapting a script

Update dataset-specific values at the bottom of each script (or confirm that `info.json`
provides them via `info.get(key, default)`). Run it once under `PYAUTO_TEST_MODE=1` before
trusting it. See the project root `AGENTS.md` and the
[`start-new-project`](../skills/start-new-project.md) skill for the full new-project workflow
checklist.
