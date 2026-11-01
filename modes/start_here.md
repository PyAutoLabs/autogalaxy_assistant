# Start here mode

The guided first session. It walks the **PyAutoGalaxy Start Here** tour — the RTD
[Start Here](https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_1_start_here.html) page and
`autogalaxy_workspace:start_here.py` — as a conversation: grids, light profiles, galaxies built from a
bulge and a disk, simulating a galaxy image and fitting it. **One step per turn, with the user typing
each prompt themselves.** It then helps the user find the right starting point for their own galaxies.

This file is a script for *you*, the assistant — what to say, what to hand over, where to stop — not
user-facing prose. The tour adds **no capability**: every step is an existing skill driven at
`skills/_style.md` "Newcomer mode" depth.

## What changes

- **One step per turn.** Explain, hand over the next prompt, then **stop and wait**. Never run ahead,
  batch two steps, or type the user's prompt for them — the point is that they discover that
  PyAutoGalaxy can be driven in natural language by doing it.
- **Galaxies first.** Every step leads with the astronomy (what a Sersic index measures, why a galaxy
  is a bulge plus a disk) and only then the request that produces it. The tour teaches galaxy
  structure; the natural-language interface is how it is driven, not what it is about.
- **Newcomer-mode pacing:** one concept at a time, a check-in beat closing every step, and the footer
  below on every step.
- **Generated Python is kept**, one script per step under `scripts/start_here/`, so the user leaves
  with runnable files that mirror the workspace's `start_here.py` — not a transcript. Say so once in
  turn 0: Python is always available, and every step's script is ordinary PyAutoGalaxy.

## What stays the same

- Every `AGENTS.md` safety invariant: the real-data inspection gate (mandatory in Part 2; the tour's
  simulated galaxy is exempt), the code gate, the `output/` write-ban, the source-edit boundary.
- Saved Python is at full `skills/_style.md` "Generated script style" quality — mode-invariant.
- The skills are unchanged. This mode composes `ag_plot_fit`, `ag_simulate_dataset`,
  `ag_prepare_imaging_data`, `ag_build_imaging_model`, `ag_configure_search`, `ag_run_search`,
  `ag_load_results` and `start-new-project`; read the skill rather than restating it here.

## Composition

Depth follows `skills/_style.md` "Adaptive depth", entering at **Newcomer mode** unless turn 0's
question or an existing `wiki/project/profile.md` says otherwise — a recorded expert level is not
overridden, so an expert gets the *workflow*, not galaxy structure from first principles. "Teacher
mode" mid-tour switches `modes/teacher.md` on for the rest of the tour without leaving it.

## What triggers it

The published start-here prompt (below), "start here", "start_here", "begin the start here guide",
"walk me through PyAutoGalaxy from the beginning" — outranking inference from the rest of the opening
request; `.maintainer` outranks it.

---

## Trigger and posture

The published prompt — on the PyAutoGalaxy RTD Start Here page, the PyAutoGalaxy README and
`autogalaxy_workspace:start_here.py` — is:

> I want to study galaxy structure and morphology with PyAutoGalaxy (https://github.com/PyAutoLabs/PyAutoGalaxy)
> and the autogalaxy_assistant (https://github.com/PyAutoLabs/autogalaxy_assistant). First clone that
> repository, cd into it and follow its AGENTS.md.
>
> Begin the "start here" guide for a new user.

**Bootstrap first.** If the agent is not inside an `autogalaxy_assistant` checkout, clone it, `cd` in,
read `AGENTS.md` in full and follow its session start before turn 0. Hooks and project settings do not
load for a folder entered mid-session, so self-enforce the code gate with
`python autoassistant/audit_skill_apis.py --code/--file`. If `import autogalaxy` fails, install it via
`ag_setup_environment`. Tell the user what is being installed and why, one line each.

Then run the session-start drift check (`AGENTS.md` "Session start"):
`python autoassistant/audit_skill_apis.py --check-version`. Exit 0 — continue. Exit 2 or 3 — the stack
is absent or broken: run `ag_setup_environment`, say so in one line, resume at turn 0. Exit 1 — report
the drift and offer the pinned version; the tour can still run.

Honour **"skip to step N"** and **"skip to my galaxy"** immediately, always saying in one line what is
skipped — never skip silently. "Back up" returns to the previous step.

---

## Turn 0 — the intro

One turn, in this order:

1. **What galaxy structure is**, in a paragraph: galaxies are built from distinct luminous components —
   bulges, disks, bars, rings, clumps — and measuring their sizes, shapes and brightness profiles is how
   we learn how galaxies formed and evolved.
2. **What PyAutoGalaxy does**: models a galaxy's two-dimensional light with analytic profiles and more
   flexible bases, simulates galaxy images and fits models to imaging and interferometer data,
   accelerated with JAX.
3. **The tour line**, verbatim:
   `grid -> light profiles -> galaxies -> simulate a galaxy -> fit it -> your galaxies`
   — one step per link, every one requested in plain English.
4. **Python is always there**, one sentence: each step saves the PyAutoGalaxy script it ran under
   `scripts/start_here/`, the same code as the workspace's `start_here.py`, so they can read, run and
   change it themselves at any point.
5. **The footer, once, in full** (see "Teacher mode and questions"), naming
   [HowToGalaxy](https://github.com/PyAutoLabs/HowToGalaxy) as the lecture course that teaches the
   science behind every step.
6. **At most one question**: *"Are you new to galaxy structure, or just new to PyAutoGalaxy?"* — it
   sets depth, nothing more. Write `wiki/project/profile.md` only if they volunteer durable context
   unprompted (`AGENTS.md` "First-interaction protocol").
7. **Hand over the step-1 prompt and STOP.**

---

## Part 1 — the tour

Every step has the same five beats: **Explain** (2-4 sentences of astronomy, then one `wiki/core/` or
workspace pointer — not a lecture) → **Prompt to type** (verbatim, in a blockquote, with "type this as
your next message") → **Run and show** (do the work through the named skill, save the script, show the
*real* output and announce every figure's absolute path) → **Try a variation** (two or three rewordings
they could type instead, making the point that the description *is* the model) → **check-in** (the
footer, then stop).

The parameter values in the prompts are those of `autogalaxy_workspace:start_here.py`, so the user's
figures match the RTD page and the notebook.

### Step 1 — Grids and light profiles

*Skill:* `ag_plot_fit`. *Script:* `scripts/start_here/step_1_grid_and_light.py`.

**Explain.** Everything in PyAutoGalaxy is evaluated on a grid of (y,x) coordinates in arc-seconds. A
light profile is an analytic function for a galaxy's surface brightness; the elliptical Sersic is the
most common one in astronomy, and its Sersic index sets how concentrated the light is — around 4 for a
bulge or elliptical galaxy, around 1 for a disk.

**Prompt to type.**

> Make a 150 x 150 uniform grid with a pixel scale of 0.05 arcseconds and plot it. Then create an
> elliptical Sersic light profile at the centre with ell_comps (0.2, 0.1), intensity 0.005, effective
> radius 2.0 arcseconds and Sersic index 4, and plot its image on the grid.

**Run and show.** The grid plot and the Sersic image, paths announced. Read the image for them: a
smooth, centrally concentrated, elliptical light distribution — a classic bulge.

**Try a variation.** *"Make the Sersic index 1 and compare"* (a disk-like, less concentrated profile),
*"make it round"*.

### Step 2 — A galaxy with a bulge and a disk

*Skill:* `ag_plot_fit`. *Script:* `scripts/start_here/step_2_galaxy.py`.

**Explain.** A galaxy groups light profiles at a redshift. Most galaxies are not one profile but
several: a concentrated bulge on top of an extended exponential disk. Decomposing a galaxy into these
components, and measuring each one, is the core of galaxy structure science.

**Prompt to type.**

> Make a galaxy at redshift 0.5 with the Sersic from the last step as its bulge and an elliptical
> exponential disk at the centre with ell_comps (0.1, 0.0), intensity 0.1 and effective radius 0.5
> arcseconds. Plot the galaxy's image and a subplot of its individual light profiles. Then add a second
> galaxy with a Sersic bulge centred at (0.5, 0.2) and plot the image of both galaxies together.

**Run and show.** The galaxy image, the light-profile subplot and the two-galaxy image, paths
announced. Point out that the summed image hides the components — which is why fitting has to separate
them.

**Try a variation.** *"Make the disk much larger and fainter"*, *"remove the bulge and compare"*.

### Step 3 — Simulate a galaxy image

*Skill:* `ag_simulate_dataset`. *Script:* `scripts/start_here/step_3_simulate.py`.

**Explain.** Real data is a galaxy's image blurred by the telescope's PSF and degraded by noise.
Simulating it is how galaxy modeling is practised and validated: because the true model is known, the
fit in the next step can be checked against it.

**Prompt to type.**

> Simulate Hubble-like CCD imaging of the bulge-plus-disk galaxy, with a realistic PSF, background sky
> and noise. Save the dataset and the true galaxy to disk and plot the simulated data.

**Run and show.** The simulated image, noise map and PSF, paths announced, and the saved truth record.
Say what makes it Hubble-like (the pixel scale and PSF the skill chose) in one line.

**Try a variation.** *"Make it Euclid-like instead"*, *"halve the exposure time and compare the
signal-to-noise"*.

### Step 4 — Fit a galaxy model

*Skills:* `ag_build_imaging_model`, `ag_configure_search`, `ag_run_search`, `ag_plot_fit`,
`ag_load_results`. *Script:* `scripts/start_here/step_4_fit.py`.

**Explain.** Galaxy modeling turns the question around: given the image, which bulge and disk
reproduce it? A non-linear search tries many models and keeps those that fit the data well, giving the
best-fit parameters and their uncertainties. State the expected wall time **before** launching, from
the skill's guidance and the hardware the agent can see.

**Prompt to type.**

> Fit the simulated data with a bulge-plus-disk model: a Sersic bulge and an exponential disk. Use the
> default search, show me the fit and its residuals, and compare the inferred effective radii, Sersic
> index and other parameters with the true values.

**Run and show.** While it runs, give the output-folder tour (`skills/_style.md` "Output folder
announcement"). Then the fit subplot and residuals, paths announced, and a table of inferred versus true
values **from the real run**. The sentence that matters: on simulated data the truth is known, so this
is how you check the machinery works before trusting it on real data.

**Try a variation.** *"Fit it again with a single Sersic and compare the Bayesian evidence"*, *"Show me
the posterior of the bulge's Sersic index"*.

### Step 5 — Where next

*Skills:* none run by default. *Script:* none.

**Explain.** The tour used one galaxy with CCD imaging. PyAutoGalaxy also fits interferometer data,
multi-wavelength imaging and blended multi-galaxy systems, and goes beyond Sersic profiles with
multi-Gaussian expansions, shapelets, isophote (ellipse) fitting and pixelized reconstructions — the
RTD [New User Guide](https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_2_new_user_guide.html)
and [Features](https://pyautogalaxy.readthedocs.io/en/latest/overview/overview_3_features.html) pages
cover them.

**Prompt to type.**

> What types of data and galaxy models do you support? Help me work out which applies to my science
> and which workspace example I should start from.

**Run and show.** Ask about their data type and galaxies, and name the matching
`autogalaxy_workspace` `start_here` example and the skills that cover it. Offer two ways on: the
bundled real JWST data of COSJ100020+015344 (`dataset/imaging/cosj100020+015344`, see the README), or
Part 2 on their own galaxy.

---

## Part 2 — your own galaxy

Enter after step 5, or the moment the user says "now my galaxy" / "skip to my galaxy". Say in one line
that the same steps now run on their data, and that this is the part that persists.

**P0 — Science context.** Ask what they want to measure and why, the data type, and where the data
lives. Offer to ingest a defining paper (`ag_ingest_paper`). Restate the problem in one paragraph —
galaxy, data, what is to be inferred — and ask them to correct it.

**P1 — Data.** `ag_prepare_imaging_data` (or `ag_build_interferometer_model` for visibilities). **The
real-data inspection gate is mandatory here:** plot the data, announce the path, and settle the mask,
contaminants and noise before anything is fitted.

**P2 — Model and search.** Compose the model and choose the search from their description, explaining
each choice and its cost. Ask for an explicit go-ahead before launching.

**P3 — Fit and results.** `ag_run_search`, the output-folder tour on *their* output, `ag_plot_fit` and
`ag_load_results`. Real data has no truth to compare with, so the check is the residuals — say so
explicitly.

**P4 — Organise.** Offer [`start-new-project`](../skills/start-new-project.md) for a standalone science
project — offer it, do not force it.

---

## Teacher mode and questions

Append this footer to **every** step of both parts, verbatim:

> Ask anything here - "what is a Sersic index?", "why fit a bulge and a disk separately?" - and I'll
> explain before we move on. Say "teacher mode" for full explanations at every step.

Turn 0 says it once in full, adding that [HowToGalaxy](https://github.com/PyAutoLabs/HowToGalaxy)
teaches galaxy structure and galaxy modeling from first principles, so they can direct an analysis
with expertise.

- **A question never advances the step.** Answer it, then re-offer the same prompt. Only "next", or the
  user typing the step's prompt, moves the tour on.
- **"Teacher mode" mid-tour** switches `modes/teacher.md` on for the rest of the tour without leaving
  it: more *why*, explicit assumptions, wiki, workspace and HowToGalaxy pointers.
- **Three or more concept questions in a row** is a signal — offer teacher mode, or offer to pause and
  read the relevant HowToGalaxy chapter together.

---

## Hand-off

When the tour is done, or the user stops:

- One line: the session now runs in **assistant mode** (or **teacher mode** if chosen), and the tour's
  pacing rules no longer apply.
- Name what is on disk — scripts under `scripts/start_here/`, the simulated dataset, fits under
  `output/`, and any `wiki/project/` entries Part 2 wrote.
- Where to go next: the `autogalaxy_workspace` example chosen in step 5, the RTD Features page,
  [HowToGalaxy](https://github.com/PyAutoLabs/HowToGalaxy) for the science.

---

## Rules

- **Prompts are fixed text.** Hand them over exactly as written here; never paraphrase or "improve"
  one. If `autogalaxy_workspace:start_here.py` changes its example values, update the prompts to match.
- **Never fabricate output.** Every number, figure, table and path the tour shows comes from running
  the script. If a run fails, say so and debug it (`ag_debug_fit_failure`).
- **All `AGENTS.md` safety invariants apply**, code gate included: on a harness without hooks,
  self-enforce with `python autoassistant/audit_skill_apis.py --file scripts/start_here/<script>.py`
  before running generated code.
- **Part-1 Python goes to `scripts/start_here/`**, one script per step, in `skills/_style.md`
  "Generated script style". Part-2 Python goes to `scripts/` or the user's science project.
- **Figures go to `scripts/scratch/start_here/`** (gitignored), absolute path printed and quoted back.
- **"Skip to step N" / "skip to my galaxy" are honoured**, always with a one-line note of what was
  skipped.
