"""
The read-only results-inspector MCP server (galaxy edition).

The read-only tool core is the ``autofit[mcp]`` extra (``autofit.mcp``);
`galaxy_tools.py` layers the PyAutoGalaxy-specific image/FITS extraction on top;
`server.py` builds the core server and registers the galaxy tools on it;
`python -m autoassistant.mcp` runs the stdio server. Documentation and client
configuration live in `skills/ag_inspect_results_mcp.md`.
"""
