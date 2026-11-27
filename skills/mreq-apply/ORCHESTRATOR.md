# Orchestrator loop

You are the orchestrator of mreq-apply's orchestrate mode: one subagent implements a phase, another verifies it, and only you write the document. Follow this loop in place of step 4 of SKILL.md. The sections this file names ("When to stop and ask", **Stopping**, step 4) are in SKILL.md, and `${CLAUDE_SKILL_DIR}` is the directory that holds it. The phase is the unit here: step 4's one task per edit does not apply.

## Phases

A `### ` heading in `## Tasks` starts a phase: the tasks under it, up to the next `### ` heading. Tasks above the first heading are a phase of their own. With no `### ` heading, all the tasks are one phase. For `refactor`, the pin task (the first task) is always a phase of its own: a verifier can run the pin against the unchanged code only before the other tasks start. When the document puts other tasks in its phase, or has no heading, split that phase in two: the pin task first, then the other tasks.

## The loop

Take the first phase that has an unchecked task.

1. **Implement.** Spawn one subagent that can edit files and run commands. Its prompt holds only: the document's absolute path, the phase (its heading, or `all tasks`; for a part of a split phase, its task numbers, for example `task 1` or `tasks 2-3`), and the instruction to read `${CLAUDE_SKILL_DIR}/IMPLEMENTER.md`, written as an absolute path, and report in its shape. After a failed verification, add the verifier's findings, word for word. After a question, add the user's answer. Never paste the file into the prompt.
2. **Act on its report.**
   - **Blocked** holds a question: it is a case of "When to stop and ask". Ask the user as that section gives, and write into the document what it says to write. Then send the answer to the same implementer when your agent can continue a subagent; otherwise spawn a new one.
   - A task is not done and **Blocked** holds none: treat it as an error you cannot resolve.
   - Every task of the phase is done: go on.
3. **Verify.** Spawn one subagent that can run commands. Its prompt holds only: the document's absolute path, the phase, the implementer's **Files changed** list (each path with `created`, `changed` or `deleted`, and no other word from a line), and the instruction to read `${CLAUDE_SKILL_DIR}/VERIFIER.md`, written as an absolute path, and report in its shape. Give it nothing else from the implementer's report: a verifier that is told the work passed tends to agree.
4. **Act on the verdict.** First, with any verdict: write each file under **Left behind**, in either report, into `## Open` as `- Follow-up: remove <path>`, unless `## Open` holds it already. A file left behind is no finding and no reason to stop.
   - **`pass`**: check off every task of the phase and delete their `Resume:` lines. For `issue`, write the implementer's **Root cause** into `## Root Cause`. Write each of the implementer's **Follow-ups** into `## Open` as `- Follow-up: <what>`. Write each item under the verifier's **Not asked for** the same way, and say in it that the document did not ask for it. Write no item that `## Open` already holds. Rewrite `## Handoff`: what is done, each command the verifier ran with its result, and the next phase. Run `update <path>`. Then take the next phase.
   - **`fail` with findings**: check off nothing, and go back to 1 with the findings. When it is the second verification of the same phase that fails with findings, ask instead: **Try again** (go back to 1), **Work it here** (work the phase yourself as step 4 gives) or **Stop**. Count only this run of the skill, and only a `fail` with findings.
   - **`fail` with no findings**: check off nothing. Every item under **Not run** names its reason:
     - Any item is `denied`: it is the denied-command case of "When to stop and ask".
     - Otherwise (`cannot reproduce`, `no safe path`): the verifier's rules keep it from that check, so spawn no other verifier for it, and add nothing to a verifier's prompt. Ask, with each check and its reason in the question: **Work it here** (work the phase yourself as step 4 gives), **Accept by reading** (do as `pass` gives, and name in `## Handoff` each check that did not run, with its reason) or **Stop**.

A stop in this mode follows **Stopping**: in the `Resume:` line, name the tasks the implementer reported done that no verifier passed, as `implemented, not verified`.
