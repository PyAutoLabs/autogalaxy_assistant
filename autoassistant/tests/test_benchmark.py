"""Tests for the benchmark harness (autoassistant/benchmark.py)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from autoassistant import benchmark

REPO_ROOT = Path(__file__).resolve().parents[2]
REPO_PROMPTS = REPO_ROOT / "benchmarks" / "prompts"

# Cards whose prompt text is deliberately NOT mirrored in README.md. Every other card
# must match the README verbatim (benchmarks/README.md "Comparability rules"), so a
# newly-added card defaults to being checked rather than silently exempt. Add a stem
# here only when a card is meant to diverge.
#
# The README advertises three starter prompts; only the second of them is a benchmark
# (the easy card). The other three cards are benchmark-only — a medium model comparison,
# a hard cross-feature synthesis and the teacher walkthrough — so they have no README
# counterpart to stay identical to.
CARDS_NOT_IN_README: frozenset = frozenset(
    {
        "medium_mge_bulge_disk",
        "hard_multi_band_pixelization",
        "teacher_workflow",
    }
)


CARD = """\
---
id: test-bench
version: 2
mode: assistant
difficulty: easy
datasets: []
workspace_packages:
  - imaging
added: 2026-07-10
---

# Benchmark: test

## Prompt

```
Assistant mode. Do the thing.
```

## Success rubric (30 points)

### Machine-checkable (20)

| # | Check | Pts |
|---|-------|-----|
| M1 | A thing exists | 10 |
| M2 | Another thing exists | 10 |

### Judged (10)

| # | Criterion | Pts |
|---|-----------|-----|
| J1 | The thing was done well | 10 |
"""


@pytest.fixture
def root(tmp_path):
    prompts = tmp_path / "benchmarks" / "prompts"
    prompts.mkdir(parents=True)
    (prompts / "test_bench.md").write_text(CARD)
    return tmp_path


def fill_score(run_dir, awards):
    path = run_dir / "score.md"
    lines = []
    for line in path.read_text().splitlines():
        m = benchmark.SCORE_ROW.match(line)
        if m and m.group(1) in awards:
            code, criterion, max_points = m.group(1), m.group(2), m.group(3)
            lines.append(
                f"| {code} | {criterion} | {max_points} | {awards[code]} | evidence |"
            )
        else:
            lines.append(line)
    path.write_text("\n".join(lines) + "\n")


def test_load_card_parses_frontmatter_and_rubric(root):
    cards = benchmark.load_cards(root)
    card = cards["test-bench"]
    assert card.version == 2
    assert [r.code for r in card.rubric] == ["M1", "M2", "J1"]
    assert card.rubric[0].max_points == 10
    assert card.rubric[0].machine and not card.rubric[2].machine


def test_new_run_scaffolds_run_directory(root):
    run_dir = benchmark.new_run(root, "test-bench", "Claude Opus 4.8", "claude-code")
    assert run_dir.name.endswith("_claude-opus-4.8_claude-code")
    assert (run_dir / "transcript.md").exists()
    assert (run_dir / "artifacts").is_dir()
    meta = yaml.safe_load((run_dir / "meta.yaml").read_text())
    assert meta["benchmark"] == "test-bench"
    assert meta["prompt_version"] == 2
    assert meta["status"] == "pending"
    assert set(meta["stack"]) == set(benchmark.STACK_PACKAGES)
    score_text = (run_dir / "score.md").read_text()
    assert "| M1 |" in score_text and "| J1 |" in score_text


def test_new_run_same_day_repeat_gets_suffix(root):
    first = benchmark.new_run(root, "test-bench", "m", "h")
    second = benchmark.new_run(root, "test-bench", "m", "h")
    assert second.name == f"{first.name}_2"


def test_new_run_unknown_benchmark_fails(root):
    with pytest.raises(SystemExit):
        benchmark.new_run(root, "nope", "m", "h")


def test_score_run_totals_and_updates_meta(root):
    run_dir = benchmark.new_run(root, "test-bench", "m", "h")
    fill_score(run_dir, {"M1": 10, "M2": 0, "J1": 7.5})
    score = benchmark.score_run(run_dir)
    assert score.machine == 10 and score.judged == 7.5 and score.total == 17.5
    meta = yaml.safe_load((run_dir / "meta.yaml").read_text())
    assert meta["score"]["total"] == 17.5
    assert meta["status"] == "complete"


def test_score_run_rejects_unfilled_rows(root):
    run_dir = benchmark.new_run(root, "test-bench", "m", "h")
    fill_score(run_dir, {"M1": 10})
    with pytest.raises(SystemExit, match="unfilled"):
        benchmark.score_run(run_dir)


def test_score_run_rejects_over_max_award(root):
    run_dir = benchmark.new_run(root, "test-bench", "m", "h")
    fill_score(run_dir, {"M1": 11, "M2": 0, "J1": 0})
    with pytest.raises(SystemExit, match="outside"):
        benchmark.score_run(run_dir)


def test_report_builds_leaderboard_and_pending(root):
    scored = benchmark.new_run(root, "test-bench", "model-a", "h")
    fill_score(scored, {"M1": 10, "M2": 10, "J1": 5})
    benchmark.score_run(scored)
    pending = benchmark.new_run(root, "test-bench", "model-b", "h")

    text = benchmark.report(root)
    assert "## test-bench" in text
    assert "| model-a | h | 1 | 25 | 25 |" in text
    assert f"`{pending.relative_to(root / 'benchmarks')}`" in text

    path = benchmark.write_report(root)
    assert path == root / "benchmarks" / "RESULTS.md"
    assert path.read_text() == text


def test_repo_prompt_cards_parse():
    """Every committed prompt card must load: unique ids, frontmatter, rubric."""
    card_files = sorted(REPO_PROMPTS.glob("*.md"))
    # The suite ships four cards (easy/medium/hard/teacher). An empty prompts/ dir would
    # make every loop below vacuous, so assert the cards are actually there.
    assert card_files, f"no prompt cards found in {REPO_PROMPTS}"
    # load_cards raises on a duplicate id, so a shortfall here means a card file
    # failed to yield a card at all.
    cards = benchmark.load_cards(REPO_ROOT)
    assert len(cards) == len(card_files), (
        f"{len(card_files)} card file(s) produced only {len(cards)} card id(s)"
    )
    for card in cards.values():
        machine = sum(r.max_points for r in card.rubric if r.machine)
        judged = sum(r.max_points for r in card.rubric if not r.machine)
        assert machine + judged == 100, f"{card.id}: rubric totals {machine + judged}"


def test_repo_card_datasets_exist():
    """Bundled datasets a card declares must exist — a missing one is a stale card."""
    for card in benchmark.load_cards(REPO_ROOT).values():
        for dataset in card.meta.get("datasets", []):
            assert (REPO_ROOT / dataset).is_dir(), f"{card.id}: missing {dataset}"


def test_repo_readme_prompts_match_cards():
    """Cards that mirror README example prompts must stay textually identical."""
    readme = (REPO_ROOT / "README.md").read_text()
    for path in sorted(REPO_PROMPTS.glob("*.md")):
        if path.stem in CARDS_NOT_IN_README:
            continue
        prompt = path.read_text().split("```\n", 1)[1].split("```", 1)[0]
        assert prompt.strip() in readme, (
            f"{path.stem}: prompt text diverges from README.md (add the stem to "
            "CARDS_NOT_IN_README if the divergence is deliberate)"
        )
