import json
import tempfile
import unittest
from pathlib import Path

from propose_locator_migration import propose


class LocatorMigrationProposalTests(unittest.TestCase):
    def test_only_unambiguous_existing_paths_are_auto_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (topic / "manuscript.md").write_text("one\ntwo\n", encoding="utf-8")
            (root / "research/topics/T-1/claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["manuscript.md:L1-L1", "missing.md:L1-L1", "manuscript.md:Heading"]}]}), encoding="utf-8")
            result = propose(root)
            statuses = [row["status"] for row in result["topics"][0]["rows"]]
            self.assertEqual(statuses, ["AUTO-CANDIDATE", "MISSING-SOURCE", "MANUAL-SELECTOR-REQUIRED"])
            self.assertEqual(result["totals"]["auto_candidates"], 1)
            self.assertEqual(result["totals"]["manual_selector"], 1)

    def test_workspace_prefixed_path_is_normalized_only_when_the_package_file_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            root = workspace / "outputs" / "test-development-ai-v2"
            topic = root / "research/topics/T-1"
            topic.mkdir(parents=True)
            source = root / "methodology/dimensions/T-1.md"
            source.parent.mkdir(parents=True)
            source.write_text("one\ntwo\n", encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["outputs/test-development-ai-v2/methodology/dimensions/T-1.md:L1-L1"]}]}), encoding="utf-8")
            result = propose(root)
            row = result["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "AUTO-CANDIDATE")
            self.assertEqual(row["proposed"], "package:methodology/dimensions/T-1.md:L1-L1")
            self.assertEqual(row["normalized_from"], "outputs/test-development-ai-v2/methodology/dimensions/T-1.md")

    def test_existing_file_with_stale_line_range_is_not_auto_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (topic / "manuscript.md").write_text("one\ntwo\n", encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["manuscript.md:L1-L9"]}]}), encoding="utf-8")
            result = propose(root)
            row = result["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "LINE-RANGE-INVALID")
            self.assertEqual(result["totals"]["line_range_invalid"], 1)

    def test_unique_csv_and_json_selectors_become_typed_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (topic / "source-pack.csv").write_text("source_id,title\nS-ONE,One\nS-TWO,Two\n", encoding="utf-8")
            (topic / "projection-ledger.json").write_text(json.dumps({"claims": [{"claim_id": "C-1"}]}), encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["source-pack.csv:S-ONE", "projection-ledger.json:C-1"]}]}), encoding="utf-8")
            result = propose(root)
            rows = result["topics"][0]["rows"]
            self.assertEqual([row["status"] for row in rows], ["AUTO-CANDIDATE", "AUTO-CANDIDATE"])
            self.assertEqual(rows[0]["proposed"], "topic:source-pack.csv#csv:key=source_id=S-ONE")
            self.assertEqual(rows[1]["proposed"], "topic:projection-ledger.json#json:/claims/0/claim_id")

    def test_topic_relative_traversal_is_normalized_only_inside_package_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            source = root / "content/modules/example.ts"; source.parent.mkdir(parents=True)
            source.write_text("one\ntwo\n", encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["../../../content/modules/example.ts:L1-L1"]}]}), encoding="utf-8")
            result = propose(root)
            row = result["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "AUTO-CANDIDATE")
            self.assertEqual(row["proposed"], "package:content/modules/example.ts:L1-L1")

    def test_explicit_legacy_json_pointer_is_preserved_as_typed_selector(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (root / "courses").mkdir()
            manifest = root / "courses/manifest.json"
            manifest.write_text(json.dumps({"package_id": "pkg-1"}), encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["../../../courses/manifest.json#/package_id"]}]}), encoding="utf-8")
            result = propose(root)
            row = result["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "AUTO-CANDIDATE")
            self.assertEqual(row["proposed"], "package:courses/manifest.json#json:/package_id")

    def test_single_legacy_line_is_normalized_to_a_closed_line_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (topic / "source-pack.csv").write_text("source_id,title\nS-ONE,One\n", encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["source-pack.csv:L2"]}]}), encoding="utf-8")
            result = propose(root)
            row = result["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "AUTO-CANDIDATE")
            self.assertEqual(row["proposed"], "topic:source-pack.csv:L2-L2")

    def test_unique_json_key_selector_becomes_a_pointer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (topic / "lab-manifest.json").write_text(json.dumps({"required_files": ["a"], "steps": [{"id": "s1"}]}), encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["lab-manifest.json:required_files"]}]}), encoding="utf-8")
            result = propose(root)
            row = result["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "AUTO-CANDIDATE")
            self.assertEqual(row["proposed"], "topic:lab-manifest.json#json:/required_files")

    def test_nested_explicit_json_selector_resolves_unique_array_member(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (topic / "projection-ledger.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "decision": "keep"}]}), encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["projection-ledger.json:claims[C-1].decision"]}]}), encoding="utf-8")
            result = propose(root)
            row = result["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "AUTO-CANDIDATE")
            self.assertEqual(row["proposed"], "topic:projection-ledger.json#json:/claims/0/decision")

    def test_plain_numeric_line_range_is_normalized(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (topic / "source-pack.csv").write_text("source_id,title\nS-ONE,One\nS-TWO,Two\n", encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["source-pack.csv:2-3"]}]}), encoding="utf-8")
            result = propose(root)
            row = result["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "AUTO-CANDIDATE")
            self.assertEqual(row["proposed"], "topic:source-pack.csv:L2-L3")

    def test_unqualified_material_path_uses_only_unique_tutorial_material_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            source = root / "tutorial/materials/bundle/fixtures/input.json"; source.parent.mkdir(parents=True)
            source.write_text("{\"ok\": true}\n", encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["fixtures/input.json:L1-L1"]}]}), encoding="utf-8")
            result = propose(root)
            row = result["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "AUTO-CANDIDATE")
            self.assertEqual(row["proposed"], "package:tutorial/materials/bundle/fixtures/input.json:L1-L1")

    def test_line_range_with_json_pointer_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (topic / "schema.json").write_text(json.dumps({"required": ["x"]}) + "\n", encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["schema.json:L1-L1#/required"]}]}), encoding="utf-8")
            result = propose(root)
            row = result["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "AUTO-CANDIDATE")
            self.assertEqual(row["proposed"], "topic:schema.json:L1-L1#json:/required")

    def test_bare_module_filename_uses_unique_canonical_content_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            module = root / "content/modules/requirements-lifecycle-supplement.ts"; module.parent.mkdir(parents=True)
            module.write_text("one\ntwo\n", encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["requirements-lifecycle-supplement.ts:L1-L1"]}]}), encoding="utf-8")
            result = propose(root)
            row = result["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "AUTO-CANDIDATE")
            self.assertEqual(row["proposed"], "package:content/modules/requirements-lifecycle-supplement.ts:L1-L1")

    def test_json_array_range_expands_to_ordered_typed_locators(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (topic / "manifest.json").write_text(json.dumps({"items": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}), encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["manifest.json:items[0-2].id"]}]}), encoding="utf-8")
            row = propose(root)["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "AUTO-CANDIDATE")
            self.assertNotIn("proposed", row)
            self.assertEqual(row["proposed_locators"], [
                "topic:manifest.json#json:/items/0/id",
                "topic:manifest.json#json:/items/1/id",
                "topic:manifest.json#json:/items/2/id",
            ])

    def test_json_selector_duplicate_indices_remain_manual(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (topic / "manifest.json").write_text(json.dumps({"items": [{"id": "a"}, {"id": "b"}]}), encoding="utf-8")
            (topic / "claim-list.v1.json").write_text(json.dumps({"claims": [{"claim_id": "C-1", "source_locations": ["manifest.json:items[0,0].id"]}]}), encoding="utf-8")
            row = propose(root)["topics"][0]["rows"][0]
            self.assertEqual(row["status"], "MANUAL-SELECTOR-REQUIRED")


if __name__ == "__main__":
    unittest.main()
