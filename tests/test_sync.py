"""tools/sync.py: each skill holds its own copy of the files in shared/, and the copies stay the same."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class SyncTest(unittest.TestCase):
    def test_every_copy_is_the_same_as_its_file_in_shared(self):
        # A failure lists the copies to fix: edit the file in shared/, then run tools/sync.py.
        run = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "sync.py"), "--check"], capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
