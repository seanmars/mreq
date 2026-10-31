---
name: mreq-grill
description: Pressure-test an mreq task document under .mreq/ with a four-quadrant Known/Unknown interview, then write what it settles back into the document's Decisions, Tasks, Assumptions, and Open sections. Use when the user says "grill", "grill me", or wants to find unspoken assumptions and blind spots in a plan, or after mreq-do hands a document over.
---

# mreq-grill

Stress-test one `.mreq/` document until every assumption is named and every open question is answered or parked. Then write the outcome into the document.

**Input**: Optional. A document path.

## Language

Write and reply in the language the agent instruction files (`AGENTS.md`, `CLAUDE.md`, ...) set. When they set none, use the language the user writes in. A reply that only picks an option (`1`, `Accept the code`) or gives a path does not change it. When the user has written no natural language yet (only a command or a path), use the language of the document: the language of its title and `## Goal`, not of the template's headings or text. A title such as `add 輸入 1,000 時當掉` means Traditional Chinese, though every heading is English. Use that language in every message, from the first line to the report, including the short notes between tool calls. Only fixed labels such as `Open:` stay as written.

## Asking the user

When the `AskUserQuestion` tool is available, ask with it: up to 4 independent questions at once, the recommended option first and labelled "(Recommended)". Otherwise, ask in plain text as a numbered list, the recommended option first, and wait for the answer.

## The script

The script is `<mreq-do directory>/scripts/mreq.py`, where `<mreq-do directory>` is `../mreq-do` from this skill's directory. Every document path you show the user is the absolute path the script printed.

Run each command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. Use the script's absolute path. Run `uv run <script> <command>` first. When `uv` fails before the script starts (`uv` is not found, or `uv` prints its own error, for example a cache directory it cannot create), run `python <script> <command>`; when `python` is not found, run `python3`. An error the script prints is not a reason to switch, and neither is a denied command: follow "When a tool call is denied". The allow rule for a denied script command is `Bash(uv run *mreq.py*)` or `PowerShell(uv run *mreq.py*)` (`python` or `python3` in place of `uv run` when you ran it).

- `list --open`: open documents, most recently updated first. An item with `warning` or `error` is a file the script cannot trust: name it to the user.
- `update <path> [--status active]`: sets `updated` to now. Never write the dates yourself.

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it, with one allow rule for each. Use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`, for example `Bash(python -m unittest discover -s tests)`. Never merge two denied commands into one rule, and never suggest a broader rule. Then stop.

## Steps

1. **Pick the document.**
   Use the path the user gave, or the one document this conversation is about. Otherwise run `list --open` and let the user pick, even when only one exists. Never pick one yourself.
   When there is no open document, say so and suggest `/mreq-do`. Do not invent a subject.

2. **Read it and the code it cites.**
   When its `status` is `done`, say so before you read the code, and ask once: **Reopen** (grill it; step 5 sets it back to `active`), **Discuss only** (grill it, but write nothing in step 5), or **New document** (suggest `/mreq-do` and stop).
   When `## Handoff` has an `Unconfirmed:` line, tell the user first: nobody confirmed this document's assumptions and decisions. Grill each of them as a known unknown.

3. **Sweep the four quadrants.** The last two hide the real risk.
   1. **Known knowns**: the claims the document rests on. Verify each against the code. A false known is the most dangerous kind.
   2. **Known unknowns**: the open questions. Ask each, with your suggested answer and its reason.
   3. **Unknown knowns**: the premises nobody said out loud. Name each and confirm it holds.
   4. **Unknown unknowns**: the blind spots. Ask "what would have to be true for this to fail?" and follow the answers.

   Report the four quadrants separately, in this order. Write "none found" under a quadrant with nothing.

   Interview rules:
   - Look up facts in the code; ask the user for decisions.
   - A fact you bring in yourself is a known too: verify it in the code or the docs before you rely on it. A fact you cannot verify goes into the restatement as an assumption, never into a decision's reason.
   - Ask unrelated questions together. Hold a question that depends on an open one.
   - Ask what each answer implies that nobody said.

4. **Restate and get confirmation.**
   In your own words: the claims that held and the ones that fell, the assumptions now explicit, the decisions made (each with its reason and the alternative ruled out), and what is still open. Ask the user to confirm or correct it. A correction means keep grilling, then restate again. Running out of questions is not confirmation; only the user's yes is.

5. **Write the outcome into the document.**
   - Change only the body, section by section, with Edit. Never rewrite the whole file and never touch the front matter: `update` owns it.
   - Write each part of the step 4 restatement into its section:
     - **Decisions made**: add or change `### Dn:` entries in `## Decisions`. When a decision replaces an old one, rewrite it and add `Changed by grill: <what it said before>`.
     - **Assumptions now explicit**: `## Assumptions`, one bullet each.
     - **Claims that fell**: correct the section that states them (`## Goal`, `## Scope`, `## Context`, or the schema's own sections). Change those sections nowhere else, except where the user corrected them.
     - **Still open**: `## Open`, one `- Open: <question>` bullet each. A follow-up you found goes there too, as `- Follow-up: <what>`.
   - Change `## Tasks` when a decision changes the work. Never uncheck or reword a done task; put the correction in a new task or in `## Open`.
   - Delete an `Unconfirmed:` line in `## Handoff`: the user has now confirmed a restatement.
   - Run `update <path>`. For a reopened `done` document, run `update <path> --status active`.

6. **Ask for the next step.**
   - **Implement (mreq-apply)**: run the `mreq-apply` skill on this document (in Claude Code: with the Skill tool).
   - **Grill more**: go back to step 3.
   - **Stop here**: give the document's absolute path.

   When the Skill call is denied, give the user `/mreq-apply <path>` and the allow rule `Skill(mreq-apply)`, then stop. Never read another skill's SKILL.md and follow it yourself.

## Guardrails

- Write only to the document being grilled. Never edit source code.
- Do not create files, even temporary ones. When a claim needs a measurement, make it a task or an `Open:` item.
- Write nothing before the user confirms the restatement.
- When the user wants to keep going after the restatement, keep going.
