"""page.py: one script builds the pages of mreq-how and mreq-graph."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "skills" / "mreq-shared" / "scripts" / "page.py"

SECTION = '<section id="overview"><h2>Overview</h2><p>Text.</p></section>\n'
FIGURE = """<figure class="diagram">
  <script type="text/x-mermaid">
flowchart TD
  a[Start] --> b[End]
  </script>
  <figcaption>From start to end.</figcaption>
</figure>
"""
HOW = "lang: en\ntitle: The title\nquestion: The question\nmeta: 2026-11-10\n---\n" + SECTION
GRAPH = "lang: en\ntitle: The title\nrequest: The request\nmeta:\n---\n" + f'<section id="flow"><h2>Flow</h2>{FIGURE}</section>\n'


class PageTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        # The script writes under the directory it runs in, so each test gets its own.
        self.root = Path(tmp.name)

    def run_page(self, *args):
        return subprocess.run(
            [sys.executable, str(PAGE), *args], cwd=self.root, capture_output=True, text=True, encoding="utf-8"
        )

    def content_file(self, kind, text):
        run = self.run_page(kind, "new", "topic")
        self.assertEqual(run.returncode, 0, run.stderr)
        path = Path(run.stdout.strip())
        path.write_text(text, encoding="utf-8")
        return path

    def built_page(self, content):
        return content.with_name(content.name.replace(".content.html", ".html"))

    def test_new_puts_each_kind_in_its_own_ignored_folder(self):
        for kind in ("how", "graph"):
            content = self.content_file(kind, "")
            self.assertEqual(content.parent.resolve(), (self.root / ".mreq" / kind).resolve())
            self.assertEqual((content.parent / ".gitignore").read_text(encoding="utf-8"), "*\n")

    def test_how_builds_a_page_without_a_diagram(self):
        content = self.content_file("how", HOW)
        run = self.run_page("how", "build", str(content))
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertIn("ok: no diagrams", run.stdout)
        html = self.built_page(content).read_text(encoding="utf-8")
        self.assertIn("The question", html)
        self.assertIn(SECTION.strip(), html)
        self.assertNotIn("{{", html.split("<script>")[0])

    def test_graph_builds_a_page_with_a_diagram(self):
        content = self.content_file("graph", GRAPH)
        run = self.run_page("graph", "build", str(content))
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertIn("ok: 1 diagram(s)", run.stdout)
        self.assertIn("The request", self.built_page(content).read_text(encoding="utf-8"))

    def test_graph_refuses_a_page_without_a_diagram(self):
        content = self.content_file("graph", GRAPH.replace(FIGURE, "<p>Text.</p>"))
        run = self.run_page("graph", "build", str(content))
        self.assertEqual(run.returncode, 1)
        self.assertIn("FAIL no diagrams", run.stdout)
        self.assertFalse(self.built_page(content).exists())

    def test_each_kind_takes_only_its_own_header(self):
        for kind, text in (("how", HOW.replace("question:", "request:")), ("graph", GRAPH.replace("request:", "question:"))):
            run = self.run_page(kind, "build", str(self.content_file(kind, text)))
            self.assertEqual(run.returncode, 1)
            self.assertIn("unknown header line", run.stdout)

    def test_build_refuses_a_content_file_of_the_other_kind(self):
        content = self.content_file("how", HOW)
        run = self.run_page("graph", "build", str(content))
        self.assertEqual(run.returncode, 1)
        self.assertIn("is not under", run.stdout)

    def test_fixed_colors_fail_the_build(self):
        content = self.content_file("graph", GRAPH.replace("a[Start] --> b[End]", "a[Start] --> b[End]\n  style a fill:#f00"))
        run = self.run_page("graph", "build", str(content))
        self.assertEqual(run.returncode, 1)
        self.assertIn("fixed colors", run.stdout)

    def test_messages_name_the_file_that_holds_the_rule(self):
        # The figure and the colors are in mreq-shared/MERMAID.md, not in a skill's WRITING.md.
        mermaid = (ROOT / "skills" / "mreq-shared" / "MERMAID.md").read_text(encoding="utf-8")
        self.assertIn("## Colors", mermaid)
        self.assertIn("## The figure", mermaid)
        colors = GRAPH.replace("a[Start] --> b[End]", "a[Start] --> b[End]\n  style a fill:#f00")
        loose = GRAPH.replace(FIGURE, '<script type="text/x-mermaid">\nflowchart TD\n  a --> b\n</script>')
        for text, expected in ((colors, "(MERMAID.md, Colors)"), (loose, "as MERMAID.md shows")):
            run = self.run_page("graph", "build", str(self.content_file("graph", text)))
            self.assertEqual(run.returncode, 1)
            self.assertIn(expected, run.stdout)

    def test_every_printed_path_uses_forward_slashes(self):
        new = self.run_page("how", "new", "topic")
        content = Path(new.stdout.strip())
        content.write_text(HOW, encoding="utf-8")
        built = self.run_page("how", "build", new.stdout.strip())
        self.assertEqual(built.returncode, 0, built.stdout)
        outside = self.root / "elsewhere.content.html"
        outside.write_text(HOW, encoding="utf-8")
        refused = self.run_page("how", "build", str(outside))
        self.assertIn("is not under", refused.stdout)
        for output in (new.stdout, built.stdout, refused.stdout):
            self.assertNotIn("\\", output)
        # The printed path is the real file, so the agent can pass it on as it is.
        self.assertTrue(Path(built.stdout.strip().splitlines()[-1]).is_file())

    def test_a_missing_or_unknown_kind_prints_the_usage(self):
        for args in ((), ("new", "topic"), ("other", "new", "topic"), ("how", "dir")):
            run = self.run_page(*args)
            self.assertEqual(run.returncode, 2)
            self.assertIn("usage: page.py <how|graph>", run.stderr)
        self.assertFalse((self.root / ".mreq").exists())


if __name__ == "__main__":
    unittest.main()
