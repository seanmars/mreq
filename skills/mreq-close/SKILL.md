---
name: mreq-close
description: Finish an mreq task document under .mreq/. Check that the code does what the document agreed, then delete the document. Use for /mreq-close.
argument-hint: "[<path>]"
disable-model-invocation: true
---

# mreq-close

Run only when the user invoked this skill: typed `/mreq-close` (`/mreq:mreq-close` with the Claude Code plugin, `$mreq-close` in Codex), or asked for it by name. If you are reading this file on your own, stop and ask the user to run `/mreq-close <path>`.

Check the code against one `.mreq/` document, then delete the document. The code is the record of what was done.

**Input**: Optional. A document path.

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

The script is `${CLAUDE_SKILL_DIR}/../mreq-shared/scripts/mreq.py`. `${CLAUDE_SKILL_DIR}` is the directory that holds this SKILL.md. Claude Code fills in its absolute path; other agents may leave the variable as written. Then put the absolute path of this SKILL.md's directory in its place yourself, before the first command or file read that uses it: the directory of the path you loaded this file from (Codex gives it in the skill's `<path>`, Grok in the skill list's `Absolute path`). Never run a command or read a path that still holds `${`: the shell reads it as an empty variable, and the command or read fails. An error that names a path starting with `/../mreq-shared` means the variable was empty: put the path in its place and run the same command again. Every document path you show the user is the absolute path the script printed.

Write every path with `/`, never with `\`, on Windows too: the script prints its paths that way, and a shell can drop a `\`. Run `uv run "${CLAUDE_SKILL_DIR}/../mreq-shared/scripts/mreq.py" <command>` first, with the script's path always in double quotes. When `uv` fails before the script starts (`uv` is not found, or `uv` prints its own error, for example a cache directory it cannot create or a download a sandbox blocks), run `python` in place of `uv run`; when `python` is not found, run `python3`. On Windows, a `python` or `python3` that prints nothing, or only a Microsoft Store hint, is not found. Once one of them starts the script, run every later script command in this conversation with it, and do not try `uv run` again. An error the script prints is not a reason to switch, and neither is a script path that does not exist (`Failed to spawn`, `can't open file`): fix the path instead. A denied command is not a reason either: follow "When a tool call is denied". In Claude Code, the allow rule for a denied script command is `Bash(uv run *mreq.py*)` or `PowerShell(uv run *mreq.py*)` (`python` or `python3` in place of `uv run` when you ran it).

- `list`: every document, most recently updated first. An item with `warning` or `error` is a file the script cannot trust: name it to the user.
- `delete <path>`: deletes the document. It refuses any file outside `.mreq/`.

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it. In Claude Code, add one allow rule for each: use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`, for example `Bash(python -m unittest discover -s tests)`. Never merge two denied commands into one rule, and never suggest a broader rule. Other agents write their rules in other forms: give only the command or path. Then stop.

## Running another mreq skill

When a step says to run another mreq skill (`mreq-apply` or `mreq-grill`), start it the way your agent allows, with the arguments the step gives:
- **With a skill tool** (Claude Code: the Skill tool): call it by the name your skill list shows: `mreq:mreq-apply` when mreq is installed as the Claude Code plugin, `mreq-apply` otherwise. When the call fails with `Unknown skill` and names the skill to use (`Did you mean ...`), call that name once: this is not a denied call.
- **Without one** (Codex, Grok, Antigravity): read that skill's SKILL.md in full, for example `${CLAUDE_SKILL_DIR}/../mreq-apply/SKILL.md`, and follow it from its first step, with the arguments as its input. In that file, the skill-directory variable means that skill's directory, not this one.

When the call is denied, give the user the command that runs it, for example `/mreq-apply <path>`, and the Claude Code allow rule for the name you called, for example `Skill(mreq:mreq-apply)`, then stop. After a denied call, never read the skill's SKILL.md and follow it yourself: the user decides.

When you give the user a command to type, write it the way their agent runs a skill: `/mreq-close <path>` in Claude Code, Grok and Antigravity (`/mreq:mreq-close <path>` also works with the plugin), `$mreq-close <path>` in Codex.

## Steps

1. **Pick the document.**
   Use the path the user gave. Otherwise run `list`. When exactly one document has `status` `done`, and that item has no `warning` or `error`, use it without asking. Otherwise let the user pick. Never pick one yourself.
   Ask one question (see "Asking the user") with one option per document: every document with `status` `done` first, then the others, each group in `list` order. Start every label with the document's `status` in brackets, then its title, for example `[done] add login retry` or `[active] fix cache key`: the user sees each status before picking. Put its task progress and absolute path in the description. With one document, add **Stop** as the second option. With more than 4, offer the first 4 and say in the question that the user can type another document's path in the free-text answer.
   Your first message starts with the line `Closing: <absolute path>`, also when the user gave the path:
   - The user gave the path: say it before any tool call.
   - You used the only `done` document: say it right after `list`.
   - Otherwise: say it right after the user picks.

   When `list` shows no document, say so, with no `Closing:` line, and stop: there is nothing to close.

2. **Check the tasks.**
   When a task is unchecked, ask once:
   - **Continue (mreq-apply)**: hand the document to `mreq-apply` (see "Handing over to mreq-apply"), with no findings.
   - **Close anyway**: go on, and name the unfinished tasks in the report.
   - **Keep it**: stop.

3. **Check the code against the document.**
   1. **Audit.** Audit it yourself, under these rules.
      - Judge only from the document and the code as you read them now, not from what you remember of this conversation.
      - Read the document and every file it cites in full: this is an audit, not a search.
      - For `## Goal`, each `### Dn:` in `## Decisions`, and each checked task: does the code do it? Answer done, partly done, done differently, or missing, with `path:line`.
      - A finding is code that contradicts the document or misses something it asked for. Code that adds a detail the document did not mention, without contradicting it, goes in the not-asked-for list.
      - Note anything the code does that the document never asked for.
      - Run no command that executes the project's code or writes a file.
   2. **Run.** After the audit, run the checks the document names, and only those.
      - **What to run**: its test command (when it names none, the one in the project's README or agent instruction files); for `issue`, the `## Symptom` repro; for `refactor`, the `## Behavior Pin`; and the check a task names.
      - **When mreq-apply already verified the work**: when the document's front matter `status` is `done` and `## Handoff` says how the work was verified (the tests or commands it ran), skip the test command and each task's own check: `mreq-apply` sets `done` only after every task is checked and the related tests pass. Do not look for another test command then. A Handoff that says the work is done but not how it was verified does not count. Still run the `issue` Repro and the `refactor` Behavior Pin: they prove the goal itself.
      - **When to skip the test command**: skip it when a checked task's work is to run the related tests (for example the `issue` template's "Run the related tests"): `mreq-apply` ran them to check that task off. Do not look for another test command then. A task that only says how it is checked, or an unchecked one, does not count. This skips only the test command: still run the repro, the Behavior Pin, and each task's own check.
      - **As written**: run each command exactly as written: add no `uv run`, and use no `python -c` in its place. When a check needs a script, run it inline.
      - **Off the real data**: when a check writes or changes files beyond caches (a data file, a database), keep it off the project's real data: point it at a new path the command accepts (for example a `--file` option), or give it to the user to run. That new path is the only change you make to a command.
      - **No checks of your own**: add none, not even to confirm a finding: the audit's `path:line` is the evidence.
      - **A denied command**: when any command you ran in this step is denied, do not retry it another way, and do not stop: it goes to **Tests not run** in step 4.

4. **Act on the result.**
   - **All done, tests pass**: go to step 5.
   - **Checks already run by mreq-apply** (step 3 skipped the test command and the task checks because the document is `done` and its Handoff says how it was verified): this alone asks nothing. When no other case in this list applies, go to step 5. Never call it a pass: name it in the report, with the verification the Handoff gives.
   - **Tests already run by a task** (step 3 skipped the test command because a checked task ran it): this alone asks nothing. When no other case in this list applies, go to step 5. Never call it a pass: name it in the report with the task number.
   - **Failing tests**: name each failure, and ask once: **Fix now (mreq-apply)**, **Close anyway**, or **Stop**.
   - **Tests not run** (a command in step 3 was denied): give the user each command that did not run, exactly as you ran it, with one allow rule for each (see "When a tool call is denied"), and ask once: **Close anyway** or **Keep it**. Never count it as a pass.
   - **No test command found** (neither the document, the README nor the agent instruction files give one): this alone asks nothing. When no other case in this list applies, go to step 5. Never call it a pass: say in the report that no test command was found and none ran.
   - **A finding** (partly done, done differently, missing): ask one question per finding. Quote the document's line, say what the code does, and offer **Accept the code** or **Fix the code**.

   Ask every question this step needs together, the test questions first, up to 4 at a time; when there are more, ask the next ones after the user answers. A **Stop** or **Keep it** ends the questions: ask no more of them. Then act on all the answers, with the first rule that applies:
   1. Any **Stop** or **Keep it**: stop, and delete nothing. Give `/mreq-apply <path>` with each failure the user did not close anyway, each finding marked **Fix the code**, and each finding not yet asked. When there is none, only stop.
   2. Any **Fix now** or **Fix the code**: hand the document to `mreq-apply` with each failure (when the user picked **Fix now**) and each finding marked **Fix the code** (see "Handing over to mreq-apply").
   3. Otherwise: go to step 5. Name in the report each failing test closed anyway, each command that did not run, and each accepted finding as an accepted departure.

5. **Delete the document.**
   Do this only after every step 4 question is answered.
   Before the delete, collect the items in `## Open`, and any follow-up, `Open:` or `Unconfirmed:` line still in `## Handoff`: nothing keeps them once the file is gone. They go in the report.
   Run `delete <path>`; never delete with another command. Do not check git, and do not ask before the delete.

6. **Report.**
   Always say what was deleted and what the check found. Then name each of these that applies:
   - Each accepted departure.
   - Each unfinished task.
   - Each failing test closed anyway.
   - Each command that did not run.
   - That no test command was found and none ran.
   - The test command not rerun, and the task that ran it.
   - The test command and task checks not rerun because the document is `done`, and the verification its Handoff gives.
   - The follow-ups from step 5.
   - Every file a check left behind (other than caches).
   - Anything the code does that the document never asked for.

## Handing over to mreq-apply

Do this only where a step above says so, and never delete the document then.
1. Run the `mreq-apply` skill (see "Running another mreq skill"). Pass the document's absolute path as its argument, then each finding or failure on its own line: the document's line, what the code does, and its `path:line` or the failing command.
2. Do nothing more in this skill. When the call is denied, give the user the findings with the command.

## Guardrails

- Never edit source code or the document. Fixes go through `mreq-apply`.
- Create no files yourself; caches the test run leaves are fine, and so is a new data path a check needs (step 3).
- Delete only in step 5, after every question in steps 1 to 4 is answered. Never delete after handing the document to `mreq-apply`.
- Run the check in step 3 unless the user explicitly asks to skip the check. "Just close it" alone does not skip it.
