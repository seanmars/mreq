---
name: mreq-apply
description: Implement an mreq task document under .mreq/ one task at a time, checking off each task, keeping its Handoff section current, and following the document's schema (feature, issue, refactor, task). Use when the user wants to start, continue, or resume work tracked in .mreq/, or after mreq-define or mreq-close hands a document over.
argument-hint: "[<path>]"
---

# mreq-apply

Implement the tasks in one `.mreq/` document. The document is the only progress record: its checkboxes say what is done, and `## Handoff` says what the next agent needs.

**Input**: Optional. A document path, or findings to fix from `mreq-close`.

## Language

Write and reply in the language the agent instruction files (`AGENTS.md`, `CLAUDE.md`, ...) set. When they set none, use the language the user writes in. A reply that only picks an option (`1`, `Accept the code`) or gives a path does not change it. When the user has written no natural language yet (only a command or a path), use the language of the document: the language of its title and `## Goal`, not of the template's headings or text. A title such as `add 輸入 1,000 時當掉` means Traditional Chinese, though every heading is English. Use that language in every message, from the first line to the report, including the short notes between tool calls. Only fixed labels such as `Open:` stay as written.

## Asking the user

When the `AskUserQuestion` tool is available, ask with it: up to 4 independent questions at once, the recommended option first and labelled "(Recommended)". Otherwise, ask in plain text as a numbered list, the recommended option first, and wait for the answer.

Ask with options, so the user picks instead of types:
- Give every question 2 to 4 options. Keep each label short (1 to 5 words) and put the detail in its description. Keep each `header` to 12 characters or fewer.
- Never add an "Other" option: `AskUserQuestion` adds a free-text answer to every question. When an answer may need a value no option holds (a path, a correction), say in the question that the user can type it there.
- Ask for a typed answer only when no option can hold it, such as an error message only the user has seen. When you can guess the answer, offer the guess as an option.
- Never ask the user to type a command that this skill's steps say to run for them.

## The script

The script is `${CLAUDE_SKILL_DIR}/../mreq-shared/scripts/mreq.py`. `${CLAUDE_SKILL_DIR}` is this skill's directory; when it still reads as a variable, put the directory's absolute path in its place. Every document path you show the user is the absolute path the script printed.

Write every path with `/`, never with `\`, on Windows too: the script prints its paths that way, and a shell can drop a `\`. Run `uv run "${CLAUDE_SKILL_DIR}/../mreq-shared/scripts/mreq.py" <command>` first, with the script's path always in double quotes. When `uv` fails before the script starts (`uv` is not found, or `uv` prints its own error, for example a cache directory it cannot create), run `python` in place of `uv run`; when `python` is not found, run `python3`. An error the script prints is not a reason to switch, and neither is a denied command: follow "When a tool call is denied". The allow rule for a denied script command is `Bash(uv run *mreq.py*)` or `PowerShell(uv run *mreq.py*)` (`python` or `python3` in place of `uv run` when you ran it).

- `list [--open]`: every document with its status, most recently updated first; `--open` leaves out the `done` ones. An item with `warning` or `error` is a file the script cannot trust: name it to the user.
- `update <path> [--status <draft|active|done>]`: sets `updated` to now. Never write the dates yourself. `update` rewrites the file: read the document again before your next Edit of it.
- `progress <path>`: prints two lines of plain text, not JSON: `Using: <absolute path>` and `<schema>: N/M tasks done. Next: <first unchecked task>`.

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it, with one allow rule for each. Use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`, for example `Bash(python -m unittest discover -s tests)`. Never merge two denied commands into one rule, and never suggest a broader rule. Then stop.

## Steps

1. **Pick the document.**
   Use the path the user gave, or the one document this conversation is about. Otherwise run `list --open`. When it gives exactly one document, and that item has no `warning` or `error`, use it without asking: step 3 shows its path. Otherwise let the user pick. Never guess.
   Ask one question (see "Asking the user") with one option per document, in the order `list` gives: its title as the label, and its status, task progress and absolute path in the description. With one document (it has a `warning` or `error`), add **Stop** as the second option. With more than 4, offer the first 4 and say in the question that the user can type another document's path in the free-text answer.
   When there is no open document, say so and stop: `/mreq-define <request>` starts new work. Do not invent a subject.

2. **Read it in full.**
   First learn the status from the `list` output. When step 1 did not run `list`, run it without `--open`: the document may be `done`. Then read the document, before any `update`. Read `## Handoff` first: it says where the last agent stopped. Then run `progress <path>` and show its output (step 3) before any other tool call.
   - When the document still holds only the template's hints (no real goal or tasks), stop before any `update`: say so, and ask once: **Grill it (mreq-grill)** (run the `mreq-grill` skill on the document; in Claude Code: with the Skill tool) or **Stop** (say that `/mreq-define <request>` starts a new document).
   - When `## Handoff` has an `Unconfirmed:` line, the user never confirmed the document: show `## Assumptions` and ask once: **Go on** (drop the line when you next rewrite `## Handoff`) or **Grill first** (run the `mreq-grill` skill on the document; in Claude Code: with the Skill tool).
   - When it is `done`, every task is checked, and you were handed no findings (see "Findings from mreq-close"), stop before any `update`: say that the work is done, and that `/mreq-close <path>`, with the absolute path filled in, finishes it. `/mreq-close` is user-invoked: do not try to run it.
   - When it is `draft`, or `done` with an unchecked task, run `update <path> --status active`, then read it again before your first Edit.

   After you hand the document to `mreq-grill`, do nothing more in this skill. When that Skill call is denied, give the user `/mreq-grill <path>` and the allow rule `Skill(mreq-grill)`, then stop. Never read another skill's SKILL.md and follow it yourself.

   Then read the code it cites.
   Run `git status` and `git diff`, each on its own and without `-C`, and compare them with `## Handoff`. A change the Handoff does not mention means the last session stopped mid-task: continue from the code, not from the Handoff alone.

3. **Show progress.**
   As soon as `progress` prints, write a message, before your next tool call, also when you stop in step 2. It starts with the two lines `progress` printed, copied unchanged, then one short sentence on what you do next, in the language from Language. Your final reply does not replace this message. A later turn that goes on with the work (the user answered a question or agreed to a change) does the same: run `progress <path>` first and show its two lines before any other tool call. Every message from here on is in the language from Language, also the short notes between tool calls.

4. **Work the tasks one at a time.**
   Take the next unchecked task. When it has a `Resume:` line, check what that line says is done against the code, then continue from it.
   1. Re-read `## Goal` and `## Decisions`: the context may have been compressed since you read them.
   2. Implement the smallest change that does the task. Follow the schema rules below.
   3. Prove it works by running something: a test, the repro, or a command that would fail if you were wrong. Reading the code is not proof. When nothing you can run reaches the behavior, say so in the report.
   4. Check the task off (`- [ ]` → `- [x]`), rewrite `## Handoff`, run `update <path>`; only then take the next task. Two check-offs always have a Handoff rewrite and an `update` between them. One task per edit: a task whose only work is running the tests still gets its own check-off. The Handoff says in a few lines what is done, what you verified and how, and the next task. Never move or remove items in `## Open` when you rewrite `## Handoff`.

5. **Finish.**
   When every task is checked off and the related tests pass, run `update <path> --status done`. Tests that did not run have not passed: then do not set `done`. Write `## Handoff` as done, with how it was verified. Tell the user that `/mreq-close <path>`, with the absolute path filled in, finishes the work after they commit. `/mreq-close` is user-invoked: do not try to run it.

## Schema rules

- **`feature`**: build only what `## Scope` puts in. Add no flexibility for later.
- **`issue`**: reproduce the bug before you change code. Fix only after `## Root Cause` holds a verified cause: verify it first, and write how you did. Fix the cause, not the symptom; when a shared function causes it, fix that function and check its other callers. When two fixes fail, stop: the root cause is probably wrong. Say so and verify it again before a third fix.
- **`refactor`**: pin the behavior first (the `## Behavior Pin` test or command) and keep it green after every step. Change no behavior. When you find a bug, write it in `## Open` as `- Follow-up: <what>` and do not fix it here.
- **`task`**: do the task as `## Goal` describes it.

## When to stop and ask

Stop and ask in these cases. Each question is an option question (see "Asking the user") with the options given; the last case asks nothing.

- A task is unclear: offer each reading of the task as an option, the most likely one first.
- An `Open:` item in `## Open` decides how to do the next task: offer your suggested answer first, with its reason, then the real alternatives. After the user answers, write the answer into `## Decisions` and remove that item.
- The code shows a decision in `## Decisions` is wrong: offer **Change Dn** (the change you propose, in the description) and **Keep Dn**. After the user agrees, edit the decision and the tasks it affects.
- A task needs work outside the document's goal or scope: name the extra work, and offer **Do it** (add it as a new task), **Add a follow-up** (write `- Follow-up: <what>` in `## Open` and go on without it) and **Stop**.
- An error you cannot resolve: offer the next step you would try first, then **Stop**, and say in the question that the user can type what they know about the error.
- A command that would prove a task done is denied. Leave the task unchecked and do not set `done`; then follow "When a tool call is denied".

**Stopping** (a question, a denied command, a pause, the user stops you, the session ends): make the record with tool calls before you reply; a stop with no Edit and no `update` is never enough.

1. Leave the box unchecked.
2. Under the next unchecked task, write or rewrite one nested bullet, not a checkbox: `  - Resume: <done so far>; <what is left>; <next action>`. Put in everything you know now, including changes that are only in the working tree; write `not started` as the done part when nothing is done.
3. When the user stops you, their words are new: add them to the line (for example `D2: the user decides later`), even when the rest of the record is current.
4. Rewrite `## Handoff` and run `update <path>`.

Delete the `Resume:` line when you check the task off. The step 2 stops before any `update` (a template-only document, `Unconfirmed:`, and a `done` document with nothing left to do) change nothing.

## Findings from mreq-close

When the user or `mreq-close` hands you findings, add each one under `## Tasks` as a new unchecked task, set the status back with `update <path> --status active`, then show progress as in step 3 and work them as in step 4.

## Guardrails

- Track progress in the document. A built-in todo list may help you, but the checkboxes are the record.
- Never delete, skip, or weaken a test to get to green. Fix the code.
- Never run git commands that change the working tree, the index or history (stash, checkout, reset, restore, commit) unless the user asks. To prove a test catches the bug, revert the fix by editing the file, run the test, then restore it.
- Edit no other `.mreq/` document.
- Write scratch files for a check inside the project, never outside it (no `/tmp`, no `$TEMP`). When the document names a scratch file, use that name. Remove them before you finish; name any you could not remove in the report.
