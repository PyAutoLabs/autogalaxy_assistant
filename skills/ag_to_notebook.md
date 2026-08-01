---
name: ag_to_notebook
description: Convert a generated narrative-docstring PyAutoGalaxy script (.py) into a Jupyter notebook (.ipynb) — each top-level docstring becomes a markdown cell, the code between becomes a code cell. Use when the user says "turn this into a notebook", "convert to ipynb", "can I get a Colab version", or otherwise wants a Jupyter form of a script the assistant produced. Not for authoring a script (that is whichever `ag_*` skill owns the science), not for the published workspace notebooks (PyAutoHands builds those), and not a reason to hand-edit an `.ipynb` — the `.py` stays the source of truth.
user-invocable: true
---

# Script → notebook

Every script this assistant saves is written in the workspace narrative-docstring style
([`_style.md`](./_style.md) "Generated script style") — a title docstring with
`__Contents__`, then each section introduced by a `"""__Section__"""` docstring. That style
was not chosen only for readability. It was chosen because it makes notebook conversion
**mechanical**: each top-level docstring block becomes a **markdown cell**, and the Python
between blocks becomes a **code cell**. Nothing has to be interpreted or reformatted, so the
notebook carries the same physics and inference narrative the script does.

## Orient

The converter is [`autoassistant/to_notebook.py`](../autoassistant/to_notebook.py) —
stdlib-only, no external tool and no extra pip dependency. It is a self-contained adaptation
of the converter the PyAuto workspaces use at build time
(`PyAutoHands:autohands/build_util.py` `py_to_notebook`, plus
`PyAutoHands:autohands/add_notebook_quotes.py`), which pipe through `ipynb-py-convert`. This
one mirrors their cell-split semantics — a line *starting* with triple quotes toggles
docstring mode — but emits nbformat-v4 JSON directly.

It is entirely generic: it knows nothing about PyAutoGalaxy, only about the docstring style.
That is worth saying out loud, because it means the conversion never silently "fixes" your
science — whatever the script says is what the notebook says.

## Ask

Usually nothing. The script to convert is normally the one just produced, and the default
output path sits beside it. Ask only when several candidate scripts are in play, or when the
user wants the notebook somewhere specific (a science project's `notebooks/`, say).

## Branch — convert

```bash
python -m autoassistant.to_notebook scripts/<name>.py            # -> scripts/<name>.ipynb
python -m autoassistant.to_notebook scripts/<name>.py <out>.ipynb
```

From inside a science project, the same module run out of the resolved assistant clone works
identically — `python <resolved-assistant>/autoassistant/to_notebook.py scripts/<name>.py`.
The CLI prints the **absolute** output path; quote it back to the user and offer to open it
(`open` on macOS, `xdg-open` on Linux, `explorer.exe` / `wslview` from WSL), the same
courtesy the plotting skills give a figure.

Three things worth knowing before you run it:

- **The input must be in the narrative style.** A script of bare `#` banner comments converts
  to one enormous code cell. That is technically correct and almost certainly not what the
  user wanted — say so, and offer to restyle the script first
  ([`_style.md`](./_style.md) has the copyable shape). This is the one failure mode of the
  conversion, and it is a failure of the *script*, not of the converter.
- **The notebook is generated output.** Never hand-edit the `.ipynb`; edit the `.py` and
  reconvert. Keep the script as the committed source of truth unless the user explicitly
  wants the notebook tracked — a Colab-facing or collaborator-facing artefact in a science
  project is the usual reason to make an exception.
- **Cells have no outputs.** The converter emits `execution_count: None` and empty
  `outputs`, so the notebook is a clean, diffable starting point rather than a record of a
  run. Executing it is the user's job.

## Branch — when a notebook is the wrong answer

Two cases where the honest reply is "not this":

- **A long-running fit.** A notebook that ends in `search.fit(...)` will sit at a running
  cell for minutes to hours, and a dropped kernel loses the session (not the fit — `output/`
  is written incrementally, see [`ag_run_search`](./ag_run_search.md) — but the notebook
  state). Suggest running the script and using the notebook for the *inspection* half:
  loading the result and plotting it.
- **Anything headed for `autogalaxy_workspace`.** The published workspace notebooks carry
  Colab setup cells and magic handling the build pipeline adds; PyAutoHands stays
  authoritative there. This skill is for assistant-generated and science-project scripts.

## Combine

- Whichever skill produced the script — [`ag_build_imaging_model`](./ag_build_imaging_model.md),
  [`ag_plot_fit`](./ag_plot_fit.md), [`ag_load_results`](./ag_load_results.md) — owns the
  content; this one only changes its container.
- A converted notebook pairs naturally with the Collaborate / Publish phases of
  [`start-new-project`](./start-new-project.md): reviewers and collaborators very often prefer
  opening a notebook to running a script, and a paper's companion repository is usually read
  before it is executed.
- For inspecting results from a chat client with no code execution at all, the notebook is not
  the tool — [`ag_inspect_results_mcp`](./ag_inspect_results_mcp.md) is.
