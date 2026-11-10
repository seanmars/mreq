"""The plugin's version and description are written in more than one file; they must agree."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class ManifestTest(unittest.TestCase):
    def setUp(self):
        self.plugin = load("plugin.json")
        self.entry = load(".claude-plugin/marketplace.json")["plugins"][0]

    def test_the_version_is_the_same_everywhere(self):
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        latest = re.search(r"(?m)^## (\d+\.\d+\.\d+)$", changelog).group(1)
        self.assertEqual(self.plugin["version"], latest)
        self.assertEqual(self.entry["version"], latest)

    def test_the_two_manifests_describe_the_same_plugin(self):
        self.assertTrue(self.plugin["description"])
        for key in ("name", "description", "keywords", "homepage", "repository", "license"):
            self.assertEqual(self.plugin[key], self.entry[key], key)


if __name__ == "__main__":
    unittest.main()
