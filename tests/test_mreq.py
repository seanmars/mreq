"""mreq.py: the life of one task document, from new to delete."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MREQ = ROOT / "skills" / "mreq-shared" / "scripts" / "mreq.py"


class MreqTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        # Not a git repository, so the script takes this directory as the project root.
        self.root = Path(tmp.name)

    def run_mreq(self, *args):
        return subprocess.run(
            [sys.executable, str(MREQ), *args], cwd=self.root, capture_output=True, text=True, encoding="utf-8"
        )

    def new_document(self, schema="issue"):
        run = self.run_mreq("new", "--schema", schema, "--slug", "fix-it", "--title=輸入 1,000 時當掉", "--desc=One sentence.")
        self.assertEqual(run.returncode, 0, run.stderr)
        return json.loads(run.stdout)

    def test_new_writes_a_draft_from_the_template(self):
        created = self.new_document()
        path = Path(created["path"])
        self.assertEqual(path.parent.resolve(), (self.root / ".mreq").resolve())
        self.assertEqual(created["status"], "draft")
        text = path.read_text(encoding="utf-8")
        self.assertIn("# 輸入 1,000 時當掉", text)
        self.assertIn("## Root Cause", text)

    def test_every_printed_path_uses_forward_slashes(self):
        path = self.new_document()["path"]
        outputs = [path]
        for args in (("list",), ("update", path), ("progress", path), ("delete", path), ("delete", path)):
            run = self.run_mreq(*args)
            outputs.append(run.stdout + run.stderr)
        for output in outputs:
            self.assertNotIn("\\", output)

    def test_list_reports_progress_and_open_skips_done(self):
        path = self.new_document()["path"]
        listed = json.loads(self.run_mreq("list").stdout)
        self.assertEqual([item["path"] for item in listed], [path])
        self.assertEqual(listed[0]["tasks"], {"done": 0, "total": 4})
        self.run_mreq("update", path, "--status", "done")
        self.assertEqual(json.loads(self.run_mreq("list", "--open").stdout), [])
        self.assertEqual(len(json.loads(self.run_mreq("list").stdout)), 1)

    def test_update_changes_only_the_front_matter(self):
        path = self.new_document()["path"]
        before = Path(path).read_text(encoding="utf-8").split("\n---\n", 1)[1]
        updated = json.loads(self.run_mreq("update", path, "--status", "active").stdout)
        self.assertEqual(updated["status"], "active")
        self.assertEqual(Path(path).read_text(encoding="utf-8").split("\n---\n", 1)[1], before)

    def test_progress_names_the_first_unchecked_task(self):
        path = Path(self.new_document()["path"])
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("- [ ] 1. Reproduce", "- [x] 1. Reproduce"), encoding="utf-8")
        lines = self.run_mreq("progress", str(path)).stdout.splitlines()
        self.assertEqual(lines[0], f"Using: {path.as_posix()}")
        self.assertEqual(lines[1], "issue: 1/4 tasks done. Next: 2. Confirm the root cause")

    def test_delete_refuses_a_file_outside_the_documents_folder(self):
        other = self.root / "notes.md"
        other.write_text("# Notes\n", encoding="utf-8")
        run = self.run_mreq("delete", str(other))
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("not a task document", run.stderr)
        self.assertTrue(other.exists())

    def test_delete_removes_the_document(self):
        path = self.new_document()["path"]
        self.assertEqual(json.loads(self.run_mreq("delete", path).stdout), {"path": path, "deleted": True})
        self.assertFalse(Path(path).exists())


if __name__ == "__main__":
    unittest.main()
