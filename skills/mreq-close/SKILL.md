---
name: mreq-close
description: Finish an mreq task document under .mreq/. Check that the code does what the document agreed, then delete the document. Use for /mreq-close.
disable-model-invocation: true
---

# mreq-close

Run only when the user typed `/mreq-close`. If you are reading this file on your own, stop and ask the user to run `/mreq-close <path>`.

Check the code against one `.mreq/` document, then delete the document. The code is the record of what was done.

**Input**: Optional. A document path.

## Language

Write and reply in the language the agent instruction files (`AGENTS.md`, `CLAUDE.md`, ...) set. When they set none, use the language the user writes in. A reply that only picks an option (`1`, `Accept the code`) or gives a path does not change it. When the user has written no natural language yet (only a command or a path), use the language of the document: the language of its title and `## Goal`, not of the template's headings or text. A title such as `add 輸入 1,000 時當掉` means Traditional Chinese, though every heading is English. Use that language in every message, from the first line to the report, including the short notes between tool calls. Only fixed labels such as `Open:` stay as written.

## Asking the user

When the `AskUserQuestion` tool is available, ask with it: up to 4 independent questions at once, the recommended option first and labelled "(Recommended)". Otherwise, ask in plain text as a numbered list, the recommended option first, and wait for the answer.

## The script

The script is `<mreq-shared directory>/scripts/mreq.py`, where `<mreq-shared directory>` is `../mreq-shared` from this skill's directory. Every document path you show the user is the absolute path the script printed.

- `list`: every document, most recently updated first. An item with `warning` or `error` is a file the script cannot trust: name it to the user.
- `delete <path>`: deletes the document. It refuses any file outside `.mreq/`.

Run each command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. Use the script's absolute path. Run `uv run <script> <command>` first. When `uv` fails before the script starts (`uv` is not found, or `uv` prints its own error, for example a cache directory it cannot create), run `python <script> <command>`; when `python` is not found, run `python3`. An error the script prints is not a reason to switch, and neither is a denied command: follow "When a tool call is denied". The allow rule for a denied script command is `Bash(uv run *mreq.py*)` or `PowerShell(uv run *mreq.py*)` (`python` or `python3` in place of `uv run` when you ran it).

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it, with one allow rule for each. Use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`, for example `Bash(python -m unittest discover -s tests)`. Never merge two denied commands into one rule, and never suggest a broader rule. Then stop.

## Steps

1. **Pick the document.**
   Use the path the user gave. Otherwise run `list` and let the user pick, documents with `status` `done` first. Never pick one yourself. Your first message starts with the line `Closing: <absolute path>`, also when the user gave the path: when they gave it, say it before any tool call; otherwise, right after they pick.
   When this conversation made the changes (for example, it ran `mreq-apply` on this document), the audit is not independent: say so, recommend running `/mreq-close <path>` in a new session, and ask once: **Continue here** or **Stop**. Stop: give `/mreq-close <path>` and stop.

2. **Check the tasks.**
   When a task is unchecked, ask once:
   - **Continue (mreq-apply)**: stop here; the user runs `/mreq-apply <path>`.
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
   2. **Run.** After the audit, run the checks the document names, and only those: its test command (when it names none, the one in the project's README or agent instruction files); for `issue`, the `## Symptom` repro; for `refactor`, the `## Behavior Pin`; and the check a task names. Run each command exactly as written: add no `uv run`, and use no `python -c` in its place. When a check needs a script, run it inline. When a check writes or changes files beyond caches (a data file, a database), keep it off the project's real data: point it at a new path the command accepts (for example a `--file` option), or give it to the user to run. That new path is the only change you make to a command. Add no checks of your own, not even to confirm a finding: the audit's `path:line` is the evidence. When any command you ran in this step is denied, do not retry it another way, and do not stop: it goes to **Tests not run** in step 4.

4. **Act on the result.**
   - **All done, tests pass**: go to step 5.
   - **Failing tests**: stop. Tell the user to run `/mreq-apply <path>` with the failures, then `/mreq-close` again.
   - **Tests not run** (a command in step 3 was denied, or you found no tests): give the user each command that did not run, exactly as you ran it, with one allow rule for each denied one (see "When a tool call is denied"), and ask once: **Close anyway** or **Keep it**. Never count it as a pass. Close anyway: go on, and name it in the report. Keep it: stop.
   - **A finding** (partly done, done differently, missing): ask one question per finding. Quote the document's line, say what the code does, and offer **Accept the code** or **Fix the code**.
     - Any **Fix the code**: stop. Tell the user to run `/mreq-apply <path>` with those findings, then `/mreq-close` again.
     - All **Accept the code**: go to step 5, and name each finding in the report as an accepted departure.

5. **Delete the document.**
   Do this only after every step 4 question is answered.
   Before the delete, collect the items in `## Open`, and any follow-up, `Open:` or `Unconfirmed:` line still in `## Handoff`: nothing keeps them once the file is gone. They go in the report.
   Run `delete <path>`; never delete with another command. Do not check git, and do not ask before the delete.

6. **Report.**
   What was deleted, what the check found, each accepted departure, unfinished tasks and tests not run if any, the follow-ups from step 5, every file a check left behind (other than caches), and anything the code does that the document never asked for.

## Guardrails

- Never edit source code or the document. Fixes go through `mreq-apply`.
- Create no files yourself; caches the test run leaves are fine, and so is a new data path a check needs (step 3).
- Delete only in step 5, after every question in steps 1 to 4 is answered.
- Run the check in step 3 unless the user explicitly asks to skip the check. "Just close it" alone does not skip it.
