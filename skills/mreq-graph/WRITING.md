# Writing the page

## The content file

You write only the content. `page.py build` wraps it in `skeleton.html` and inlines the Pele bundle, so the page draws its diagrams offline. Never read, copy or edit the skeleton, the bundle, or the built page. The file starts with four header lines, then a line that is exactly `---`, then the sections:

```html
lang: zh-Hant-TW
title: 訂單狀態的生命週期
request: 畫出訂單從建立到完成或取消的狀態變化
meta: 2026-11-02
---
<section id="overview">
  <h2>總覽</h2>
  <p class="lede">...</p>
</section>
```

- `lang` is the language you answer in (`zh-Hant-TW`, `en`, ...). It also picks the language of the page's own labels.
- `title`, `request` (the user's description, shortened to one sentence) and `meta` (the date, as `2026-11-02`; add ` · <project name>` only when the diagrams are about that project) are plain text: the build escapes them, so write `<` and `&` as they are. `meta` may be empty.
- Everything after `---` is HTML and goes into the page as written, so escape `<`, `>` and `&` in the text there yourself. No `<html>`, `<head>`, `<body>`, `<meta>` or `<style>`: the skeleton has them. No `<script>` besides the Mermaid sources, no event handler attributes (`onclick=`, ...), and nothing loaded from outside the file (`<img src="https://...">`, ...). Close every `<!--` and `<textarea>` you open.

## Sections

Each section is a `<section id="...">` with an `<h2>`. The page builds its table of contents from the `<h2>` headings only. Use the sections that apply, in this order:

- **Overview** (`id="overview"`): when the user skipped the confirmation, open with a `<div class="callout note">` that states your reading of the request. Then a `<p class="lede">`: what the diagrams show and the one thing to take from them. A reader who stops here knows the answer.
- **One section per diagram** (`id` in kebab-case, such as `id="signup-flow"`), in this order:
  1. An `<h2>` that names what the diagram shows.
  2. **The legend**: what each color, line style and shape means, as a `ul.legend` (see Components), with no heading. It goes right above the figure, so the reader knows the colors before reading the diagram, and a tall diagram does not push it off the screen. List only what the diagram uses.
  3. The figure.
  4. **Walkthrough**: an `<h3>`, then the path through the diagram, in order, as an `ol.steps` list. One step is one node, transition or message group. Use the labels as they appear in the diagram, so the reader can find each one.
- **Key Points** (`id="key-points"`): 2-5 conclusions or rules the diagrams show, as a `<ul>`. Skip when the walkthroughs already say them.
- **Assumptions** (`id="assumptions"`): one `callout warn` with a `<ul>`: what the request left open and what you chose, each fact you picked that no source gives, and each detail or step you left out of a diagram (see "Keep it readable"). Skip when there is nothing.

## Style

- Short sentences, one idea each. Active voice. One term for one concept: the term the diagram uses.
- Concrete over abstract: "付款失敗時訂單回到 `待付款`", not "the system handles errors".
- Do not repeat the diagram as prose. The text says what the diagram cannot: why, under what condition, what it means.
- Write in the language SKILL.md's Language section picks. Identifiers and established technical terms stay as they are.

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
flowchart LR
  cart[購物車] -->|使用者送出訂單| pay{付款成功?}
  pay -->|是| ship[等待出貨]
  pay -->|否| retry[等待重新付款]
  retry -->|"使用者重新付款 [24 小時內]"| pay
  retry -->|超過 24 小時| failed[訂單失敗]
  class cart,pay,retry teal
  class failed danger
  </script>
  <figcaption>What this diagram shows, in one sentence</figcaption>
</figure>
```

The source is plain Mermaid text, not HTML: write `<br>`, `-->` and `&` as they are, never as `&lt;br&gt;` or `&amp;`. It must not hold `</script` or `<!--`. The page shows only the drawn diagram, not its source.

## Labels and arrows

The diagram shows the subject in the words of the person who reads it, the reader.

- **Nodes**: label each node with what the reader sees or cares about, such as "付款中" or "等待審核, 已鎖定庫存". Keep variable, function and table names out of labels. Use them only when the reader works with that code, and then as they are written.
- **Arrows**: label each arrow with what happens, as the reader sees it happen, such as "使用者按下付款" or "付款失敗". Do not name the code that does it.
- **Conditions**: when a decision node draws the branch, label its arrows with the outcomes only, such as `是` and `否`. When an arrow with no decision node happens only in some conditions, end its label with the condition in brackets, in the reader's words, and quote the label: `|"使用者按下付款 [庫存足夠時]"|`. Use a decision node when the reader must see the question; use brackets when the condition is a detail of one step.
- **One arrow for one outcome**: when two causes end the same in the diagram, give them one label and one arrow.
- **Hidden values**: when a value that no label shows decides where a step goes, name the result in the label, such as "庫存查詢失敗".

## Keep it readable

Aim for about 20 arrows or fewer in a diagram (a sequence: 6 participants, 15 messages), because a busier diagram is hard to read. When a diagram is too busy, do these in order:

A diagram must also fit the page: the canvas is about 820 px wide, and the build fails a diagram wider than 1100 px, because the page shrinks it until its labels are too small to read. Prefer `TD`; long arrow labels in an `LR` diagram make it wide fast.

1. Give one node to the states or steps that act the same for the reader.
2. Leave out a detail the reader does not need, such as a call whose result changes nothing.
3. Leave out an arrow that every node has, such as "取消", and say it once in the prose.
4. Split the picture into an overview and a zoom-in, each in its own section.

When you leave something out, keep each node reachable by arrows from a start node, and keep at least one arrow out of each node that has a step out. Keep every node and arrow the request asks about. List what you left out under Assumptions.

## Colors

The page opens in the light theme and has a button for the dark theme. It colors nodes by class, in both themes. Colors work in `flowchart` and `stateDiagram-v2`.

- **Phases**: when the nodes fall into phases or groups the reader cares about, give each phase one color class: `blue`, `orange`, `purple`, `yellow`, `teal`, `tan`, `pink`. Write `class a,b,c teal`. Use phases only when they help the reader, and name each one in the legend.
- **Marks**: mark a node that needs the reader's attention: `primary` (the focus of the request, a blue border), `success` (a good end), `warning` (needs a person, or can go wrong), `danger` (an error or a bad end), `muted` (out of scope or optional, a dashed border). Write `class c danger`. A node can have a phase color and a mark; the mark shows over the phase color.
- Write no `classDef`, `style`, `linkStyle` or `%%{init}%%`: the page has the colors for every class, and fixed colors become unreadable in the dark theme. The build fails a diagram that has them.
- Use color for meaning only. The legend names each color the diagram uses.

## Mermaid rules

Pele draws the diagrams. It reads Mermaid syntax, with these differences:

- **IDs and labels**: give nodes and states short ASCII IDs and put the text in the label: `pay{付款成功?}`, `state "審核中" as review`. A state diagram rejects non-ASCII IDs.
- **Quotes**: wrap a label in double quotes when it holds `()`, `[]`, `{}`, `:`, `;`, `#` or `|`: `a["訂單 (待付款)"]`.
- **Line breaks**: write `<br>` in a label. No other HTML works in labels.
- **Edges**: `-->` for the main path, `-.->` for optional or async, `==>` for the one path to stress.
- **Direction**: `TD` by default. `LR` only for a short chain with short labels. On a narrow screen Pele turns a wide diagram vertical on its own.
- **Sequence diagrams**: `->>` for a call, `-->>` for a reply, `--)` for an async message, `alt` / `else` / `end` for branches, `loop` for repeats, and `Note over A,B: text` for a phase heading all work.
- **Not supported**: `click` callbacks, `fa:` icons, `$$` math, ZenUML. Do not use them.

## Components

```html
<ul class="legend">
  <li><span class="swatch teal"></span> 付款階段</li>
  <li><span class="swatch primary"></span> 這次要討論的步驟</li>
  <li><span class="swatch danger"></span> 訂單失敗</li>
  <li><span class="swatch muted"></span> 不在這次範圍內</li>
  <li><span class="swatch"></span> 一般步驟</li>
  <li><span class="swatch solid"></span> 呼叫 (實線)</li>
  <li><span class="swatch dotted"></span> 回應或非同步 (虛線)</li>
  <li>菱形是判斷點, 箭頭上的文字是判斷結果.</li>
</ul>

<ol class="steps">
  <li><strong>建立訂單</strong>: 使用者送出購物車.</li>
</ol>

<div class="callout warn"><strong>假設</strong><ul>
  <li>描述沒有提到退款, 所以圖中沒有畫退款.</li>
</ul></div>
```

A `swatch` takes the same class names as the nodes, or `solid`, `dotted` and `thick` for the line styles `-->`, `-.->` and `==>` (a sequence diagram: `->>` is solid, `-->>` and `--)` are dotted). An item with no swatch, such as what a shape means, takes a whole row. Also available: `<div class="callout note">` (a fact to keep in mind), `<div class="callout tip">` (advice), `<table>`, `<code>`.
