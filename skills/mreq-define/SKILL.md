---
name: mreq-define
description: Start a new piece of work. Classify what the user wants (feature, issue, refactor, or another task), interview until the goal is clear, get the user to confirm a restatement, then write a task document under .mreq/ that tracks progress and hands off to the next agent. For a small request, or when the user asks for no document, implement the confirmed restatement directly instead. Use for /mreq-define.
argument-hint: "[<request>]"
disable-model-invocation: true
---

# mreq-define

Run only when the user invoked this skill: typed `/mreq-define` (`/mreq:mreq-define` with the Claude Code plugin, `$mreq-define` in Codex), or asked for it by name. If you are reading this file on your own, stop and ask the user to run `/mreq-define <request>`.

Turn a request into one confirmed task document. Do not implement anything: `mreq-apply` does that, after the user chooses it. The one exception is "Without a document": the user chooses in step 4 to implement the restatement here, with no document.

**Input**: What the user wants: a feature, a bug, a refactor, or any other task. It can be vague. It can also be the prompt mreq-pro or mreq-terms wrote in this conversation: see "A request from mreq-pro or mreq-terms".

## Language

Write and reply in the language the agent instruction files (`AGENTS.md`, `CLAUDE.md`, ...) set. When they set none, use the language the user writes in. A reply that only picks an option (`1`, `Accept the code`) or gives a path does not change it. Use that language in every message, from the first line to the report, including the short notes between tool calls. Only fixed labels such as `Open:` stay as written.

## Asking the user

When your agent has a tool that asks the user option questions, ask with it: `AskUserQuestion` in Claude Code, `ask_user_question` in Grok, `ask_question` in Antigravity, `request_user_input` in Codex. Ask up to 4 independent questions at once, or as many as the tool takes, the recommended option first and labelled "(Recommended)". When a question has more options than the tool takes, ask that question in plain text. When the tool returns an error (Codex allows it only in Plan mode), ask in plain text for the rest of this conversation. Without such a tool, ask in plain text as a numbered list, the recommended option first, and wait for the answer.

Ask with options, so the user picks instead of types:
- Give every question 2 to 4 options. Keep each label short (1 to 5 words) and put the detail in its description. Keep each `header` to 12 characters or fewer.
- Never add an "Other" option: these tools add a free-text answer to every question. When an answer may need a value no option holds (a path, a correction), say in the question that the user can type it there.
- Ask for a typed answer only when no option can hold it, such as an error message only the user has seen. When you can guess the answer, offer the guess as an option.
- Never ask the user to type a command that this skill's steps say to run for them.

## The script

The script is `${CLAUDE_SKILL_DIR}/scripts/mreq.py`. `${CLAUDE_SKILL_DIR}` is the directory that holds this SKILL.md. Claude Code fills in its absolute path; other agents may leave the variable as written. Then put the absolute path of this SKILL.md's directory in its place yourself, before the first command or file read that uses it: the directory of the path you loaded this file from (Codex gives it in the skill's `<path>`, Grok in the skill list's `Absolute path`). Never run a command or read a path that still holds `${`: the shell reads it as an empty variable, and the command or read fails. An error that names a path starting with `/scripts/` means the variable was empty: put the path in its place and run the same command again. It creates and lists task documents. It prints JSON. Every document path you show the user is the absolute path the script printed.

Write every path with `/`, never with `\`, on Windows too: the script prints its paths that way, and a shell can drop a `\`. Run `uv run "${CLAUDE_SKILL_DIR}/scripts/mreq.py" <command>` first, with the script's path always in double quotes. When `uv` fails before the script starts (`uv` is not found, or `uv` prints its own error, for example a cache directory it cannot create or a download a sandbox blocks), run `python` in place of `uv run`; when `python` is not found, run `python3`. On Windows, a `python` or `python3` that prints nothing, or only a Microsoft Store hint, is not found. Once one of them starts the script, run every later script command in this conversation with it, and do not try `uv run` again. An error the script prints is not a reason to switch, and neither is a script path that does not exist (`Failed to spawn`, `can't open file`): fix the path instead. A denied command is not a reason either: follow "When a tool call is denied". In Claude Code, the allow rule for a denied script command is `Bash(uv run *mreq.py*)` or `PowerShell(uv run *mreq.py*)` (`python` or `python3` in place of `uv run` when you ran it).

- `new --schema <feature|issue|refactor|task> --slug <kebab-case> --title="<title>" --desc="<one sentence>"`: creates `.mreq/<yyyyMMdd-HHmmss>-<slug>.md` at the git root, from the matching template.
- `list [--open]`: every document's front matter and checkbox progress under `## Tasks`, most recently updated first. An item with `warning` or `error` is a file the script cannot trust: name it to the user.

Never write the front matter dates yourself: the script owns them.

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it. In Claude Code, add one allow rule for each: use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`, for example `Bash(python -m unittest discover -s tests)`. Never merge two denied commands into one rule, and never suggest a broader rule. Other agents write their rules in other forms: give only the command or path. Then stop.

## Running another mreq skill

When a step says to run another mreq skill (`mreq-apply` or `mreq-grill`), start it the way your agent allows, with the arguments the step gives:
- **With a skill tool** (Claude Code: the Skill tool): call it by the name your skill list shows: `mreq:mreq-apply` when mreq is installed as the Claude Code plugin, `mreq-apply` otherwise. When the call fails with `Unknown skill` and names the skill to use (`Did you mean ...`), call that name once: this is not a denied call.
- **Without one** (Codex, Grok, Antigravity): read that skill's SKILL.md in full, for example `${CLAUDE_SKILL_DIR}/../mreq-apply/SKILL.md`, and follow it from its first step, with the arguments as its input. In that file, the skill-directory variable means that skill's directory, not this one.

When the skill is not installed (the skill tool knows no such skill and names no other, or its SKILL.md does not exist), tell the user which skill to install, and stop.

When the call is denied, give the user the command that runs it, for example `/mreq-apply <path>`, and the Claude Code allow rule for the name you called, for example `Skill(mreq:mreq-apply)`, then stop. After a denied call, never read the skill's SKILL.md and follow it yourself: the user decides.

When you give the user a command to type, write it the way their agent runs a skill: `/mreq-close <path>` in Claude Code, Grok and Antigravity (`/mreq:mreq-close <path>` also works with the plugin), `$mreq-close <path>` in Codex.

## A request from mreq-pro or mreq-terms

Do this when this conversation holds a reply from mreq-pro or mreq-terms, and the user gave no request or gave that reply's rewritten prompt as the request. Use the latest such reply, whichever of the two wrote it. The request is the rewritten prompt in its code block, with any change the user asked for since. Use the reply as it is written: do not work out again what it answers, and do not ask the user for it. In step 4, keep the terms as the prompt writes them: "in your own words" does not replace them.

**A reply from mreq-pro** changes the steps as follows. Do not answer its four questions again.
- **Step 1**: read the code as for any request. mreq-pro read no code, so the code can contradict the reply. Then the code wins: name the difference in step 4.
- **Step 3**: ask each question the reply leaves for the user that the conversation has not answered since. Never ask about a choice the prompt says to prototype: an experiment settles it, not the user.
- **Step 4**: keep the methods, the tools and the pass/fail condition as the prompt names them, as you keep the terms. Write the pass/fail condition in **Goal**. Write under **Decided**, each with the reply's reason: what to do about the crux, the raw material to start from, the methods and tools, and each choice to prototype. Write what the reply removed or narrowed under **Out of scope**.
- **The tasks** (`## Tasks` in step 5, the task list in "Without a document"): each choice to prototype is one task, before the tasks that depend on it. Its check is what the experiment showed. The pass/fail condition is the check of the last task.

**A reply from mreq-terms** changes the steps as follows.
- **Step 3**: ask about each thing the reply says the user left out, unless the conversation has settled it since. Never put one in scope without the user's answer.
- **Step 4**: when the reply picked one problem out of several the prompt could name, and the user has not confirmed the pick, write it under **Assumptions**.
- **Every message and the document**: never use a term the reply says does not fit the user's situation. Use the term it gives in its place.

## Steps

1. **Read before you ask.**
   When the request reads only as a question about how the code works, ask one question (see "Asking the user") first, before you run any command or read any code. Judge it from the request's words alone:
   - **Explain it (/mreq-how)**: give the user `/mreq-how <the question>`, with the question filled in so they can copy it, and stop. `/mreq-how` is user-invoked, so it does not appear in your skill list; do not say it is missing, and do not try to run it.
   - **Treat it as a task**: go on with this step.
   Find the git root: run `git rev-parse --show-toplevel` on its own, without `-C`. When it fails (not a git repository), use the current directory. When the git root is not the directory the agent was started in, say so in your first reply, before any `new`: the document goes to `<git root>/.mreq/`, and the agent cannot read or edit it from here in later turns. Ask the user to start the agent from the git root, then stop.
   Run `list --open`. When an open document already covers this request, ask one question (see "Asking the user"), with the document's title and absolute path in the question:
   - **Continue it (mreq-apply)**: run the `mreq-apply` skill on that document (see "Running another mreq skill"), and do nothing more in this skill.
   - **Start a new document**: go on with this step.
   Read the project's README and agent instruction files, from the git root. Then size the request:
   - **Simple**: one module, one function, one file. Read the code it touches and its tests yourself.
   - **Complex**: several modules, a cross-cutting change, or code you cannot place yet. Split it into 2-4 distinct angles (for example: the code the request touches and its callers; the tests and how to run them; for a bug, the history of the code the symptom runs through). When you can spawn subagents, spawn one read-only explorer per angle in a single message (for example Codex's `explorer` role, Grok's `explore` type, or Antigravity's `research` subagent). Each prompt holds only the request, that explorer's angle, and the instruction to read `${CLAUDE_SKILL_DIR}/EXPLORER.md`, written as an absolute path, and report in its shape. Never paste the file into the prompt. Otherwise, work the angles yourself, one at a time, with notes in the shape `EXPLORER.md` gives. Then reconcile: merge overlaps, and settle a contradiction by reading the code yourself, not by picking one account.

   When in doubt, take the simple path. Remember the size: step 4 uses it. Never ask the user what the codebase answers: the facts you found answer it, and the decisions the code cannot settle are step 3's questions.

2. **Classify the request.**

   | schema | The user wants to | Signals |
   |---|---|---|
   | `feature` | add or change behavior | "add", "support", "allow", a new screen, command, or option |
   | `issue` | fix behavior that is wrong | an error, a stack trace, "broken", "should X but does Y" |
   | `refactor` | change structure, keep behavior | "clean up", "extract", "rename", "split", "simplify" |
   | `task` | anything else | docs, config, CI, dependency bumps, scripts |

   When two fit, pick the one whose done state the user cares about most, and name the choice in step 4.

3. **Interview until the goal is clear.**
   Skip every question the request or the code already answers. A clear request goes straight to step 4.
   - Ask each decision as an option question (see "Asking the user"): your suggested answer first, with its reason in the description, then the real alternatives. When the decision does not block the document, add **Decide later** as the last option.
   - Ask for a typed answer only for a fact that only the user has, such as an exact repro or an error message. Then say so in the question, and still offer your best guess as an option when you have one.
   - Ask unrelated questions together. Hold a question that depends on an open one.
   - Look up facts; ask for decisions (behavior, scope, trade-offs).
   - Ask what each answer implies that nobody said.
   - When the user defers a decision ("decide later"), that answers it: it stays open, and you do not ask again.

   Ask in this order, by schema:
   - `feature`: done state; who uses it; what is out of scope; error paths; what data persists.
   - `issue`: exact repro; expected vs actual; since when, or what changed; who is affected.
   - `refactor`: the behavior that must not change and how to prove it; the target shape; what is out of scope.
   - `task`: done state; constraints; what is out of scope.

4. **Restate and get confirmation.**
   Restate only after the user has answered every step 3 question. Say back, in your own words, not the user's:
   - **Type**: the schema, and why.
   - **Goal**: what is true when this is done.
   - **Problem**: what is wrong or missing now.
   - **Decided**: each choice made, with its reason. Omit when none.
   - **Out of scope**: omit when none.
   - **Assumptions**: what you inferred and the user never said, each marked as a guess.
   - **Open**: each decision the user deferred. Omit when none.

   Then ask one question (see "Asking the user") with four options. The same answer confirms the restatement and picks the next step, so step 6 asks nothing.
   - The first three options depend on the request. Offer the no-document set when the request is simple (step 1) and **Open** is empty, or when the user has already asked for no document. Offer the document set in every other case.
     - The document set:
       - **Correct, write the document, then implement**: go to step 5, then run `mreq-apply` on the document (step 6).
       - **Correct, write the document, then grill it**: go to step 5, then run `mreq-grill` on the document (step 6).
       - **Correct, write the document only**: go to step 5, then stop (step 6).
     - The no-document set:
       - **Correct, implement now, no document**: go to "Without a document"; skip steps 5 and 6.
       - **Correct, grill it first, no document**: go to "Grill without a document", which comes back to this step.
       - **Correct, write the document, then implement**: go to step 5, then run `mreq-apply` on the document (step 6).
   - **Something is wrong**: always the last option. Ask one multi-select question (`multiSelect`) that lists up to 4 restated items most likely to be wrong, assumptions first, each as an option. Then ask about each item the user picked as in step 3, and restate again.

   Recommend the first option of the set you offer: **Correct, write the document, then implement** in the document set, **Correct, implement now, no document** in the no-document set. In the document set, when the plan still feels untested, recommend **Correct, write the document, then grill it** and put that one first.

   Word the options in your own words each time; keep their meaning. A free answer that corrects something is a correction. A correction means something is still hidden: go back to step 3, then restate again. Only a "Correct" option moves on.

   When the free answer confirms and names a next step that no option holds (for example "write the document only" in the no-document set), it confirms the restatement: do that step.

   When the free answer asks to implement without a document (for example "no document, just do it") and corrects nothing, it confirms the restatement: go to "Without a document", whatever the size of the request and also when **Open** has items. When it also corrects something, handle the correction first, then offer **Correct, implement now, no document** in the next restatement.

   Only an explicit request to skip this confirmation (for example "stop asking, just write the document") skips it. "Just write it" alone, or answering the questions, does not: restate. When the user skips it, go to step 5 without restating: write every assumption in `## Assumptions`, mark the document unconfirmed in `## Handoff`, and name the assumptions in your reply.

5. **Write the document.**
   Run `new`. Then fill the file with Edit, in the language the Language section picks; `--title` and `--desc` use it too:
   - Change only the body, section by section, with Edit. Never rewrite the whole file and never touch the front matter: the script owns it.
   - Replace every `<!-- -->` hint with content, or delete it when a section does not apply.
   - Keep the `##` headings as they are: other mreq skills look for them.
   - Write `## Tasks` as small steps, each with how to check it. Keep the template's fixed steps for `issue` and `refactor`.
   - When the tasks fall into stages that each leave the code working and can be checked alone (for example the data layer, then the API), group them into phases: put each stage's tasks under a `### <phase name>` heading in `## Tasks`, and keep the task numbers running from one phase to the next. `mreq-apply --orch` implements and verifies one phase at a time. Write no heading when there are 4 tasks or fewer, or no such stages; `refactor` and `issue` are the exception.
   - For `refactor` and `issue`, always keep the template's two headings, and name them in the document's language. Under the first one go only the tasks that are proved against the code before it changes: for `refactor` the pin task alone, for `issue` the tasks that reproduce the bug and confirm its root cause. Every task that changes the code goes under the second one or under more headings after it. A pin or a reproduction proves something only when it ran before the code changed, and `mreq-apply --orch` verifies a phase only after all of its tasks are done.
   - Write each step 4 field into its section:
     - **Type**: the `--schema` of `new`.
     - **Goal**: `## Goal`.
     - **Problem**: `## Symptom` for `issue`, `## Goal` for `refactor`, `## Context` otherwise.
     - **Decided**: `## Decisions`, one `### Dn:` each.
     - **Out of scope**: `## Scope`, under `Out:`. Write `None` when there is none. For `feature`, also write under `In:` what **Goal** and **Decided** put in scope: `mreq-apply` builds only that.
     - **Assumptions**: `## Assumptions`, each still marked as a guess. Never turn an assumption into a decision.
     - **Open**: `## Open`, one `- Open: <question>` bullet each. Delete the hint and leave the section empty when there is none.
   - Write `## Handoff` as: not started; the first task to take. When the user skipped step 4's confirmation, add a line `Unconfirmed: the user did not confirm a restatement; check ## Assumptions and ## Decisions with the user first.`
   - Leave `status` as `draft`.

6. **Go on to the next step.**
   Ask nothing here: the user picked the next step in step 4.
   - **Correct, write the document, then implement** or **Correct, write the document, then grill it**: run the skill they picked on this document now, `mreq-apply` or `mreq-grill` (see "Running another mreq skill").
   - **Correct, write the document only**, or the user skipped step 4's confirmation: give the absolute path the script printed, and stop.

## Grill without a document

Do this only when step 4 sent you here. Pressure-test the confirmed restatement in this conversation. Write no file, edit no code, and do not run `mreq-grill`: it needs a document.

Read `${CLAUDE_SKILL_DIR}/GRILL.md` and follow it. The subject is the restatement. Report the four quadrants separately, in the order it gives. When this conversation already grilled this subject, follow its "A later round" section instead.

Then go back to step 4 and restate again, with what the grill changed: the claims that fell, the assumptions now explicit, the decisions made, and what is still open. Step 4 picks its options from the new restatement: when the grill left an **Open** item, or showed that the request is not simple, it offers the document set.

## Without a document

Do this only when step 4 sent you here. Implement the confirmed restatement in this conversation. The restatement is the record: run no `new`, write no file under `.mreq/`, and run no `mreq-apply`. There is nothing for `/mreq-close` to close afterwards.

1. **List the tasks.** In one short message, write the work as small steps, each with how to check it.
2. **Work the tasks one at a time.** Implement the smallest change that does the task, and follow the schema rules below. Prove it works by running something: a test, the repro, or a command that would fail if you were wrong. Reading the code is not proof. When nothing you can run reaches the behavior, say so in the report.
3. **Finish.** Run the related tests. Then report against the restatement:
   - **Goal** and each **Decided** item: done, partly done, done differently, or missing, with `path:line`.
   - What you ran and its result. Tests that did not run have not passed: say so.
   - Anything the code now does that the restatement never asked for.
   - Each **Open** item still open, and each follow-up.

**Schema rules:**
- **`feature`**: build only what the restatement puts in scope. Add no flexibility for later.
- **`issue`**: reproduce the bug before you change code. Verify the root cause before you fix it, and fix the cause, not the symptom. When two fixes fail, stop: the root cause is probably wrong. Say so and verify it again before a third fix.
- **`refactor`**: pin the behavior first with a test or a command, and keep it green after every step. Change no behavior. When you find a bug, name it in the report as a follow-up and do not fix it here.
- **`task`**: do the task as **Goal** describes it.

**Questions.** When a task is unclear, or an **Open** item decides how to do the next task, ask it as an option question (see "Asking the user") and go on after the answer. A question alone needs no document.

**Switch to a document.** The restatement lives only in this conversation, so write the document when the work stops being small or stops unfinished:
- **The work outgrows the restatement** (a task needs work outside **Goal** or the scope, or the change turns out to span several modules): name the extra work and ask once: **Write the document, continue with mreq-apply** (recommended), **Do it here**, or **Leave it out** (name it in the report as a follow-up).
- **The work stops before it is done** (a denied command, an error you cannot resolve, the user stops or pauses you): write the document before you reply, then give the user `/mreq-apply <path>`.

To write it, follow step 5, with these changes: check off (`- [x]`) each task that is done and proven; under the next unchecked task, add one nested bullet `  - Resume: <done so far>; <what is left>; <next action>`, with changes that are only in the working tree; write `## Handoff` as what is done, what you verified and how, and the next task. For **Write the document, continue with mreq-apply**, then run the `mreq-apply` skill on it as in step 6. When the document cannot be written (a denied `new` or Edit), put the same record in your reply.

## Guardrails

- Write only the task document under `.mreq/`. Never edit source code or other files, except in "Without a document".
- Never start the next step yourself: the user picks it in step 1 (continue an open document) or step 4 (implement or grill, each with or without a document, or the document only).
- In "Without a document": never delete, skip, or weaken a test to get to green. Never run git commands that change the working tree, the index or history unless the user asks. Write scratch files inside the project and remove them before you finish.
- Never skip step 4, even when the request looks clear. The only exception is the user's explicit request to skip the confirmation (step 4), and then the document records it as `Unconfirmed:`.
