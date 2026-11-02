# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Assemble and check an mreq-graph page.

  page.py dir                     print the folder pages are written to
  page.py new <topic-slug>        print a new content file path, stamped with the current time
  page.py build <x.content.html>  assemble <x>.html from skeleton.html and check it

The agent writes only a content file: header lines, "---", then the sections.
The build inlines the Pele bundle (vendor/pele.global.js), so the page draws its
Mermaid diagrams offline. The browser shows a broken diagram as an error box the
agent never sees, so the build renders every diagram with the same bundle in Node
first. Without Node it still builds, and says the diagrams were not checked.
"""

import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# The agent runs every command from the session root (no cd), so the cwd is that root.
OUTPUT_DIR = Path.cwd() / ".mreq" / "graph"
SKILL_DIR = Path(__file__).resolve().parent
SKELETON = SKILL_DIR / "skeleton.html"
PELE = SKILL_DIR / "vendor" / "pele.global.js"
CHECKER = SKILL_DIR / "check.mjs"
CONTENT_SUFFIX = ".content.html"
NODE_TIMEOUT = 60
# The diagram canvas in skeleton.html is about 820 px wide. A wider diagram is shrunk to fit, and below
# three quarters of its size the 16 px labels are too small to read. maxWidth does not make Pele lay it out again.
CANVAS_WIDTH = 820
MAX_WIDTH = 1100

PLACEHOLDERS = ("{{LANG}}", "{{TITLE}}", "{{REQUEST}}", "{{META}}", "{{CSP}}", "{{PELE}}", "<!-- CONTENT -->")
PLACEHOLDER = re.compile("|".join(re.escape(p) for p in PLACEHOLDERS))
HEADER_KEYS = ("lang", "title", "request", "meta")
REQUIRED_KEYS = ("lang", "title", "request")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

HEADER_LINE = re.compile(r"^\s*([a-z]+)\s*:\s*(.*)$", re.IGNORECASE)
WHOLE_PAGE = re.compile(r"<(?:!doctype|html|head|body|style)\b", re.IGNORECASE)
META_TAG = re.compile(r"<meta\b", re.IGNORECASE)
MERMAID_TYPE = "text/x-mermaid"
# Any <script> but a Mermaid source: the Content-Security-Policy runs only the skeleton's scripts.
SCRIPT_TAG = re.compile(r"<script\b(?![^>]*text/x-mermaid)", re.IGNORECASE)
START_TAG = re.compile(r"""<[a-z][^\s/>]*(?:"[^"]*"|'[^']*'|[^"'>])*>""", re.IGNORECASE)
QUOTED = re.compile(r""""[^"]*"|'[^']*'""")
EVENT_ATTR = re.compile(r"[\s/]on[a-z]+\s*=", re.IGNORECASE)
# What the HTML parser reads as text up to a closing string. Left open, one swallows the skeleton's scripts.
OPENER = re.compile(r"<!--|<(script|textarea|title|xmp|iframe|noembed|noframes|noscript|plaintext)\b", re.IGNORECASE)
EXTERNAL_TAG = re.compile(
    r"""<(?:script|img|link|iframe|source|video|audio)\b[^>]*\b(?:src|href)\s*=\s*["']?(?:[a-z]+:)?//""",
    re.IGNORECASE,
)
EXTERNAL_CSS = re.compile(r"""url\(\s*["']?(?:https?:)?//""", re.IGNORECASE)
# WRITING.md's figure. The source ends where the figure goes on, so a "</script>" inside it stays in the source.
DIAGRAM = re.compile(
    r'<figure class="diagram">\s*<script type="text/x-mermaid">(.*?)</script>(?=\s*(?:<figcaption|</figure>))',
    re.DOTALL,
)
ANY_MERMAID = re.compile(r"<script\b[^>]*text/x-mermaid", re.IGNORECASE)
SOURCE_BREAK = re.compile(r"</script|<!--", re.IGNORECASE)
# Fixed colors in a source: Pele writes them as style attributes, which beat the page's class colors and
# stay the same in the dark theme. Checked only in the types where these are statements, not node text.
FIXED_COLOR_TYPES = re.compile(r"^\s*(?:flowchart|graph|stateDiagram|classDiagram)\b")
FIXED_COLOR = re.compile(r"^\s*(classDef|style|linkStyle)\s|%%\{\s*init", re.MULTILINE)
HTML_ENTITY = re.compile(r"&(?:lt|gt|amp|quot|apos|nbsp|#\d+|#x[0-9a-f]+);", re.IGNORECASE)
# A script the page runs: no attributes, as the skeleton writes them.
RUN_SCRIPT = re.compile(r"<script>(.*?)</script>", re.DOTALL)


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def is_inside(file: Path, directory: Path) -> bool:
    # realpath expands Windows 8.3 names and links, so both sides compare as real locations.
    f = os.path.normcase(os.path.realpath(file))
    d = os.path.normcase(os.path.realpath(directory))
    try:
        return f != d and os.path.commonpath([f, d]) == d
    except ValueError:
        return False


def unclosed(markup: str) -> str:
    """The first comment or raw-text element the markup opens and never closes, or "" when all close."""
    at = 0
    while True:
        match = OPENER.search(markup, at)
        if not match:
            return ""
        name = match.group(1)
        if name is None:
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


def mermaid_source(raw: str) -> str:
    """The text the page script hands to Pele: the same trim, step for step."""
    return re.sub(r"^\s*\n", "", raw).rstrip()


def parse_content(text: str) -> tuple[dict, str, list]:
    """Split a content file into header values and body, at the first line that is exactly "---"."""
    lines = re.split(r"\r?\n", text)
    end = next((i for i, line in enumerate(lines) if line.strip() == "---"), -1)
    if end == -1:
        return {}, "", [
            'no "---" line: start the content file with lang / title / request / meta lines, then "---", then the sections'
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
    # A Mermaid source is text for Pele, so a "<style>" or "<br>" in it is not a tag.
    markup = DIAGRAM.sub("", body)
    if WHOLE_PAGE.search(markup):
        problems.append("the content holds a whole page (<html>, <head>, <body> or <style>); write only the <section> elements")
    if META_TAG.search(markup):
        problems.append("the content holds a <meta> tag; the skeleton has the page's meta tags, so drop it")
    if SCRIPT_TAG.search(markup):
        problems.append("the content holds a <script> element; the page runs only the skeleton's scripts, so drop it")
    if any(EVENT_ATTR.search(QUOTED.sub(" ", tag)) for tag in START_TAG.findall(markup)):
        problems.append(
            "the content holds an event handler attribute (onclick=, onerror=, ...);"
            " the page runs only the skeleton's scripts, so drop it"
        )
    opener = unclosed(markup)
    if opener:
        problems.append(
            f'the content opens "{opener}" and never closes it, so the page\'s scripts would not run;'
            ' close it, or write "<" in text as "&lt;"'
        )
    if EXTERNAL_TAG.search(markup) or EXTERNAL_CSS.search(markup):
        problems.append("the content loads something from outside the file; the page must work offline, so drop it")
    if not body.strip():
        problems.append('no sections after "---"')
    return header, body, problems


def diagram_problems(body: str) -> tuple[list, list]:
    """The Mermaid sources in the body, and what is wrong with their markup."""
    problems = []
    sources = []
    for index, match in enumerate(DIAGRAM.finditer(body), start=1):
        raw = match.group(1)
        if ANY_MERMAID.search(raw):
            # A second source in this figure: the count below reports it.
            sources.append("")
            continue
        if SOURCE_BREAK.search(raw):
            problems.append(f'diagram {index}: the source holds "</script" or "<!--"; reword that label')
        entity = HTML_ENTITY.search(raw)
        if entity:
            problems.append(
                f'diagram {index}: the source holds the HTML entity "{entity.group(0)}";'
                " the source is plain text, so write the character itself"
            )
        source = mermaid_source(raw)
        if not source:
            problems.append(f"diagram {index}: the Mermaid source is empty")
        fixed = FIXED_COLOR.search(source) if FIXED_COLOR_TYPES.match(source) else None
        if fixed:
            problems.append(
                f'diagram {index}: the source sets fixed colors ("{fixed.group(0).strip()}");'
                ' drop it and use the color classes (WRITING.md, Colors)'
            )
        sources.append(source)
    if len(ANY_MERMAID.findall(body)) != len(sources):
        problems.append('put each Mermaid source first inside <figure class="diagram">, as WRITING.md shows')
    return sources, problems


def render_check(sources: list) -> tuple[list, str]:
    """Render every source with Pele in Node. Returns (problems, warning)."""
    node = shutil.which("node")
    if not node:
        return [], "WARN node not found: the diagrams were not checked; open the page and look for red error boxes"
    try:
        run = subprocess.run(
            [node, str(CHECKER), str(PELE)],
            input=json.dumps(sources),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=NODE_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as err:
        return [], f"WARN the diagram check did not finish ({err}); open the page and look for red error boxes"
    if run.returncode != 0:
        detail = (run.stderr.strip().splitlines() or ["no output"])[-1]
        return [], f"WARN the diagram check failed ({detail}); open the page and look for red error boxes"
    problems = []
    for index, result in enumerate(json.loads(run.stdout), start=1):
        if result.get("ok"):
            width = result.get("width") or 0
            if width > MAX_WIDTH:
                problems.append(
                    f"diagram {index}: it is {round(width)} px wide, so the page shrinks it to"
                    f" {round(CANVAS_WIDTH / width * 100)}% and its labels are too small to read;"
                    " use TD, remove \"direction LR\", shorten the labels, or split it (WRITING.md, Keep it readable)"
                )
            continue
        where = f" at line {result['line']}" if result.get("line") else ""
        # Pele's message holds the source line and a "^" under the column: keep its lines, indented under the FAIL.
        message = "\n".join("    " + line for line in result.get("message", "").splitlines() if line.strip())
        problems.append(f"diagram {index}: Pele {result.get('code')} error{where} of the Mermaid source:\n{message}")
    return problems, ""


def script_hashes(html: str) -> str:
    hashes = []
    for match in RUN_SCRIPT.finditer(html):
        digest = hashlib.sha256(match.group(1).encode("utf-8")).digest()
        hashes.append(f"'sha256-{base64.b64encode(digest).decode('ascii')}'")
    return " ".join(hashes)


def assemble(skeleton: str, pele: str, header: dict, body: str) -> str:
    values = {
        "{{LANG}}": escape_html(header.get("lang", "")),
        "{{TITLE}}": escape_html(header.get("title", "")),
        "{{REQUEST}}": escape_html(header.get("request", "")),
        "{{META}}": escape_html(header.get("meta", "")),
        "{{CSP}}": "{{CSP}}",
        "{{PELE}}": pele,
        "<!-- CONTENT -->": body,
    }
    # One pass over the skeleton: a value that holds a placeholder stays as written.
    html = PLACEHOLDER.sub(lambda match: values[match.group(0)], skeleton)
    # The HTML parser turns CRLF into LF before the browser hashes a script, so hash and write LF only.
    html = html.replace("\r\n", "\n")
    # The CSP sits before the scripts and holds no script text, so hashing first and filling it after is safe.
    return html.replace("{{CSP}}", script_hashes(html), 1)


def fail(page: Path, problems: list) -> int:
    # A page left from an earlier build would pass for this one.
    page.unlink(missing_ok=True)
    for p in problems:
        print(f"FAIL {p}")
    print("Fix the content file and build again.")
    return 1


def build(content_file: str) -> int:
    source = Path(content_file)
    # Nothing is deleted before these two pass: a wrong name has no page, and a project file is not ours.
    if not source.name.endswith(CONTENT_SUFFIX):
        print(f"FAIL name the content file <topic>{CONTENT_SUFFIX}")
        return 1
    if not is_inside(source, OUTPUT_DIR):
        print(f"FAIL the content file is not under {OUTPUT_DIR}; write it there")
        return 1
    page = source.with_name(source.name[: -len(CONTENT_SUFFIX)] + ".html")
    try:
        text = source.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return fail(page, [f"{source}: not UTF-8 text; save the content file as UTF-8"])
    except OSError as err:
        return fail(page, [f"{source}: {err.strerror or err}"])
    header, body, problems = parse_content(text)
    if problems:
        return fail(page, problems)
    sources, problems = diagram_problems(body)
    if not sources:
        problems.append('no diagrams: add at least one <figure class="diagram">, as WRITING.md shows')
    if problems:
        return fail(page, problems)
    problems, warning = render_check(sources)
    if problems:
        return fail(page, problems)

    with open(SKELETON, encoding="utf-8", newline="") as file:
        skeleton = file.read()
    missing = [p for p in PLACEHOLDERS if p not in skeleton]
    if missing or not PELE.is_file():
        return fail(page, ["skeleton.html or vendor/pele.global.js is missing or changed; reinstall the skill"])
    pele = PELE.read_text(encoding="utf-8")
    page.write_text(assemble(skeleton, pele, header, body), encoding="utf-8", newline="")
    if warning:
        print(warning)
    checked = "not checked" if warning else "checked with Pele"
    print(f"ok: {len(sources)} diagram(s), {checked}")
    print(page.resolve())
    return 0


def make_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # The pages are not project files: keep them out of git status, which mreq-apply compares with its Handoff.
    ignore = OUTPUT_DIR / ".gitignore"
    if not ignore.exists():
        ignore.write_text("*\n", encoding="utf-8")


def new(slug: str) -> int:
    if not SLUG_RE.fullmatch(slug):
        print(f"invalid slug {slug!r}: use kebab-case, e.g. order-states", file=sys.stderr)
        return 2
    make_output_dir()
    print(OUTPUT_DIR / f"{slug}-{datetime.now().strftime('%Y%m%d-%H%M%S')}{CONTENT_SUFFIX}")
    return 0


def main(argv: list) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if argv[:1] == ["dir"]:
        make_output_dir()
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
