"""The SKILL.md files repeat some text on purpose, so each skill works alone. These tests keep the copies the same.

test_sync.py does the same for the files tools/sync.py copies from shared/.
"""

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
# The skills that start another mreq skill, and the section that says how in every agent.
HANDOFF_SKILLS = ("define", "grill", "apply", "close")
HANDOFF_SECTION = "## Running another mreq skill"
# Only the user starts these. Each agent marks that its own way.
USER_ONLY = ("define", "close", "how", "graph", "pro", "terms")


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
            self.assertIn(f'uv run "${{CLAUDE_SKILL_DIR}}/scripts/{script}"', text, name)
            self.assertIn(RUN_RULE, text, name)
            self.assertTrue((SKILLS_DIR / f"mreq-{name}" / "scripts" / script).is_file(), name)

    def test_the_run_rule_is_stated_once_in_each_skill(self):
        # The section on denied calls holds it; a second copy in "The script" only drifts.
        for name in SCRIPTS:
            self.assertEqual(skill_text(name).count("command on its own: no `cd`"), 1, name)

    def test_no_skill_file_shows_a_windows_path(self):
        for path in SKILLS_DIR.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"\b[A-Za-z]:\\|\\[\w.-]+\\", text), path.as_posix())

    def test_the_grill_method_is_written_once(self):
        # GRILL.md holds the four quadrants; the SKILL.md of each skill that grills points to it and repeats none of it.
        shared = (ROOT / "shared" / "GRILL.md").read_text(encoding="utf-8")
        self.assertIn("**Unknown unknowns**", shared)
        for name in ("grill", "define"):
            text = skill_text(name)
            self.assertIn("Read `${CLAUDE_SKILL_DIR}/GRILL.md` and follow it.", text, name)
            self.assertNotIn("**Unknown unknowns**", text, name)

    def test_the_handoff_section_is_word_for_word_the_same(self):
        copies = {name: section(skill_text(name), HANDOFF_SECTION) for name in HANDOFF_SKILLS}
        self.assertTrue(copies["define"])
        for name, copy in copies.items():
            self.assertEqual(copy, copies["define"], f"{HANDOFF_SECTION} in mreq-{name} differs from mreq-define")
            # Agents without a skill tool can only read the file; only a denied call forbids that.
            self.assertNotIn("Never read another skill's SKILL.md", skill_text(name), name)

    def test_a_skill_directory_left_as_written_is_never_run(self):
        # Only Claude Code fills in ${CLAUDE_SKILL_DIR}; elsewhere the shell reads it as empty.
        for name in SCRIPTS:
            text = section(skill_text(name), "## The script")
            self.assertIn("Never run a command or read a path that still holds `${`", text, name)
            # An empty variable makes uv fail too; switching to python would only repeat the bad path.
            self.assertIn("neither is a script path that does not exist", text, name)

    def test_reference_files_are_named_by_the_skill_directory(self):
        # A bare file name leaves the agent to guess the start; it often takes the project root.
        for path in SKILLS_DIR.rglob("*.md"):
            self.assertNotIn("from this skill's directory", path.read_text(encoding="utf-8"), path.as_posix())
        for name, shared in (("define", "GRILL.md"), ("grill", "GRILL.md"), ("how", "MERMAID.md"), ("graph", "MERMAID.md")):
            self.assertIn(f"`${{CLAUDE_SKILL_DIR}}/{shared}`", skill_text(name), name)
            self.assertTrue((SKILLS_DIR / f"mreq-{name}" / shared).is_file(), name)

    def test_a_skill_uses_only_the_files_in_its_own_directory(self):
        # A path that leaves the skill directory makes the skill need another one.
        # Only a handoff may: it reads the SKILL.md of the skill it starts.
        for path in SKILLS_DIR.rglob("*.md"):
            for target in re.findall(r"\.\./([^\s`\"')]*)", path.read_text(encoding="utf-8")):
                self.assertRegex(target, r"^mreq-[a-z]+/SKILL\.md$", path.as_posix())
        self.assertFalse((SKILLS_DIR / "mreq-shared").exists())

    def test_the_user_only_guard_takes_every_agents_invocation(self):
        for name in ("define", "close", "how", "graph"):
            text = skill_text(name)
            self.assertIn(f"typed `/mreq-{name}` (`/mreq:mreq-{name}` with the Claude Code plugin, `$mreq-{name}` in Codex)", text, name)
            self.assertNotIn("Run only when the user typed", text, name)

    def test_codex_keeps_the_user_only_skills_from_the_model(self):
        # Codex ignores disable-model-invocation; agents/openai.yaml is its switch.
        for skill in sorted(SKILLS_DIR.iterdir()):
            front = (skill / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
            user_only = "disable-model-invocation: true" in front
            self.assertEqual(user_only, skill.name.removeprefix("mreq-") in USER_ONLY, skill.name)
            yaml = skill / "agents" / "openai.yaml"
            hidden = yaml.is_file() and "allow_implicit_invocation: false" in yaml.read_text(encoding="utf-8")
            self.assertEqual(hidden, user_only, skill.name)

    def test_skill_files_end_lines_with_lf(self):
        for path in SKILLS_DIR.rglob("*"):
            if path.suffix in (".md", ".yaml"):
                self.assertNotIn(b"\r", path.read_bytes(), path.as_posix())

    def test_the_page_skills_name_their_own_kind(self):
        for name in ("how", "graph"):
            text = skill_text(name)
            self.assertIn(f"`page.py {name} new <topic-slug>`", text)
            self.assertIn(f"`page.py {name} build <content file>`", text)


if __name__ == "__main__":
    unittest.main()
