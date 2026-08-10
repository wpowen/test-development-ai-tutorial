#!/usr/bin/env python3
"""Regression tests for public release isolation and cross-artifact closure."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_public_release import normalized_hash, validate_release


class PublicReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        pages = [{
            "page_id": f"P{index}", "module_id": "M1", "delivery_status": "desk-researched",
            "title": f"Page {index}", "slug": f"p{index}", "learner_result": "checked result",
        } for index in range(8)]
        tutorial = {
            "release_scope": {"mode": "pilot-path", "promised_page_ids": [page["page_id"] for page in pages]},
            "modules": [{"module_id": "M1", "title": "Module"}], "pages": pages,
        }
        embedded = {
            "modules": [{"id": "M1", "title": "Module"}],
            "pages": [{"id": page["page_id"], "moduleId": "M1", "status": "desk-researched"} for page in pages],
        }
        self.write_json("tutorial/tutorial-site.json", tutorial)
        self.write("tutorial/README.md", "# Tutorial\n\nAll published lessons have actions and checks.\n")
        self.write("site/index.html", f"<html><script>const COURSE_DATA={json.dumps(embedded)};const DATA=COURSE_DATA</script></html>")
        manifest = {
            "schema_version": "1.2", "source_commit": "abc", "release_scope": "pilot-path",
            "catalog_complete": False, "page_count": 8, "delivered_page_count": 8,
            "promised_page_ids": [page["page_id"] for page in pages],
            "validation_verdict": "PASS", "publication_targets": ["github-pages", "chatgpt-site"],
            "learner_artifact_roots": ["site", "tutorial"], "content_hash": "",
        }
        manifest["content_hash"] = normalized_hash(self.root, manifest["learner_artifact_roots"])
        self.write_json("RELEASE-MANIFEST.json", manifest)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_json(self, relative: str, data: object) -> None:
        self.write(relative, json.dumps(data))

    def refresh_hash(self) -> None:
        path = self.root / "RELEASE-MANIFEST.json"
        manifest = json.loads(path.read_text())
        manifest["content_hash"] = normalized_hash(self.root, manifest["learner_artifact_roots"])
        self.write_json("RELEASE-MANIFEST.json", manifest)

    def test_valid_public_release_passes(self) -> None:
        self.assertEqual(validate_release(self.root), [])

    def test_extra_search_index_cannot_publish_planned_page(self) -> None:
        self.write_json("site/search-index.json", [{"page_id": "LEAK", "title": "Leak", "status": "planned"}])
        self.refresh_hash()
        self.assertTrue(any("search-index.json" in error for error in validate_release(self.root)))

    def test_html_extra_navigation_id_fails(self) -> None:
        path = self.root / "site/index.html"
        self.write("site/index.html", path.read_text().replace("</html>", '<button data-page-id="LEAK">Leak</button></html>'))
        self.refresh_hash()
        self.assertTrue(any("unknown data-page-id=LEAK" in error for error in validate_release(self.root)))

    def test_course_tree_placeholder_fails(self) -> None:
        self.write("tutorial/course-tree.md", "# Tree\n\n仅保留知识位置\n")
        self.refresh_hash()
        self.assertTrue(any("placeholder copy" in error for error in validate_release(self.root)))

    def test_internal_course_package_is_forbidden(self) -> None:
        self.write_json("course-package/curriculum.json", {"courses": [{"delivery_status": "planned"}]})
        self.assertTrue(any("internal course-package" in error for error in validate_release(self.root)))

    def test_release_json_cannot_contain_planned_curriculum(self) -> None:
        self.write_json("docs/curriculum.json", {"courses": [{"delivery_status": "planned"}]})
        self.assertTrue(any("docs/curriculum.json" in error for error in validate_release(self.root)))

    def test_manifest_hash_drift_fails(self) -> None:
        self.write("tutorial/README.md", "changed")
        self.assertTrue(any("content_hash" in error for error in validate_release(self.root)))


if __name__ == "__main__":
    unittest.main()
