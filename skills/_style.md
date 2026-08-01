---
name: _style
description: Writing guide for every workspace skill. Read first before adding or revising a skill. Defines tone (conversational, physics-first, encourages reading), structure (Orient → Ask → Branch → Combine), the five properties every skill must have, the python-first rule, and the source-citation form (project-name + repo-relative path).
---

# How to write a workspace skill

This file is a meta-skill: it does not help a user run a galaxy-modelling task directly. It
is the writing guide every other skill in this folder is authored against. Read it before
adding a new skill and re-read it before revising one.

## What a skill is

A skill is a single Markdown file at `skills/<name>.md`. It guides an AI agent through
one galaxy-structure task — composing an imaging model, running a search, inspecting a fit,
simulating a dataset — and in doing so produces or evolves a **Python script** the user
can run. The deliverable is *understanding + a runnable script*, not a chat answer.

The agent reads the skill when activated (either by the user typing `/ag_<name>` or by
the agent matching the skill's frontmatter `description` to the user's request).

## The five properties every skill must have

1. **Scientific and statistical context first.** Before showing API calls, set both the
   astrophysics and the inference. *Why* are we loading the result, fitting this model, or
   running this profile? *What is being inferred*, with what likelihood, what priors,
   what search? The API is in service of the science and the inference, not the other
   way around. Both framings come before code — neither is optional.

2. **Encourage reading the wiki.** Every skill should point at relevant `wiki/`
   pages for the *what* (what is a Sersic index, what is Nautilus, what is a
   pixelisation). Skills are procedure; the wiki is content. If a piece of content
   doesn't exist yet, draft the wiki page in the same change as the skill.

3. **Conversational tone, invites questions.** Talk to the user the way a postdoc
   collaborator would. Ask what they want before doing it. After explaining a concept,
   invite a follow-up. Don't narrate procedures (`Step 1. Step 2.`) when prose works.

4. **Skills compose.** Each skill should leave breadcrumbs to other skills that build on
   it. Mention adjacent skills by name when chaining would unlock something a single
   skill can't.

5. **Records work to the project wiki.** When a skill produces or evolves a non-trivial
   script, the agent must offer (default-yes) to add a dated
   `wiki/project/YYYY-MM-DD-<slug>.md` entry covering (a) *domain motivation* — what
   astrophysics question this is in service of, (b) *statistical motivation* — what's being
   inferred and how, (c) *implementation choice* — the script produced and the key
   decisions. Cross-link every named concept and profile/model into `wiki/core/` and
   `wiki/literature/` using `[[wiki-link]]` slugs (e.g. `[[Sersic1968]]`,
   `[[Emsellem1994]]`, `[[bulge-disk-decomposition]]`). Default to **no** only
   for typo fixes, throwaway exploration, or repeated re-runs of an existing pipeline.

## Python-first

This is the rule that distinguishes the workspace from a tutorial workspace.

- Every skill's main deliverable is a Python script written *for this user's data*.
- The skill body contains the API recipe inline, in fenced ```python``` blocks.
- The skill should leave the user with a `.py` file in `scripts/` they can re-run and
  modify themselves.
- Do **not** just point the user at a pre-existing script in another repo. If you
  reference an example (e.g. inside `autogalaxy_workspace`), say so as a citation but
  produce the user-specific script in the working directory regardless.

## Generated script style

Every Python script the agent saves — whether to `scripts/` or `scripts/scratch/` — follows the
PyAutoGalaxy **workspace** style, not ad-hoc banner comments. It is the same style used by
every script in `autogalaxy_workspace/scripts/` (canonical example:
`autogalaxy_workspace:scripts/imaging/start_here.py`), and it exists for two reasons: it
keeps the science and inference narrative inline with the code, and it makes the script
mechanically convertible to a Jupyter notebook — each top-level `"""..."""` block becomes a
markdown cell and the code between blocks becomes a code cell.

Two rules.

The level of detail in a saved script is **mode-invariant**. Teacher and assistant modes —
at any autonomy level — may change the pacing and depth of the surrounding conversation, but they must not
change the completeness of the script artefact. Write docstrings as if the script may become
part of the open-source repository accompanying a paper: preserve the scientific motivation,
what is inferred and how, consequential assumptions and configuration choices, enough context
to reproduce or adapt the analysis, and resolvable source citations. Avoid tutorial padding and
repetition, but do not remove this information merely because the user is experienced or has
asked for concise interaction.

**1. Title block + `__Contents__` header.** The module opens with a single docstring: a
title underlined with `=`, two or three sentences of orientation, then a `__Contents__`
list with one `- **Name:** one-line summary.` bullet per section that follows.

```python
"""
Galaxy Structure: JWST Imaging
==============================

Fit the morphology of a galaxy observed with JWST imaging: load the data, mask it, compose
a Sersic bulge plus an Exponential disk, and fit it with Nautilus to measure the effective
radius, Sersic index and bulge-to-total light ratio.

__Contents__

- **Imports:** Import the required libraries.
- **Dataset:** Load imaging, apply the mask and over-sampling.
- **Model:** Compose the galaxy's bulge and disk light profiles.
- **Search:** Configure the Nautilus non-linear search.
- **Fit:** Run the fit and inspect the result.
- **Plot:** Save the best-fit subplot.
"""
```

**2. Per-section narrative docstrings, not banner comments.** Each logical section is
introduced by a `"""__Section__"""` docstring whose name matches a `__Contents__` bullet.
The prose carries the astrophysics and inference framing (property #1) and any source citations
(see below) — *not* `# ---` banner comments and *not* `# source:` lines.

Do this:

```python
"""
__Dataset__

We load three ingredients for galaxy modeling: the image (CCD counts), a per-pixel
noise-map, and the PSF. Deconvolving the PSF is what separates a genuinely compact bulge
from a seeing-broadened one, so it is not optional. `pixel_scales` converts pixels to
arcseconds — set it correctly for your instrument (JWST/NIRCam ~ 0.03", HST/ACS ~ 0.05").
Loading is handled by `ag.Imaging.from_fits`
(`PyAutoArray:autoarray/dataset/imaging/dataset.py`).
"""
dataset = ag.Imaging.from_fits(
    data_path=DATASET_PATH / "data.fits",
    noise_map_path=DATASET_PATH / "noise_map.fits",
    psf_path=DATASET_PATH / "psf.fits",
    pixel_scales=PIXEL_SCALES,
)
```

Not this:

```python
# ---------------------------------------------------------------------------
# 1. Load imaging
# ---------------------------------------------------------------------------
# source: PyAutoArray:autoarray/dataset/imaging/dataset.py  (Imaging.from_fits)
dataset = ag.Imaging.from_fits(...)
```

Short clarifying `#` comments *inside* a code block are still fine (e.g. annotating a
single prior). What changes is that section structure and citations live in the docstring,
not in comment banners.

A model section in the same style — note that the physics of the decomposition is stated
before the API, and that the two components are named for what they are measuring:

```python
"""
__Model__

We decompose the galaxy's light into two components: a `Sersic` bulge, whose `sersic_index`
is free so the fit can distinguish a de Vaucouleurs-like spheroid (n ~ 4) from an
exponential one (n ~ 1), and an `Exponential` disk with n fixed to 1. The ratio of their
inferred luminosities is the bulge-to-total light ratio. Both profiles are elliptical,
parameterised by `ell_comps` rather than an axis-ratio/angle pair, which avoids the
periodic-boundary pathology a position angle creates for a non-linear search
(`PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic.py`).
"""
bulge = af.Model(ag.lp.Sersic)
disk = af.Model(ag.lp.Exponential)

galaxy = af.Model(ag.Galaxy, redshift=0.5, bulge=bulge, disk=disk)

model = af.Collection(galaxies=af.Collection(galaxy=galaxy))
```

## Source citations

Code references inside a skill must use the **project name + path relative to that
project's repo root**, resolvable via [`../sources.yaml`](../sources.yaml).

Good:

> See `PyAutoFit:autofit/non_linear/search/nest/nautilus/` for the search's default
> settings, and `wiki/core/api/searches.md#nautilus` for when to pick it.

Bad:

> See `/Users/other/autogalaxy/fit/autofit/non_linear/search/nest/nautilus.py`.

The reason: this workspace is meant to be cloned to other machines. Absolute local paths
break the moment anyone else opens it.

The same `<Project>:<path>` form is used in **generated scripts**, but there it belongs
inside the section docstring prose (see "Generated script style" above) — woven into the
sentence that explains what the call does, never as a standalone `# source:` comment
banner.

## Adaptive depth

Adaptive depth governs the conversation and teaching around a script; it does not reduce the
publication-quality docstring detail required by "Generated script style" above.

Users arrive with different backgrounds. The same skill needs to serve all of them:

- **The galaxy-morphology newcomer.** Knows Python, maybe some astronomy, but hasn't
  fitted a surface-brightness profile before. Doesn't yet know what a Sersic index, an
  effective radius, or a bulge-to-total ratio is, or why the PSF has to be forward-modelled
  rather than divided out. Frame the physics each time a new concept appears; lean heavily
  on the wiki.
- **The PyAuto\* newcomer.** Knows the science fluently — Sersic, de Vaucouleurs,
  Kormendy, the mass-size relation, isophotal analysis — but new to the API. Map straight
  from science question to object; skip the physics lecture.
- **The returning user.** Has used PyAutoGalaxy before. Just wants to load a fit and
  inspect the residuals. Quick API recall, no lecture.

Pick depth from cues in the user's question. *"I'm new to galaxy morphology"* → newcomer.
*"How do I get the bulge-to-total ratio?"* → already knows the science. *"Load
`output/.../abc/`"* → returning user. If ambiguous, ask one disambiguating question; never
default to the longest explanation.

Read `wiki/project/profile.md` if it exists — that's the persistent record of the user's
level and goal, built up over sessions. If it disagrees with what the user just said,
trust the user and update the profile.

### Resource routing by audience

Three external resources cover different audiences. Match the user's level to the source:

| Audience | Lead resource | Secondary |
|----------|---------------|-----------|
| Galaxy-morphology newcomer | **HowToGalaxy** notebook — *surfaced before the code block, not after* | RTD `overview/overview_1_start_here` |
| PyAutoGalaxy newcomer (morphology-fluent) | **RTD** `overview/overview_2_new_user_guide` + `overview/overview_3_features` | Workspace example script |
| Returning PyAutoGalaxy user | **Workspace** script for the science case | RTD API reference |

Never dump all three on the user unprejudiced — pick one to lead, optionally cite a
second.

Expand a cell into a URL with:

- **HowToGalaxy (notebook):** `https://github.com/PyAutoLabs/HowToGalaxy/blob/main/notebooks/<cell>.ipynb`
- **HowToGalaxy (script):** `https://github.com/PyAutoLabs/HowToGalaxy/blob/main/scripts/<cell>.py`
- **RTD:** `https://pyautogalaxy.readthedocs.io/en/latest/<cell>.html`
- **Workspace script:** `https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/<cell>`

Default to `.ipynb` for student-leaning users and `.py` for returning PyAutoGalaxy users.
A per-skill routing table under `wiki/core/external/` will replace this hand expansion in a
later phase (see the repo-root `PENDING.md`); until it lands, resolve a path against the
target repo's own generated catalogue (`llms.txt` / `llms-full.txt` at its root) rather than
guessing, and never cite a tutorial you have not confirmed exists.

The HowToGalaxy lecture series runs in five parts, and the chapter you route to should
match what the user is actually stuck on:

| Chapter | Teaches | Route here when the user… |
|---------|---------|---------------------------|
| `chapter_1_introduction` | grids, galaxies, light profiles, imaging data, fitting, the likelihood | …has never fitted a light profile, or asks what a Sersic/chi-squared/PSF convolution *is* |
| `chapter_2_modeling` | non-linear search, realism and complexity, dealing with failure, linear profiles, masking, results | …can fit but the search fails, stalls, or returns something unphysical |
| `chapter_3_search_chaining` | chaining searches, prior passing, two-galaxy fits | …has a model too complex for one search, or blended neighbours |
| `chapter_4_pixelizations` | pixelisations, mappers, inversions, Bayesian regularisation | …has an irregular/clumpy galaxy no smooth profile fits |
| `chapter_optional` | the non-linear search zoo | …is choosing between samplers |

### Newcomer mode

When the user signals they're new to galaxy structure — *"I'm new to this"*, *"I've never
fitted a galaxy before"*, *"can you explain what the Sersic index means?"* — the agent
shifts into a more pedagogical shape. The conversation arc still applies; what changes is
the depth, ordering, and pacing.

1. **Lead with the HowToGalaxy notebook.** Before any code block, surface the tutorial
   notebook URL (expanded per the table above). The notebook is the primary path; the
   skill-produced script is the follow-up artefact, not the lead.
2. **One concept at a time.** Don't stack three concepts in one branch — pick the
   one most central to the user's question, frame it, then offer to go deeper.
   *"Let's get the effective radius clear first; once that lands we can move on to
   how the Sersic index changes the profile's shape"* beats firing all three
   simultaneously.
3. **Physics framing → statistical framing → code.** Property 1 already requires
   both framings; for newcomers each framing gets at least one short paragraph and
   at least one `wiki/core/` link before any code.
4. **Check-in beat after each concept.** End with an explicit invitation: *"does
   that make sense, or want me to unpack X further?"*. Don't barrel into the next
   branch.
5. **Encourage running HowToGalaxy themselves.** A newcomer who runs the linked
   notebook alongside the script learns far faster than one who only reads
   citations. Mention this once per session: *"the notebook is short — if you run
   it as you read along, it'll click faster."*

Newcomer mode is a default for the morphology-newcomer audience, not a separate state.
As soon as the user shows they've absorbed a concept, drop the check-in beats and
move on.

## The conversation arc — Orient → Ask → Branch → Combine

Structure every skill as a conversation, not a checklist.

**Orient.** When the skill activates, give a short opening: what this task is
scientifically, what the user is about to do, the most relevant wiki page, and one
concrete data example tailored to what they mentioned (HST, JWST, Euclid, ALMA, JVLA…).
Two short paragraphs at most.

**Ask.** Before writing code, ask what the user wants out of the task. *"Do you want a
single Sersic first, or go straight to a bulge-disk decomposition?"* The answer chooses the
branch and lets the skill calibrate depth. Skip this step only when the user has already
told you.

**Branch.** Each sub-task lives in its own narrative branch. A branch has four parts:

- Physics framing (one or two sentences, scaled to the user's depth).
- The Python recipe — actual code, in a fenced block, that the agent should adapt and
  save to `scripts/`. When the recipe is a full saved script (not a one-off fragment),
  write it in the **Generated script style** above: title + `__Contents__` header and
  `"""__Section__"""` narrative sections rather than banner comments.
- The wiki page that teaches this in depth, plus the source-code citation
  (`<Project>:<path>`).
- An invitation to dig deeper.

**Combine.** End the skill (or the chosen branch) with a short note on what else the
user could do, especially with other skills. *"Once you have the fit running, feed the
output into the results-loading and fit-plotting skills."* Name a skill with a relative
link only once its file exists; while a skill is still pending, refer to it by role
instead of linking to a file that isn't there.

A slim agent-facing procedural checklist at the very bottom of the file is fine — but
the user-facing content above should read like a conversation arc, not a recipe.

## Voice rules

**Do**

- Speak in second person. The user is the protagonist.
- Invite questions explicitly (*"ask if you want me to explain how this works"*).
- Tie at least one concrete example to the user's data when their data type is known.
- Point at the wiki by relative path every time you teach a concept.
- For newcomers, surface the relevant HowToGalaxy notebook before the code block, not
  after. See "Newcomer mode" in Adaptive depth above.
- When a script produces plot files, quote the absolute path and offer to open it
  with the platform's opener. See "Plot output and path announcement" below.

**Don't**

- Don't open with a numbered procedure.
- Don't dump a wall of links — one or two per concept, chosen for relevance.
- Don't present code as the deliverable on its own — the deliverable is understanding +
  a saved script.
- Don't build a skill's *default* prose around a "just run this for me" tone — the standing
  deliverable is understanding plus a runnable script, so frame the science and cite the wiki
  rather than assuming black-box automation. This governs how the skill reads by default; it
  does **not** override an explicit user opt-out. When the user asks to one-shot it (see
  [`../modes/assistant.md`](../modes/assistant.md) "Opt-out — silent execution"), honour that
  and run it — the two are not in conflict.

## Frontmatter

Every skill file starts with YAML frontmatter:

```markdown
---
name: <kebab-case-name>
description: <one paragraph the agent reads when deciding whether to activate this skill>
---
```

The `description` is what the agent uses to decide when the skill applies. Write it so
a future agent that has only read the description (not the body) can decide from it
alone. Mention the kind of task, the kind of input, and what the skill should NOT be
used for.

## When a skill needs new wiki content

If you cannot point at a wiki page that explains a concept your new skill uses, draft
the wiki page in the same change. The wiki page should follow the wiki frontmatter
format (see [`../wiki/README.md`](../wiki/README.md)) and cite source code by
`<Project>:<path>`.

The reverse is also true: don't write a wiki page nobody references. The wiki exists to
back up the skills.

## Plot output and path announcement

Skills that produce visualisations save them through the function-style plotting API
imported as `aplt` — every entry point takes `output_path` / `output_filename`
/ `output_format` kwargs directly. Three rules:

1. **Pass `output_path` / `output_filename` / `output_format` directly to
   each plot function.** Every `plot_*` and `subplot_*` helper in `aplt` accepts
   these kwargs, e.g. `aplt.subplot_imaging_dataset(dataset=…,
   output_path="scripts/scratch/<context>/", output_filename=…,
   output_format="png")`. Never rely on interactive display — the user is
   often running the script from a terminal where `plt.show()` flashes and
   vanishes. The `<context>` slug is usually the dataset name; for general
   exploration any short slug works.
2. **`print(...)` each plot's path** at the end of the Python recipe so the
   absolute location lands in stdout. Use
   `print(f"Saved to: {PLOT_DIR.resolve()}")` once per branch (sufficient
   because each `aplt.*` call writes deterministically inside `PLOT_DIR`); for
   single-figure calls it's fine to print the exact `.png` path instead.
3. **The agent quotes the path back** to the user after running the script
   and offers to open it — one offer per plot run, not nagging. Use the
   platform's opener: `open <path>` on macOS, `xdg-open <path>` on Linux,
   `explorer.exe` (or `wslview`) from WSL.

There is deliberately no object-oriented plotter or figure-configuration object to
construct: the whole plotting surface is the module-level functions, and `dir(aplt)` is the
authoritative list of them. If a call you remember is not in that list, it is not part of
the current API — check before you emit it. A `wiki/core/api/plotting.md` catalogue of these
entry points arrives in a later phase (see `PENDING.md`).

The full convention — committed Python lives in `scripts/`; throwaway plots and data
dumps go to the gitignored `scripts/scratch/` — is in [`../AGENTS.md`](../AGENTS.md)
"Conventions". Skills here are the application of that rule.

## Output folder announcement

A running fit is not a black box. `search.fit(...)` writes to
`output/<path_prefix>/<name>/<unique_id>/` **on the fly**, using the highest-likelihood
model found so far, so the folder is worth opening the moment the search starts — not
when it terminates hours later. Users new to the stack rarely know this and sit watching
a silent terminal. Three rules:

1. **Announce the folder at launch, not at the end.** Quote the absolute path once the
   fit is running, and say `model.results` and the `image/` subplots refresh as the
   search goes — there is nothing to wait for.
2. **Point at the workspace's own layout prose; don't restate it.** The annotated tree of
   `files/`, `image/`, `model.info`, `model.results`, `search.summary` and the
   `<unique_hash>` resume behaviour is `__Output Folder Layout__` in
   [`autogalaxy_workspace/scripts/imaging/modeling.py`](https://github.com/PyAutoLabs/autogalaxy_workspace/blob/main/scripts/imaging/modeling.py)
   (the same section appears in the `interferometer`, `multi_dataset`, `multi_galaxy` and
   `cluster` `modeling.py` scripts). Link it once per fit; never copy the tree into a
   skill, where it would rot.
3. **Name what to open first.** `model.results` for the human-readable fit summary and
   `image/fit.png` for data / model image / residuals — then the results-loading skill for
   the programmatic read.

Depth follows "Adaptive depth" above. For either **newcomer** audience, and whenever
[`../modes/teacher.md`](../modes/teacher.md) is active, walk all three rules — reading the
output folder *is* part of the workflow being taught. For a returning user, rule 1 alone
(one line quoting the path) is enough.

## External resource citation

Every `ag_*` skill ends with a single `## Further reading` block above the agent
checklist (if present). The block follows this shape, with URLs expanded per "Resource
routing by audience" above:

```markdown
## Further reading

- **Student / new to galaxy morphology** — [HowToGalaxy: <tutorial title>](<expanded URL>):
  one line on what the tutorial teaches.
- **General reference** — [RTD: <page title>](<expanded URL>): canonical PyAutoGalaxy
  documentation page.
- **Experienced PyAutoGalaxy user** — [workspace: <script name>](<expanded URL>):
  production-style example to fork from.
```

Rules:

- Three bullets max, one per audience. Omit any for which no suitable resource exists.
- Every URL must be one you have confirmed resolves — against the target repo's `llms.txt`
  catalogue or the RTD page list, never from memory.
- The agent **picks one of the three to surface in the conversation** — the audience
  match comes from `wiki/project/profile.md` (or, lacking that, from the user's
  immediate cues). The other two stay in the block as references the user can fall
  back on.
- For non-`ag_*` skills (project workflow, meta), this section is optional; include
  it only if a single external resource is the canonical reference.

## Iteration

This guide is the workspace v1 writing guide. As patterns emerge, update this file in
the same change as whatever motivated the update. Note the change at the top of that
PR description.
