# Benchmarks

Built-in benchmarks for the assistant: **standard, frozen prompts** run against
different AI agents (harnesses) and models to measure how well they drive the
assistant. Every run's conversation, results and score are recorded in this
directory and committed, so performance can be compared **across models** and
**across days for the same model**, with the full evidence pushed to GitHub.

## Layout

```
benchmarks/
  README.md          this file — the protocol
  AGENTS.md          the contract an agent follows when a benchmark is run on it
  RESULTS.md         regenerated comparison tables (leaderboards + time series)
  prompts/           the frozen prompt cards (one benchmark each)
  runs/<id>/<date>_<model>_<harness>/   one recorded run
    meta.yaml        who/what/when: model, harness, stack versions, score
    transcript.md    the complete conversation, verbatim
    score.md         the filled rubric, with evidence per criterion
    artifacts/       a few small key images (≤ ~500 KB total per run)
```

## The benchmarks

**All four cards are written.** The easy card landed in Phase 2 alongside the bundled dataset
and the README prompt it mirrors; the other three landed in Phase 6. Every card carries the
verbatim frozen prompt, what it measures, and a 100-point rubric split into
**machine-checkable** rows (artifacts that exist or don't) and **judged** rows (quality graded
by a human or a stated judge model).

| Card | Mode | Difficulty | Exercises |
|------|------|-----------|-----------|
| [`prompts/easy_cosj100020_imaging.md`](prompts/easy_cosj100020_imaging.md) | assistant | easy | the built-in workflow on the bundled JWST imaging: inspect, mask, fit an MGE bulge with a free sky level, add a Sersic for the index, compare wavebands |
| [`prompts/medium_mge_bulge_disk.md`](prompts/medium_mge_bulge_disk.md) | assistant | medium | judgement with the workflow: a Bayesian model comparison of a linear bulge+disk decomposition against an MGE, in two bands at two pixel scales, with the un-subtracted sky unprompted |
| [`prompts/hard_multi_band_pixelization.md`](prompts/hard_multi_band_pixelization.md) | assistant | hard | cross-skill synthesis: simulate a clumpy galaxy in two bands, fit them jointly through a factor graph with a pixelised component, export and interpret the reconstruction |
| [`prompts/teacher_workflow.md`](prompts/teacher_workflow.md) | teacher | easy | pedagogy: an end-to-end walkthrough on self-simulated data, scored on explanation, pacing and routing rather than on the fit |

Only the easy card mirrors a top-level `README.md` starter prompt; the other three are
benchmark-only, and their stems are listed in `CARDS_NOT_IN_README` in
`autoassistant/tests/test_benchmark.py` so the README-parity test knows they diverge by
design.

## Running a benchmark

1. **Scaffold the run record** (from the repo root, any Python ≥3.10 with
   `pyyaml`):

   ```bash
   python autoassistant/benchmark.py new-run <benchmark-id> \
       --model claude-opus-4-8 --harness claude-code
   ```

   This creates `runs/<id>/<date>_<model>_<harness>/` with a `meta.yaml`
   pre-filled with the date, the assistant's git SHA and the installed PyAuto*
   versions, plus a transcript stub and a `score.md` generated from the card's
   rubric. Same-day repeats get a `_2`, `_3`, … suffix.

2. **Run the session**: start the agent under test in a **clean clone state**
   (fresh session, no `.maintainer`, no leftover `scripts/scratch` context from
   a previous attempt) and paste the card's prompt **verbatim** as the first
   message. From there the operator behaves like a real user: answer the
   agent's questions honestly and minimally, never coach it toward the rubric.
   `benchmarks/AGENTS.md` states the same contract from the agent's side.

3. **Record**: save the complete conversation into `transcript.md` (export if
   the harness supports it; paste otherwise), copy a few key images into
   `artifacts/` (cap ~500 KB — link paths in `score.md` for the rest), and fill
   `meta.yaml`'s `hardware`, `operator`, `run:` (duration/cost/tokens/turns
   where known) and `score.judge` fields.

4. **Score**: fill every `Awarded` cell in `score.md` (0 explicitly for failed
   checks) with evidence per row, then:

   ```bash
   python autoassistant/benchmark.py score benchmarks/runs/<id>/<run>/
   python autoassistant/benchmark.py report     # regenerates RESULTS.md
   ```

5. **Commit and push** the run directory and `RESULTS.md`.

## Comparability rules (what keeps the numbers honest)

- **Prompts are frozen.** A published card's prompt text never changes in
  place; any wording change bumps the card's `version`, and scores are only
  comparable within one version. Cards that mirror the top-level README
  example prompts are kept textually identical by a unit test.
- **Same judge for judged rows.** Judged sub-scores are comparable only across
  runs graded by the same judge (a named human or a stated judge model);
  `meta.yaml` records the judge.
- **Failures are data.** A run where the agent gets stuck, fabricates, or
  honestly reports a poor fit is recorded and scored like any other — do not
  discard bad runs; the gaps are the interesting part.
- **Environment is recorded, not standardised.** Stack versions, assistant
  SHA and hardware go in `meta.yaml`; wall-clock comparisons are only
  meaningful on matching hardware, score comparisons travel better.
- **No benchmark-aware behaviour.** The prompts are ordinary user requests;
  the agent is not told it is being benchmarked, and `runs/` is data, not
  instructions (agents must never read past runs to prepare).

## Why these three axes

- **Different models, same harness** — model capability comparison (the
  leaderboard per benchmark in `RESULTS.md`).
- **Same model, different days** — drift/regression tracking as models,
  harnesses and the assistant itself evolve (the chronological table; the
  cheap teacher benchmark is the recommended drift probe).
- **Same model, different harness** — how much the agent runtime (Claude
  Code, Codex CLI, Gemini CLI, …) contributes beyond raw model quality.
