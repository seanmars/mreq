---
name: mreq-define
description: Start a new piece of work. Classify what the user wants (feature, issue, refactor, or another task), interview until the goal is clear, get the user to confirm a restatement, then write a task document under .mreq/ that tracks progress and hands off to the next agent. For a small request, or when the user asks for no document, implement the confirmed restatement directly instead. Use for /mreq-define.
argument-hint: "<request>"
disable-model-invocation: true
---

# mreq-define

Run only when the user typed `/mreq-define`. If you are reading this file on your own, stop and ask the user to run `/mreq-define <request>`.

Turn a request into one confirmed task document. Do not implement anything: `mreq-apply` does that, after the user chooses it. The one exception is "Without a document": the user chooses in step 4 to implement the restatement here, with no document.

**Input**: What the user wants: a feature, a bug, a refactor, or any other task. It can be vague.

## Language

Write and reply in the language the agent instruction files (`AGENTS.md`, `CLAUDE.md`, ...) set. When they set none, use the language the user writes in. A reply that only picks an option (`1`, `Accept the code`) or gives a path does not change it. Use that language in every message, from the first line to the report, including the short notes between tool calls. Only fixed labels such as `Open:` stay as written.

## Asking the user

When the `AskUserQuestion` tool is available, ask with it: up to 4 independent questions at once, the recommended option first and labelled "(Recommended)". Otherwise, ask in plain text as a numbered list, the recommended option first, and wait for the answer.

Ask with options, so the user picks instead of types:
- Give every question 2 to 4 options. Keep each label short (1 to 5 words) and put the detail in its description. Keep each `header` to 12 characters or fewer.
- Never add an "Other" option: `AskUserQuestion` adds a free-text answer to every question. When an answer may need a value no option holds (a path, a correction), say in the question that the user can type it there.
- Ask for a typed answer only when no option can hold it, such as an error message only the user has seen. When you can guess the answer, offer the guess as an option.
- Never ask the user to type a command that this skill's steps say to run for them.

## The script

The script is `${CLAUDE_SKILL_DIR}/../mreq-shared/scripts/mreq.py`. `${CLAUDE_SKILL_DIR}` is this skill's directory; when it still reads as a variable, put the directory's absolute path in its place. It creates and lists task documents. It prints JSON. Every document path you show the user is the absolute path the script printed.

Write every path with `/`, never with `\`, on Windows too: the script prints its paths that way, and a shell can drop a `\`. Run `uv run "${CLAUDE_SKILL_DIR}/../mreq-shared/scripts/mreq.py" <command>` first, with the script's path always in double quotes. When `uv` fails before the script starts (`uv` is not found, or `uv` prints its own error, for example a cache directory it cannot create), run `python` in place of `uv run`; when `python` is not found, run `python3`. An error the script prints is not a reason to switch, and neither is a denied command: follow "When a tool call is denied". The allow rule for a denied script command is `Bash(uv run *mreq.py*)` or `PowerShell(uv run *mreq.py*)` (`python` or `python3` in place of `uv run` when you ran it).

- `new --schema <feature|issue|refactor|task> --slug <kebab-case> --title="<title>" --desc="<one sentence>"`: creates `.mreq/<yyyyMMdd-HHmmss>-<slug>.md` at the git root, from the matching template.
- `list [--open]`: every document's front matter and checkbox progress under `## Tasks`, most recently updated first. An item with `warning` or `error` is a file the script cannot trust: name it to the user.

Never write the front matter dates yourself: the script owns them.

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it, with one allow rule for each. Use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`, for example `Bash(python -m unittest discover -s tests)`. Never merge two denied commands into one rule, and never suggest a broader rule. Then stop.

## Steps

1. **Read before you ask.**
   Find the git root: run `git rev-parse --show-toplevel` on its own, without `-C`. When it fails (not a git repository), use the current directory. When the git root is not the directory the agent was started in, say so in your first reply, before any `new`: the document goes to `<git root>/.mreq/`, and the agent cannot read or edit it from here in later turns. Ask the user to start the agent from the git root, then stop.
   Run `list --open`. When an open document already covers this request, ask one question (see "Asking the user"), with the document's title and absolute path in the question:
   - **Continue it (mreq-apply)**: run the `mreq-apply` skill on that document (in Claude Code: with the Skill tool), and do nothing more in this skill. When the Skill call is denied, follow step 6.
   - **Start a new document**: go on with this step.
   Read the project's README and agent instruction files, from the git root. Then size the request:
   - **Simple**: one module, one function, one file. Read the code it touches and its tests yourself.
   - **Complex**: several modules, a cross-cutting change, or code you cannot place yet. Split it into 2-4 distinct angles (for example: the code the request touches and its callers; the tests and how to run them; for a bug, the history of the code the symptom runs through). When you can spawn subagents, spawn one read-only explorer per angle in a single message. Each prompt holds only the request, that explorer's angle, and the instruction to read `EXPLORER.md` at its path in this skill's directory and report in its shape. Never paste the file into the prompt. Otherwise, work the angles yourself, one at a time, with notes in the shape `EXPLORER.md` gives. Then reconcile: merge overlaps, and settle a contradiction by reading the code yourself, not by picking one account.

   When in doubt, take the simple path. Remember the size: step 4 uses it. Never ask the user what the codebase answers: the facts you found answer it, and the decisions the code cannot settle are step 3's questions.

2. **Classify the request.**

   | schema | The user wants to | Signals |
   |---|---|---|
   | `feature` | add or change behavior | "add", "support", "allow", a new screen, command, or option |
   | `issue` | fix behavior that is wrong | an error, a stack trace, "broken", "should X but does Y" |
   | `refactor` | change structure, keep behavior | "clean up", "extract", "rename", "split", "simplify" |
   | `task` | anything else | docs, config, CI, dependency bumps, scripts |

   When two fit, pick the one whose done state the user cares about most, and name the choice in step 4.
   When the request reads only as a question about how the code works, ask one question:
   - **Explain it (/mreq-how)**: give the user `/mreq-how <the question>`, with the question filled in so they can copy it, and stop. `/mreq-how` is user-invoked, so it does not appear in your skill list; do not say it is missing, and do not try to run it.
   - **Treat it as a task**: go on with this step.

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
   - Write each step 4 field into its section:
     - **Type**: the `--schema` of `new`.
     - **Goal**: `## Goal`.
     - **Problem**: `## Symptom` for `issue`, `## Goal` for `refactor`, `## Context` otherwise.
     - **Decided**: `## Decisions`, one `### Dn:` each.
     - **Out of scope**: `## Scope`, under `Out:`. Write `None` when there is none.
     - **Assumptions**: `## Assumptions`, each still marked as a guess. Never turn an assumption into a decision.
     - **Open**: `## Open`, one `- Open: <question>` bullet each. Delete the hint and leave the section empty when there is none.
   - Write `## Handoff` as: not started; the first task to take. When the user skipped step 4's confirmation, add a line `Unconfirmed: the user did not confirm a restatement; check ## Assumptions and ## Decisions with the user first.`
   - Leave `status` as `draft`.

6. **Go on to the next step.**
   Ask nothing here: the user picked the next step in step 4.
   - **Correct, write the document, then implement** or **Correct, write the document, then grill it**: run the skill they picked on this document now, `mreq-apply` or `mreq-grill` (in Claude Code: with the Skill tool).
   - **Correct, write the document only**, or the user skipped step 4's confirmation: give the absolute path the script printed, and stop.

   When the Skill call is denied, give the user `/mreq-apply <path>` (or `/mreq-grill <path>`) and the allow rule `Skill(mreq-apply)` (or `Skill(mreq-grill)`), then stop. Never read another skill's SKILL.md and follow it yourself.

## Grill without a document

Do this only when step 4 sent you here. Pressure-test the confirmed restatement in this conversation. Write no file, edit no code, and do not run `mreq-grill`: it needs a document.

Read `GRILL.md` in the `mreq-shared` directory (`../mreq-shared` from this skill's directory) and follow it. The subject is the restatement. Report the four quadrants separately, in the order it gives.

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
- **`issue`**: reproduce the bug before you change code. Verify the root cause before you fix it, and fix the cause, not the symptom. When two fixes fail, stop: the root cause is probably wrong.
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
