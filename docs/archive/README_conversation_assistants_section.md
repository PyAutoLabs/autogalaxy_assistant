<!-- Archived 2026-09-10 from README.md (sections "### Supported Coding Agents", "## Conversation Assistants" and
     "## Free AI tools") when the assistants moved to an agentic-only support policy. UNSUPPORTED: the browser-chat
     routes described here (GitHub-connector chats, the PyAutoLens custom GPT, Project uploads) are retired and not
     coming back as supported onboarding; the Gemini CLI row is now maintainer-only evaluation guidance. Kept for
     reference; the dated observations are left as written. -->

> **Archived and unsupported (2026-09-10).** Historical text; see the [README](../../README.md) for the supported
> agentic setup.

### Supported Coding Agents

The two supported coding agents are **Claude Code** and **Codex**, both of which normally
require a paid subscription. The table below shows the agents `autogalaxy_assistant` has been
tested with — the others work in practice but are not first-class supported.

| Interface | Support | Access and cost | Notes |
|---|---|---|---|
| **Claude Code** | Primary; thoroughly tested | Normally a [paid Claude subscription or metered API usage](https://code.claude.com/docs/en/costs). | Loads the canonical instructions through `CLAUDE.md`. |
| **Codex CLI** | Primary; thoroughly tested | A [limited free plan](https://developers.openai.com/codex/pricing/) may be available; paid plans or API billing provide more usage. | Reads `AGENTS.md` directly and can edit and run the project locally. |
| **Gemini CLI** | Not first-class supported | Offers [limited free quotas](https://github.com/google-gemini/gemini-cli/blob/main/docs/resources/quota-and-pricing.md); subscriptions or usage billing provide higher limits. | Loads the repository instructions through `.gemini/settings.json`. |
| **OpenCode** | Not first-class supported | The client is open source; model-provider access may be free or paid. | Use it from the repository root so it can discover the project context. |

## Conversation Assistants

Conversation assistants such as **ChatGPT** and **Claude** used in a browser **are supported**, on a paid plan. A chat
assistant cannot run code or inspect the `.fits` files on your machine, so it plans the analysis, explains the physics
and drafts the scripts — and it will ask *you* to plot and confirm the data before it composes a fit. Running the fit
is where a coding agent takes over.

| Option | Cost | How to set it up |
|---|---|---|
| **ChatGPT** | Paid (Plus/Pro/Team) | Enable its **GitHub connector**, give it this repository's URL, and point it explicitly at [`llms.txt`](../../llms.txt) |
| **Claude chat** | Paid (Pro/Max/Team) | Enable its **GitHub connector**, give it this repository's URL, and point it explicitly at [`llms.txt`](../../llms.txt) |

Connectors do not reliably fetch `llms.txt` on their own, and results are markedly better when it is named, so prefix
either starter prompt above with:

```
Use the autogalaxy_assistant (www.github.com/PyAutoLabs/autogalaxy_assistant) with the
GitHub connector, first reading its llms.txt file for initial start up.
```

> **GitHub connectors.** On paid plans the connector is the route for both assistants — it reads the repository live,
> so it always sees current content. On Claude's free plan the connector is missing features which hurt performance, so
> there create a **Project** and upload this repository into its knowledge (download the ZIP from the green **Code**
> button) instead.

Free plans work for short questions and planning sessions but go through their token allowance quickly. There is no
PyAutoGalaxy custom GPT yet; an experimental prototype exists for the sibling
**[PyAutoLens AI Assistant](https://chatgpt.com/g/g-6a74c33c58c48191b8cd353e7b46f18b-pyautolens-ai-assistant)**, but be
warned that its performance is currently not great. Step-by-step recipes for each of these routes are written up in the
sibling assistant's [setup guides](https://github.com/PyAutoLabs/autolens_assistant/tree/main/docs/setup); the same
steps apply here with this repository's URL.

## Free AI tools

We are actively testing free AI tools, but cannot yet provide first-class support for any of them. The free coding
agent **OpenCode** is the most promising option so far, with preliminary testing showing encouraging results — if you
do not have a paid Claude Code or Codex subscription it is the one to try. The free chat routes are covered in
[Conversation Assistants](#conversation-assistants) above.

