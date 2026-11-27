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
# The briefs the two subagents of mreq-apply's orchestrate mode read.
BRIEFS = ("IMPLEMENTER.md", "VERIFIER.md")
# A subagent reads only its brief, so the implementer's brief repeats these rules of mreq-apply word for word.
IMPLEMENTER_RULES = (
    "Never delete, skip, or weaken a test to get to green. Fix the code.",
    "To prove a test catches the bug, revert the fix by editing the file, run the test, then restore it.",
    "Write scratch files for a check inside the project, never outside it (no `/tmp`, no `$TEMP`). When the document names a scratch file, use that name.",
    "Prove it works by running something: a test, the repro, or a command that would fail if you were wrong. Reading the code is not proof. When nothing you can run reaches the behavior, say so in the report.",
    "- **`feature`**: build only what `## Scope` puts in. Add no flexibility for later.",
    "Fix the cause, not the symptom; when a shared function causes it, fix that function and check its other callers.",
    "pin the behavior first (the `## Behavior Pin` test or command) and keep it green after every step. Change no behavior.",
    "- **`task`**: do the task as `## Goal` describes it.",
)


def skill_text(name: str) -> str:
    return (SKILLS_DIR / f"mreq-{name}" / "SKILL.md").read_text(encoding="utf-8")


def brief_text(name: str) -> str:
    return (SKILLS_DIR / "mreq-apply" / name).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    """The lines from a "## " or "### " heading up to the next heading of its level or above."""
    level = len(heading) - len(heading.lstrip("#"))
    for part in re.split(rf"(?m)^(?=#{{2,{level}}} )", text):
        if part.split("\n", 1)[0] == heading:
            return part.strip()
    return ""


def orchestrate_mode() -> str:
    return section(skill_text("apply"), "## Orchestrate mode")


def orchestrator_loop() -> str:
    return brief_text("ORCHESTRATOR.md")


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
        references = (("define", "GRILL.md"), ("grill", "GRILL.md"), ("how", "MERMAID.md"), ("graph", "MERMAID.md"), ("apply", "ORCHESTRATOR.md"))
        for name, reference in references:
            self.assertIn(f"`${{CLAUDE_SKILL_DIR}}/{reference}`", skill_text(name), name)
            self.assertTrue((SKILLS_DIR / f"mreq-{name}" / reference).is_file(), name)

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

    def test_a_prompt_handoff_is_written_at_both_ends(self):
        # The earlier skill names the command to type next; the later one says what it takes from that reply.
        for earlier, later in (("terms", "pro"), ("terms", "define"), ("pro", "define")):
            self.assertIn(f"`/mreq-{later}` (`$mreq-{later}` in Codex) with no", skill_text(earlier), earlier)
            self.assertIn(f"reply from mreq-{earlier}", skill_text(later), later)

    def test_the_orchestrator_loop_is_written_once(self):
        # A loop in SKILL.md costs its tokens in every run of the skill, also with the mode off.
        mode = orchestrate_mode()
        self.assertIn("read that file in full before you spawn the first subagent", mode)
        self.assertIn("read it again when you take a phase and the loop is no longer in your context", mode)
        self.assertNotIn("**Act on the verdict.**", skill_text("apply"))
        self.assertIn("**Act on the verdict.**", orchestrator_loop())

    def test_the_orchestrate_briefs_are_read_by_an_absolute_path(self):
        loop = orchestrator_loop()
        for brief in BRIEFS:
            self.assertIn(f"`${{CLAUDE_SKILL_DIR}}/{brief}`, written as an absolute path", loop, brief)
        self.assertIn('argument-hint: "[<path>] [--orch]"', skill_text("apply"))

    def test_the_implementer_brief_keeps_the_rules_it_copies(self):
        implementer = brief_text("IMPLEMENTER.md")
        for rule in IMPLEMENTER_RULES:
            self.assertIn(rule, skill_text("apply"), rule)
            self.assertIn(rule, implementer, rule)

    def test_only_the_orchestrator_writes_the_document(self):
        # Two writers of one document lose each other's edits: update rewrites the whole file.
        self.assertIn("only you write the document", orchestrate_mode())
        self.assertIn("Never edit the document", brief_text("IMPLEMENTER.md"))
        self.assertIn("not the source code, not the document", brief_text("VERIFIER.md"))

    def test_the_verifier_is_not_told_what_the_implementer_concluded(self):
        loop = orchestrator_loop()
        self.assertIn("Give it nothing else from the implementer's report", loop)
        # The file list is the one part of that report the verifier gets, so a line holds a path and the kind of change only.
        self.assertIn("(each path with `created`, `changed` or `deleted`, and no other word from a line)", loop)
        implementer = brief_text("IMPLEMENTER.md")
        self.assertIn("its path, then `created`, `changed` or `deleted`, and nothing else", implementer)
        self.assertIn("A file you changed for a check and then restored is not in this list", implementer)

    def test_orchestrate_mode_needs_a_request_not_only_the_word(self):
        # The mode costs more tokens, so a document about an orchestrator must not turn it on.
        mode = orchestrate_mode()
        self.assertIn("The mode is on when the input holds `--orch`, or when the user asks for this mode", mode)
        self.assertIn("The word alone does not turn it on", mode)
        self.assertIn("When you cannot tell, the mode is off.", mode)

    def test_every_skill_that_writes_tasks_names_the_phase_heading(self):
        # mreq-define writes the headings; mreq-grill and mreq-apply must keep them when they add tasks.
        self.assertIn("`### <phase name>` heading in `## Tasks`", skill_text("define"))
        for name in ("grill", "apply"):
            self.assertIn("`### ` heading in `## Tasks`", skill_text(name), name)

    def test_the_refactor_pin_is_a_phase_of_its_own(self):
        # A verifier comes after the whole phase: it can run the pin against the unchanged code only when no other task shares the phase.
        self.assertIn("the pin task alone under the first one", skill_text("define"))
        self.assertIn("the pin task stays alone in the first phase", skill_text("grill"))
        loop = orchestrator_loop()
        self.assertIn("the pin task (the first task) is always a phase of its own", loop)
        self.assertIn("split that phase in two", loop)
        template = (SKILLS_DIR / "mreq-define" / "templates" / "refactor.md").read_text(encoding="utf-8")
        phases = re.split(r"(?m)^### .*\n", section(template, "## Tasks"))[1:]
        self.assertEqual(len(phases), 2)
        self.assertEqual(re.findall(r"(?m)^- \[ \] (\d+)\.", phases[0]), ["1"])

    def test_a_check_that_did_not_run_names_its_reason(self):
        # Only a denied command is solved by an allow rule. A check the verifier's rules keep it from needs the user's choice.
        verifier = brief_text("VERIFIER.md")
        report = section(verifier, "### Not run")
        loop = orchestrator_loop()
        for reason in ("denied", "cannot reproduce", "no safe path"):
            self.assertIn(f"under **Not run** as `{reason}`", verifier, reason)
            self.assertIn(f"`{reason}` (", report, reason)
        self.assertIn("Any item is `denied`: it is the denied-command case of \"When to stop and ask\"", loop)
        self.assertIn("Otherwise (`cannot reproduce`, `no safe path`)", loop)
        self.assertIn("add nothing to a verifier's prompt", loop)
        self.assertIn('**Work it here** (see "Work it here"), **Accept by reading**', loop)

    def test_what_the_verifier_found_unasked_reaches_the_document(self):
        # Only the orchestrator reads the verifier's report: what it does not write down, the user never learns.
        loop = orchestrator_loop()
        self.assertIn("Write each item under the verifier's **Not asked for** into `## Open` as `- Follow-up: <what>`, and say in it that the document did not ask for it", loop)
        self.assertIn("Write no item that `## Open` already holds.", loop)
        # Each item costs the user a decision, so how the code is built stays out.
        verifier = brief_text("VERIFIER.md")
        self.assertIn("Behavior the code adds that the document did not mention", verifier)
        self.assertIn("How the code is built (a helper function, a name, one more test case) does not go there.", verifier)
        self.assertIn("Each behavior the code adds that the document never asked for", section(verifier, "### Not asked for"))

    def test_the_briefs_say_where_commands_start(self):
        # A subagent that is not sure of its directory puts a path in front of its first command, and no allow rule matches that.
        run_rule = "- Run every command on its own: no `cd`, `&&`, `||`, `;`, `|` or `$()`."
        self.assertIn(run_rule.removeprefix("- "), section(skill_text("apply"), "## When a tool call is denied"))
        rules = [next(line for line in brief_text(brief).splitlines() if line.startswith(run_rule)) for brief in BRIEFS]
        self.assertEqual(*rules)
        self.assertIn("Your commands already start in the project root, the directory that holds `.mreq/`", rules[0])
        self.assertIn("put nothing between `git` and its subcommand (no `-C <path>`, no `-c <setting>`)", rules[0])
        self.assertIn("The user allows a command by its first words", rules[0])
        for brief in BRIEFS:
            self.assertIn("no `-C`, no `-c`, no `cd` in front", brief_text(brief), brief)

    def test_a_file_a_check_left_does_not_fail_the_phase(self):
        # A removal proves nothing about the work: when it is denied, every check may still have passed.
        verifier = brief_text("VERIFIER.md")
        self.assertIn("After the check, remove what it wrote there, with one command", verifier)
        self.assertIn("Give a path inside the project, never outside it", verifier)
        self.assertIn("the removal of a file a check left goes under **Left behind**", verifier)
        self.assertIn("**Left behind** does not change the verdict", verifier)
        self.assertIn("### Left behind\n", verifier)
        implementer = brief_text("IMPLEMENTER.md")
        self.assertIn("The removal of a scratch file is the one exception", implementer)
        self.assertIn("name the file under **Left behind** and go on", implementer)
        self.assertIn("A command or an edit is denied, except the removal of a scratch file", implementer)
        loop = orchestrator_loop()
        self.assertIn("each file under **Left behind**, in either report, as `- Follow-up: remove <path>`", loop)
        self.assertIn("A file left behind is no finding and no reason to stop.", loop)

    def test_what_a_report_found_is_written_before_the_orchestrator_acts(self):
        # A new implementer gets only the findings, and a stop ends the run: what is not in the document by then is lost.
        leaves = section(orchestrator_loop(), "## What a report leaves in the document")
        self.assertIn("As soon as you read a report, and before you act on it", leaves)
        self.assertIn("each of the implementer's **Follow-ups**, as `- Follow-up: <what>`", leaves)
        loop = section(orchestrator_loop(), "## The loop")
        for step in ("2. **Act on its report.**", "4. **Act on the verdict.**"):
            self.assertIn(f'{step} First do as "What a report leaves in the document" gives.', loop, step)

    def test_working_a_phase_here_lifts_the_rule_against_editing(self):
        # The loop offers the answer, so the rule that forbids its work must name it.
        self.assertIn("The one exception is a phase the user tells you to work yourself (**Work it here** in that file).", orchestrate_mode())
        here = section(orchestrator_loop(), "## Work it here")
        self.assertIn("For this phase the rule against reading and editing source code does not apply.", here)
        self.assertIn("Do what step 2 left out", here)
        self.assertIn("A task the implementer reported done is not proved.", here)

    def test_done_needs_a_test_run_after_the_last_change(self):
        # A verifier's run proves the code it saw. A phase worked or accepted later is not in that proof.
        finish = section(orchestrator_loop(), "## Step 5 in this mode")
        self.assertIn("counts when it passed and no code changed after it", finish)
        self.assertIn("You worked a phase yourself after that run: run the related tests as step 5 gives.", finish)
        self.assertIn("the check that did not run is the test command: the tests have not passed. Do not set `done`.", finish)
        self.assertIn("does not keep the document from `done`", finish)

    def test_the_second_failed_verification_is_counted_in_one_run(self):
        # The document holds no counter, so a count across sessions would rest on how an agent reads the Handoff.
        loop = orchestrator_loop()
        self.assertIn("the second verification of the same phase that fails with findings", loop)
        self.assertIn("Count only this run of the skill, and only a `fail` with findings.", loop)

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
