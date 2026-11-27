---
name: mreq-apply
description: Implement an mreq task document under .mreq/ one task at a time, checking off each task, keeping its Handoff section current, and following the document's schema (feature, issue, refactor, task). With --orch, subagents implement and verify each phase. Use when the user wants to start, continue, or resume work tracked in .mreq/, or after mreq-define, mreq-grill or mreq-close hands a document over.
argument-hint: "[<path>] [--orch]"
---

# mreq-apply

Implement the tasks in one `.mreq/` document. The document is the only progress record: its checkboxes say what is done, and `## Handoff` says what the next agent needs.

**Input**: Optional. A document path, or findings to fix from `mreq-close`. `--orch` anywhere in the input turns on "Orchestrate mode": it is no part of the path or the findings.

## Language

Write and reply in the language the agent instruction files (`AGENTS.md`, `CLAUDE.md`, ...) set. When they set none, use the language the user writes in. A reply that only picks an option (`1`, `Accept the code`) or gives a path does not change it. When the user has written no natural language yet (only a command or a path), use the language of the document: the language of its title and `## Goal`, not of the template's headings or text. A title such as `add 輸入 1,000 時當掉` means Traditional Chinese, though every heading is English. Use that language in every message, from the first line to the report, including the short notes between tool calls. Only fixed labels such as `Open:` stay as written.

## Asking the user

When your agent has a tool that asks the user option questions, ask with it: `AskUserQuestion` in Claude Code, `ask_user_question` in Grok, `ask_question` in Antigravity, `request_user_input` in Codex. Ask up to 4 independent questions at once, or as many as the tool takes, the recommended option first and labelled "(Recommended)". When a question has more options than the tool takes, ask that question in plain text. When the tool returns an error (Codex allows it only in Plan mode), ask in plain text for the rest of this conversation. Without such a tool, ask in plain text as a numbered list, the recommended option first, and wait for the answer.

Ask with options, so the user picks instead of types:
- Give every question 2 to 4 options. Keep each label short (1 to 5 words) and put the detail in its description. Keep each `header` to 12 characters or fewer.
- Never add an "Other" option: these tools add a free-text answer to every question. When an answer may need a value no option holds (a path, a correction), say in the question that the user can type it there.
- Ask for a typed answer only when no option can hold it, such as an error message only the user has seen. When you can guess the answer, offer the guess as an option.
- Never ask the user to type a command that this skill's steps say to run for them.

## The script

The script is `${CLAUDE_SKILL_DIR}/scripts/mreq.py`. `${CLAUDE_SKILL_DIR}` is the directory that holds this SKILL.md. Claude Code fills in its absolute path; other agents may leave the variable as written. Then put the absolute path of this SKILL.md's directory in its place yourself, before the first command or file read that uses it: the directory of the path you loaded this file from (Codex gives it in the skill's `<path>`, Grok in the skill list's `Absolute path`). Never run a command or read a path that still holds `${`: the shell reads it as an empty variable, and the command or read fails. An error that names a path starting with `/scripts/` means the variable was empty: put the path in its place and run the same command again. Every document path you show the user is the absolute path the script printed.

Write every path with `/`, never with `\`, on Windows too: the script prints its paths that way, and a shell can drop a `\`. Run `uv run "${CLAUDE_SKILL_DIR}/scripts/mreq.py" <command>` first, with the script's path always in double quotes. When `uv` fails before the script starts (`uv` is not found, or `uv` prints its own error, for example a cache directory it cannot create or a download a sandbox blocks), run `python` in place of `uv run`; when `python` is not found, run `python3`. On Windows, a `python` or `python3` that prints nothing, or only a Microsoft Store hint, is not found. Once one of them starts the script, run every later script command in this conversation with it, and do not try `uv run` again. An error the script prints is not a reason to switch, and neither is a script path that does not exist (`Failed to spawn`, `can't open file`): fix the path instead. A denied command is not a reason either: follow "When a tool call is denied". In Claude Code, the allow rule for a denied script command is `Bash(uv run *mreq.py*)` or `PowerShell(uv run *mreq.py*)` (`python` or `python3` in place of `uv run` when you ran it).

- `list --open`: open documents, most recently updated first. An item with `warning` or `error` is a file the script cannot trust: name it to the user.
- `update <path> [--status <draft|active|done>]`: sets `updated` to now. Never write the dates yourself. `update` rewrites the file: read the document again before your next Edit of it.
- `progress <path>`: prints three lines of plain text, not JSON: `Using: <absolute path>`, `<schema>: N/M tasks done. Next: <first unchecked task>` and `Status: <draft|active|done>`. A `Warning:` line after them means the script cannot trust the file's front matter.

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it. In Claude Code, add one allow rule for each: use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`, for example `Bash(python -m unittest discover -s tests)`. Never merge two denied commands into one rule, and never suggest a broader rule. Other agents write their rules in other forms: give only the command or path. Then stop.

## Running another mreq skill

When a step says to run another mreq skill (`mreq-apply` or `mreq-grill`), start it the way your agent allows, with the arguments the step gives:
- **With a skill tool** (Claude Code: the Skill tool): call it by the name your skill list shows: `mreq:mreq-apply` when mreq is installed as the Claude Code plugin, `mreq-apply` otherwise. When the call fails with `Unknown skill` and names the skill to use (`Did you mean ...`), call that name once: this is not a denied call.
- **Without one** (Codex, Grok, Antigravity): read that skill's SKILL.md in full, for example `${CLAUDE_SKILL_DIR}/../mreq-apply/SKILL.md`, and follow it from its first step, with the arguments as its input. In that file, the skill-directory variable means that skill's directory, not this one.

When the skill is not installed (the skill tool knows no such skill and names no other, or its SKILL.md does not exist), tell the user which skill to install, and stop.

When the call is denied, give the user the command that runs it, for example `/mreq-apply <path>`, and the Claude Code allow rule for the name you called, for example `Skill(mreq:mreq-apply)`, then stop. After a denied call, never read the skill's SKILL.md and follow it yourself: the user decides.

When you give the user a command to type, write it the way their agent runs a skill: `/mreq-close <path>` in Claude Code, Grok and Antigravity (`/mreq:mreq-close <path>` also works with the plugin), `$mreq-close <path>` in Codex.

## Steps

1. **Pick the document.**
   Use the path the user gave, or the one document this conversation is about. Otherwise run `list --open`. When it gives exactly one document, and that item has no `warning` or `error`, use it without asking: step 3 shows its path. Otherwise let the user pick. Never pick one yourself.
   Ask one question (see "Asking the user") with one option per document, in the order `list` gives: its title as the label, and its status, task progress and absolute path in the description. With one document (it has a `warning` or `error`), add **Stop** as the second option. With more than 4, offer the first 4 and say in the question that the user can type another document's path in the free-text answer.
   When there is no open document, say so and stop: `/mreq-define <request>` starts new work. Do not invent a subject.

2. **Read it in full.**
   Read the document, before any `update`. Read `## Handoff` first: it says where the last agent stopped. Then run `progress <path>` and show its output (step 3) before any other tool call. Its `Status:` line gives the status: a document whose path you were given may be `done`. Run no `list` to learn it. When `progress` prints a `Warning:` line, name it to the user in that message.
   - When the document still holds only the template's hints (no real goal or tasks), stop before any `update`: say so, and ask once: **Grill it (mreq-grill)** (run the `mreq-grill` skill on the document; see "Running another mreq skill") or **Stop** (say that `/mreq-define <request>` starts a new document).
   - When `## Handoff` has an `Unconfirmed:` line, the user never confirmed the document: show `## Assumptions` and ask once: **Go on** (drop the line when you next rewrite `## Handoff`) or **Grill first** (run the `mreq-grill` skill on the document; see "Running another mreq skill").
   - When it is `done`, every task is checked, and you were handed no findings (see "Findings from mreq-close"), stop before any `update`: say that the work is done, and that `/mreq-close <path>`, with the absolute path filled in, finishes it. `/mreq-close` is user-invoked: do not try to run it.
   - When it is `draft`, or `done` with an unchecked task, run `update <path> --status active`, then read it again before your first Edit.

   After you hand the document to `mreq-grill`, do nothing more in this skill.

   Then read the code it cites.
   Run `git status` and `git diff`, each on its own and without `-C`, and compare them with `## Handoff`. A change the Handoff does not mention means the last session stopped mid-task: continue from the code, not from the Handoff alone.

3. **Show progress.**
   As soon as `progress` prints, write a message, before your next tool call, also when you stop in step 2. It starts with the lines `progress` printed, copied unchanged, then one short sentence on what you do next, in the language from Language. Your final reply does not replace this message. Show it once in each run of this skill: a later turn that goes on with the work (the user answered a question or agreed to a change) does not run `progress` again. Every message from here on is in the language from Language, also the short notes between tool calls.

4. **Work the tasks one at a time.**
   In orchestrate mode, follow "Orchestrate mode" in place of this step.
   Take the next unchecked task. A `### ` heading in `## Tasks` names a phase: it groups tasks and changes nothing in this step. When the task has a `Resume:` line, check what that line says is done against the code, then continue from it.
   1. Re-read `## Goal` and `## Decisions`: the context may have been compressed since you read them.
   2. Implement the smallest change that does the task. Follow the schema rules below.
   3. Prove it works by running something: a test, the repro, or a command that would fail if you were wrong. Reading the code is not proof. When nothing you can run reaches the behavior, say so in the report.
   4. Check the task off (`- [ ]` → `- [x]`), rewrite `## Handoff`, run `update <path>`; only then take the next task. Two check-offs always have a Handoff rewrite and an `update` between them. One task per edit: a task whose only work is running the tests still gets its own check-off. The Handoff says in a few lines what is done, what you verified and how, and the next task. Never move or remove items in `## Open` when you rewrite `## Handoff`. Keep any `Not run:` line already in `## Handoff` word for word, in step 4, step 5 and **Stopping**: `mreq-close` reports it.

5. **Finish.**
   When every task is checked off and the related tests pass, run `update <path> --status done`. Tests that did not run have not passed: then do not set `done`. Write `## Handoff` as done, with how it was verified. Tell the user that `/mreq-close <path>`, with the absolute path filled in, finishes the work. `/mreq-close` is user-invoked: do not try to run it.

## Orchestrate mode

The mode is on when the input holds `--orch`, or when the user asks for this mode in their own words in this conversation: by its name (for example "orch mode", "orchestrate it", "use the orchestrator") or by what it does ("let subagents do the work"). The word alone does not turn it on: not when it is only in the document, in the findings, or in the subject of the work (for example a task about an orchestrator). When you cannot tell, the mode is off. It lasts for this run of the skill. When it is on, say so in the step 3 message. In it you are the orchestrator: one subagent implements a phase, another verifies it, and only you write the document. Your context stays small, and the agent that checks the work did not write it.

When you cannot spawn a subagent that can edit files and run commands (your agent has none, or you are a subagent yourself), say so in one line. The mode is then off: follow every step as written, step 2 too.

**What changes in the steps.** In step 2, do not read the code the document cites, and run no git command: the implementer does both. In place of step 4, follow the loop in `${CLAUDE_SKILL_DIR}/ORCHESTRATOR.md`: read that file in full before you spawn the first subagent, and read it again when you take a phase and the loop is no longer in your context. In step 5, a verifier's test run counts as that file gives. Never edit source code in this mode, and never read it or run the project's code to check a report: a verifier does that. The one exception is a phase the user tells you to work yourself (**Work it here** in that file).

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

When the user or `mreq-close` hands you findings, add each one under `## Tasks` as a new unchecked task (when `## Tasks` has `### ` headings, under a new last heading that names the findings), set the status back with `update <path> --status active`, then show progress as in step 3 and work them as in step 4.

## Guardrails

- Track progress in the document. A built-in todo list may help you, but the checkboxes are the record.
- Never delete, skip, or weaken a test to get to green. Fix the code.
- Never run git commands that change the working tree, the index or history (stash, checkout, reset, restore, commit) unless the user asks. To prove a test catches the bug, revert the fix by editing the file, run the test, then restore it.
- Edit no other `.mreq/` document.
- Write scratch files for a check inside the project, never outside it (no `/tmp`, no `$TEMP`). When the document names a scratch file, use that name. Remove them before you finish; name any you could not remove in the report.
