# Writing the page

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
  2. **The legend**, as a `ul.legend` (see "The legend"). It goes right above the figure, so the reader knows the colors before reading the diagram. Leave it out only when the diagram uses no color class and no line style besides the plain one.
  3. **The figure**, with its one-line caption (see "Diagram figures").
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

## Diagram figures

Put each diagram in its own figure, written exactly like this:

```html
<figure class="diagram">
  <script type="text/x-mermaid">
flowchart TD
  cart[Cart] -->|User places the order| pay{Payment OK?}
  pay -->|Yes| ship[Awaiting shipment]
  pay -->|No| retry[Awaiting another payment]
  retry -->|"User pays again [within 24 hours]"| pay
  retry -->|24 hours pass| failed[Order failed]
  class cart,pay,retry teal
  class failed danger
  </script>
  <figcaption>From placing the order to shipment. Refunds are not drawn.</figcaption>
</figure>
```

The caption is one line. It gives the diagram's bounds: where it starts and ends, what it leaves out, or which file it is drawn from. It does not repeat the `<h2>`.

The source is plain Mermaid text, not HTML: write `<br>`, `-->` and `&` as they are, never as `&lt;br&gt;` or `&amp;`. It must not hold `</script` or `<!--`. The page shows only the drawn diagram, not its source.

## Labels and arrows

The diagram shows the subject in the words of the person who reads it, the reader.

- **Nodes**: label each node with what the reader sees or cares about, such as "Paying" or "In review, stock reserved". Keep variable, function and table names out of labels. Use them only when the reader works with that code, and then as they are written.
- **Arrows**: label each arrow with what happens, as the reader sees it happen, such as "User clicks Pay" or "Payment fails". Do not name the code that does it.
- **Conditions**: when a decision node draws the branch, label its arrows with the outcomes only, such as `Yes` and `No`. When an arrow with no decision node happens only in some conditions, end its label with the condition in brackets, in the reader's words, and quote the label: `|"User clicks Pay [when in stock]"|`. Use a decision node when the reader must see the question; use brackets when the condition is a detail of one step.
- **Decision nodes**: the question is short, about 3-5 words, such as "Payment OK?" or "Rice evenly colored?". A diamond grows in both width and height with its label, so a long question makes it far larger than the boxes around it. Put the detail in the boxes or on the arrows.
- **One arrow for one outcome**: when two causes end the same in the diagram, give them one label and one arrow.
- **Hidden values**: when a value that no label shows decides where a step goes, name the result in the label, such as "Stock check failed".

## Keep it readable

Aim for about 20 arrows or fewer in a diagram (a sequence: 6 participants, 15 messages), because a busier diagram is hard to read.

A diagram must also fit the page: the canvas is about 820 px wide, and the build fails a diagram wider than 1100 px, because the page shrinks it until its labels are too small to read. Prefer `TD`; long arrow labels in an `LR` diagram make it wide fast.

When a diagram is too busy or too wide, do these in order:

1. Give one node to the states or steps that act the same for the reader.
2. Leave out a detail the reader does not need, such as a call whose result changes nothing.
3. Leave out an arrow that every node has, such as "Cancel", and say it once in the caption.
4. Split the picture into an overview and zoom-ins, grouped in one section, each under its own `<h3>`.

When you leave something out, keep each node reachable by arrows from a start node, and keep at least one arrow out of each node that has a step out. Keep every node and arrow the request asks about. List what you left out under Assumptions.

## Colors

The page opens in the light theme and has a button for the dark theme. It colors nodes by class, in both themes. Colors work in `flowchart` and `stateDiagram-v2`.

Pele colors the other types itself. The page draws every mindmap branch and timeline period in one neutral color, because there the color only follows the order. Pie slices, sankey flows, journey actors and gitGraph branches keep Pele's colors, because there the color tells one item from another; their legend is Pele's own labels, so they need no `ul.legend`.

- **Phases**: when the nodes fall into phases or groups the reader cares about, give each phase one color class: `blue`, `orange`, `purple`, `yellow`, `teal`, `tan`, `pink`. Write `class a,b,c teal`. Use phases only when they help the reader, and name each one in the legend.
- **Marks**: mark a node that needs the reader's attention: `primary` (the focus of the request, a blue border), `success` (a good end), `warning` (needs a person, or can go wrong), `danger` (an error or a bad end), `muted` (out of scope or optional, a dashed border). Write `class c danger`. A node can have a phase color and a mark; the mark shows over the phase color.
- Write no `classDef`, `style`, `linkStyle` or `%%{init}%%`: the page has the colors for every class, and fixed colors become unreadable in the dark theme. The build fails a diagram that has them.
- Use color for meaning only. The legend names each color the diagram uses.

## Mermaid rules

Pele draws the diagrams. It reads Mermaid syntax, with these differences:

- **IDs and labels**: give nodes and states short ASCII IDs and put the text in the label: `pay{Payment OK?}`, `state "In review" as review`. A state diagram rejects non-ASCII IDs, so a label in another script always needs an ASCII ID.
- **Quotes**: wrap a label in double quotes when it holds `()`, `[]`, `{}`, `:`, `;`, `#` or `|`: `a["Order (awaiting payment)"]`.
- **Line breaks**: write `<br>` in a label. No other HTML works in labels. Pele wraps a long label by width and can split a word, and Chinese or Japanese words have no spaces to wrap at. When a label runs past about 12 characters of Chinese or Japanese, or 25 of English, break it yourself with `<br>` between two phrases.
- **Edges**: `-->` for the main path, `-.->` for optional or async, `==>` for the one path to stress.
- **Direction**: `TD` by default. `LR` only for a short chain with short labels. On a narrow screen Pele turns a wide diagram vertical on its own.
- **Sequence diagrams**: `->>` for a call, `-->>` for a reply, `--)` for an async message, `alt` / `else` / `end` for branches, `loop` for repeats, and `Note over A,B: text` for a phase heading all work.
- **Not supported**: `click` callbacks, `fa:` icons, `$$` math, ZenUML. Do not use them.

## The legend

```html
<ul class="legend">
  <li><span class="swatch teal"></span> Payment phase</li>
  <li><span class="swatch primary"></span> The step this page is about</li>
  <li><span class="swatch danger"></span> Order failed</li>
  <li><span class="swatch muted"></span> Out of scope</li>
  <li><span class="swatch"></span> Other steps</li>
  <li><span class="swatch solid"></span> Call</li>
  <li><span class="swatch dotted"></span> Reply, or a notice that waits for no reply</li>
  <li>A diamond is a decision; the words on its arrows are the outcomes.</li>
</ul>
```

A `swatch` takes the same class names as the nodes, or `solid`, `dotted` and `thick` for the line styles `-->`, `-.->` and `==>` (a sequence diagram: `->>` is solid, `-->>` and `--)` are dotted). List only what the diagram uses. An item with no swatch, such as what a shape means, takes a whole row.
