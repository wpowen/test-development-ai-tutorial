import json
import tempfile
import unittest
from pathlib import Path

from apply_locator_migration import migrate_topic
from propose_locator_migration import propose


class ApplyLocatorMigrationTests(unittest.TestCase):
    def _fixture(self, *, status: str = "AUTO-CANDIDATE"):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        topic = root / "research/topics/T-1"
        topic.mkdir(parents=True)
        (topic / "manuscript.md").write_text("one\ntwo\n", encoding="utf-8")
        claims = {
            "schema_version": "claim-list.v1",
            "topic_id": "T-1",
            "reviewed_by": "auditor",
            "unmapped_propositions": 0,
            "claims": [{
                "claim_id": "C-1", "statement": "statement", "claim_type": "boundary",
                "risk": "high", "scope": "fixture", "source_locations": ["manuscript.md:L1-L1"],
                "required_dimensions": ["scope"], "proposed_disposition": "SCOPED",
            }],
        }
        claims_path = topic / "claim-list.v1.json"
        claims_path.write_text(json.dumps(claims), encoding="utf-8")
        proposal = root / "proposal.json"
        proposal.write_text(json.dumps({"topics": [{"topic_id": "T-1", "rows": [{"claim_id": "C-1", "raw": "manuscript.md:L1-L1", "status": status, "proposed": "topic:manuscript.md:L1-L1"}]}]}), encoding="utf-8")
        return tmp, root, proposal

    def test_dry_run_does_not_write_inventory(self):
        tmp, root, proposal = self._fixture()
        try:
            result = migrate_topic(package_root=root, proposal_path=proposal, topic_id="T-1", source_files=["manuscript.md"], author_id="author", independent_auditor_id="auditor", write=False)
            self.assertEqual(result["status"], "READY-AUTO-ONLY")
            self.assertFalse(result["write"])
            self.assertFalse((root / "research/topics/T-1/claim-inventory.json").exists())
        finally:
            tmp.cleanup()

    def test_unresolved_row_never_writes_inventory(self):
        tmp, root, proposal = self._fixture(status="MANUAL-SELECTOR-REQUIRED")
        try:
            result = migrate_topic(package_root=root, proposal_path=proposal, topic_id="T-1", source_files=["manuscript.md"], author_id="author", independent_auditor_id="auditor", write=True)
            self.assertEqual(result["status"], "BLOCKED-MANUAL-REVIEW")
            self.assertFalse((root / "research/topics/T-1/claim-inventory.json").exists())
        finally:
            tmp.cleanup()

    def test_write_uses_prepare_inventory_and_records_provenance(self):
        tmp, root, proposal = self._fixture()
        try:
            result = migrate_topic(package_root=root, proposal_path=proposal, topic_id="T-1", source_files=["manuscript.md"], author_id="author", independent_auditor_id="auditor", write=True)
            self.assertTrue(result["write"])
            inventory = json.loads((root / "research/topics/T-1/claim-inventory.json").read_text())
            self.assertEqual(inventory["root_manifest"]["schema_version"], "locator-root-manifest.v1")
            self.assertEqual(inventory["claims"][0]["source_locations"], ["topic:manuscript.md:L1-L1"])
            self.assertEqual(inventory["locator_migration"]["status"], "APPLIED-AUTO-CANDIDATES")
        finally:
            tmp.cleanup()

    def test_multi_locator_proposal_expands_source_locations(self):
        tmp, root, proposal = self._fixture()
        try:
            document = json.loads(proposal.read_text())
            row = document["topics"][0]["rows"][0]
            row.pop("proposed")
            row["proposed_locators"] = ["topic:manuscript.md#json:/items/0", "topic:manuscript.md#json:/items/1"]
            proposal.write_text(json.dumps(document), encoding="utf-8")
            result = migrate_topic(package_root=root, proposal_path=proposal, topic_id="T-1", source_files=["manuscript.md"], author_id="author", independent_auditor_id="auditor", write=False)
            self.assertEqual(result["status"], "READY-AUTO-ONLY")
            self.assertEqual(result["locator_count"], 1)
            self.assertEqual(result["auto_candidate_count"], 2)
        finally:
            tmp.cleanup()

    def test_duplicate_multi_locator_proposal_is_blocked(self):
        tmp, root, proposal = self._fixture()
        try:
            document = json.loads(proposal.read_text())
            row = document["topics"][0]["rows"][0]
            row.pop("proposed")
            row["proposed_locators"] = ["topic:manuscript.md:L1-L1", "topic:manuscript.md:L1-L1"]
            proposal.write_text(json.dumps(document), encoding="utf-8")
            result = migrate_topic(package_root=root, proposal_path=proposal, topic_id="T-1", source_files=["manuscript.md"], author_id="author", independent_auditor_id="auditor", write=True)
            self.assertEqual(result["status"], "BLOCKED-MANUAL-REVIEW")
            self.assertEqual(result["pending"][0]["status"], "DUPLICATE-CANONICAL-LOCATOR")
            self.assertFalse((root / "research/topics/T-1/claim-inventory.json").exists())
        finally:
            tmp.cleanup()

    def test_generated_multi_locator_proposal_writes_valid_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); topic = root / "research/topics/T-1"; topic.mkdir(parents=True)
            (topic / "manifest.json").write_text(json.dumps({"items": [{"id": "a"}, {"id": "b"}]}), encoding="utf-8")
            claims = {
                "schema_version": "claim-list.v1", "topic_id": "T-1", "reviewed_by": "auditor",
                "unmapped_propositions": 0,
                "claims": [{"claim_id": "C-1", "statement": "statement", "claim_type": "boundary", "risk": "high", "scope": "fixture", "source_locations": ["manifest.json:items[0-1].id"], "required_dimensions": ["scope"], "proposed_disposition": "SCOPED"}],
            }
            (topic / "claim-list.v1.json").write_text(json.dumps(claims), encoding="utf-8")
            proposal = root / "proposal.json"; proposal.write_text(json.dumps(propose(root)), encoding="utf-8")
            result = migrate_topic(package_root=root, proposal_path=proposal, topic_id="T-1", source_files=["manifest.json"], author_id="author", independent_auditor_id="auditor", write=True)
            self.assertTrue(result["write"])
            inventory = json.loads((topic / "claim-inventory.json").read_text())
            self.assertEqual(inventory["claims"][0]["source_locations"], ["topic:manifest.json#json:/items/0/id", "topic:manifest.json#json:/items/1/id"])


if __name__ == "__main__":
    unittest.main()
