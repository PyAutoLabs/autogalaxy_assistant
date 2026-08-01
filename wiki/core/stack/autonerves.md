---
title: PyAutoNerves (autonerves)
sources:
  - project: PyAutoNerves
    paths:
      - autonerves/conf.py
      - autonerves/dictable.py
      - autonerves/fitsable.py
      - autonerves/json_prior/
      - autonerves/jax_wrapper.py
      - autonerves/workspace.py
      - pyproject.toml
      - README.md
    pinned_commit: e82c17fd6c8966f6b3a2f6ffbcb655db7035fdb1
last_updated: 2026-08-01
content_sha256: 061e843e1a71dd329025c6c232f6fcd4dfeffeb4e8f7aaf173753fe60ad5cc59
---

# PyAutoNerves — the configuration layer

Project: [`PyAutoNerves`](https://github.com/PyAutoLabs/PyAutoNerves). Import: `autonerves`.

PyAutoNerves is the configuration and serialisation layer the rest of the stack reads
from. Every PyAutoArray / PyAutoFit / PyAutoGalaxy package ships its own
`<pkg>/config/` directory of YAML files; autonerves is the machinery that finds, merges,
and queries them.

You rarely call autonerves directly. You call `conf.instance` to read a setting, or you
edit a YAML file under one of the other packages' `config/` folders (or the workspace's
own `config/`), or you use `output_to_json` / `from_json` to serialise model objects to
disk.

## What lives in autonerves

- **`autonerves/conf.py`** — the `Config` class and the `conf.instance` global accessor;
  loads YAML config from a priority-ordered list of `config/` directories.
- **`autonerves/dictable.py`** — the `Dictable` mixin plus `output_to_json` /
  `from_json`. PyAutoGalaxy uses these to serialise `Galaxy` / `Galaxies` / profile
  objects to JSON so a finished fit can be reloaded later.
- **`autonerves/fitsable.py`** — FITS I/O (`output_to_fits`, `ndarray_via_fits_from`),
  re-exported as `ag.output_to_fits` / `ag.ndarray_via_fits_from`.
- **`autonerves/json_prior/`** — the JSON representation of priors for the autofit model
  system.
- **`autonerves/workspace.py`** — the workspace ↔ library version handshake that warns
  when a cloned workspace and the installed library disagree.
- **`autonerves/test_mode.py`** — the `PYAUTO_TEST_MODE` machinery, surfaced as
  `ag.is_test_mode` / `ag.test_mode_level`.
- **`autonerves/setup_colab.py`** / **`setup_notebook.py`** — environment setup used by
  workspace `start_here.py` scripts; the galaxy entry point is
  `setup_colab.for_autogalaxy(...)`.
- **`autonerves/jax_wrapper.py`** — imported first in every workspace script to set JAX
  environment variables before anything else loads.

## Configuration layering

A `Config` holds an ordered list of `config/` directories: **the first entry wins**.
The default instance is built from the current working directory's `config/` folder, and
each library registers its own `<pkg>/config/` behind it, so:

1. The workspace `config/` in the current working directory (highest priority).
2. Each package's own `<pkg>/config/` defaults (autogalaxy, autofit, autoarray).

`conf.instance.push(path)` inserts another directory at the front, which is what the
Colab / notebook setup helpers do. Workspace-level config therefore beats library
defaults — that is why a workspace copy of `priors/` or `visualize/` silently changes
model and plotting behaviour.

Source: `PyAutoNerves:autonerves/conf.py`.

## Dictable — JSON serialisation

`Dictable` is the mixin that gives objects round-trippable JSON. A `Galaxy` is
serialisable; a `LightProfile` subclass that includes `Dictable` in its inheritance
becomes serialisable too.

```python
from autonerves.dictable import output_to_json, from_json

output_to_json(obj=galaxy, file_path="galaxy.json")
galaxy_2 = from_json(file_path="galaxy.json")
```

The same two functions are re-exported as `ag.output_to_json` / `ag.from_json`, and the
dict-level pair as `ag.to_dict` / `ag.from_dict`.

## Dependencies

`autonerves` itself is deliberately thin: `typing-inspect`, `PyYAML`, `numpy`. JAX is an
**optional extra** (`autonerves[jax]` → `jax`, `jaxlib`, `jaxnnls`), pulled in
transitively by `autogalaxy[jax]`. The reason `jax_wrapper` lives this low in the stack
is that the JAX environment variables must be set *before* any other PyAuto\* import,
which is why every workspace script begins with
`from autogalaxy import jax_wrapper` as its first import line.

## See also

- [`stack/overview`](./overview.md) — where autonerves sits in the dependency chain.
- [`stack/autofit`](./autofit.md) — the consumer of the prior YAMLs autonerves loads.
