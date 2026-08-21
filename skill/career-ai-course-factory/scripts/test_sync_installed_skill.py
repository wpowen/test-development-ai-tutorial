import tempfile
import unittest
from pathlib import Path

from sync_installed_skill import sync


class SkillSyncTests(unittest.TestCase):
    def test_check_detects_drift_and_sync_restores_exact_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "canonical"; target = root / "installed"
            source.mkdir(); (source / "SKILL.md").write_text("v1\n", encoding="utf-8")
            self.assertFalse(sync(source, target, write=False))
            self.assertTrue(sync(source, target, write=True))
            (source / "SKILL.md").write_text("v2\n", encoding="utf-8")
            self.assertFalse(sync(source, target, write=False))
            self.assertTrue(sync(source, target, write=True))
            self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "v2\n")


if __name__ == "__main__":
    unittest.main()
