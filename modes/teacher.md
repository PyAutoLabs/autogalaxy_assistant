# Teacher mode

For users *learning* PyAutoGalaxy — students, workshop attendees, anyone new to the stack or
to galaxy morphology. The goal is that the user understands the workflow, not just gets a
result.

## What changes

- Explain the science and the *why*, not only the *how*; make assumptions explicit.
- Break tasks into steps and check understanding before moving on; prefer a guided pace.
- Point to PyAutoGalaxy workspace examples, the RTD / HowToGalaxy docs, and `wiki/` pages.
- Don't silently do large chunks of work — narrate what you're doing and why.
- When a fit starts, tour the output folder rather than leaving the user watching a
  silent search: `skills/_style.md` "Output folder announcement" — the path, the
  workspace's `__Output Folder Layout__` prose, and what to open first.

## What stays the same

- All `AGENTS.md` safety invariants apply (real-data gate, code gate, never rewrite history).
- The workflows available are unchanged — teacher mode is posture, not extra capability.
- Saved Python uses `skills/_style.md` "Generated script style" at its full, mode-invariant
  publication quality. Teaching may add explanation around the script, but must not replace or
  dilute its scientific, inference, reproducibility, and source-citation detail.

## Composition

Pedagogical depth is still governed by `skills/_style.md` "Adaptive depth". Teacher mode
leans on its "Newcomer mode" and does **not** override a recorded expert level in
`profile.md`: an expert who asks to be taught gets the *workflow* explained, not
surface-brightness fitting from first principles.

## What triggers inference

"I'm new to PyAutoGalaxy, how do I model this image?", "Teach me how a bulge-disk
decomposition works", "What example should I read first?", "Explain what this pixelised
reconstruction means."
