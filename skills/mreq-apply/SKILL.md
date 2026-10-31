---
name: mreq-apply
description: Implement an mreq task document under .mreq/ one task at a time, checking off each task, keeping its Handoff section current, and following the document's schema (feature, issue, refactor, task). Use when the user wants to start, continue, or resume work tracked in .mreq/, or after mreq-do or mreq-close hands a document over.
---

# mreq-apply

Implement the tasks in one `.mreq/` document. The document is the only progress record: its checkboxes say what is done, and `## Handoff` says what the next agent needs.

**Input**: Optional. A document path, or findings to fix from `mreq-close`.

## Language

Write and reply in the language the agent instruction files (`AGENTS.md`, `CLAUDE.md`, ...) set. When they set none, use the language the user writes in. A reply that only picks an option (`1`, `Accept the code`) or gives a path does not change it. When the user has written no natural language yet (only a command or a path), use the language of the document: the language of its title and `## Goal`, not of the template's headings or text. A title such as `add 輸入 1,000 時當掉` means Traditional Chinese, though every heading is English. Use that language in every message, from the first line to the report, including the short notes between tool calls. Only fixed labels such as `Open:` stay as written.

## Asking the user

When the `AskUserQuestion` tool is available, ask with it: up to 4 independent questions at once, the recommended option first and labelled "(Recommended)". Otherwise, ask in plain text as a numbered list, the recommended option first, and wait for the answer.

## The script

The script is `<mreq-do directory>/scripts/mreq.py`, where `<mreq-do directory>` is `../mreq-do` from this skill's directory. Every document path you show the user is the absolute path the script printed.

Run each command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. Use the script's absolute path. Run `uv run <script> <command>` first; only when that fails because `uv` is not found, run `python <script> <command>`. The allow rule for a denied script command is `Bash(uv run *mreq.py*)` or `PowerShell(uv run *mreq.py*)` (`python` in place of `uv run` when you ran `python`).

- `list [--open]`: every document with its status, most recently updated first; `--open` leaves out the `done` ones. An item with `warning` or `error` is a file the script cannot trust: name it to the user.
- `update <path> [--status <draft|active|done>]`: sets `updated` to now. Never write the dates yourself. `update` rewrites the file: read the document again before your next Edit of it.

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it, with one allow rule for each. Use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`, for example `Bash(python -m unittest discover -s tests)`. Never merge two denied commands into one rule, and never suggest a broader rule. Then stop.

## Steps

1. **Pick the document.**
   Use the path the user gave, or the one document this conversation is about. Otherwise run `list --open` and let the user pick, even when only one exists. Never guess.

2. **Read it in full.**
   First learn the status from the `list` output. When step 1 did not run `list`, run it without `--open`: the document may be `done`. Then read the document, before any `update`. Read `## Handoff` first: it says where the last agent stopped. Right after this Read, show progress (step 3).
   - When the document still holds only the template's hints (no real goal or tasks), stop before any `update`: say so, and suggest `/mreq-grill <path>` or ask for the goal.
   - When `## Handoff` has an `Unconfirmed:` line, the user never confirmed the document: show `## Assumptions` and ask once: **Go on** (drop the line when you next rewrite `## Handoff`) or **Grill first** (give `/mreq-grill <path>` and stop).
   - When it is `draft`, run `update <path> --status active`, then read it again before your first Edit.

   Then read the code it cites.
   Run `git status` and `git diff`, each on its own and without `-C`, and compare them with `## Handoff`. A change the Handoff does not mention means the last session stopped mid-task: continue from the code, not from the Handoff alone.

3. **Show progress.**
   Your first message starts with these two lines, said right after you read the document and before you read the code, also when you stop in step 2: `Using: <absolute path>`, then `<schema>: N/M tasks done. Next: <task>`, with the task in the document's words. A later turn that goes on with the work (the user answered a question or agreed to a change) starts with them too, before its first tool call. Every message from here on is in the language from Language, also the short notes between tool calls. `<schema>` is the `schema` value in the document's front matter (`feature`, `issue`, `refactor` or `task`), not the project's name.

4. **Work the tasks one at a time.**
   Take the next unchecked task. When it has a `Resume:` line, check what that line says is done against the code, then continue from it.
   1. Re-read `## Goal` and `## Decisions`: the context may have been compressed since you read them.
   2. Implement the smallest change that does the task. Follow the schema rules below.
   3. Prove it works by running something: a test, the repro, or a command that would fail if you were wrong. Reading the code is not proof. When nothing you can run reaches the behavior, say so in the report.
   4. Check the task off (`- [ ]` → `- [x]`), rewrite `## Handoff`, run `update <path>`; only then take the next task. Two check-offs always have a Handoff rewrite and an `update` between them. One task per edit: a task whose only work is running the tests still gets its own check-off. The Handoff says in a few lines what is done, what you verified and how, and the next task. Never move or remove items in `## Open` when you rewrite `## Handoff`.

5. **Finish.**
   When every task is checked off and the related tests pass, run `update <path> --status done`. Tests that did not run have not passed: then do not set `done`. Write `## Handoff` as done, with how it was verified. Tell the user `/mreq-close` finishes the work.

## Schema rules

- **`feature`**: build only what `## Scope` puts in. Add no flexibility for later.
- **`issue`**: reproduce the bug before you change code. Fix only after `## Root Cause` holds a verified cause: verify it first, and write how you did. Fix the cause, not the symptom; when a shared function causes it, fix that function and check its other callers. When two fixes fail, stop: the root cause is probably wrong. Say so and verify it again before a third fix.
- **`refactor`**: pin the behavior first (the `## Behavior Pin` test or command) and keep it green after every step. Change no behavior. When you find a bug, write it in `## Open` as `- Follow-up: <what>` and do not fix it here.
- **`task`**: do the task as `## Goal` describes it.

## When to stop and ask

- A task is unclear.
- An `Open:` item in `## Open` decides how to do the next task. After the user answers, write the answer into `## Decisions` and remove that item.
- The code shows a decision in `## Decisions` is wrong. Propose the change; after the user agrees, edit the decision and the tasks it affects.
- A task needs work outside the document's goal or scope. Name the extra work and ask before you do it.
- An error you cannot resolve.
- A command that would prove a task done is denied. Leave the task unchecked and do not set `done`; then follow "When a tool call is denied".

**Stopping** (a question, a denied command, a pause, the user stops you, the session ends): make the record with tool calls before you reply; a stop with no Edit and no `update` is never enough. Leave the box unchecked. Under the next unchecked task, write or rewrite one nested bullet, not a checkbox: `  - Resume: <done so far>; <what is left>; <next action>`. Put in everything you know now, including changes that are only in the working tree; write `not started` as the done part when nothing is done. When the user stops you, their words are new: add them to the line (for example `D2: the user decides later`), even when the rest of the record is current. Rewrite `## Handoff` and run `update <path>`. Delete the `Resume:` line when you check the task off. The two step 2 stops before any `update` (a template-only document, and `Unconfirmed:`) change nothing.

## Findings from mreq-close

When the user hands you findings, add each one under `## Tasks` as a new unchecked task, set the status back with `update <path> --status active`, then show progress as in step 3 and work them as in step 4.

## Guardrails

- Track progress in the document. A built-in todo list may help you, but the checkboxes are the record.
- Never delete, skip, or weaken a test to get to green. Fix the code.
- Never run git commands that change the working tree, the index or history (stash, checkout, reset, restore, commit) unless the user asks. To prove a test catches the bug, revert the fix by editing the file, run the test, then restore it.
- Edit no other `.mreq/` document.
- Write scratch files for a check inside the project, never outside it (no `/tmp`, no `$TEMP`). When the document names a scratch file, use that name. Remove them before you finish; name any you could not remove in the report.
