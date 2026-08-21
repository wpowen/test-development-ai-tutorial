#!/usr/bin/env python3
"""Regression tests for public release isolation and cross-artifact closure."""

from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from validate_public_release import file_hash, normalized_hash, validate_release


class PublicReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        pages = [{
            "page_id": f"P{index}", "module_id": "M1", "delivery_status": "desk-researched",
            "display_number": index + 1,
            "title": f"Page {index}", "slug": f"p{index}", "learner_result": "checked result",
            "architecture": {"title": "Workflow", "caption": "Evidence and decision flow", "nodes": ["input", "analysis", "artifact", "execution", "decision"]},
            "materials": [{"title": "Guide", "description": "Learner handoff", "href": "materials/guide.md", "kind": "guide", "validation": "static-reviewed"}],
        } for index in range(8)]
        tutorial = {
            "release_scope": {"mode": "validated-subset", "promised_page_ids": [page["page_id"] for page in pages]},
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
        page_ids = [page["page_id"] for page in pages]
        self.write_json("CATALOG-MANIFEST.json", {
            "schema_version":"1.0", "catalog_id":"career-ai", "page_ids":page_ids,
            "previous_validated_page_ids":page_ids,
        })
        self.write_json("EXECUTABILITY-MANIFEST.json", {
            "schema_version":"1.0", "audit_id":"release-audit", "audited_at":"2026-01-01T00:00:00Z",
            "pages":[{"page_id":page_id,"verdict":"PASS","finding_count":0} for page_id in page_ids],
        })
        guide_hash = file_hash(self.root / "site/materials/guide.md")
        self.write_json("PAGE-PROMOTION-MANIFEST.json", {
            "schema_version":"1.0", "pages":[{
                "page_id":page_id, "verdict":"PASS", "research_package_complete":True,
                "editorial_score":95, "boundary_preservation_score":100,
                "executability_verdict":"PASS", "material_hashes":{"materials/guide.md":guide_hash},
            } for page_id in page_ids],
        })
        archive_path = self.root / "COURSE-RELEASE.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.write(self.root / "site/materials/guide.md", "site/materials/guide.md")
        self.write_json("ARTIFACT-CLOSURE.json", {
            "schema_version":"1.0", "canonical_catalog_ref":"CATALOG-MANIFEST.json",
            "canonical_catalog_hash":file_hash(self.root / "CATALOG-MANIFEST.json"),
            "tutorial_ref":"tutorial/tutorial-site.json",
            "tutorial_hash":file_hash(self.root / "tutorial/tutorial-site.json"),
            "archive_ref":"COURSE-RELEASE.zip",
            "material_entries":[{
                "page_id":page_id, "href":"materials/guide.md", "dist_ref":"site/materials/guide.md",
                "archive_member":"site/materials/guide.md", "sha256":guide_hash,
            } for page_id in page_ids],
        })
        self.write_json("CAPABILITY-PROFILES.json", {
            "schema_version":"1.0",
            "pages":[{
                "page_id":page_id, "capabilities":["ai-system-evaluation"],
                "rationale":"The page evaluates AI-related behavior through an independent evidence gate.",
                "risk":"Plausible output could pass without evidence.", "reviewer":"independent reviewer",
                "reviewed_at":"2026-01-01T00:00:00Z", "evidence_refs":["EXECUTABILITY-MANIFEST.json"],
            } for page_id in page_ids],
        })
        self.write_json("PROFESSIONAL-EVIDENCE.json", {
            "schema_version":"1.0",
            "pages":[{
                "page_id":page_id, "maturity_claim":"desk-researched",
                "model":{"status":"NOT_RUN", "receipt_refs":[], "limitations":"No real model run."},
                "integration":{"status":"NOT_RUN", "receipt_refs":[], "limitations":"No target integration."},
                "clean_room":{"status":"NOT_RUN", "receipt_refs":[], "limitations":"No clean-room command is claimed by this static page."},
                "practitioner":{"status":"NOT_RUN", "receipt_refs":[], "limitations":"No practitioner review."},
                "learner":{"status":"NOT_RUN", "receipt_refs":[], "limitations":"No learner study."},
            } for page_id in page_ids],
        })
        self.write_json("STATUS-REGISTRY.json", {
            "schema_version":"1.0", "records":[{
                "record_id":"release-verdict", "artifact_type":"release-verdict", "scope_id":"public-tutorial",
                "path":"RELEASE-MANIFEST.json", "as_of":"2026-01-01T00:00:00Z", "status":"current",
                "page_ids":page_ids, "supersedes":[], "evidence_refs":["EXECUTABILITY-MANIFEST.json"],
            }],
        })
        self.write_json("SOURCE-ASSIMILATION-MANIFEST.json", {
            "schema_version":"1.0", "source_count":1, "section_count":2, "atom_count":2,
            "accounted_section_count":2, "accounted_atom_count":2, "unaccounted_ids":[], "verdict":"PASS",
        })
        self.write_json("SOURCE-SEMANTIC-PROJECTION.json", {
            "schema_version":"1.0", "verdict":"PASS",
            "units":[{
                "unit_id":"SEM-1", "function_kind":"visual", "status":"projected",
                "page_ids":page_ids, "visual_refs":[f"site/visuals/{page_id}.svg" for page_id in page_ids],
                "reusable_asset_refs":["site/materials/guide.md"], "exercise_refs":[],
            }],
            "coverage":{"required_source_item_ids":["A-1"], "covered_source_item_ids":["A-1"], "unaccounted_source_item_ids":[], "verdict":"PASS"},
        })
        self.write_json("LEARNER-USABILITY-REUSE.json", {
            "schema_version":"1.0", "verdict":"PASS-DESIGN",
            "pages":[{"page_id":page_id, "display_number":index + 1} for index, page_id in enumerate(page_ids)],
        })
        for index, page_id in enumerate(page_ids):
            self.write(f"site/visuals/{page_id}.svg", f'<svg xmlns="http://www.w3.org/2000/svg"><title>{page_id}</title></svg>')
        self.write_json("VISUAL-SEQUENCE-MANIFEST.json", {
            "schema_version":"1.0", "ordered_page_ids":page_ids, "verdict":"PASS",
            "pages":[{
                "page_id":page_id, "display_number":index + 1,
                "visuals":[{"source_path":f"site/visuals/{page_id}.svg"}],
            } for index, page_id in enumerate(page_ids)],
        })
        self.write_json("site/evidence/solution-receipt.json", {"receipt_id":"R1","verdict":"PASS"})
        self.write_json("SOLUTION-MANIFEST.json", {
            "schema_version":"1.0", "source_contract_hash":"sha256:source-contract",
            "solution_units":[{
                "solution_id":"SOLUTION-1", "page_ids":[page["page_id"] for page in pages],
                "design_status":"complete", "execution_status":"fixture-tested",
                "practitioner_review_status":"reviewed", "publication_status":"pilot",
                "architecture_view_kinds":["context","building-block","runtime","deployment","data-flow","security-trust-boundary"],
                "acceptance_gate_status":"pass", "execution_receipt_refs":["site/evidence/solution-receipt.json"],
                "residual_risk_count":1,
            }],
        })
        manifest = {
            "schema_version": "1.2", "source_commit": "abc", "release_scope": "validated-subset",
            "catalog_complete": False, "page_count": 8, "delivered_page_count": 8,
            "promised_page_ids": [page["page_id"] for page in pages],
            "validation_verdict": "PASS", "publication_targets": ["github-pages", "chatgpt-site"],
            "learner_artifact_roots": ["site", "tutorial"], "content_hash": "",
            "solution_manifest_hash": file_hash(self.root / "SOLUTION-MANIFEST.json"),
            "catalog_manifest_hash": file_hash(self.root / "CATALOG-MANIFEST.json"),
            "promotion_manifest_hash": file_hash(self.root / "PAGE-PROMOTION-MANIFEST.json"),
            "executability_manifest_hash": file_hash(self.root / "EXECUTABILITY-MANIFEST.json"),
            "artifact_closure_hash": file_hash(self.root / "ARTIFACT-CLOSURE.json"),
            "capability_profiles_hash": file_hash(self.root / "CAPABILITY-PROFILES.json"),
            "professional_evidence_hash": file_hash(self.root / "PROFESSIONAL-EVIDENCE.json"),
            "status_registry_hash": file_hash(self.root / "STATUS-REGISTRY.json"),
            "source_assimilation_hash": file_hash(self.root / "SOURCE-ASSIMILATION-MANIFEST.json"),
            "source_semantic_projection_hash": file_hash(self.root / "SOURCE-SEMANTIC-PROJECTION.json"),
            "learner_usability_reuse_hash": file_hash(self.root / "LEARNER-USABILITY-REUSE.json"),
            "visual_sequence_hash": file_hash(self.root / "VISUAL-SEQUENCE-MANIFEST.json"),
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

    def test_fixture_preview_preserves_promotion_blockers_without_becoming_formal_release(self) -> None:
        promotion_path = self.root / "PAGE-PROMOTION-MANIFEST.json"
        promotion = json.loads(promotion_path.read_text())
        for page in promotion["pages"]:
            page.update({
                "verdict": "FAIL",
                "research_package_complete": False,
                "higher_maturity_blocker": ["formal claim research and independent review remain incomplete"],
            })
        self.write_json("PAGE-PROMOTION-MANIFEST.json", promotion)
        self.write_json("PUBLICATION-BLOCKERS.json", {
            "schema_version": "publication-blockers.v1",
            "blockers": [{"status": "BLOCKED-HIGHER-MATURITY"}],
        })
        manifest_path = self.root / "RELEASE-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        manifest.update({
            "release_profile": "fixture-preview.v1",
            "validation_verdict": "BLOCKED-HIGHER-MATURITY",
            "publication_blockers_ref": "PUBLICATION-BLOCKERS.json",
            "promotion_manifest_hash": file_hash(promotion_path),
        })
        self.write_json("RELEASE-MANIFEST.json", manifest)

        errors = validate_release(self.root)
        self.assertFalse(any("promotion must PASS" in error for error in errors), errors)
        self.assertNotIn("release manifest validation_verdict must be PASS", errors)

    def test_fixture_preview_requires_an_explicit_blocker_artifact(self) -> None:
        manifest_path = self.root / "RELEASE-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        manifest.update({
            "release_profile": "fixture-preview.v1",
            "validation_verdict": "BLOCKED-HIGHER-MATURITY",
            "publication_blockers_ref": "PUBLICATION-BLOCKERS.json",
        })
        self.write_json("RELEASE-MANIFEST.json", manifest)
        self.assertTrue(any("fixture preview requires" in error for error in validate_release(self.root)))

    def test_release_accepts_split_static_course_projection(self) -> None:
        """The small static shell must validate the same full course as inline data."""
        html = (self.root / "site/index.html").read_text(encoding="utf-8")
        embedded = json.loads(html.split("const COURSE_DATA=", 1)[1].split(";const DATA", 1)[0])
        self.write_json("site/course-index.json", {
            "modules": embedded["modules"],
            "pages": embedded["pages"],
            "releaseScope": {"promisedPageIds": [page["id"] for page in embedded["pages"]]},
            "sourceNotes": {},
            "moduleOverviews": [],
        })
        self.write_json("site/glossary.json", {"glossary": [], "glossaryCategories": []})
        self.write_json("site/course-modules/M1.json", {"pages": embedded["pages"]})
        self.write("site/index.html", "<html><script>const COURSE_INDEX={};</script></html>")
        self.refresh_hash()
        self.assertEqual(validate_release(self.root), [])

    def test_release_accepts_source_triggered_career_and_agent_capabilities(self) -> None:
        path = self.root / "CAPABILITY-PROFILES.json"
        data = json.loads(path.read_text())
        data["pages"][0]["capabilities"] = ["career-evolution-system"]
        data["pages"][1]["capabilities"] = ["agent-architecture-testing"]
        self.write_json("CAPABILITY-PROFILES.json", data)
        manifest_path = self.root / "RELEASE-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["capability_profiles_hash"] = file_hash(path)
        self.write_json("RELEASE-MANIFEST.json", manifest)
        self.assertEqual(validate_release(self.root), [])

    def test_release_requires_capability_and_professional_evidence_projections(self) -> None:
        (self.root / "CAPABILITY-PROFILES.json").unlink()
        self.assertTrue(any("CAPABILITY-PROFILES.json" in error for error in validate_release(self.root)))

    def test_release_requires_source_beginner_reuse_and_visual_projections(self) -> None:
        (self.root / "SOURCE-ASSIMILATION-MANIFEST.json").unlink()
        self.assertTrue(any("SOURCE-ASSIMILATION-MANIFEST.json" in error for error in validate_release(self.root)))

    def test_release_requires_source_semantic_projection(self) -> None:
        (self.root / "SOURCE-SEMANTIC-PROJECTION.json").unlink()
        self.assertTrue(any("SOURCE-SEMANTIC-PROJECTION.json" in error for error in validate_release(self.root)))

    def test_release_rejects_semantic_visual_reduced_to_prose(self) -> None:
        path = self.root / "SOURCE-SEMANTIC-PROJECTION.json"
        data = json.loads(path.read_text()); data["units"][0]["visual_refs"] = []; self.write_json("SOURCE-SEMANTIC-PROJECTION.json", data)
        manifest_path = self.root / "RELEASE-MANIFEST.json"; manifest = json.loads(manifest_path.read_text())
        manifest["source_semantic_projection_hash"] = file_hash(path); self.write_json("RELEASE-MANIFEST.json", manifest)
        self.assertTrue(any("visual function lacks a rendered visual" in error for error in validate_release(self.root)))

    def test_release_rejects_non_contiguous_display_number(self) -> None:
        path = self.root / "tutorial/tutorial-site.json"
        data = json.loads(path.read_text()); data["pages"][1]["display_number"] = 76; self.write_json("tutorial/tutorial-site.json", data)
        self.refresh_hash()
        self.assertTrue(any("display_number must be contiguous" in error for error in validate_release(self.root)))

    def test_release_rejects_missing_topic_visual_source(self) -> None:
        (self.root / "site/visuals/P0.svg").unlink()
        self.refresh_hash()
        self.assertTrue(any("visual source is missing" in error for error in validate_release(self.root)))

    def test_release_rejects_professional_evidence_hash_drift(self) -> None:
        path = self.root / "PROFESSIONAL-EVIDENCE.json"
        data = json.loads(path.read_text()); data["pages"][0]["model"]["status"] = "BLOCKED"; self.write_json("PROFESSIONAL-EVIDENCE.json", data)
        self.assertTrue(any("professional_evidence_hash" in error for error in validate_release(self.root)))

    def test_release_rejects_provider_none_model_pass(self) -> None:
        path = self.root / "PROFESSIONAL-EVIDENCE.json"
        data = json.loads(path.read_text()); data["pages"][0]["model"].update({"status":"PASS", "provider":"none"}); self.write_json("PROFESSIONAL-EVIDENCE.json", data)
        manifest_path = self.root / "RELEASE-MANIFEST.json"; manifest = json.loads(manifest_path.read_text())
        manifest["professional_evidence_hash"] = file_hash(path); self.write_json("RELEASE-MANIFEST.json", manifest)
        self.assertTrue(any("model PASS cannot use provider none/offline" in error for error in validate_release(self.root)))

    def test_release_rejects_failed_page_executability(self) -> None:
        path = self.root / "EXECUTABILITY-MANIFEST.json"
        data = json.loads(path.read_text())
        data["pages"][0].update({"verdict":"FAIL", "finding_count":1})
        self.write_json("EXECUTABILITY-MANIFEST.json", data)
        manifest_path = self.root / "RELEASE-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["executability_manifest_hash"] = file_hash(path)
        self.write_json("RELEASE-MANIFEST.json", manifest)
        self.assertTrue(any("public page P0 executability must PASS with zero findings" in error for error in validate_release(self.root)))

    def test_release_rejects_missing_page_promotion_receipt(self) -> None:
        path = self.root / "PAGE-PROMOTION-MANIFEST.json"
        data = json.loads(path.read_text())
        data["pages"] = data["pages"][:-1]
        self.write_json("PAGE-PROMOTION-MANIFEST.json", data)
        manifest_path = self.root / "RELEASE-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["promotion_manifest_hash"] = file_hash(path)
        self.write_json("RELEASE-MANIFEST.json", manifest)
        self.assertTrue(any("promotion manifest page IDs must exactly equal public page IDs" in error for error in validate_release(self.root)))

    def test_release_rejects_archive_member_hash_drift(self) -> None:
        archive_path = self.root / "COURSE-RELEASE.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("site/materials/guide.md", "DRIFT")
        self.assertTrue(any("artifact closure hash mismatch for archive member" in error for error in validate_release(self.root)))

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

    def test_markdown_prompt_example_may_teach_blocked_stop_state(self) -> None:
        self.write(
            "site/materials/prompt.md",
            "# Conflict-aware prompt\n\n```json\n{\"status\": \"BLOCKED\", \"reason\": \"source conflict\"}\n```\n",
        )
        self.refresh_hash()
        self.assertEqual(validate_release(self.root), [])

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

    def test_missing_solution_manifest_fails(self) -> None:
        (self.root / "SOLUTION-MANIFEST.json").unlink()
        self.assertTrue(any("SOLUTION-MANIFEST.json" in error for error in validate_release(self.root)))

    def test_public_page_without_solution_coverage_fails(self) -> None:
        path = self.root / "SOLUTION-MANIFEST.json"
        data = json.loads(path.read_text())
        data["solution_units"][0]["page_ids"] = data["solution_units"][0]["page_ids"][:-1]
        self.write_json("SOLUTION-MANIFEST.json", data)
        manifest_path = self.root / "RELEASE-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["solution_manifest_hash"] = file_hash(path)
        self.write_json("RELEASE-MANIFEST.json", manifest)
        self.assertTrue(any("complete-solution coverage" in error for error in validate_release(self.root)))

    def test_public_solution_cannot_claim_public_with_fixture_only(self) -> None:
        path = self.root / "SOLUTION-MANIFEST.json"
        data = json.loads(path.read_text())
        data["solution_units"][0]["publication_status"] = "public"
        self.write_json("SOLUTION-MANIFEST.json", data)
        manifest_path = self.root / "RELEASE-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["solution_manifest_hash"] = file_hash(path)
        self.write_json("RELEASE-MANIFEST.json", manifest)
        self.assertTrue(any("public release lacks integration proof" in error for error in validate_release(self.root)))


if __name__ == "__main__":
    unittest.main()
