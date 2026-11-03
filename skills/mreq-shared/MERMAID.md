# Writing a diagram

The rules every mreq page shares for its Mermaid diagrams. The skill's own `WRITING.md` says which diagrams to draw, how to label them for its reader, and how busy one may be.

The examples in this file are in English. Write the diagrams in the language the skill's Language section picks: carry over what each example does, not its words.

## The figure

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

The caption is one line. It gives the diagram's bounds: where it starts and ends, what it leaves out, or which file it is drawn from. It does not repeat the heading.

The source is plain Mermaid text, not HTML: write `<br>`, `-->` and `&` as they are, never as `&lt;br&gt;` or `&amp;`. It must not hold `</script` or `<!--`. The page shows only the drawn diagram, not its source.

## Size

The canvas is about 820 px wide, and the build fails a diagram wider than 1100 px, because the page shrinks it until its labels are too small to read. Prefer `TD`; long arrow labels in an `LR` diagram make it wide fast. When a diagram is too wide, follow "Keep it readable" in the skill's `WRITING.md`.

## Colors

The page opens in the light theme and has a button for the dark theme. It colors nodes by class, in both themes. Colors work in `flowchart` and `stateDiagram-v2`.

- **Groups**: when the nodes fall into phases, layers or groups the reader cares about, give each group one color class: `blue`, `orange`, `purple`, `yellow`, `teal`, `tan`, `pink`. Write `class a,b,c teal`. Use groups only when they help the reader, and name each one in the legend. A `subgraph` already draws a boundary: do not color it as well.
- **Marks**: mark a node that needs the reader's attention: `primary` (the focus of the page, a blue border), `success` (a good end), `warning` (needs a person, or can go wrong), `danger` (an error or a bad end), `muted` (out of scope or optional, a dashed border). Write `class c danger`. A node can have a group color and a mark; the mark shows over the group color.
- Write no `classDef`, `style`, `linkStyle` or `%%{init}%%`: the page has the colors for every class, and fixed colors become unreadable in the dark theme. The build fails a diagram that has them.
- Use color for meaning only. The legend names each color the diagram uses.

Pele colors the other types itself. The page draws every mindmap branch and timeline period in one neutral color, because there the color only follows the order. Pie slices, sankey flows, journey actors and gitGraph branches keep Pele's colors, because there the color tells one item from another; their legend is Pele's own labels, so they need no `ul.legend`.

## Mermaid rules

Pele draws the diagrams. It reads Mermaid syntax, with these differences:

- **IDs and labels**: give nodes and states short ASCII IDs and put the text in the label: `pay{Payment OK?}`, `state "In review" as review`. A state diagram rejects non-ASCII IDs, so a label in another script always needs an ASCII ID.
- **Quotes**: wrap a label in double quotes when it holds `()`, `[]`, `{}`, `:`, `;`, `#` or `|`: `a["Order (awaiting payment)"]`.
- **Line breaks**: write `<br>` in a label. No other HTML works in labels. Pele wraps a long label by width and can split a word, and Chinese or Japanese words have no spaces to wrap at. When a label runs past about 12 characters of Chinese or Japanese, or 25 of English, break it yourself with `<br>` between two phrases.
- **Decision nodes**: keep the question short, about 3-5 words, such as "Payment OK?". A diamond grows in both width and height with its label, so a long question makes it far larger than the boxes around it. Put the detail in the boxes or on the arrows.
- **Conditions**: when a decision node draws the branch, label its arrows with the outcomes only, such as `Yes` and `No`. When an arrow with no decision node happens only in some conditions, end its label with the condition in brackets and quote the label: `|"User pays again [within 24 hours]"|`.
- **Shapes**: `[box]` for a step, a module or a service, `[(store)]` for a database, file or cache, `([pill])` for a person or an entry point, `{decision}` for a branch.
- **Edges**: `-->` for the main path or a call, `-.->` for optional, async or read-only, `==>` for the one path to stress.
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

Put the legend right above its figure, so the reader knows the colors before reading the diagram. Leave it out only when the diagram uses no color class and no line style besides the plain one. A `swatch` takes the same class names as the nodes, or `solid`, `dotted` and `thick` for the line styles `-->`, `-.->` and `==>` (a sequence diagram: `->>` is solid, `-->>` and `--)` are dotted). List only what the diagram uses. An item with no swatch, such as what a shape means, takes a whole row.
