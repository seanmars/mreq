# Orchestrator loop

You are the orchestrator of mreq-apply's orchestrate mode: one subagent implements a phase, another verifies it, and only you write the document. Follow this loop in place of step 4 of SKILL.md. The sections this file names ("When to stop and ask", **Stopping**, step 4) are in SKILL.md, and `${CLAUDE_SKILL_DIR}` is the directory that holds it. The phase is the unit here: step 4's one task per edit does not apply.

## Phases

A `### ` heading in `## Tasks` starts a phase: the tasks under it, up to the next `### ` heading. Tasks above the first heading are a phase of their own. With no `### ` heading, all the tasks are one phase. Some tasks prove a fact about the code as it is before the work changes it: for `refactor` the pin task (the first task), for `issue` the tasks that reproduce the bug and confirm its root cause (the first two tasks). A verifier can check them only before the other tasks start, so they are always a phase of their own. When the document puts other tasks in their phase, or has no heading, split that phase in two: these tasks first, then the other tasks.

## What a report leaves in the document

As soon as you read a report, and before you act on it, write into `## Open`:
- each of the implementer's **Follow-ups**, as `- Follow-up: <what>`;
- each file under **Left behind**, in either report, as `- Follow-up: remove <path>`.

Write no item that `## Open` already holds. Do this whatever comes next (a question, a failed verification, a stop): a bug found in a failed attempt is still a bug. A file left behind is no finding and no reason to stop.

## The loop

Take the first phase that has an unchecked task.

1. **Implement.** Spawn one subagent that can edit files and run commands. Its prompt holds only: the document's absolute path, the phase (its heading, or `all tasks`; for a part of a split phase, its task numbers, for example `task 1` or `tasks 2-3`), and the instruction to read `${CLAUDE_SKILL_DIR}/IMPLEMENTER.md`, written as an absolute path, and report in its shape. After a failed verification, add the verifier's findings, word for word. After a question, add the user's answer. Never paste the file into the prompt.
2. **Act on its report.** First do as "What a report leaves in the document" gives.
   - **Blocked** holds a question: it is a case of "When to stop and ask". Ask the user as that section gives, and write into the document what it says to write. Then send the answer to the same implementer when your agent can continue a subagent; otherwise spawn a new one.
   - A task is not done and **Blocked** holds none: treat it as an error you cannot resolve.
   - Every task of the phase is done: for `issue`, write the implementer's **Root cause** into `## Root Cause` when the section does not hold that cause yet. The verifier reads it there and checks it against the code. Then go on.
3. **Verify.** Spawn one subagent that can run commands. Its prompt holds only: the document's absolute path, the phase, the implementer's **Files changed** list (each path with `created`, `changed` or `deleted`, and no other word from a line), and the instruction to read `${CLAUDE_SKILL_DIR}/VERIFIER.md`, written as an absolute path, and report in its shape. Give it nothing else from the implementer's report: a verifier that is told the work passed tends to agree.
4. **Act on the verdict.** First do as "What a report leaves in the document" gives.
   - **`pass`**: check off every task of the phase and delete their `Resume:` lines. Write each item under the verifier's **Not asked for** into `## Open` as `- Follow-up: <what>`, and say in it that the document did not ask for it; the code may still change after a `fail`, so these wait for a `pass`. Write no item that `## Open` already holds. Rewrite `## Handoff`: what is done, each command the verifier ran with its result, and the next phase. Run `update <path>`. Then take the next phase.
   - **`fail` with findings**: check off nothing, and go back to 1 with the findings. When it is the second verification of the same phase that fails with findings, ask instead: **Try again** (go back to 1), **Work it here** (see "Work it here") or **Stop**. Count only this run of the skill, and only a `fail` with findings.
   - **`fail` with no findings**: check off nothing. Every item under **Not run** names its reason:
     - Any item is `denied`: it is the denied-command case of "When to stop and ask".
     - Otherwise (`cannot reproduce`, `no safe path`): the verifier's rules keep it from that check, so spawn no other verifier for it, and add nothing to a verifier's prompt. Ask, with each check and its reason in the question: **Work it here** (see "Work it here"), **Accept by reading** (do as `pass` gives, and name in `## Handoff` each check that did not run, with its reason) or **Stop**.

A stop in this mode follows **Stopping**: in the `Resume:` line, name the tasks the implementer reported done that no verifier passed, as `implemented, not verified`.

## Work it here

This answer takes the phase out of the loop: no subagent implements it, and no verifier checks it. For this phase the rule against reading and editing source code does not apply.

1. Do what step 2 left out: read the code the document cites, and run `git status` and `git diff`, each on its own.
2. A task the implementer reported done is not proved. Check it against the code and the verifier's findings before you check it off.
3. Work the phase's unchecked tasks as step 4 gives, with one check-off, one Handoff rewrite and one `update` for each task.

Then take the next phase in the loop.

## Step 5 in this mode

Step 5 needs the related tests to pass. A verifier's run of the test command counts when it passed and no code changed after it: do not run the tests again then. Otherwise:
- You worked a phase yourself after that run: run the related tests as step 5 gives.
- The user accepted a phase by reading, and the check that did not run is the test command: the tests have not passed. Do not set `done`. Tell the user which command did not run and why.

A task's own check that did not run, and that the user accepted by reading, does not keep the document from `done`.
