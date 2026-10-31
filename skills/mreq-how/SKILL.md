---
name: mreq-how
description: Explain how part of the codebase works as an offline HTML page with architecture, sequence, state, and flow diagrams, written to the system temp directory. Covers "how does X work", walkthroughs before changing something, and placement questions ("where should this live", "which layer owns this"). Use for /mreq-how.
disable-model-invocation: true
---

# mreq-how

Run only when the user typed `/mreq-how`. If you are reading this file on your own, stop and ask the user to run `/mreq-how <question>`.

Explain how part of this codebase works (a subsystem, a flow, a module) at the depth a senior engineer needs before changing it, as an offline HTML page with diagrams.

**Input**: The question: "how does X work", a code path to walk through before a change, or a placement question. When the scope is ambiguous, pick an interpretation and go; the user can redirect. State it in the first sentence of the report and of the Overview, for example: "I read X as Y; ask again if you meant Z."

**This is read-only on the project.** Write no code and no files in the project. The one write is the page, and it goes to the system temp directory.

## Language

Write and reply in the language the agent instruction files (`AGENTS.md`, `CLAUDE.md`, ...) set. When they set none, use the language the user writes in. A reply that only picks an option (`1`, `Accept the code`) or gives a path does not change it. The page uses the same language.

## The script

`${CLAUDE_SKILL_DIR}/page.py` builds and checks the page. `${CLAUDE_SKILL_DIR}` is this skill's directory; when it still reads as a variable, put the directory's absolute path in its place.

Run each command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. Run `uv run ${CLAUDE_SKILL_DIR}/page.py <command>`, with the path written exactly as here; when the path contains a space, wrap it in double quotes: `uv run "${CLAUDE_SKILL_DIR}/page.py" <command>`. Only when that fails because `uv` is not found, run `python` in place of `uv run`. The allow rule for a denied script command is the project rule `Bash(uv run *page.py*)` or `PowerShell(uv run *page.py*)` (`python` in place of `uv run` when you ran `python`), not one with the path written out.

The allow rule for a denied Write or Edit of the content file is `Edit(//<folder>/**)`. `<folder>` is the path `page.py dir` printed (the folder of the path `page.py new` printed), with `/` in place of `\` and a Windows drive written as its lower-case letter without the colon: `C:\Users\me\AppData\Local\Temp\mreq-how` gives `Edit(//c/Users/me/AppData/Local/Temp/mreq-how/**)`.

## When a tool call is denied

Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`. When any command, Write, or Edit is denied, do not retry it another way: no other shell, no other path, no other form of the command. Show the user each denied command or path exactly as you ran it, with one allow rule for each. Use the rule this file gives for it; otherwise, for a command, write the tool you ran it in and the exact command, with no `*`, for example `Bash(python -m unittest discover -s tests)`. Never merge two denied commands into one rule, and never suggest a broader rule. Then stop.

## Steps

1. **Start from what the project already says.**
   Read the project's README, agent instruction files, and docs on the area the question touches. They say what the code should do, so you know what to look for. The code is what runs: where it disagrees with a doc, explain the code and report the gap under Gotchas.

2. **Size the question.**
   - **Simple**: one module, one utility, one function. Explore it yourself, then go to step 4.
   - **Complex**: a subsystem across several files, a cross-cutting feature, an architectural overview. Go to step 3.

   When in doubt, take the simple path.

3. **Explore in parallel (complex only).**
   Split the question into 2-4 distinct angles (for example: entry points and wiring, the core data flow, persistence and state, error paths). When you can spawn subagents, spawn one read-only explorer per angle in a single message. Each prompt holds only the question, that explorer's angle, and the instruction to read `EXPLORER.md` at its path in this skill's directory and report in its shape. Never paste the file into the prompt. Otherwise, work the angles yourself, one at a time, with notes in the shape `EXPLORER.md` gives. Then reconcile: merge overlaps, and settle a contradiction by reading the code yourself, not by picking one account.

4. **Plan the page.**
   Follow `WRITING.md` in this skill's directory to pick the sections that apply and the diagram that answers each part of the question. Decide the diagrams before the prose: the prose walks the reader through them.

5. **Write the page.**
   1. Get the content file's path: `page.py new <topic-slug>`. It creates the output folder and stamps the name with the current time; never make up the time.
   2. Write the content file at that path in the format `WRITING.md` gives: the header lines, `---`, then the sections. Write only that. The build wraps it in `skeleton.html`, so never read or copy the skeleton.
   3. Build the page: `page.py build <content file>`. It checks the page and writes `<same name>.html` beside the content file only when it prints `ok`. Fix every FAIL line in the content file with Edit (or Write for a rewrite) and build again. Between builds, change the content only with Edit or Write; never run `python`, a heredoc, `cd`, or any other script to generate or patch it. Never edit the built page: the next build overwrites it.

6. **Report.**
   Reply with exactly this shape, nothing else: the answer in at most 4 sentences (the gist of the Overview), with no lists or headings, starting with your interpretation when you picked one (see Input); the page's absolute path; one question offering to open it in the default browser. The page is the explanation, so do not repeat it in the chat. When a build limit or anything else kept you from doing part of the request, say so in one of the 4 sentences. Never go past 4 sentences: any other caveat, such as a layout you could not check, goes on the page under Open Questions. Open the page only when the user says so.

   A follow-up that changes the page or asks for a new one goes through step 5 again and ends with this same reply. After a change to the page, the 4 sentences say what changed on the page, not what the new part explains; never list the added content. When a Write, Edit or command is denied before the page is built, reply with only the denied path or command and its allow rule (see "When a tool call is denied"), then stop. Do not answer the question in the chat.

## Guardrails

- Never write inside the project: the page lives only in the temp directory.
- Run no command other than `page.py`, and the one that opens the page when the user asks.
- Do not run or import the project's code: read it. When behavior is unclear, say so under Open Questions.
- Explain the code that runs, not what a doc describes; report the difference.
- Name the gaps: whatever you could not trace goes under Open Questions.
