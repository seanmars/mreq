# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Assemble and check an mreq-how page.

  page.py dir                     print the folder pages are written to
  page.py new <topic-slug>        print a new content file path, stamped with the current time
  page.py build <x.content.html>  assemble <x>.html from skeleton.html and check it

The agent writes only a content file: header lines, "---", then the sections.
The skeleton reaches the page byte for byte, so retyping it never costs tokens
or breaks the diagrams. The page draws diagrams in the browser, where a broken
spec is a red box the agent never sees, so the build repeats that validation.
"""

import json
import math
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(tempfile.gettempdir()) / "mreq-how"
SKELETON = Path(__file__).resolve().parent / "skeleton.html"
CONTENT_SUFFIX = ".content.html"

# The skeleton's CJK ranges: a CJK glyph is about twice as wide as a Latin one.
CJK_RANGES = "ᄀ-ᅟ⺀-꓏가-힣豈-﫿︰-﹏＀-｠￠-￦"
# The skeleton's emoji ranges, U+2300-23FF, U+2600-27BF, U+2B00-2BFF and all above U+FFFF:
# an emoji is wider still, so it counts 3 (one is about 18 px; a line of 21 units is 160 px).
EMOJI_RANGES = "⌀-⏿☀-➿⬀-⯿𐀀-􏿿"
CJK = re.compile(f"[{CJK_RANGES}]")
EMOJI = re.compile(f"[{EMOJI_RANGES}]")
TOKENS = re.compile(f"[{CJK_RANGES}]|[^\\s{CJK_RANGES}]+|\\s+")
# The node kinds WRITING.md lists; the browser draws any other value as a box.
KINDS = ("box", "store", "external", "actor", "decision", "state", "start", "end")
# Units a line holds, by node kind, as the skeleton draws them.
LINE_UNITS = {"decision": 17}
DEFAULT_LINE_UNITS = 21
MAX_LINES = 3
# A start or end label sits below its circle: a third line reaches up into the circle.
END_LINE_UNITS = 20
END_MAX_LINES = 2
# An edge label, as the skeleton's labelSize() wraps it: two lines always fit the smallest canvas (268 x 164 px).
EDGE_LINE_UNITS = 22
EDGE_MAX_LINES = 2
PLACEHOLDERS = ("{{LANG}}", "{{TITLE}}", "{{QUESTION}}", "{{META}}", "<!-- CONTENT -->")
PLACEHOLDER = re.compile("|".join(re.escape(p) for p in PLACEHOLDERS))
HEADER_KEYS = ("lang", "title", "question", "meta")
REQUIRED_KEYS = ("lang", "title", "question")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

HEADER_LINE = re.compile(r"^\s*([a-z]+)\s*:\s*(.*)$", re.IGNORECASE)
WHOLE_PAGE = re.compile(r"<(?:!doctype|html|head|body|style)\b", re.IGNORECASE)
# The body needs no <meta>, and a refresh one leaves the page: the Content-Security-Policy stops loads, not navigation.
META_TAG = re.compile(r"<meta\b", re.IGNORECASE)
# The Content-Security-Policy runs only the skeleton's script, so a script in the content would silently not run.
# A JSON <script> outside its figure is not run either: the spec count below reports it.
SCRIPT_TAG = re.compile(r"<script\b(?![^>]*application/json)", re.IGNORECASE)
# A start tag, quoted values included, so a ">" inside a value does not end it.
START_TAG = re.compile(r"""<[a-z][^\s/>]*(?:"[^"]*"|'[^']*'|[^"'>])*>""", re.IGNORECASE)
QUOTED = re.compile(r""""[^"]*"|'[^']*'""")
# An attribute name follows a space or a "/", as the HTML parser reads it.
EVENT_ATTR = re.compile(r"[\s/]on[a-z]+\s*=", re.IGNORECASE)
# What the HTML parser reads as text up to a closing string: a comment and the raw-text elements (<style> is refused
# above). Left open, one swallows the skeleton's own script after the content. A <plaintext> never ends.
OPENER = re.compile(r"<!--|<(script|textarea|title|xmp|iframe|noembed|noframes|noscript|plaintext)\b", re.IGNORECASE)
EXTERNAL_TAG = re.compile(
    r"""<(?:script|img|link|iframe|source|video|audio)\b[^>]*\b(?:src|href)\s*=\s*["']?(?:[a-z]+:)?//""",
    re.IGNORECASE,
)
EXTERNAL_CSS = re.compile(r"""url\(\s*["']?(?:https?:)?//""", re.IGNORECASE)
# WRITING.md's figure. The spec ends where the figure goes on, so a "</script>" in a label stays in the spec.
DIAGRAM = re.compile(
    r'<figure class="diagram">\s*<script type="application/json">(.*?)</script>(?=\s*(?:<figcaption|</figure>))',
    re.DOTALL,
)
# Any JSON script, whatever its quotes or attributes: more of these than DIAGRAM matches is a misplaced spec.
JSON_SCRIPT = re.compile(r"<script\b[^>]*application/json", re.IGNORECASE)
# Where the HTML parser leaves the script early: the spec ends there, or the page's own script never runs.
SPEC_BREAK = re.compile(r"</script|<!--", re.IGNORECASE)
HTML_ENTITY = re.compile(r"&(?:lt|gt|amp|quot|apos|nbsp|#\d+|#x[0-9a-f]+);", re.IGNORECASE)


def units(ch: str) -> int:
    return 3 if EMOJI.match(ch) else 2 if CJK.match(ch) else 1


def width(text: str) -> int:
    return sum(units(ch) for ch in text)


def wrap(label: str, max_units: int) -> list:
    """The skeleton's wrap(), step for step, so the build counts the lines the browser draws."""
    out = []
    for para in label.split("\n"):
        line, used = "", 0
        for tok in TOKENS.findall(para):
            if tok.isspace():
                if line:
                    line, used = line + " ", used + 1
                continue
            w = width(tok)
            if used + w > max_units and line.strip():
                out.append(line.strip())
                line, used = "", 0
            while w > max_units:
                cut, cw = "", 0
                for ch in tok:
                    if cw + units(ch) > max_units - used:
                        break
                    cut, cw = cut + ch, cw + units(ch)
                if not cut:
                    if line.strip():
                        out.append(line.strip())
                    line, used = "", 0
                    continue
                if (line + cut).strip():
                    out.append((line + cut).strip())
                line, used = "", 0
                tok = tok[len(cut):]
                w = width(tok)
            line, used = line + tok, used + w
        if line.strip():
            out.append(line.strip())
    return out or [""]


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def no_constant(name: str):
    # Python's json reads NaN, Infinity and -Infinity; the browser's JSON.parse does not.
    raise ValueError(f"{name} is not JSON; write a number")


def finite(text: str) -> None:
    # Python's json reads 1e400 as inf and 400 digits as an exact integer; the browser's JSON.parse reads both as Infinity.
    if not math.isfinite(float(text)):
        shown = text if len(text) <= 20 else text[:17] + "..."
        raise ValueError(f"{shown} is too large; write a smaller number")


def parse_float(text: str) -> float:
    finite(text)
    return float(text)


def parse_int(text: str) -> int:
    finite(text)
    return int(text)


def is_name(value) -> bool:
    return isinstance(value, str) and value != ""


def js_str(value) -> str:
    # Messages quote values the way the browser's copy of this check prints them.
    if value is None:
        return "undefined"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def objects(spec: dict, key: str, errors: list) -> list:
    """(index, item) for each object in spec[key]; anything else is an error."""
    value = spec.get(key, [])
    if not isinstance(value, list):
        errors.append(f'"{key}" must be a list')
        return []
    found = []
    for i, item in enumerate(value):
        if isinstance(item, dict):
            found.append((i, item))
        else:
            errors.append(f"{key}[{i}] must be an object")
    return found


def flow_errors(spec: dict) -> list:
    errors = []
    ids = set()
    cells = {}
    for i, n in objects(spec, "nodes", errors):
        node_id = n.get("id")
        if not is_name(node_id):
            errors.append(f'nodes[{i}]: missing "id"' if not node_id else f'nodes[{i}]: "id" must be a string')
            continue
        if node_id in ids:
            errors.append(f'node "{node_id}" is defined twice')
        ids.add(node_id)
        col, row = n.get("col"), n.get("row")
        if not (is_number(col) and is_number(row)):
            errors.append(f'node "{node_id}": "col" and "row" must be numbers')
        elif col < 0 or row < 0:
            errors.append(f'node "{node_id}": "col" and "row" must be 0 or more')
        cell = f"{js_str(col)},{js_str(row)}"
        if cell in cells:
            errors.append(f'nodes "{cells[cell]}" and "{node_id}" share cell col {js_str(col)}, row {js_str(row)}')
        cells[cell] = node_id
        label = n.get("label")
        kind = n.get("kind", "box")
        # Tuple membership uses ==, so a list or dict kind cannot raise here.
        if kind not in KINDS:
            errors.append(f'node "{node_id}": unknown "kind" {json.dumps(kind, ensure_ascii=False)} (use {", ".join(KINDS)})')
        elif label is not None and not isinstance(label, str):
            errors.append(f'node "{node_id}": "label" must be a string')
        elif kind in ("start", "end"):
            # The skeleton draws only a given label here, not the id.
            if label and len(wrap(label, END_LINE_UNITS)) > END_MAX_LINES:
                errors.append(f'node "{node_id}": a start or end label is longer than two lines; move the detail into "note"')
        else:
            lines = wrap(label or node_id, LINE_UNITS.get(kind, DEFAULT_LINE_UNITS))
            if len(lines) > MAX_LINES:
                errors.append(f'node "{node_id}": label is longer than three lines; move the detail into "note"')
    if not ids:
        errors.append("no nodes")
    for i, e in objects(spec, "edges", errors):
        for end in ("from", "to"):
            if not isinstance(e.get(end), str) or e.get(end) not in ids:
                errors.append(f'edges[{i}]: unknown "{end}" node "{js_str(e.get(end))}"')
        label = e.get("label")
        if isinstance(label, str) and len(wrap(label, EDGE_LINE_UNITS)) > EDGE_MAX_LINES:
            errors.append(f'edges[{i}]: label is longer than two lines; move the detail into "note"')
    for i, st in objects(spec, "steps", errors):
        show = st.get("show", [])
        if not isinstance(show, list):
            errors.append(f'steps[{i}]: "show" must be a list')
            continue
        for key in show:
            if not isinstance(key, str):
                errors.append(f'steps[{i}]: "show" holds {js_str(key)}; use node ids and "from->to" strings')
                continue
            parts = key.split("->")
            # The browser reads a key of three or more parts as one node id, and lights nothing.
            if len(parts) > 2:
                errors.append(f'steps[{i}]: "{key}" is neither a node id nor a "from->to" edge')
                continue
            for node_id in parts:
                if node_id not in ids:
                    errors.append(f'steps[{i}]: unknown node "{node_id}" in "{key}"')
    for i, g in objects(spec, "groups", errors):
        for key in ("cols", "rows"):
            value = g.get(key)
            if not (isinstance(value, list) and len(value) == 2 and all(is_number(v) for v in value)):
                errors.append(f'groups[{i}]: "{key}" must be [first, last] numbers')
            elif not 0 <= value[0] <= value[1]:
                errors.append(f'groups[{i}]: "{key}" must be [first, last] with 0 <= first <= last')
    return errors


def sequence_errors(spec: dict) -> list:
    errors = []
    ids = set()
    for i, p in objects(spec, "participants", errors):
        participant_id = p.get("id")
        if not is_name(participant_id):
            errors.append(f'participants[{i}]: missing "id"' if not participant_id else f'participants[{i}]: "id" must be a string')
            continue
        if participant_id in ids:
            errors.append(f'participant "{participant_id}" is defined twice')
        ids.add(participant_id)
        label = p.get("label")
        if label is not None and not isinstance(label, str):
            errors.append(f'participant "{participant_id}": "label" must be a string')
    if not ids:
        errors.append("no participants")
    for i, m in objects(spec, "messages", errors):
        if "divider" in m:
            continue
        for end in ("from", "to"):
            if not isinstance(m.get(end), str) or m.get(end) not in ids:
                errors.append(f'messages[{i}]: unknown "{end}" participant "{js_str(m.get(end))}"')
    return errors


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)


def is_inside(file: Path, directory: Path) -> bool:
    # realpath expands Windows 8.3 names, which the temp directory can come back as.
    f = os.path.normcase(os.path.realpath(file))
    d = os.path.normcase(os.path.realpath(directory))
    try:
        return f != d and os.path.commonpath([f, d]) == d
    except ValueError:
        return False


def unclosed(markup: str) -> str:
    """The first comment or raw-text element the markup opens and never closes, or "" when all close.

    Reads left to right as the HTML parser does, so a "<!--" inside a <textarea> is text, not a comment."""
    at = 0
    while True:
        match = OPENER.search(markup, at)
        if not match:
            return ""
        name = match.group(1)
        if name is None:
            # "<!-->" already closes the comment, so the search for "-->" starts inside the opener.
            end = markup.find("-->", match.start() + 2)
            if end == -1:
                return match.group(0)
            at = end + 3
            continue
        if name.lower() == "plaintext":
            return match.group(0)
        close = re.compile(rf"</{name}[\s/>]", re.IGNORECASE).search(markup, match.end())
        if not close:
            return match.group(0)
        at = close.end()


def parse_content(text: str) -> tuple[dict, str, list]:
    """Split a content file into header values and body, at the first line that is exactly "---"."""
    lines = re.split(r"\r?\n", text)
    end = next((i for i, line in enumerate(lines) if line.strip() == "---"), -1)
    if end == -1:
        return {}, "", [
            'no "---" line: start the content file with lang / title / question / meta lines, then "---", then the sections'
        ]
    problems = []
    header = {}
    for line in lines[:end]:
        if not line.strip():
            continue
        match = HEADER_LINE.match(line)
        if not match or match.group(1).lower() not in HEADER_KEYS:
            problems.append(f'unknown header line "{line.strip()}" (expected {", ".join(HEADER_KEYS)})')
            continue
        header[match.group(1).lower()] = match.group(2).strip()
    for key in REQUIRED_KEYS:
        if not header.get(key):
            problems.append(f'header "{key}" is missing or empty')
    body = "\n".join(lines[end + 1:])
    # The skeleton supplies the document shell; a second one inside it means the agent copied the skeleton.
    # A diagram spec is text for the browser to draw, so a "<style>" in a note is not a tag.
    markup = DIAGRAM.sub("", body)
    if WHOLE_PAGE.search(markup):
        problems.append("the content holds a whole page (<html>, <head>, <body> or <style>); write only the <section> elements")
    if META_TAG.search(markup):
        problems.append("the content holds a <meta> tag; the skeleton has the page's meta tags, so drop it")
    if SCRIPT_TAG.search(markup):
        problems.append("the content holds a <script> element; the page runs only the skeleton's script, so drop it")
    # Quoted values become a space: "onclick=" inside a title is text, and a name right after a quote still counts.
    if any(EVENT_ATTR.search(QUOTED.sub(" ", tag)) for tag in START_TAG.findall(markup)):
        problems.append(
            "the content holds an event handler attribute (onclick=, onerror=, ...);"
            " the page runs only the skeleton's script, so drop it"
        )
    opener = unclosed(markup)
    if opener:
        problems.append(
            f'the content opens "{opener}" and never closes it, so the page\'s own script would not run;'
            ' close it, or write "<" in text as "&lt;"'
        )
    if not body.strip():
        problems.append('no sections after "---"')
    return header, body, problems


def assemble(skeleton: str, header: dict, body: str) -> str:
    values = {
        "{{LANG}}": escape_html(header.get("lang", "")),
        "{{TITLE}}": escape_html(header.get("title", "")),
        "{{QUESTION}}": escape_html(header.get("question", "")),
        "{{META}}": escape_html(header.get("meta", "")),
        "<!-- CONTENT -->": body,
    }
    # One pass over the skeleton: a value that holds "{{META}}" stays as written.
    return PLACEHOLDER.sub(lambda match: values[match.group(0)], skeleton)


def check_page(file: Path, html: str) -> tuple[list, int]:
    problems = []
    if not is_inside(file, Path(tempfile.gettempdir())):
        problems.append(f"the page is not under the temp directory {tempfile.gettempdir()}; write it to {OUTPUT_DIR}")
    if "Content-Security-Policy" not in html:
        problems.append("the skeleton's Content-Security-Policy meta tag is missing")
    if EXTERNAL_TAG.search(html) or EXTERNAL_CSS.search(html):
        problems.append("the page loads something from outside the file; inline it or drop it")

    index = 0
    for match in DIAGRAM.finditer(html):
        index += 1
        # A second spec in this figure: the count below reports it.
        if JSON_SCRIPT.search(match.group(1)):
            continue
        if SPEC_BREAK.search(match.group(1)):
            problems.append(f'diagram {index}: the spec holds "</script" or "<!--"; write "<" in JSON strings as \\u003c')
            continue
        try:
            spec = json.loads(match.group(1), parse_constant=no_constant, parse_float=parse_float, parse_int=parse_int)
        except ValueError as err:
            problems.append(f"diagram {index}: invalid JSON ({err})")
            continue
        if not isinstance(spec, dict):
            problems.append(f"diagram {index}: the spec must be a JSON object")
            continue
        kind = spec.get("type")
        if kind is not None and kind not in ("flow", "sequence"):
            problems.append(f'diagram {index}: unknown "type" "{js_str(kind)}" (use "flow" or "sequence")')
            continue
        errors = sequence_errors(spec) if kind == "sequence" else flow_errors(spec)
        # The browser draws JSON strings as plain text, so "&gt;" shows up as those four characters.
        errors.extend(
            f'"{text}" holds an HTML entity; JSON strings are plain text, so write the character itself'
            for text in strings(spec) if HTML_ENTITY.search(text)
        )
        problems.extend(f"diagram {index}: {e}" for e in errors)
    # The browser draws only the first spec in a figure.diagram; any other spec is skipped or unchecked.
    if len(JSON_SCRIPT.findall(html)) != index:
        problems.append('put each diagram spec first inside <figure class="diagram">, as WRITING.md shows')
    return problems, index


def fail(page: Path, problems: list) -> int:
    # A page left from an earlier build would pass for this one.
    page.unlink(missing_ok=True)
    for p in problems:
        print(f"FAIL {p}")
    return 1


def build(content_file: str) -> int:
    source = Path(content_file)
    # Nothing is deleted before these two pass: a wrong name has no page, and a project file is not ours.
    if not source.name.endswith(CONTENT_SUFFIX):
        print(f"FAIL name the content file <topic>{CONTENT_SUFFIX}")
        return 1
    if not is_inside(source, Path(tempfile.gettempdir())):
        print(f"FAIL the content file is not under the temp directory {tempfile.gettempdir()}; write it to {OUTPUT_DIR}")
        return 1
    page = source.with_name(source.name[: -len(CONTENT_SUFFIX)] + ".html")
    try:
        text = source.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return fail(page, [f"{source}: not UTF-8 text; save the content file as UTF-8"])
    except OSError as err:
        return fail(page, [f"{source}: {err.strerror or err}"])
    header, body, content_problems = parse_content(text)
    if content_problems:
        return fail(page, content_problems)
    # newline="" keeps the skeleton's line endings, so the page is the skeleton byte for byte.
    with open(SKELETON, encoding="utf-8", newline="") as file:
        skeleton = file.read()
    missing = [p for p in PLACEHOLDERS if p not in skeleton]
    if missing:
        return fail(page, [f"skeleton.html lost its placeholders {', '.join(missing)}; reinstall the skill"])
    html = assemble(skeleton, header, body)
    problems, diagrams = check_page(page, html)
    if problems:
        fail(page, problems)
        print("Fix the content file and build again.")
        return 1
    page.write_text(html, encoding="utf-8", newline="")
    print(f"ok: {diagrams} diagram spec(s)")
    print(page.resolve())
    return 0


def new(slug: str) -> int:
    if not SLUG_RE.fullmatch(slug):
        print(f"invalid slug {slug!r}: use kebab-case, e.g. top-words", file=sys.stderr)
        return 2
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(OUTPUT_DIR / f"{slug}-{datetime.now().strftime('%Y%m%d-%H%M%S')}{CONTENT_SUFFIX}")
    return 0


def main(argv: list) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if argv[:1] == ["dir"]:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(OUTPUT_DIR)
        return 0
    if len(argv) == 2 and argv[0] == "new":
        return new(argv[1])
    if len(argv) == 2 and argv[0] == "build":
        return build(argv[1])
    print(f"usage: page.py dir | page.py new <topic-slug> | page.py build <topic>{CONTENT_SUFFIX}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
