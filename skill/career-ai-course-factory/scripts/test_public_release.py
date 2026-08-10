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
            "architecture": {"title": "Workflow", "caption": "Evidence and decision flow", "nodes": ["input", "analysis", "artifact", "execution", "decision"]},
            "materials": [{"title": "Guide", "description": "Learner handoff", "href": "materials/guide.md", "kind": "guide", "validation": "static-reviewed"}],
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
        self.write("site/materials/guide.md", "# Guide\n\nRun the checked workflow.\n")
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

    def test_tutorial_html_extra_navigation_id_fails(self) -> None:
        self.write("tutorial/index.html", '<button data-page-id="LEAK">Leak</button>')
        self.refresh_hash()
        self.assertTrue(any("tutorial/index.html" in error and "LEAK" in error for error in validate_release(self.root)))

    def test_every_incomplete_state_is_rejected_in_search_js(self) -> None:
        for status in ("planned", "outlined", "blocked"):
            with self.subTest(status=status):
                path = self.root / "site/search-index.js"
                self.write("site/search-index.js", f'window.SEARCH=[{{page_id:"LEAK",status:"{status}"}}]')
                self.refresh_hash()
                errors = validate_release(self.root)
                self.assertTrue(any("search-index.js" in error and status in error for error in errors), errors)
                path.unlink()

    def test_sitemap_xml_cannot_publish_incomplete_state(self) -> None:
        self.write("site/sitemap.xml", "<url><status>planned</status></url>")
        self.refresh_hash()
        self.assertTrue(any("sitemap.xml" in error and "planned" in error for error in validate_release(self.root)))

    def test_secondary_html_cannot_publish_incomplete_state(self) -> None:
        self.write("site/search.html", '<article data-page-id="P1" data-status="outlined"></article>')
        self.refresh_hash()
        self.assertTrue(any("search.html" in error and "outlined" in error for error in validate_release(self.root)))

    def test_markdown_frontmatter_cannot_publish_incomplete_state(self) -> None:
        self.write("courses/catalog.md", "---\ndelivery_status: blocked\n---\n")
        self.assertTrue(any("courses/catalog.md" in error and "blocked" in error for error in validate_release(self.root)))

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

    def test_missing_linked_material_fails(self) -> None:
        (self.root / "site/materials/guide.md").unlink()
        self.assertTrue(any("missing or empty file" in error for error in validate_release(self.root)))

    def test_missing_architecture_fails(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text())
        del data["pages"][0]["architecture"]
        self.write_json("tutorial/tutorial-site.json", data)
        self.refresh_hash()
        self.assertTrue(any("architecture/workflow" in error for error in validate_release(self.root)))


if __name__ == "__main__":
    unittest.main()
