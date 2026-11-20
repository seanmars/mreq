"""Copy the files in shared/ into each skill that uses them, so every skill holds all the files it needs.

  python tools/sync.py          copy every file
  python tools/sync.py --check  list what is out of step, and change nothing

Edit a file in shared/, never a copy: the next sync overwrites the copy.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared"
SKILLS = ROOT / "skills"
TASK_SKILLS = ("define", "grill", "apply", "close")
PAGE_SKILLS = ("how", "graph")
# Each file in shared/, and the skills that hold a copy of it at the same path.
COPIES = {
    "scripts/mreq.py": TASK_SKILLS,
    "GRILL.md": ("define", "grill"),
    "scripts/page.py": PAGE_SKILLS,
    "scripts/check.mjs": PAGE_SKILLS,
    "vendor/pele.global.js": PAGE_SKILLS,
    "vendor/pele.LICENSE": PAGE_SKILLS,
    "MERMAID.md": PAGE_SKILLS,
}


def show(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def pairs() -> list:
    """Every (source, copy) pair."""
    return [(SHARED / name, SKILLS / f"mreq-{skill}" / name) for name, skills in COPIES.items() for skill in skills]


def problems() -> list:
    found = []
    # A file here that no skill gets is a file someone forgot to list.
    for path in sorted(SHARED.rglob("*")):
        if path.is_file() and path.relative_to(SHARED).as_posix() not in COPIES:
            found.append(f"not in COPIES: {show(path)}")
    for source, copy in pairs():
        if not source.is_file():
            found.append(f"missing: {show(source)}")
        elif not copy.is_file():
            found.append(f"missing: {show(copy)}")
        # Bytes, not text: a copy with other line endings is not the same file.
        elif copy.read_bytes() != source.read_bytes():
            found.append(f"differs from {show(source)}: {show(copy)}")
    return found


def main(argv: list) -> int:
    if argv == ["--check"]:
        found = problems()
        for problem in found:
            print(problem)
        if found:
            print("Edit the file in shared/, then run: python tools/sync.py")
        return 1 if found else 0
    if argv:
        print("usage: sync.py [--check]", file=sys.stderr)
        return 2
    for source, copy in pairs():
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, copy)
        print(show(copy))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
