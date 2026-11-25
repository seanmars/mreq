# /// script
# requires-python = ">=3.10"
# dependencies = ["tiktoken"]
# ///
"""Print how many tokens each skill puts in an agent's context.

  uv run tools/tokens.py              every skill under skills/
  uv run tools/tokens.py --files      each file too
  uv run tools/tokens.py <dir> ...    the skills under other directories

The counts are an estimate: tiktoken's o200k_base, not the tokenizer of any one agent.
"""

import argparse
import re
import sys
from pathlib import Path

import tiktoken

ROOT = Path(__file__).resolve().parent.parent
ENCODING = tiktoken.get_encoding("o200k_base")
NOTES = """\
description  name and description: in the context of every conversation.
             (n) = disable-model-invocation, so the agent leaves it out and the total skips it.
SKILL.md     read when the skill starts.
references   the other .md files: each one read only when SKILL.md says to.
Files of other types (scripts, skeleton.html, vendor/) are run or copied, never read, so they are not counted.
Estimate from tiktoken o200k_base: each agent's own tokenizer gives other numbers."""


def count(text: str) -> int:
    return len(ENCODING.encode(text, disallowed_special=()))


def front_matter(text: str) -> dict:
    block = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if not block:
        return {}
    fields = re.findall(r"(?m)^([\w-]+):[ \t]*(.*)$", block.group(1))
    return {key: value.strip().strip('"') for key, value in fields}


def measure(skill_file: Path) -> dict:
    directory = skill_file.parent
    text = skill_file.read_text(encoding="utf-8")
    fields = front_matter(text)
    name = fields.get("name", directory.name)
    references = sorted(path for path in directory.rglob("*.md") if path != skill_file)
    return {
        "name": name,
        "user_only": fields.get("disable-model-invocation") == "true",
        "description": count(f"{name}: {fields.get('description', '')}"),
        "skill": count(text),
        "references": [
            (path.relative_to(directory).as_posix(), count(path.read_text(encoding="utf-8"))) for path in references
        ],
    }


def find_skills(directories: list) -> list:
    files = sorted(path for directory in directories for path in directory.rglob("SKILL.md"))
    return [measure(path) for path in files]


def print_table(skills: list) -> None:
    width = max(len(skill["name"]) for skill in skills + [{"name": "total"}])
    line = f"{{:<{width}}}  {{:>11}}  {{:>8}}  {{:>10}}  {{:>7}}"
    print(line.format("skill", "description", "SKILL.md", "references", "total"))
    print(line.format("-" * width, "-" * 11, "-" * 8, "-" * 10, "-" * 7))
    totals = [0, 0, 0]
    for skill in skills:
        references = sum(tokens for _, tokens in skill["references"])
        description = f"({skill['description']:,})" if skill["user_only"] else f"{skill['description']:,}"
        total = skill["skill"] + references
        print(line.format(skill["name"], description, f"{skill['skill']:,}", f"{references:,}", f"{total:,}"))
        totals[0] += 0 if skill["user_only"] else skill["description"]
        totals[1] += skill["skill"]
        totals[2] += references
    print(line.format("-" * width, "-" * 11, "-" * 8, "-" * 10, "-" * 7))
    print(line.format("total", *(f"{tokens:,}" for tokens in (*totals, totals[1] + totals[2]))))


def print_files(skills: list) -> None:
    for skill in skills:
        print()
        print(skill["name"])
        for path, tokens in [("SKILL.md", skill["skill"])] + skill["references"]:
            print(f"  {tokens:>7,}  {path}")


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(description="Print how many tokens each skill puts in an agent's context.")
    parser.add_argument("directories", nargs="*", type=Path, default=[ROOT / "skills"], help="default: skills/")
    parser.add_argument("--files", action="store_true", help="list the tokens of each file too")
    args = parser.parse_args(argv)
    skills = find_skills(args.directories)
    if not skills:
        print("no SKILL.md under: " + ", ".join(str(directory) for directory in args.directories), file=sys.stderr)
        return 1
    print_table(skills)
    if args.files:
        print_files(skills)
    print()
    print(NOTES)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
