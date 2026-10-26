# What works today, and what is coming

A status report on the PyAutoGalaxy Assistant: what it can do now, and what it can't do yet. Back to the
[README](../README.md).

The assistant was built in public, in phases, and every phase has now landed. [`ROADMAP.md`](../ROADMAP.md) covers
what comes next and what is deliberately left out. No file in this repository links to something that does not exist.

## Live today

- **The core modelling loop (nine skills).** Environment setup, imaging data preparation, dataset simulation, model
  building, search configuration, running the fit, plotting the fit, loading results, and debugging a failed fit. A
  galaxy-science request routes into these.
- **Features beyond a single smooth profile (eight skills).** Basis profiles and MGE, pixelised reconstruction, extra
  galaxies, sky and operated profiles, ellipse fitting, multi-dataset fits, interferometer modelling, multi-galaxy and
  cluster fields, and search chaining.
- **Two ways to use your results.** Converting a generated script into a Jupyter notebook, and a read-only results
  browser (an MCP server) for looking through and comparing your finished fits from an app that can't run code.
  Alongside these sit two meta-skills, two project-workflow skills, one literature skill and four
  repository-maintenance skills: twenty-eight in total, listed in [`skills/README.md`](../skills/README.md).
- **The reference wiki**, [`wiki/core/`](../wiki/core/index.md): 39 pages across `stack/`, `api/`, `concepts/`,
  `operations/` and `external/`. Every page records the source commits it was checked against.
- **The literature wiki**, [`wiki/literature/`](../wiki/literature/index.md): a galaxy-structure science reference
  with 16 concept pages, 10 survey and instrument pages and 13 annotated source bibliographies, over a BibTeX layer in
  which **every entry was checked against a public record before it was allowed in**.
- **The bundled dataset**: four real JWST NIRCam wavebands with full provenance, plus
  [`wiki/core/operations/dataset.md`](../wiki/core/operations/dataset.md), which documents the on-disk layout and the
  `info.json` schema.
- **HPC cluster support**: `hpc/` ships a pipeline template, CPU and GPU SLURM submit templates and a `sync` command
  for transfers and job control, documented in [`wiki/core/operations/hpc.md`](../wiki/core/operations/hpc.md) and
  [`hpc_infrastructure.md`](../wiki/core/operations/hpc_infrastructure.md).
- **Four benchmark prompts**: easy (the second prompt in the README), medium, hard and teacher, each frozen with a
  100-point scoring rubric under [`benchmarks/`](../benchmarks/README.md).

## Not yet

The benchmark suite has been written but not run. [`benchmarks/RESULTS.md`](../benchmarks/RESULTS.md) records no
scored runs, and it is regenerated automatically rather than written by hand, so there is no performance claim here
yet. That, and everything else the assistant doesn't do, is in [`ROADMAP.md`](../ROADMAP.md).

The phased build is tracked at [PyAutoBrain#188](https://github.com/PyAutoLabs/PyAutoBrain/issues/188).
