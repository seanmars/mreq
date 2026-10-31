# Writing the page

## The content file

You write only the content; `page.py build` wraps it in `skeleton.html`, whose stylesheet, script and Content-Security-Policy reach the page unchanged. Never read, copy or edit the skeleton or the built page. The file starts with four header lines, then a line that is exactly `---`, then the sections:

```html
lang: zh-Hant-TW
title: How the CLI derives artifact status
question: How does the status command know each artifact's state?
meta: my-project · 2026-10-23
---
<section id="overview">
  <h2>Overview</h2>
  <p class="lede">...</p>
</section>
```

- `lang` is the language you answer in (`zh-Hant-TW`, `en`, ...); it also picks the language of the page's buttons.
- `title`, `question` (the user's question) and `meta` (project name and date) are plain text: the build escapes them, so write `<` and `&` as they are. `meta` may be empty.
- Everything after `---` is HTML and goes into the page as written, so escape `<`, `>` and `&` in the text there yourself. No `<html>`, `<head>`, `<body>`, `<meta>` or `<style>`: the skeleton has them. No `<script>` besides the diagram specs and no event handler attributes (`onclick=`, `onerror=`, ...): the page runs only the skeleton's script. Close every `<!--` and `<textarea>` you open: one left open swallows the page's script.

## Sections

Each section is a `<section>` with an `<h2>`; the page builds its table of contents from them. Use the ones that apply, in this order:

- **Overview** — one or two paragraphs: what this is, what it does, why it exists. Open with `<p class="lede">`. A reader who stops here can still decide whether to read on.
- **Key Concepts** — the types, services and abstractions the rest depends on, as a concept grid. Short definitions, not an inventory.
- **How It Works** — the core, and the longest section. What triggers it, what happens step by step, where data goes, where it branches. Lead with the diagram, then walk it in prose or a numbered step list.
- **Where Things Live** — a short file map: only what someone needs to start working here.
- **Gotchas** — non-obvious behavior, historical context, pitfalls, and every place the code disagrees with a spec. Skip it when there is nothing.
- **Open Questions** — what could not be traced. Skip it when there is nothing.

## Style

- Concrete over abstract: "`archive` calls `confirmDeletion()`", not "the command delegates to a helper".
- When something is complex, say why it is complex, not only what it does. When it is simple, do not pad it.
- Prose, not pseudocode. Cite `path:line` so the reader knows where to look; quote code only when a snippet is essential to the point.
- Use an analogy when one helps; never force one.
- Write in the language SKILL.md's Language section picks. Identifiers, paths and established technical terms stay as they are.

## Choosing diagrams

| The reader needs to see | Diagram |
| --- | --- |
| Which parts exist and what depends on what | architecture: `flow` with `groups` for layers or processes |
| Who calls whom, in what order, for one request or command | `sequence` |
| The lifecycle of one thing: its statuses and what moves it | state: `flow` with `state` nodes, `start` / `end`, and events on the edges |
| Branching logic | flowchart: `flow` with `decision` nodes |

A diagram has to explain something the prose would explain worse; skip it when prose covers the point. Keep each one to 12 nodes or fewer (a sequence: 6 participants, 14 messages). Split a bigger picture into an overview and a zoom-in. Add `steps` when order matters: the reader walks them with Previous / Next (or the arrow keys), and each step lights up its part of the diagram.

## Diagram specs

Put each spec in its own figure, written exactly like this, and the page draws it:

```html
<figure class="diagram">
  <script type="application/json">{ "type": "flow", ... }</script>
  <figcaption>What this diagram shows</figcaption>
</figure>
```

The JSON must be valid (double quotes, no trailing commas, no comments, no `NaN` or `Infinity`, and no number too large for the browser, such as `1e400`). Its strings are plain text, not HTML: write `>` and `&` as they are, never as `&gt;` or `&amp;`. Write `<` as `\u003c`: a raw `</script` or `<!--` ends the spec early in the browser, and the build fails on them.

### flow

```json
{
  "type": "flow",
  "groups": [{ "label": "CLI process", "cols": [0, 1], "rows": [0, 0] }],
  "nodes": [
    { "id": "cli", "label": "commander program", "col": 0, "row": 0, "note": "Parses argv and dispatches to a command.", "ref": "src/cli/index.ts:422" },
    { "id": "cmd", "label": "statusCommand", "col": 1, "row": 0 },
    { "id": "fs", "label": "change directory", "kind": "store", "col": 1, "row": 1 }
  ],
  "edges": [
    { "from": "cli", "to": "cmd", "label": "status --json" },
    { "from": "cmd", "to": "fs", "label": "reads files", "dashed": true }
  ],
  "steps": [
    { "title": "Dispatch", "text": "commander matches the subcommand.", "show": ["cli", "cli->cmd"] },
    { "title": "Derive status", "text": "Status comes from which files exist.", "show": ["cmd->fs"] }
  ]
}
```

- **Grid**: `col` and `row` count from 0 and are never negative. Each cell is 220 × 116 px and holds one node; two nodes in one cell is an error. A fractional value (`0.5`) centres a node between two cells.
- **Layout**: run the main path left to right (or top to bottom) in reading order. Keep a flow to 4 columns: wrap a longer path onto the next row, or split it into an overview and a zoom-in. Put a store below or beside what writes it, and external systems at the edges. An edge that would cross another node bends around it by itself; set `"bend": 60` (px, the sign picks the side) to override.
- **Groups**: `cols` and `rows` are inclusive `[first, last]` ranges, with `first <= last`. Use them for a layer, a process or a package boundary.
- **Node kinds**: `box` (the default: module, function, service), `store` (database, file, cache), `external` (outside the codebase), `actor` (a person or a calling tool), `decision` (a branch; label it as a question), `state`, `start`, `end`.
- **Labels**: a name, not a sentence. About 20 Latin, 10 CJK or 7 emoji a line (a `decision`: 17 Latin, 8 CJK or 5 emoji), three lines at most; `\n` forces a break, and a word never splits unless it is longer than a line. A `start` or `end` label sits below its circle: about 20 Latin or 10 CJK a line, two lines at most. The explanation goes in `note`, shown when the reader clicks the node or edge; `ref` adds a copyable `path:line`.
- **Edges**: `label` names what moves (a call, an event, data): about 22 Latin or 11 CJK a line, two lines at most; the detail goes in `note`. `"dashed": true` marks an async, optional or read-only link. In a state diagram the label is the event or condition.
- **Steps**: `show` lists node ids and `"from->to"` edges (one arrow); an edge lights its two ends with it.

### sequence

```json
{
  "type": "sequence",
  "participants": [
    { "id": "user", "label": "User", "kind": "actor" },
    { "id": "cmd", "label": "validate command", "ref": "src/commands/validate.ts" },
    { "id": "parser", "label": "spec parser" },
    { "id": "fs", "label": "file system", "kind": "store" }
  ],
  "messages": [
    { "from": "user", "to": "cmd", "label": "validate \u003cname>" },
    { "divider": "Read" },
    { "from": "cmd", "to": "fs", "label": "read specs/" },
    { "from": "fs", "to": "cmd", "label": "spec files", "reply": true },
    { "divider": "Check" },
    { "from": "cmd", "to": "parser", "label": "parse requirements" },
    { "from": "parser", "to": "cmd", "label": "issues", "reply": true, "note": "Any ERROR fails the run." }
  ]
}
```

- Participants are columns, left to right in the order a request first reaches them.
- Each message is a row. `"reply": true` draws a dashed return; `from` equal to `to` is a self-call; `{ "divider": "..." }` labels a phase.
- Every message is a step on its own, with its `note` as the step text. Set `"steps": false` to turn that off.

### Hand-drawn SVG

When neither type fits, put an `<svg viewBox="...">` straight into the figure, with no `<script>`. Use the page's classes so it matches: `<g class="node k-store">` around a shape and its `<text>`, `<g class="edge">` around a `<path class="line">`. Add `data-key`, `data-title` and `data-note` to a group to make it clickable. Nothing lays this out for you, so check every coordinate.

## Components

```html
<section id="overview">
  <h2>Overview</h2>
  <p class="lede">The answer in one paragraph.</p>
</section>

<dl class="concepts">
  <div><dt>Artifact graph <code class="ref">src/core/artifact-graph/</code></dt><dd>What it is, in one or two sentences.</dd></div>
</dl>

<ol class="steps">
  <li><strong>Resolve the root.</strong> Walk up to the nearest directory holding the project folder. <code class="ref">src/core/root-selection.ts:12</code></li>
</ol>

<table>
  <tr><th>Path</th><th>What lives there</th></tr>
  <tr><td><code class="ref">src/commands/</code></td><td>One file per command body.</td></tr>
</table>

<aside class="callout warn"><strong>Title</strong><p>A gotcha.</p></aside>
<aside class="callout open"><strong>Title</strong><p>An open question.</p></aside>
<aside class="callout note"><strong>Title</strong><p>A side note.</p></aside>

<details><summary>Deep dive: ...</summary><p>Detail most readers can skip.</p></details>
```

A `<code class="ref">` copies its text when clicked: use it for every path and `path:line`, and plain `<code>` for identifiers.

## Before reporting

`page.py build` checks the page before it writes it. It fails on a missing header value, a whole page pasted in as content, an unknown node id, two nodes in one cell, an unknown node kind, a label too long for three lines (two for an edge, `start` or `end`), a negative `col` or `row`, a group range with `first > last`, a `show` key with two arrows, a field of the wrong type, a spec outside its figure, invalid JSON (`NaN`, `Infinity` and numbers such as `1e400` too), `</script` or `<!--` or an HTML entity in a spec, a `<meta>` tag, a `<script>` outside a spec, an event handler attribute, a `<!--` or `<textarea>` left open, anything loaded from outside the file, and a file outside the temp directory. The checks for outside loads, scripts and event handlers only catch common mistakes: the skeleton's Content-Security-Policy is what blocks them. Fix every FAIL line in the content file and build again. It cannot judge the writing, so also confirm that every claim about the code carries a `path` or `path:line`.
