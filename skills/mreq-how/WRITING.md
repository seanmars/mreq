# Writing the page

Read this file and `MERMAID.md` in the `mreq-shared` directory (`../mreq-shared` from this skill's directory). This file says what goes on the page; `MERMAID.md` says how to write each diagram figure, its colors and its legend.

## The content file

You write only the content. `page.py build` wraps it in `skeleton.html` and inlines the Pele bundle, so the page draws its diagrams offline. Never read, copy or edit the skeleton, the bundle, or the built page. The file starts with four header lines, then a line that is exactly `---`, then the sections:

```html
lang: en
title: How the CLI derives artifact status
question: How does the status command know each artifact's state?
meta: 2026-11-03 · my-project
---
<section id="overview">
  <h2>Overview</h2>
  <p class="lede">...</p>
</section>
```

- `lang` is the language you answer in (`zh-Hant-TW`, `en`, ...). It also picks the language of the page's own labels.
- `title`, `question` (the user's question, shortened to one sentence) and `meta` (the date, as `2026-11-03`, then ` · <project name>`) are plain text: the build escapes them, so write `<` and `&` as they are. `meta` may be empty.
- Everything after `---` is HTML and goes into the page as written, so escape `<`, `>` and `&` in the text there yourself. No `<html>`, `<head>`, `<body>`, `<meta>` or `<style>`: the skeleton has them. No `<script>` besides the Mermaid sources, no event handler attributes (`onclick=`, ...), and nothing loaded from outside the file (`<img src="https://...">`, ...). Close every `<!--` and `<textarea>` you open.

The examples in this file are in English. Write the page in the language SKILL.md's Language section picks: carry over what each example does, not its words. Identifiers, paths and established technical terms stay as they are.

The rules below are for the default reader, an engineer. With `--plain`, "Plain style" at the end of this file overrides them where the two differ.

## The page

After `---` write only `<section>` elements. Give each one an `id` in kebab-case, such as `id="how-it-works"`, and an `<h2>`. Use the sections that apply, in this order:

- **Overview** (`id="overview"`): one or two paragraphs: what this is, what it does, why it exists. Open with `<p class="lede">`. A reader who stops here can still decide whether to read on. When the user skipped the confirmation, its first sentence states your reading of the question.
- **Key Concepts** (`id="key-concepts"`): the types, services and abstractions the rest depends on, as a concept grid. Short definitions, not an inventory.
- **How It Works** (`id="how-it-works"`): the core, and the longest section. What triggers it, what happens step by step, where data goes, where it branches. Lead with the diagram (its legend, then its figure), then walk it in prose or an `ol.steps`. When it has two or more parts, such as an overview and its zoom-ins, give each part its own `<h3>`, then its diagram and its walk.
- **Where Things Live** (`id="where-things-live"`): a short file map: only what someone needs to start working here.
- **Gotchas** (`id="gotchas"`): non-obvious behavior, historical context, pitfalls, and every place the code disagrees with a doc. Skip it when there is nothing.
- **Open Questions** (`id="open-questions"`): what you could not trace, and each detail you left out of a diagram (see "Keep it readable"). Skip it when there is nothing.

A contents panel on the left lists every section's `<h2>`, with the `<h3>` inside it one level down, and jumps to each. Headings are its entries, so keep each one short and different from the others.

## Style

- Concrete over abstract: "`archive` calls `confirmDeletion()`", not "the command delegates to a helper".
- When something is complex, say why it is complex, not only what it does. When it is simple, do not pad it.
- Prose, not pseudocode. Cite `path:line` so the reader knows where to look; quote code only when a snippet is essential to the point.
- Use an analogy when one helps; never force one.
- One term for one concept: the term the code uses, or the term the diagram uses.

## Choosing diagrams

| The reader needs to see | Mermaid type |
| --- | --- |
| Which parts exist and what depends on what | `flowchart` with `subgraph` for each layer, process or package |
| Who calls whom, in what order, for one request or command | `sequenceDiagram` |
| The lifecycle of one thing: its statuses and what moves it | `stateDiagram-v2` |
| Branching logic | `flowchart` with `{decision}` nodes |
| Types, fields and inheritance | `classDiagram` |
| Tables or records and their relations | `erDiagram` |

A diagram has to explain something the prose would explain worse; skip it when prose covers the point. A page may have no diagram. Pick the type that answers the part of the question with the fewest elements. Add a second diagram only when it shows something the first cannot.

Walk each diagram in the text right after it: the prose or the `ol.steps` names the nodes as the diagram labels them, in the order the arrows go.

## Labels and arrows

The reader is an engineer who is about to work in this code.

- **Nodes**: label a node with the name of what it is in the code: a module, a function, a type, a store, as written, such as `statusCommand` or `artifact-graph`. When the name says little, add what it does after a `<br>`. A `path:line` goes in the text, not in the label.
- **Arrows**: label each arrow with what moves (a call, an event, data), such as "reads", "status --json" or "emits change". In a state diagram the label is the event or condition.
- **Conditions**: name the condition as the code checks it, such as `[on timeout]` or "Cache hit?" (see "Mermaid rules" in `MERMAID.md`).
- **One arrow for one outcome**: when two causes end the same in the diagram, give them one label and one arrow.

## Keep it readable

Aim for about 12 nodes or fewer in a diagram (a sequence: 6 participants, 14 messages), because a busier diagram is hard to read. A diagram must also fit the page (see "Size" in `MERMAID.md`).

When a diagram is too busy or too wide, do these in order:

1. Give one node to the parts that act the same for this question.
2. Leave out a detail the question does not need, such as a call whose result changes nothing.
3. Leave out an arrow that every node has, such as "logs", and say it once in the caption.
4. Split the picture into an overview and zoom-ins, each under its own `<h3>`.

When you leave something out, keep each node reachable by arrows from a start node. Keep every node and arrow the question asks about. List what you left out under Open Questions.

## Components

```html
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

<pre><code>a short snippet, only when it is essential</code></pre>
```

A `<code class="ref">` copies its text when clicked: use it for every path and `path:line`, and plain `<code>` for identifiers. Every claim about the code carries a `path` or `path:line`: the build cannot check that, so check it yourself before the build.

## Plain style (`--plain`)

The reader knows the product by its features, such as a planner or a PM, and does not read code. They want to know what the feature does, when, under which conditions, and with which values: not where the code is. These rules override the ones above.

### Words

- **Reader words**: name each thing by what the reader calls it. Take the names from the README, the docs, the text the user sees in the product, and the settings or data the reader edits. When a part has a name only in the code, say what it does, such as "the part that checks the stock". Never make up a product name.
- **No code**: write no path, no `path:line`, no `<code class="ref">`, and no function, class, variable, file or table name. One exception: a name the reader uses themselves, such as a setting they edit or a data column they fill in, is a reader word. Write it as they see it, in plain `<code>`.
- **Values and conditions**: give the concrete values and conditions as the reader meets them: limits, timers, chances, costs, triggers, and what happens at each edge, such as "after 3 failed tries, the account locks for 10 minutes". Say where the reader changes a value when they can change it themselves.
- **No jargon**: no "call", "return", "null", "async", "cache" or "thread". Say what the reader sees happen, such as "the server checks", "it waits", "the saved copy".

### Sections

Use these sections, in this order, with their headings in the reader's words:

- **Overview** (`id="overview"`): as above, in the reader's words.
- **Key Terms** (`id="key-terms"`): the feature terms the rest of the page uses, as a concept grid. Each `<dt>` holds the term only, with no `<code class="ref">`.
- **How It Works** (`id="how-it-works"`): as above, but the steps follow what the user or the product does, not the code's calls. An `ol.steps` item ends with no reference.
- **Rules and Values** (`id="rules-and-values"`): a `<table>` of the rules, values and conditions the reader may want to check or change. Skip it when there are none.
- **Things to Know** (`id="things-to-know"`): behavior the reader would not expect, and every place the product works differently from what a doc says. Skip it when there is nothing.
- **Open Questions** (`id="open-questions"`): as above. Name what you could not confirm, in the reader's words.

Leave out **Where Things Live**.

### Diagrams

- Use `flowchart`, `stateDiagram-v2` or `sequenceDiagram`. Do not use `classDiagram` or `erDiagram`: they show code, not the product.
- In a `sequenceDiagram`, each participant is someone or something the reader knows, such as Player, Game server or Payment provider, not a module.
- **Nodes**: label each node with what the reader sees or cares about, such as "Waiting for payment".
- **Arrows**: label each arrow with what happens, as the reader sees it happen, such as "Player taps Buy" or "Payment fails". Do not name the code that does it.
- **Conditions**: write a condition in the reader's words, such as `[when in stock]`.

### Checking

The page shows no path, but every claim still comes from the code. Check each claim against the code before the build, as above. Then leave the path out of the page.
