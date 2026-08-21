#!/usr/bin/env python3
"""The factory must not recreate the removed learning-path product."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NoLearningPathContractTests(unittest.TestCase):
    def test_factory_contracts_use_task_document_navigation(self) -> None:
        files = [
            ROOT / "SKILL.md",
            ROOT / "references/tutorial-site-contract.md",
            ROOT / "scripts/scaffold_career_package.py",
            ROOT / "scripts/validate_public_release.py",
            ROOT / "scripts/validate_career_package.py",
        ]
        forbidden = [
            "professional learning pathway",
            "Minimum distributable learning path",
            "end-to-end learner path",
            "firstUsablePath",
            "## 学习路线",
            "pilot-path",
        ]
        findings = []
        for path in files:
            text = path.read_text(encoding="utf-8")
            findings.extend(f"{path.name}: {token}" for token in forbidden if token in text)
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
