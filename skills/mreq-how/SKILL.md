---
name: mreq-how
description: Explain how part of the codebase works as an offline HTML page with architecture, sequence, state, and flow diagrams in Mermaid, written to .mreq/how/ under the session root. Pele (https://pele.run/) renders the diagrams, inlined in the page so it works with no network. Covers "how does X work", walkthroughs before changing something, and placement questions ("where should this live", "which layer owns this"). `--plain` writes it for readers who know the product by its features (planners, PMs) and do not read code, so the page holds no paths and no code names. Confirms its reading of the question with the user before any analysis. Use for /mreq-how.
argument-hint: "[--plain] <question>"
disable-model-invocation: true
---

# mreq-how

Run only when the user typed `/mreq-how`. If you are reading this file on your own, stop and ask the user to run `/mreq-how <question>`.

Explain how part of this codebase works (a subsystem, a flow, a module) at the depth its reader needs (see "Reader"), as an offline HTML page: prose that walks the reader through Mermaid diagrams, each with a legend and a one-line caption.

**Input**: `/mreq-how [--<style>] <question>`. The question: "how does X work", a code path to walk through before a change, or a placement question. Confirm your reading of it with the user before any analysis (step 1). The style, when given, is the first word; it is not part of the question. See "Reader".

**This is read-only on the project.** Write no code and no files in the project. The one write is the page, and it goes to `.mreq/how/` under the session root (the directory the agent was started in).

## Language

Write and reply in the language the agent instruction files (`AGENTS.md`, `CLAUDE.md`, ...) set. When they set none, use the language the user writes in. A reply that only picks an option (`1`, `Accept the code`) or gives a path does not change it. Use that language in every message, from the first line to the report, including the short notes between tool calls, and on the page.

## Reader

The style picks who reads the page:

- **No style** (default): an engineer about to change this code. The page cites `path:line` and names the code as written.
- **`--plain`**: a reader who knows the product by its features, such as a planner or a PM, and does not read code. The page explains what the feature does in their words, and holds no path, no `path:line` and no code name the reader does not use themselves. "Plain style" in `WRITING.md` says how.

When the first word starts with `--` and is not a style above, do not guess. In step 1, ask which reader the page is for, with **Plain (--plain)** and **Engineer (no style)** as options, and say that `<the word>` is not a style.

The facts come from the code for every reader: the style changes how the page says them, not what you read.

## Asking the user

When the `AskUserQuestion` tool is available, ask with it: up to 4 independent questions at once, the recommended option first and labelled "(Recommended)". Otherwise, ask in plain text as a numbered list, the recommended option first, and wait for the answer.

Ask with options, so the user picks instead of types:
- Give every question 2 to 4 options. Keep each label short (1 to 5 words) and put the detail in its description. Keep each `header` to 12 characters or fewer.
- Never add an "Other" option: `AskUserQuestion` adds a free-text answer to every question. When an answer may need a value no option holds (a path, a correction), say in the question that the user can type it there.
- Ask for a typed answer only when no option can hold it, such as an error message only the user has seen. When you can guess the answer, offer the guess as an option.
- Never ask the user to type a command that this skill's steps say to run for them.

## The script

`${CLAUDE_SKILL_DIR}/page.py` builds and checks the page. `${CLAUDE_SKILL_DIR}` is this skill's directory; when it still reads as a variable, put the directory's absolute path in its place.

Run each command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. Run `uv run ${CLAUDE_SKILL_DIR}/page.py <command>`, with the path written exactly as here; when the path contains a space, wrap it in double quotes: `uv run "${CLAUDE_SKILL_DIR}/page.py" <command>`. When `uv` fails before the script starts (`uv` is not found, or `uv` prints its own error, for example a cache directory it cannot create), run `python` in place of `uv run`; when `python` is not found, run `python3`. An error the script prints is not a reason to switch, and neither is a denied command: follow "When a tool call is denied". The allow rule for a denied script command is the project rule `Bash(uv run *page.py*)` or `PowerShell(uv run *page.py*)` (`python` or `python3` in place of `uv run` when you ran it), not one with the path written out.

The build renders every diagram with Pele in Node to catch Mermaid errors. Without Node it still builds and prints a `WARN` line: the diagrams were not checked.

The allow rule for a denied Write or Edit of the content file is `Edit(./.mreq/how/**)`.

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it, with one allow rule for each. Use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`, for example `Bash(python -m unittest discover -s tests)`. Never merge two denied commands into one rule, and never suggest a broader rule. Then stop.

## Steps

1. **Confirm the question.**
   Say back, in your own words, not the user's:
   - **Question**: what the page will explain, and the kind of question (how it works, a walkthrough before a change, or a placement question).
   - **Scope**: the subsystem, flow, or files it covers.
   - **Out of scope**: what the page will leave out. Omit when none.
   - **Reader**: who the page is written for, from the style (see "Reader"). Omit when no style was given.

   With `--plain`, write the restatement in the reader's words too: name the scope by its features, not by files.

   Then ask one question (see "Asking the user"). When the first word is a `--` word that is not a style, ask the reader question from "Reader" with it, in the same call:
   - When the question can be read more than one way, give each reading as an option, the most likely one first, with its scope in the description. Picking a reading confirms it.
   - Otherwise, offer **Correct, go on** first, then **Correct, also cover <X>**, where X is the out-of-scope item the user most likely wants too. With nothing out of scope, offer **Stop** as the second option.

   Say in the question that the user can type a correction in the free-text answer. A correction means you read it wrong: restate again. Only a pick that confirms a reading moves on.

   Before the yes, read only what you need to name the scope (file and directory names). Do not explore the code, spawn explorers, or run `page.py`.

   Only an explicit request to skip this confirmation (for example "don't ask, just explain") skips it. Then pick the most likely reading and go on, and state it in the first sentence of the report and of the Overview, for example: "I read X as Y; ask again if you meant Z."

2. **Start from what the project already says.**
   Read the project's README, agent instruction files, and docs on the area the question touches. They say what the code should do, so you know what to look for. The code is what runs: where it disagrees with a doc, explain the code and report the gap under Gotchas.

3. **Size the question.**
   - **Simple**: one module, one utility, one function. Explore it yourself, then go to step 5.
   - **Complex**: a subsystem across several files, a cross-cutting feature, an architectural overview. Go to step 4.

   When in doubt, take the simple path.

4. **Explore in parallel (complex only).**
   Split the question into 2-4 distinct angles (for example: entry points and wiring, the core data flow, persistence and state, error paths). When you can spawn subagents, spawn one read-only explorer per angle in a single message. Each prompt holds only the question, that explorer's angle, the line "Reader: plain" when the style is `--plain`, and the instruction to read `EXPLORER.md` at its path in this skill's directory and report in its shape. Never paste the file into the prompt. Otherwise, work the angles yourself, one at a time, with notes in the shape `EXPLORER.md` gives. Then reconcile: merge overlaps, and settle a contradiction by reading the code yourself, not by picking one account.

5. **Plan the page.**
   Follow `WRITING.md` in this skill's directory and `MERMAID.md` in the `mreq-shared` directory (`../mreq-shared` from this skill's directory): pick the sections that apply and the diagram that answers each part of the question, then write each diagram's Mermaid source, its legend and its caption. Decide the diagrams before the prose: the prose walks the reader through them.

6. **Write the page.**
   1. Get the content file's path: `page.py new <topic-slug>`. It creates the output folder and stamps the name with the current time; never make up the time.
   2. Write the content file at that path in the format `WRITING.md` gives: the header lines, `---`, then the sections. Write only that. The build wraps it in `skeleton.html` and inlines Pele, so never read or copy the skeleton or the Pele bundle.
   3. Build the page: `page.py build <content file>`. It checks the page and every diagram, and writes `<same name>.html` beside the content file only when it prints `ok`. Fix every FAIL line in the content file with Edit (or Write for a rewrite) and build again. A FAIL line from Pele gives the line inside the Mermaid source. When the same Pele error is still there after 3 builds, stop: give the user Pele's error and the content file's absolute path, and ask once: **Simplify the diagram** (rewrite it as "Keep it readable" in `WRITING.md` says, then build up to 3 more times), **Use prose instead** (remove the diagram, explain that part in the text, and say so under Open Questions), or **Stop**. Between builds, change the content only with Edit or Write; never run `python`, a heredoc, `cd`, or any other script to generate or patch it. Never edit the built page: the next build overwrites it.

7. **Report.**
   Reply with exactly this shape, nothing else: the answer in at most 4 sentences (the gist of the Overview), with no lists or headings, starting with your interpretation when the user skipped the confirmation (see step 1); the page's absolute path; one question (see "Asking the user") with **Open it** (in the default browser) and **Don't open**, which says the user can type a follow-up in the free-text answer. The page is the explanation, so do not repeat it in the chat: give each sentence one point, never join clauses with a semicolon to fit more in, and list no inputs, cases or files (the page has them). With `--plain`, write the sentences in the reader's words too, as "Plain style" in `WRITING.md` says: no path in the code and no code name. When a build limit or anything else kept you from doing part of the request, say so in one of the 4 sentences. When the build printed a `WARN` line, say in one of the 4 sentences that the diagrams were not checked. Never go past 4 sentences: any other caveat, such as a layout you could not check, goes on the page under Open Questions. Open the page only when the user says so.

   A follow-up that asks a new question starts again at step 1. A follow-up that changes the page goes through step 6 again. Both end with this same reply. After a change to the page, the 4 sentences say what changed on the page, not what the new part explains; never list the added content. When a Write, Edit or command is denied before the page is built, reply with only the denied path or command and its allow rule (see "When a tool call is denied"), then stop. Do not answer the question in the chat.

## Guardrails

- Never start the analysis before the user confirms your reading of the question (step 1), unless they asked to skip it.
- Never write inside the project outside `.mreq/how/`: the page lives only there.
- Run no command other than `page.py`, and the one that opens the page when the user asks.
- Do not run or import the project's code: read it. When behavior is unclear, say so under Open Questions.
- Explain the code that runs, not what a doc describes; report the difference.
- With `--plain`, the page and the report hold no path, no `path:line`, no `<code class="ref">` and no code name the reader does not use themselves, but every claim on the page is still checked against the code.
- Name the gaps: whatever you could not trace goes under Open Questions.
