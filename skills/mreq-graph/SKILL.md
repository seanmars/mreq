---
name: mreq-graph
description: Turn the user's description into Mermaid diagrams on an offline single-page HTML, each with a legend for its colors and line styles, written to .mreq/graph/ under the session root. Pele (https://pele.run/) renders the diagrams, inlined in the page so it works with no network. Covers flowcharts, sequence, state, ER, class, gantt, timeline, mindmap and other Mermaid charts. Confirms its reading of the description with the user before drawing. Use for /mreq-graph.
disable-model-invocation: true
---

# mreq-graph

Run only when the user typed `/mreq-graph`. If you are reading this file on your own, stop and ask the user to run `/mreq-graph <description>`.

Turn the user's description into one or more Mermaid diagrams on a single offline HTML page. The page holds the diagrams and nothing else: each one has a legend and a one-line caption, and the assumptions close the page.

**Input**: A description of what to draw: a process, a system, a lifecycle, a schedule, a set of relations. It may point at files or code to draw from. Confirm your reading of it with the user before drawing (step 1).

**This is read-only on the project.** Write no code and no files in the project. The one write is the page, and it goes to `.mreq/graph/` under the session root (the directory the agent was started in).

## Language

Write and reply in the language the agent instruction files (`AGENTS.md`, `CLAUDE.md`, ...) set. When they set none, use the language the user writes in. A reply that only picks an option (`1`, `Accept`) or gives a path does not change it. Use that language in every message, from the first line to the report, including the short notes between tool calls, and on the page and in the diagram labels.

## Asking the user

When the `AskUserQuestion` tool is available, ask with it: up to 4 independent questions at once, the recommended option first and labelled "(Recommended)". Otherwise, ask in plain text as a numbered list, the recommended option first, and wait for the answer.

## The script

`${CLAUDE_SKILL_DIR}/page.py` builds and checks the page. `${CLAUDE_SKILL_DIR}` is this skill's directory; when it still reads as a variable, put the directory's absolute path in its place.

Run each command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. Run `uv run ${CLAUDE_SKILL_DIR}/page.py <command>`, with the path written exactly as here; when the path contains a space, wrap it in double quotes: `uv run "${CLAUDE_SKILL_DIR}/page.py" <command>`. When `uv` fails before the script starts (`uv` is not found, or `uv` prints its own error), run `python` in place of `uv run`; when `python` is not found, run `python3`. An error the script prints is not a reason to switch, and neither is a denied command: follow "When a tool call is denied". The allow rule for a denied script command is the project rule `Bash(uv run *page.py*)` or `PowerShell(uv run *page.py*)` (`python` or `python3` in place of `uv run` when you ran it), not one with the path written out.

The build renders every diagram with Pele in Node to catch Mermaid errors. Without Node it still builds and prints a `WARN` line: the diagrams were not checked.

The allow rule for a denied Write or Edit of the content file is `Edit(./.mreq/graph/**)`.

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it, with one allow rule for each. Use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`. Never merge two denied commands into one rule, and never suggest a broader rule. Then stop.

## Steps

1. **Confirm the request.**
   Say back, in your own words, not the user's:
   - **Subject**: what the diagrams will show.
   - **Diagrams**: each diagram you plan, with its Mermaid type (see "Choosing diagrams" in `WRITING.md`) and what it shows.
   - **Assumptions**: what the description leaves open and what you will choose. Omit when none.

   When the description can be read more than one way, or two diagram types fit, give each as an option, the most likely one first. Ask the user to confirm or correct it. A correction means you read it wrong: restate again. Only the user's yes moves on.

   Before the yes, read only what you need to name the subject: the files the user pointed at, by name. Do not draw, and do not run `page.py`.

   Only an explicit request to skip this confirmation (for example "don't ask, just draw") skips it. Then pick the most likely reading and go on, and state it in the first sentence of the report and as the first assumption on the page (see `WRITING.md`).

2. **Gather the facts.**
   The diagrams are for a reader: the person who reads the page and decides whether the picture is right. Draw in that reader's words (see "Labels and arrows" in `WRITING.md`).

   When the description points at files, code or documents, read them, and draw what they say. When code and a document disagree, draw the code and say so on the page. When the description alone is the source, draw only what it says and the assumptions the user confirmed. Do not invent steps, names or numbers: what is missing goes under Assumptions. When a diagram cannot be drawn without a fact that no source gives (for example, which side opens a link in a sequence diagram), pick the usual answer and list it under Assumptions.

3. **Plan the page.**
   Follow `WRITING.md` in this skill's directory: pick the diagrams and their types, then write each diagram's Mermaid source, then its legend and caption.

4. **Write the page.**
   1. Get the content file's path: `page.py new <topic-slug>`. It creates the output folder and stamps the name with the current time; never make up the time.
   2. Write the content file at that path in the format `WRITING.md` gives: the header lines, `---`, then the sections. Write only that. The build wraps it in `skeleton.html` and inlines Pele, so never read or copy the skeleton or `vendor/`.
   3. Build the page: `page.py build <content file>`. It checks the page and every diagram, and writes `<same name>.html` beside the content file only when it prints `ok`. Fix every FAIL line in the content file with Edit (or Write for a rewrite) and build again. A FAIL line from Pele gives the line inside the Mermaid source. When the same Pele error is still there after 3 builds, stop: give the user Pele's error and the content file's absolute path, and ask how to go on. Between builds, change the content only with Edit or Write; never run `python`, a heredoc, `cd`, or any other script to generate or patch it. Never edit the built page: the next build overwrites it.

5. **Report.**
   Reply with exactly this shape, nothing else:
   1. What the page shows, in at most 3 sentences, with no lists or headings. Start with your interpretation when the user skipped the confirmation (see step 1). When a diagram leaves out something the user may expect, say what in one of the sentences. When the build printed a `WARN` line, say in one of the sentences that the diagrams were not checked.
   2. The page's absolute path.
   3. One question offering to open it in the default browser.

   Do not repeat the page's captions or assumptions in the chat, and do not show the Mermaid source. Open the page only when the user says so.

   A follow-up that asks for a new subject starts again at step 1. A follow-up that changes the page goes through step 4 again; the 3 sentences then say what changed. When a Write, Edit or command is denied before the page is built, reply with only the denied path or command and its allow rule (see "When a tool call is denied"), then stop.

## Guardrails

- Never draw before the user confirms your reading of the request (step 1), unless they asked to skip it.
- Never write inside the project outside `.mreq/graph/`: the page lives only there.
- Run no command other than `page.py`, and the one that opens the page when the user asks.
- Do not run or import the project's code: read it.
- Draw only what the description or the sources say. Every assumption is on the page.
