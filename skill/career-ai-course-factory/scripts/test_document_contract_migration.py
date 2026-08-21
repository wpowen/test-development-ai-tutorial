#!/usr/bin/env python3
"""Regression tests for the task-oriented document contract migration."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from test_validator import build_valid
from validate_career_package import validate


class DocumentContractMigrationTests(unittest.TestCase):
    def test_tutorial_contract_accepts_task_navigation_and_split_static_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid(root)

            readme = root / "tutorial/README.md"
            index = root / "tutorial/index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace("COURSE_DATA", "COURSE_INDEX"),
                encoding="utf-8",
            )

            errors = validate(root)
            tutorial_contract_errors = [
                error for error in errors
                if "tutorial file" in error or "missing viewer marker" in error
            ]
            self.assertEqual(tutorial_contract_errors, [])

    def test_new_document_contract_replaces_learning_path_and_page_type(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid(root)
            site_path = root / "tutorial/tutorial-site.json"
            site = json.loads(site_path.read_text(encoding="utf-8"))
            site["release_scope"]["mode"] = "validated-subset"
            for page in site["pages"]:
                page.pop("page_type", None)
                page.update({
                    "document_type": "professional-how-to",
                    "reader_job": "do",
                    "audience": ["practitioner"],
                    "scope": {
                        "inScope": ["execute the bounded task"],
                        "outOfScope": ["production effectiveness"],
                        "assumptions": ["fixture inputs are available"],
                    },
                    "claims": ["The bounded fixture demonstrates the documented procedure."],
                    "document_contract": {
                        "documentType": "professional-how-to",
                        "readerJob": "do",
                        "audience": ["practitioner"],
                        "scope": {
                            "inScope": ["execute the bounded task"],
                            "outOfScope": ["production effectiveness"],
                            "assumptions": ["fixture inputs are available"],
                        },
                        "claims": ["The bounded fixture demonstrates the documented procedure."],
                        "procedure": {
                            "prerequisites": [],
                            "inputs": ["fixture"],
                            "steps": ["run"],
                            "expectedResults": ["PASS"],
                            "recovery": ["preserve failure evidence"],
                            "rollback": "restore the fixture",
                        },
                    },
                    "delivery_mode": "guided-lab",
                })
            site_path.write_text(json.dumps(site), encoding="utf-8")
            errors = validate(root)
            migration_errors = [
                error for error in errors
                if any(token in error for token in ("page_type", "document_type", "document contract", "学习路线", "pilot-path"))
            ]
            self.assertEqual(migration_errors, [])


if __name__ == "__main__":
    unittest.main()
