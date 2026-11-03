# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Create, list, touch, show progress of, and delete mreq task documents under <project>/.mreq/."""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCHEMAS = ("feature", "issue", "refactor", "task")
STATUSES = ("draft", "active", "done")
FIELDS = ("title", "desc", "date", "schema", "status", "updated")
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_SLUG = 60
FIELD_RE = re.compile(r"^([A-Za-z_][\w-]*):(.*)$")
CHECKBOX_RE = re.compile(r"^\s*- \[([ xX])\] ", re.MULTILINE)
OPEN_TASK_RE = re.compile(r"^\s*- \[ \] (.*)$")
COMMENT_RE = re.compile(r"<!--.*?-->")
FENCE_RE = re.compile(r"(`{3,}|~{3,})")


def show(path) -> str:
    # Every printed path uses "/": Git Bash strips unquoted backslashes, Windows tools accept "/".
    return Path(path).as_posix()


def project_root(start: Path | None = None) -> Path:
    # The git top level keeps .mreq/ in one place when the agent runs from a subdirectory.
    # Only "no git" or "not a repository" means the cwd is the project; any other failure
    # (e.g. dubious ownership) would put .mreq/ in the wrong place. LC_ALL=C keeps git's message in English.
    cwd = start or Path.cwd()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "LC_ALL": "C"},
        )
    except OSError:
        return cwd
    if result.returncode == 0:
        return Path(result.stdout.strip())
    if "not a git repository" in result.stderr:
        return cwd
    message = result.stderr.strip().splitlines() or [f"exit code {result.returncode}"]
    raise SystemExit(f"git rev-parse --show-toplevel in {show(cwd)}: {message[0]}")


def mreq_directory() -> Path:
    directory = project_root() / ".mreq"
    if directory.exists() and not directory.is_dir():
        raise SystemExit(f"{show(directory)} is not a directory: move that file away, mreq keeps its documents there")
    return directory


def is_document(path: Path, directory: Path) -> bool:
    # Compare real locations: a junction .mreq/ still matches, a link out of .mreq/ does not.
    real = path.resolve()
    return real.suffix.lower() == ".md" and real.parent == directory.resolve()


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def render_field(key: str, value) -> str:
    # JSON strings are valid YAML double-quoted scalars, so ":" or "#" in a title stays safe.
    return f"{key}: {json.dumps(value, ensure_ascii=False)}"


def render_front_matter(meta: dict) -> str:
    return "---\n" + "\n".join(render_field(key, meta[key]) for key in FIELDS) + "\n---\n"


def split_document(text: str) -> tuple[list | None, str]:
    """Return the front matter lines and the body; None when there is no front matter."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    return text[4:end].split("\n"), text[end + 5:]


def parse_fields(lines: list) -> dict:
    meta = {}
    for line in lines:
        match = FIELD_RE.match(line)
        if not match:
            continue
        value = match.group(2).strip()
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        meta[match.group(1)] = value
    return meta


def set_fields(lines: list, values: dict) -> list:
    # Rewrite only the given keys, so unknown fields, comments and their order survive.
    out = []
    seen = set()
    for line in lines:
        match = FIELD_RE.match(line)
        if match and match.group(1) in values:
            key = match.group(1)
            out.append(render_field(key, values[key]))
            seen.add(key)
        else:
            out.append(line)
    out.extend(render_field(key, value) for key, value in values.items() if key not in seen)
    return out


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def describe(err: Exception) -> str:
    if isinstance(err, UnicodeDecodeError):
        return "not UTF-8 text"
    return getattr(err, "strerror", None) or str(err)


def tasks_section(body: str) -> str:
    """The lines under "## Tasks", without HTML comments and fenced code blocks.

    As in CommonMark, only a line that starts with "<!--" opens a comment, so "<!--" in a
    code span or after a checkbox does not. A fence closes only on a line of the same
    character, at least as long, with nothing else on it.
    """
    lines = []
    in_tasks = False
    fence = None
    in_comment = False
    for line in body.split("\n"):
        stripped = line.strip()
        if in_comment:
            in_comment = "-->" not in line
            continue
        if fence:
            if len(stripped) >= len(fence) and stripped == fence[0] * len(stripped):
                fence = None
            continue
        opener = FENCE_RE.match(stripped)
        if opener:
            fence = opener.group(1)
            continue
        if stripped.startswith("<!--"):
            in_comment = "-->" not in stripped[4:]
            continue
        if re.match(r"#{1,2} ", line):
            in_tasks = line.strip() == "## Tasks"
            continue
        if in_tasks:
            lines.append(line)
    return "\n".join(lines)


def task_progress(body: str) -> dict:
    marks = CHECKBOX_RE.findall(tasks_section(body))
    return {"done": sum(1 for m in marks if m != " "), "total": len(marks)}


def next_task(body: str) -> str:
    """The first unchecked task in the document's words, without HTML comments; "none" when all are done."""
    for line in tasks_section(body).split("\n"):
        match = OPEN_TASK_RE.match(line)
        if match:
            return COMMENT_RE.sub("", match.group(1)).strip()
    return "none"


def warnings(meta: dict, lines: list | None) -> list:
    found = []
    if lines is None:
        found.append("no front matter")
    else:
        if meta.get("status") not in STATUSES:
            found.append(f"status {meta.get('status')!r} is not one of {', '.join(STATUSES)}")
        if meta.get("schema") not in SCHEMAS:
            found.append(f"schema {meta.get('schema')!r} is not one of {', '.join(SCHEMAS)}")
    return found


def document_path(command: str, raw: str) -> Path:
    """Refuse anything but a document in <project>/.mreq/; return the path as given, made absolute."""
    # Not resolved, so a junction .mreq/ keeps the path that new and list printed.
    path = Path(os.path.abspath(raw))
    if not is_document(path, project_root(path.parent.parent) / ".mreq"):
        raise SystemExit(f"{command}: {show(path)}: not a task document; give a .mreq/<name>.md path at the project root")
    if not path.is_file():
        raise SystemExit(f"{command}: {show(path)}: {'not a file' if path.exists() else 'no such file'}")
    return path


def read_document(command: str, path: Path) -> tuple[list, str, dict]:
    """Front matter lines, body and fields; refuse a file without the schema and date mreq writes."""
    lines, body = split_document(read_text(path))
    meta = parse_fields(lines or [])
    if lines is None or "schema" not in meta or "date" not in meta:
        raise SystemExit(f"{command}: {show(path)}: no mreq front matter (schema and date are missing)")
    return lines, body, meta


def cmd_new(args: argparse.Namespace) -> dict:
    if not SLUG_RE.fullmatch(args.slug):
        raise SystemExit(f"invalid slug {args.slug!r}: use kebab-case, e.g. fix-login-timeout")
    if len(args.slug) > MAX_SLUG:
        raise SystemExit(f"invalid slug {args.slug!r}: use at most {MAX_SLUG} characters")
    for name in ("title", "desc"):
        if re.search(r"[\r\n]", getattr(args, name)):
            raise SystemExit(f"invalid --{name}: write it on one line")
    stamp = datetime.now()
    created = stamp.strftime("%Y-%m-%d %H:%M:%S")
    directory = mreq_directory()
    directory.mkdir(exist_ok=True)
    path = directory / f"{stamp.strftime('%Y%m%d-%H%M%S')}-{args.slug}.md"
    meta = {
        "title": args.title,
        "desc": args.desc,
        "date": created,
        "schema": args.schema,
        "status": "draft",
        "updated": created,
    }
    body = read_text(TEMPLATE_DIR / f"{args.schema}.md").replace("{{title}}", args.title)
    # "x" creates the file or fails, so two runs in the same second cannot overwrite each other.
    try:
        with path.open("x", encoding="utf-8", newline="\n") as file:
            file.write(render_front_matter(meta) + "\n" + body)
    except FileExistsError:
        raise SystemExit(f"already exists: {show(path)}")
    return {"path": show(path), **meta}


def cmd_list(args: argparse.Namespace) -> list:
    directory = mreq_directory()
    if not directory.is_dir():
        return []
    items = []
    # The same check as update and delete, so every listed path is one they accept.
    for path in directory.iterdir():
        if not path.is_file() or not is_document(path, directory):
            continue
        try:
            lines, body = split_document(read_text(path))
        except (OSError, UnicodeDecodeError) as err:
            # One unreadable file must not hide the others.
            items.append({"path": show(path), "error": describe(err)})
            continue
        meta = parse_fields(lines or [])
        if args.open and meta.get("status") == "done":
            continue
        item = {"path": show(path), **meta, "tasks": task_progress(body)}
        found = warnings(meta, lines)
        if found:
            item["warning"] = "; ".join(found)
        items.append(item)
    return sorted(items, key=lambda item: str(item.get("updated", "")), reverse=True)


def cmd_update(args: argparse.Namespace) -> dict:
    path = document_path("update", args.path)
    lines, body, meta = read_document("update", path)
    values = {key: "" for key in FIELDS if key not in meta}
    if args.status:
        values["status"] = args.status
    values["updated"] = now()
    write_text(path, "---\n" + "\n".join(set_fields(lines, values)) + "\n---\n" + body)
    return {"path": show(path), **meta, **values, "tasks": task_progress(body)}


def cmd_progress(args: argparse.Namespace) -> str:
    # Plain text, not JSON: the agent shows these two lines to the user as they are.
    path = document_path("progress", args.path)
    _, body, meta = read_document("progress", path)
    tasks = task_progress(body)
    return (
        f"Using: {show(path)}\n"
        f"{meta['schema']}: {tasks['done']}/{tasks['total']} tasks done. Next: {next_task(body)}"
    )


def cmd_delete(args: argparse.Namespace) -> dict:
    # The only command that removes a file checks at least as much as update does.
    path = document_path("delete", args.path)
    read_document("delete", path)
    path.unlink()
    return {"path": show(path), "deleted": True}


def main() -> None:
    # Before argparse, which can already write an error: both streams in UTF-8, whatever the locale.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="mreq", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="create a task document from a template")
    new.add_argument("--schema", required=True, choices=SCHEMAS)
    new.add_argument("--slug", required=True, help="kebab-case file name part")
    new.add_argument("--title", required=True)
    new.add_argument("--desc", required=True, help="one sentence")
    new.set_defaults(run=cmd_new)

    lst = sub.add_parser("list", help="list task documents, most recently updated first")
    lst.add_argument("--open", action="store_true", help="skip documents with status done")
    lst.set_defaults(run=cmd_list)

    upd = sub.add_parser("update", help="refresh 'updated', optionally set status")
    upd.add_argument("path")
    upd.add_argument("--status", choices=STATUSES)
    upd.set_defaults(run=cmd_update)

    prog = sub.add_parser("progress", help="print the two progress lines: Using, and tasks done / next")
    prog.add_argument("path")
    prog.set_defaults(run=cmd_progress)

    delete = sub.add_parser("delete", help="delete a task document")
    delete.add_argument("path")
    delete.set_defaults(run=cmd_delete)

    args = parser.parse_args()
    try:
        result = args.run(args)
    except (OSError, UnicodeDecodeError) as err:
        where = getattr(err, "filename", None) or getattr(args, "path", "")
        raise SystemExit(f"{args.command}: {show(where) if where else where}: {describe(err)}")
    print(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
