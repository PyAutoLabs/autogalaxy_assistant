"""Pin `colab/contexts.yaml`: sound mapping, PyAutoHands-identical ids, metadata-only stamping.

Stdlib + PyYAML, fast: nothing is executed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from autoassistant import colab_contexts

NOTEBOOK_NAME = "autogalaxy_workspace/notebooks/imaging/modeling.ipynb"


def test_mapping_is_sound():
    assert colab_contexts.check() == []


def test_project_and_name():
    contexts = colab_contexts.load()
    assert contexts["project"] == "autogalaxy"
    assert contexts["default"]["skills"]


def test_context_id_matches_pyautohands():
    # PyAutoHands' build_util.gemini_context_id("autogalaxy") — the id every generated
    # autogalaxy_workspace notebook carries. Literal, so a drift on either side fails here.
    assert colab_contexts.context_id("autogalaxy") == "eeaf2f2f-9ba2-5080-af36-9325f0df29b8"


def test_check_flags_never_map_and_over_cap(tmp_path):
    root = tmp_path / "assistant"
    (root / "colab").mkdir(parents=True)
    (root / "skills").mkdir()
    (root / "skills" / "small.md").write_text("small")
    (root / "skills" / "maint.md").write_text("maint")
    (root / "skills" / "huge.md").write_text("x" * colab_contexts.CAP)
    (root / "colab" / "contexts.yaml").write_text(
        "name: T\nproject: autogalaxy\npreface: P\nrules: R {notebook} {repo}\n"
        "never_map: [maint]\ndefault: {skills: [small]}\ncontexts:\n"
        "  - {match: a/*, skills: [maint]}\n  - {match: b/*, skills: [huge]}\n"
        "  - {match: c/*, skills: [missing]}\n"
    )
    problems = "\n".join(colab_contexts.check(root))
    assert "never_map" in problems and "over the" in problems and "missing" in problems


def test_apply_changes_metadata_only(tmp_path):
    notebook = {
        "cells": [{"cell_type": "markdown", "id": "cell-0", "metadata": {}, "source": ["Hi é"]}],
        "metadata": {"colab": {"provenance": []}, "kernelspec": {"name": "python3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path = tmp_path / "x.ipynb"
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    colab_contexts.apply(path, NOTEBOOK_NAME)
    first = path.read_text()
    colab_contexts.apply(path, NOTEBOOK_NAME)  # idempotent
    assert path.read_text() == first
    stamped = json.loads(first)
    assert stamped["cells"] == notebook["cells"]
    assert stamped["metadata"]["kernelspec"] == {"name": "python3"}
    colab = stamped["metadata"]["colab"]
    assert colab["provenance"] == []
    assert colab["selectedAiContext"] == "eeaf2f2f-9ba2-5080-af36-9325f0df29b8"
    (entry,) = colab["aiContexts"].values()
    assert NOTEBOOK_NAME.split("/", 1)[1] in entry["context"]
    assert first.endswith("}\n") and "Hi é" in first


def _mini(tmp_path, cap_line=""):
    root = tmp_path / "assistant"
    (root / "colab").mkdir(parents=True)
    (root / "skills").mkdir()
    (root / "skills" / "mid.md").write_text("y" * 25_000)
    (root / "colab" / "contexts.yaml").write_text(
        f"{cap_line}\nname: T\nproject: p\npreface: P\nrules: R {{notebook}} {{repo}}\n"
        "default: {skills: [mid]}\ncontexts: []\n"
    )
    return root


def test_cap_defaults_to_20k(tmp_path):
    root = _mini(tmp_path)
    assert colab_contexts.cap_of(colab_contexts.load(root)) == colab_contexts.CAP == 20_000
    assert "over the 20000 cap" in "\n".join(colab_contexts.check(root))


def test_custom_cap_honoured(tmp_path):
    root = _mini(tmp_path, "cap: 30000")
    assert colab_contexts.check(root) == []


@pytest.mark.parametrize("cap", ["50001", "0", "-1", "lots", "true"])
def test_cap_out_of_range_rejected(tmp_path, cap):
    root = _mini(tmp_path, f"cap: {cap}")
    assert "no larger than 50000" in "\n".join(colab_contexts.check(root))
    with pytest.raises(ValueError, match="no larger than 50000"):
        colab_contexts.cap_of(colab_contexts.load(root))
