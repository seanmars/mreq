# Writing the page

Read this file and `MERMAID.md` in the `mreq-shared` directory (`../mreq-shared` from this skill's directory). This file says what goes on the page; `MERMAID.md` says how to write each diagram figure, its colors and its legend.

## The content file

You write only the content. `page.py build` wraps it in `skeleton.html` and inlines the Pele bundle, so the page draws its diagrams offline. Never read, copy or edit the skeleton, the bundle, or the built page. The file starts with four header lines, then a line that is exactly `---`, then the sections:

```html
lang: en
title: The lifecycle of an order
request: Draw how an order moves from creation to completion or cancellation
meta: 2026-11-02
---
<section id="order-states">
  <h2>Order statuses</h2>
  <ul class="legend">...</ul>
  <figure class="diagram">...</figure>
</section>
```

- `lang` is the language you answer in (`zh-Hant-TW`, `en`, ...). It also picks the language of the page's own labels.
- `title`, `request` (the user's description, shortened to one sentence) and `meta` (the date, as `2026-11-02`; add ` · <project name>` only when the diagrams are about that project) are plain text: the build escapes them, so write `<` and `&` as they are. `meta` may be empty.
- Everything after `---` is HTML and goes into the page as written, so escape `<`, `>` and `&` in the text there yourself. No `<html>`, `<head>`, `<body>`, `<meta>` or `<style>`: the skeleton has them. No `<script>` besides the Mermaid sources, no event handler attributes (`onclick=`, ...), and nothing loaded from outside the file (`<img src="https://...">`, ...). Close every `<!--` and `<textarea>` you open.

The examples in this file are in English. Write the page in the language SKILL.md's Language section picks: carry over what each example does, not its words.

## The page

The page holds the diagrams and nothing else. After `---` write only these sections, in this order:

- **One section per diagram**: `<section id="...">` with an `id` in kebab-case, such as `id="signup-flow"`, holding:
  1. An `<h2>` that names what the diagram shows.
  2. **The legend**, as a `ul.legend` (see "The legend" in `MERMAID.md`).
  3. **The figure**, with its one-line caption (see "The figure" in `MERMAID.md`).
- **A section for a group of diagrams**: when two or more diagrams belong together, such as an overview and its zoom-ins, put them in one section. Its `<h2>` names the group; each diagram follows under its own `<h3>`, which names what that diagram shows, then its legend and figure.
- **Assumptions** (`id="assumptions"`), last: an `<h2>` that names both kinds of item, such as "Assumptions and omissions", then a `<ul>`: what the request left open and what you chose, each fact you picked that no source gives, and each detail or step you left out of a diagram (see "Keep it readable"). When the user skipped the confirmation, the first item states your reading of the request. Skip the section when there is nothing.

A contents panel on the left lists every section's `<h2>`, with the `<h3>` inside it one level down, and jumps to each. Headings are its entries, so keep each one short and different from the others.

Write no other text: no introduction, no walkthrough, no summary, no notes beside a diagram. What the reader needs to read a diagram goes into its labels, its legend or its caption.

Captions, legend items and assumptions are short and plain, in the reader's words. One term for one concept: the term the diagram uses.

## Choosing diagrams

| The reader needs to see | Mermaid type |
| --- | --- |
| Steps of a process, with branches | `flowchart` with `{decision}` nodes |
| Parts of a system and how they connect | `flowchart` with `subgraph` for each layer or boundary |
| Who calls whom, in what order | `sequenceDiagram` |
| The statuses of one thing and what moves it | `stateDiagram-v2` |
| Entities and their relations | `erDiagram` |
| Types, fields and inheritance | `classDiagram` |
| Work over dates, with dependencies | `gantt` |
| Events in order over time | `timeline` |
| Ideas broken into sub-ideas | `mindmap` |
| Shares of a whole | `pie` |
| Items placed on two axes (effort and value, ...) | `quadrantChart` |
| Values over a series (months, versions, ...) | `xychart` |
| Quantities flowing between stages | `sankey` |
| A user's steps and how each one feels | `journey` |
| Branches and merges | `gitGraph` |

Pick the type that answers the request with the fewest elements. Add a second diagram only when it shows something the first cannot.

## Labels and arrows

The diagram shows the subject in the words of the person who reads it, the reader.

- **Nodes**: label each node with what the reader sees or cares about, such as "Paying" or "In review, stock reserved". Keep variable, function and table names out of labels. Use them only when the reader works with that code, and then as they are written.
- **Arrows**: label each arrow with what happens, as the reader sees it happen, such as "User clicks Pay" or "Payment fails". Do not name the code that does it.
- **Conditions**: write a condition in the reader's words, such as `[when in stock]`. Use a decision node when the reader must see the question; use brackets when the condition is a detail of one step (see "Mermaid rules" in `MERMAID.md`).
- **One arrow for one outcome**: when two causes end the same in the diagram, give them one label and one arrow.
- **Hidden values**: when a value that no label shows decides where a step goes, name the result in the label, such as "Stock check failed".

## Keep it readable

Aim for about 20 arrows or fewer in a diagram (a sequence: 6 participants, 15 messages), because a busier diagram is hard to read. A diagram must also fit the page (see "Size" in `MERMAID.md`).

When a diagram is too busy or too wide, do these in order:

1. Give one node to the states or steps that act the same for the reader.
2. Leave out a detail the reader does not need, such as a call whose result changes nothing.
3. Leave out an arrow that every node has, such as "Cancel", and say it once in the caption.
4. Split the picture into an overview and zoom-ins, grouped in one section, each under its own `<h3>`.

When you leave something out, keep each node reachable by arrows from a start node, and keep at least one arrow out of each node that has a step out. Keep every node and arrow the request asks about. List what you left out under Assumptions.
