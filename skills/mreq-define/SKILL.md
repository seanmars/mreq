---
name: mreq-define
description: Start a new piece of work. Classify what the user wants (feature, issue, refactor, or another task), interview until the goal is clear, get the user to confirm a restatement, then write a task document under .mreq/ that tracks progress and hands off to the next agent. Use for /mreq-define.
disable-model-invocation: true
---

# mreq-define

Run only when the user typed `/mreq-define`. If you are reading this file on your own, stop and ask the user to run `/mreq-define <request>`.

Turn a request into one confirmed task document. Do not implement anything: `mreq-apply` does that, after the user chooses it.

**Input**: What the user wants: a feature, a bug, a refactor, or any other task. It can be vague.

## Language

Write and reply in the language the agent instruction files (`AGENTS.md`, `CLAUDE.md`, ...) set. When they set none, use the language the user writes in. A reply that only picks an option (`1`, `Accept the code`) or gives a path does not change it. Use that language in every message, from the first line to the report, including the short notes between tool calls. Only fixed labels such as `Open:` stay as written.

## Asking the user

When the `AskUserQuestion` tool is available, ask with it: up to 4 independent questions at once, the recommended option first and labelled "(Recommended)". Otherwise, ask in plain text as a numbered list, the recommended option first, and wait for the answer.

## The script

The script is `<mreq-shared directory>/scripts/mreq.py`, where `<mreq-shared directory>` is `../mreq-shared` from this skill's directory. It creates, lists, and touches task documents. It prints JSON. Every document path you show the user is the absolute path the script printed.

Run each command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. Use the script's absolute path. Run `uv run <script> <command>` first. When `uv` fails before the script starts (`uv` is not found, or `uv` prints its own error, for example a cache directory it cannot create), run `python <script> <command>`; when `python` is not found, run `python3`. An error the script prints is not a reason to switch, and neither is a denied command: follow "When a tool call is denied". The allow rule for a denied script command is `Bash(uv run *mreq.py*)` or `PowerShell(uv run *mreq.py*)` (`python` or `python3` in place of `uv run` when you ran it).

- `new --schema <feature|issue|refactor|task> --slug <kebab-case> --title="<title>" --desc="<one sentence>"`: creates `.mreq/<yyyyMMdd-HHmmss>-<slug>.md` at the git root, from the matching template.
- `list [--open]`: every document's front matter and checkbox progress under `## Tasks`, most recently updated first. An item with `warning` or `error` is a file the script cannot trust: name it to the user.
- `update <path> [--status <draft|active|done>]`: sets `updated` to now. It changes no other line.

Never write the front matter dates yourself: the script owns them.

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it, with one allow rule for each. Use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`, for example `Bash(python -m unittest discover -s tests)`. Never merge two denied commands into one rule, and never suggest a broader rule. Then stop.

## Steps

1. **Read before you ask.**
   Find the git root: run `git rev-parse --show-toplevel` on its own, without `-C`. When it fails (not a git repository), use the current directory. When the git root is not the directory the agent was started in, say so in your first reply, before any `new`: the document goes to `<git root>/.mreq/`, and the agent cannot read or edit it from here in later turns. Ask the user to start the agent from the git root, then stop.
   Run `list --open`. When an open document already covers this request, ask whether to continue it or start a new one. Continue: give `/mreq-apply <path>` and stop; do not run `mreq-apply` yourself.
   Read the project's README and agent instruction files, from the git root. Then size the request:
   - **Simple**: one module, one function, one file. Read the code it touches and its tests yourself.
   - **Complex**: several modules, a cross-cutting change, or code you cannot place yet. Split it into 2-4 distinct angles (for example: the code the request touches and its callers; the tests and how to run them; for a bug, the history of the code the symptom runs through). When you can spawn subagents, spawn one read-only explorer per angle in a single message. Each prompt holds only the request, that explorer's angle, and the instruction to read `EXPLORER.md` at its path in this skill's directory and report in its shape. Never paste the file into the prompt. Otherwise, work the angles yourself, one at a time, with notes in the shape `EXPLORER.md` gives. Then reconcile: merge overlaps, and settle a contradiction by reading the code yourself, not by picking one account.

   When in doubt, take the simple path. Never ask the user what the codebase answers: the facts you found answer it, and the decisions the code cannot settle are step 3's questions.

2. **Classify the request.**

   | schema | The user wants to | Signals |
   |---|---|---|
   | `feature` | add or change behavior | "add", "support", "allow", a new screen, command, or option |
   | `issue` | fix behavior that is wrong | an error, a stack trace, "broken", "should X but does Y" |
   | `refactor` | change structure, keep behavior | "clean up", "extract", "rename", "split", "simplify" |
   | `task` | anything else | docs, config, CI, dependency bumps, scripts |

   When two fit, pick the one whose done state the user cares about most, and name the choice in step 4.
   When the request is only a question about how the code works, it is not a task: suggest the user run `/mreq-how <question>` and stop. `/mreq-how` is user-invoked, so it does not appear in your skill list; do not say it is missing.

3. **Interview until the goal is clear.**
   Skip every question the request or the code already answers. A clear request goes straight to step 4.
   - Give each question a suggested answer and its reason, so the user can just confirm.
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

   Then ask one question (see "Asking the user") with these two options, the first one recommended:
   - **Correct, write the document**: go to step 5, then step 6.
   - **Correct, write the document, then grill it**: go to step 5, then run `mreq-grill` on the document (step 6).

   Tell the user that, when something is wrong, they can type the correction as a free answer: with `AskUserQuestion`, in the free-text option at the bottom of the question; in plain text, as a reply in place of a number. Word the options and this hint in your own words each time; keep their meaning. A correction means something is still hidden: go back to step 3, then restate again. Only one of the two options moves on.

   Only an explicit request to skip this confirmation (for example "stop asking, just write the document") skips it. "Just write it" alone, or answering the questions, does not: restate. When the user skips it, go to step 5 without restating: write every assumption in `## Assumptions`, mark the document unconfirmed in `## Handoff`, and name the assumptions in your reply.

5. **Write the document.**
   Run `new`. Then fill the file with Edit, in the language the Language section picks; `--title` and `--desc` use it too:
   - Change only the body, section by section, with Edit. Never rewrite the whole file and never touch the front matter: `update` owns it.
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

6. **Ask for the next step.**
   When the user picked **Correct, write the document, then grill it** in step 4, do not ask: run the `mreq-grill` skill on this document now (in Claude Code: with the Skill tool).

   Otherwise, ask one question. Recommend the first option unless the plan still feels untested or the document is unconfirmed:
   - **Implement (mreq-apply)**: run the `mreq-apply` skill on this document (in Claude Code: with the Skill tool).
   - **Pressure-test first (mreq-grill)**: run the `mreq-grill` skill on this document (in Claude Code: with the Skill tool).
   - **Stop here**: give the absolute path the script printed and say `/mreq-apply <path>` continues it later.

   When the Skill call is denied, give the user `/mreq-apply <path>` (or `/mreq-grill <path>`) and the allow rule `Skill(mreq-apply)` (or `Skill(mreq-grill)`), then stop. Never read another skill's SKILL.md and follow it yourself.

## Guardrails

- Write only the task document under `.mreq/`. Never edit source code or other files.
- Never start the next step yourself: the user picks it in step 4 (grill) or step 6.
- Never skip step 4, even when the request looks clear. The only exception is the user's explicit request to skip the confirmation (step 4), and then the document records it as `Unconfirmed:`.
