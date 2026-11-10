"""The SKILL.md files repeat some text on purpose, so each skill works alone. These tests keep the copies the same."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
# The skills that run a script, and the script each one runs.
SCRIPTS = {
    "define": "mreq.py",
    "grill": "mreq.py",
    "apply": "mreq.py",
    "close": "mreq.py",
    "how": "page.py",
    "graph": "page.py",
}
SHARED_SECTIONS = ("## Asking the user", "## When a tool call is denied")
RUN_RULE = "Write every path with `/`, never with `\\`, on Windows too"


def skill_text(name: str) -> str:
    return (SKILLS_DIR / f"mreq-{name}" / "SKILL.md").read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    """The lines from a "## " heading up to the next one."""
    for part in re.split(r"(?m)^(?=## )", text):
        if part.split("\n", 1)[0] == heading:
            return part.strip()
    return ""


class SkillTextTest(unittest.TestCase):
    def test_shared_sections_are_word_for_word_the_same(self):
        for heading in SHARED_SECTIONS:
            copies = {name: section(skill_text(name), heading) for name in SCRIPTS}
            self.assertTrue(copies["define"], heading)
            for name, copy in copies.items():
                self.assertEqual(copy, copies["define"], f"{heading} in mreq-{name} differs from mreq-define")

    def test_each_skill_runs_its_script_by_the_quoted_skill_directory(self):
        for name, script in SCRIPTS.items():
            text = section(skill_text(name), "## The script")
            self.assertIn(f'uv run "${{CLAUDE_SKILL_DIR}}/../mreq-shared/scripts/{script}"', text, name)
            self.assertIn(RUN_RULE, text, name)
            self.assertTrue((SKILLS_DIR / "mreq-shared" / "scripts" / script).is_file(), script)

    def test_the_run_rule_is_stated_once_in_each_skill(self):
        # The section on denied calls holds it; a second copy in "The script" only drifts.
        for name in SCRIPTS:
            self.assertEqual(skill_text(name).count("command on its own: no `cd`"), 1, name)

    def test_no_skill_file_shows_a_windows_path(self):
        for path in SKILLS_DIR.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"\b[A-Za-z]:\\|\\[\w.-]+\\", text), path.as_posix())

    def test_the_page_skills_name_their_own_kind(self):
        for name in ("how", "graph"):
            text = skill_text(name)
            self.assertIn(f"`page.py {name} new <topic-slug>`", text)
            self.assertIn(f"`page.py {name} build <content file>`", text)


if __name__ == "__main__":
    unittest.main()
