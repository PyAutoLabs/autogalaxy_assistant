---
name: ag_inspect_results_mcp
description: Run and configure the read-only results-inspector MCP server, which lets chat harnesses without code execution (Claude Desktop, Claude Code) inspect PyAutoGalaxy fit results — list completed fits ranked by evidence, read model and posterior summaries, view result images inline in chat, and combine subplot panels or extract FITS HDUs across many fits at once. Use when the user wants to browse or triage their `output/` folder from chat, asks about the MCP server, or wants Claude Desktop wired to a results directory. Not for loading results in Python (that is `ag_load_results`), not for running or composing fits, and not a way to make a chat client fit a galaxy.
user-invocable: true
---

# The results-inspector MCP server

[`autoassistant/mcp/`](../autoassistant/mcp/) is a read-only MCP (Model Context Protocol)
stdio server over PyAutoFit/PyAutoGalaxy output directories. It exists for one situation: a
harness that **cannot execute code**. A Claude Desktop chat has no Python, so without this it
can talk about your fits but never look at them. With it, the same chat can list what
finished, rank it by Bayesian evidence, read a `model.results`, and render the residual map of
the best fit inline — against the same `output/` folder a scripted session works with.

It is deliberately **not** a fitting interface. Composing models and running searches stay
python-first through the other skills, because flattening a compositional API
(`af.Model` / `af.Collection` trees, priors, assertions) into JSON tool schemas would lose
most of what makes it usable. Read-only is a design decision, not a missing feature.

## Orient

- **Server**: [`autoassistant/mcp/server.py`](../autoassistant/mcp/server.py), run as
  `python -m autoassistant.mcp` from the repo root. It speaks stdio; nothing listens on a port.
- **The core is a library extra, not a copy.** The generic read-only tools ship as
  `pip install autofit[mcp]` — the `core_server` builder in `PyAutoFit:autofit/mcp/server.py`,
  backed by `PyAutoFit:autofit/mcp/tools.py`. (Those two are deliberately cited by path rather
  than as dotted symbols: the extra is not installed in the audit's wheel environment, so a
  dotted reference would resolve to a `ModuleNotFoundError` rather than to the API.) This
  repo's `server.py` builds that core and layers the galaxy-specific image/FITS extraction on
  top; [`galaxy_tools.py`](../autoassistant/mcp/galaxy_tools.py) is the only part that is ours.
  The galaxy layer additionally needs PyAutoGalaxy installed. Both are
  assistant-environment dependencies — never a library requirement.
- **Everything is read-only against `output/`.** The one tool that writes at all,
  `extract_galaxy_fits`, refuses any destination inside the search-output directory.

## Tools

Core (from `autofit[mcp]`):

| Tool | Returns |
|------|---------|
| `list_searches(directory, ...)` | The completed fits found under `directory`, one row each — the ranking entry point. |
| `get_model(directory)` | The model that was fitted. |
| `get_result_summary(directory)` | The human-readable result text (what `model.results` holds). |
| `get_samples_summary(directory)` | Posterior medians and errors. |
| `get_search_info(directory)` | The search and its settings. |
| `list_images(directory)` / `fetch_image(directory, name)` | The figures a fit wrote, and one of them rendered inline. |

Galaxy layer (this repo):

| Tool | Returns |
|------|---------|
| `list_extractable_images()` | The `ag.agg` enum groups and member names the two tools below accept, as `"group.name"` specs. |
| `combine_galaxy_images(directory, subplots, subplot_width=0)` | Named panels pulled from *every* fit under `directory` and combined into one image rendered inline in chat (`af.AggregateImages`). |
| `extract_galaxy_fits(directory, hdus, destination_path, overwrite=False)` | A single `.fits` holding the named HDUs from every fit, written to `destination_path` (refused inside the output directory); returns the path (`af.AggregateFITS`). |

There are exactly **three** enum groups on `ag.agg`, and the specs are `group.name`:

| Group | Members |
|---|---|
| `subplot_dataset` | `data`, `data_log_10`, `noise_map`, `psf`, `psf_log_10`, `signal_to_noise_map`, `over_sample_size_lp`, `over_sample_size_pixelization` |
| `subplot_fit` | `data`, `signal_to_noise_map`, `model_data`, `normalized_residual_map`, `normalized_residual_map_one_sigma`, `chi_squared_map` |
| `fits_fit` | `model_data`, `residual_map`, `normalized_residual_map`, `chi_squared_map` |

So `subplot_fit.data` and `subplot_fit.chi_squared_map` are image specs for
`combine_galaxy_images`, while `fits_fit.residual_map` is an HDU spec for
`extract_galaxy_fits`. Call `list_extractable_images()` rather than trusting this table if the
stack has moved — it is generated from `dir(ag.agg)` at run time, which is why the table can
be checked rather than believed.

The combining tools are the reason the galaxy layer exists at all. One fit's figures are
already on disk; what a chat client cannot otherwise do is put *thirty* galaxies' residual maps
side by side and let you see which three failed. That is sample triage, and it is the natural
chat-shaped task.

## Configure a client

**Claude Desktop** (`claude_desktop_config.json`, Settings → Developer → Edit Config):

```json
{
  "mcpServers": {
    "pyauto-results-inspector": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["-m", "autoassistant.mcp"],
      "env": { "PYTHONPATH": "/absolute/path/to/autogalaxy_assistant" }
    }
  }
}
```

Use the interpreter that has PyAutoGalaxy and `mcp` installed. Then ask about fits by absolute
path — *"list the fits under /home/me/project/output ranked by evidence, then show me the data
and the normalised residuals of the best one side by side"*.

MCP clients spawn the server with a **minimal environment**: nothing from your shell
propagates. Anything the stack needs — `PYTHONPATH` for a source checkout, `NUMBA_CACHE_DIR` /
`MPLCONFIGDIR` in a restricted setup ([`../wiki/core/operations/sandbox.md`](../wiki/core/operations/sandbox.md))
— has to be declared in the config's `env` block.

**Windows (Claude Desktop → WSL):** when the interpreter lives in WSL, launch it through
`wsl.exe`. Nothing beyond `PYTHONPATH` is required — the server pins its own `config/`
directory and forces JAX onto CPU *before* importing autofit, so it does not depend on the
launch directory:

```json
{
  "mcpServers": {
    "pyauto-results-inspector": {
      "command": "wsl.exe",
      "args": ["-e", "bash", "-c",
        "PYTHONPATH=/home/you/autogalaxy_assistant /home/you/venv/bin/python -m autoassistant.mcp"]
    }
  }
}
```

For the Microsoft Store build of Claude Desktop the config and the failure log
(`logs/mcp-server-pyauto-results-inspector.log`) live under
`%LOCALAPPDATA%\Packages\Claude_*\LocalCache\Roaming\Claude\`, not `%APPDATA%\Claude\`.

**Claude Code**: the repo-root [`.mcp.json`](../.mcp.json) registers the same server
automatically for sessions opened in this repo, so there is nothing to configure.

## When it fails, it fails silently

The single most common symptom is the server simply not appearing in the client, with no
error. Two causes account for nearly all of it:

1. **The wrong interpreter.** The client's `command` must be the venv Python that has the
   stack; a bare `python` resolves to whatever the client's minimal environment finds.
2. **A stray print.** `stdout` *is* the JSON-RPC channel. One line of library chatter on
   stdout corrupts the protocol and the client drops the connection. This is why `server.py`
   sets `JAX_PLATFORMS=cpu` and wraps its autofit import in
   `contextlib.redirect_stdout(sys.stderr)` before anything under autofit loads, and why
   `galaxy_tools.py` runs every aggregator call inside `_stdout_to_stderr()`.

Read the client's MCP log before debugging anything else.

## Deployment tiers

1. **Local stdio (what is built, above)** — Claude Desktop or Claude Code on the machine
   holding `output/`.
2. **Remote (documented only)** — claude.ai web/mobile custom connectors and ChatGPT developer
   mode speak MCP, but only to servers reachable over the public internet; stdio is not an
   option. The route is `mcp.run(transport="streamable-http")` behind a tunnel. Not built and
   not hardened here — do not expose a machine you care about without thinking about auth.
3. **Hosted (future)** — a shared deployment beside collaboration-scale outputs. Same tools;
   hosting, auth and scale are their own problem.

## Combine

- **Loading results in Python** — [`ag_load_results`](./ag_load_results.md). That is the right
  tool whenever code execution *is* available; the MCP server is the fallback, not the upgrade.
- **Understanding what you are looking at** — [`ag_plot_fit`](./ag_plot_fit.md) for reading
  residual and chi-squared maps, and [`ag_debug_fit_failure`](./ag_debug_fit_failure.md) when
  the triage turns up a fit that went wrong.
- **Sharing the analysis rather than the results** — [`ag_to_notebook`](./ag_to_notebook.md).

## Design rules (maintainers)

- **Glue, not code.** Every tool is argument parsing + one existing public
  PyAutoFit/PyAutoGalaxy call + serialization. If a tool needs more than that, add the method
  to the library first — `galaxy_tools.py` says so in its own module docstring, and it is
  under 80 lines for that reason.
- **Read-only.** No fit-running, no compute, no writes into `output/`. `extract_fits` enforces
  the last of those explicitly rather than by convention.
- **stdout is the protocol.** Keep the import guard and `_stdout_to_stderr()` when adding
  tools.
- **Anti-drift.** `autoassistant/mcp/*.py` is inside the symbol audit's scan set
  (`autoassistant/audit_skill_apis.py --scope scripts`, see
  [`ag_audit_skill_apis`](./ag_audit_skill_apis.md)), and
  `autoassistant/tests/test_mcp_tools.py` builds its fixture by running a real tiny fit, so a
  change in PyAutoFit's on-disk format fails loudly rather than quietly.
