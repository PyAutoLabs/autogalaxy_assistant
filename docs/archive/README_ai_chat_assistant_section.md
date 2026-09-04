<!-- Archived 2026-09-03 from README.md (section "### AI Chat Assistant") for reinstatement when
     conversation-assistant support returns — see autolens_assistant#120 -->

### AI Chat Assistant

Ask questions to a conversational AI assistant such as **ChatGPT** or **Claude** in a
desktop browser.

This requires two things:

- Make sure your assistant has a **GitHub connector** enabled so it can read this
  repository, and give it this repository's URL
  (https://github.com/PyAutoLabs/autogalaxy_assistant) in your opening prompt.
- Point the assistant explicitly at [`llms.txt`](llms.txt), which gives it the start-up
  instructions for how `autogalaxy_assistant` works. Connectors do not reliably fetch that
  file on their own, and results are markedly better when it is named.

So prefix either starter prompt below with:

```
Use the autogalaxy_assistant (www.github.com/PyAutoLabs/autogalaxy_assistant) with the
GitHub connector, first reading its llms.txt file for initial start up.
```

A chat assistant cannot run code or inspect the `.fits` files on your machine, so it will
plan the analysis, explain the physics and draft the scripts — and it will ask *you* to plot
and confirm the data before it composes a fit. Running the fit is where a coding agent takes
over.

