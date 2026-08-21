import json
import hashlib
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from plan_claim_research_clusters import canonical_fields, canonical_key, classify_claim, plan
from validate_cluster_evidence import validate_cluster_evidence

ROOT = Path(__file__).resolve().parents[1]
DIGEST = "sha256:" + "a" * 64


class PlannerTests(unittest.TestCase):
    def test_routes_and_unknowns_are_fail_closed(self):
        cases = [
            ({"statement": "repository validator hash", "claim_type": "status"}, "LOCAL-DETERMINISTIC"),
            ({"statement": "synthetic fixture red green result"}, "LOCAL-DETERMINISTIC"),
            ({"statement": "learner exercise default"}, "TEACHING-PROFESSIONAL"),
            ({"statement": "protocol role meaning", "claim_type": "definition"}, "STABLE-DEFINITION"),
            ({"statement": "usually improves industry outcomes"}, "SHARED-MECHANISM"),
            ({"statement": "current production provider response"}, "TARGET-EMPIRICAL"),
            ({"statement": "ACL prevents prompt injection"}, "SECURITY-AUTHORITY"),
            ({"statement": "p95 <= 8s for n=30"}, "NUMERIC-STATISTICAL"),
            ({"statement": "API behavior", "vendor": "Acme", "version": "v2"}, "VENDOR-VERSION"),
            ({"statement": "not production evidence"}, "UNCLASSIFIED"),
            ({"statement": "something ambiguous"}, "UNCLASSIFIED"),
        ]
        for claim, expected in cases:
            self.assertEqual(classify_claim(claim)[0], expected, claim)

    def test_explicit_class_wins_and_conflict_is_unknown(self):
        self.assertEqual(classify_claim({"statement": "production fixture", "evidence_class": "LOCAL-DETERMINISTIC"})[0], "LOCAL-DETERMINISTIC")
        self.assertEqual(classify_claim({"statement": "claim", "evidence_class": "TARGET-EMPIRICAL", "route": "LOCAL-VERIFY"})[0], "UNCLASSIFIED")
        self.assertEqual(classify_claim({"statement": "claim", "evidence_class": "future"})[0], "UNCLASSIFIED")

    def test_canonical_key_includes_statement_and_all_scope_dimensions(self):
        base = {"statement": "same fact", "predicate": "supports", "subject": "tool", "object": "calls", "scope": "bounded", "claim_type": "mechanism", "version": "1", "environment": "api", "population": "all", "region-language": "en", "risk": "low"}
        altered = dict(base, version="2")
        self.assertNotEqual(canonical_key(canonical_fields(base, "SHARED-MECHANISM"))["key_digest"], canonical_key(canonical_fields(altered, "SHARED-MECHANISM"))["key_digest"])
        self.assertEqual(canonical_key(canonical_fields(base, "SHARED-MECHANISM"))["key_digest"], canonical_key(canonical_fields(dict(base, statement="different instructional wording"), "SHARED-MECHANISM"))["key_digest"])

    def test_missing_cluster_defaults_to_blocked_k00(self):
        fields = canonical_fields({"claim_type": "definition", "statement": "x"}, "STABLE-DEFINITION")
        self.assertEqual(canonical_key(fields)["normalized_cluster"], "K00")

    def test_target_evidence_requirement_overrides_non_target_text_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "claims.json"
            source.write_text(json.dumps({"claims": [{"claim_id": "A", "statement": "repository validator hash", "claim_type": "status", "risk": "high", "primary_cluster_id": "K03", "target_evidence_required": True}]}), encoding="utf-8")
            result = plan(root, [source])
            claim = result["claims"][0]
            self.assertEqual(claim["evidence_class"], "TARGET-EMPIRICAL")
            self.assertEqual(claim["route"], "TARGET-EVIDENCE")

    def test_external_claim_with_incomplete_identity_is_blocked_before_deduplication(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "claims.json"
            source.write_text(json.dumps({"claims": [{
                "claim_id": "A", "statement": "protocol definition", "claim_type": "definition",
                "risk": "medium", "primary_cluster_id": "K03"
            }]}), encoding="utf-8")
            result = plan(root, [source])
            claim = result["claims"][0]
            self.assertEqual(claim["evidence_class"], "UNCLASSIFIED")
            self.assertEqual(claim["route"], "BLOCKED-UNCLASSIFIED")
            self.assertEqual(result["manifest"]["reuse"]["DIRECT-REUSE"], 0)
            self.assertEqual(result["manifest"]["counts"]["identity_blocked_units"], 1)

    def test_rejects_malformed_duplicate_and_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "claims.json"
            source.write_text(json.dumps({"claims": [{"claim_id": "A", "statement": "x"}, {"claim_id": "A", "statement": "y"}]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                plan(root, [source])
            source.write_text(json.dumps({"claims": [{"statement": "x"}]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing"):
                plan(root, [source])
            outside = root.parent / "outside.json"; outside.write_text('{"claims":[]}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "escapes"):
                plan(root, [outside])

    def test_dry_run_schema_and_target_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "claims.json"
            source.write_text(json.dumps({"claims": [
                {"claim_id": "A", "statement": "protocol definition", "claim_type": "definition", "risk": "medium", "primary_cluster_id": "K03"},
                {"claim_id": "B", "statement": "current production system", "risk": "medium", "primary_cluster_id": "K10"},
            ]}), encoding="utf-8")
            result = plan(root, [source])
            self.assertTrue(result["dry_run"]); self.assertEqual(result["manifest"]["status"], "BLOCKED")
            map_schema = json.loads((ROOT / "assets/schemas/claim-cluster-map.v1.schema.json").read_text())
            manifest_schema = json.loads((ROOT / "assets/schemas/research-route-dry-run-manifest.v1.schema.json").read_text())
            self.assertEqual(list(Draft202012Validator(map_schema).iter_errors(result["claim_map"])), [])
            self.assertEqual(list(Draft202012Validator(manifest_schema).iter_errors(result["manifest"])), [])
            target = next(row for row in result["claims"] if row["claim_id"] == "B")
            self.assertEqual(target["route"], "TARGET-EVIDENCE"); self.assertEqual(target["target_evidence"]["status"], "UNKNOWN")
            self.assertIn("K01", {c["cluster_id"] for c in result["claim_map"]["clusters"]}); self.assertEqual(len(result["claim_map"]["clusters"]), 12)

    def test_output_file_is_the_schema_bound_manifest_not_wrapper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "claims.json"; output = root / "route-manifest.json"
            source.write_text(json.dumps({"claims": [{"claim_id": "A", "statement": "x", "risk": "medium", "primary_cluster_id": "K03"}]}), encoding="utf-8")
            result = plan(root, [source], output=output)
            written = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(written, result["manifest"])
            self.assertNotIn("claim_map", written)

    def test_candidate_reuse_is_undecided_and_performance_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "claims.json"
            rows = [{"claim_id": f"C-{i}", "statement": f"protocol definition variant {i}", "claim_type": "definition"} for i in range(600)]
            source.write_text(json.dumps({"claims": rows}), encoding="utf-8")
            started = time.monotonic(); result = plan(root, [source]); elapsed = time.monotonic() - started
            self.assertLess(elapsed, 5.0); self.assertTrue(all(x["reuse_decision"] == "UNDECIDED" for x in result["candidate_map"]))
            self.assertEqual(result["manifest"]["reuse"]["DIRECT-REUSE"], 0)

    def test_overlay_schema_digest_identity_and_pending_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source_root=root/"source"; output_root=root/"output"; source_root.mkdir(); output_root.mkdir()
            (source_root / "research").mkdir()
            (source_root / "research" / "catalog-manifest.json").write_text(json.dumps({"release_scope":{"promised_page_ids":["T-1"]}}), encoding="utf-8")
            source=source_root/"claims.json"; source.write_text(json.dumps({"topic_id":"T-1","claims":[{"claim_id":"A","statement":"x","risk":"medium","primary_cluster_id":"K01"}]}),encoding="utf-8")
            fd="sha256:"+hashlib.sha256(source.read_bytes()).hexdigest()
            semantic={"subject":"tool","predicate":"supports","object":"calls","claim_type_family":"mechanism","scope":"bounded","version":"1","time_boundary":"current","vendor_or_tool":"Acme","environment":"fixture","population":"bounded","region_language":"en","authority_risk":"medium","required_dimensions":["scope"],"execution_contract":"openai-deep-research.v1","local_validation_locators":[],"target_evidence_required":False}
            semantic["field_digests"]={k:"sha256:"+hashlib.sha256((json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False) if isinstance(v,(list,dict,bool)) else str(v)).lower().encode()).hexdigest() for k,v in semantic.items()}
            overlay={"schema_version":"classification-overlay.v1","overlay_id":"o1","source_inventory_digests":[fd],"generated_by":"author","reviewed_by":"auditor","independent_review":True,"review_status":"pending","claim_count":1,"claims":[{"claim_id":"A","evidence_class":"STABLE-DEFINITION","risk":"medium","primary_cluster_id":"K01","related_cluster_ids":[],"source_family_policy":"primary","classification_reason":"audited proposal","route":"EXTERNAL-RESEARCH",**semantic}]}
            of=source_root/"overlay.json"; of.write_text(json.dumps(overlay),encoding="utf-8")
            result=plan(output_root,[Path("claims.json")],source_root=source_root,classification_overlay=Path("overlay.json"))
            self.assertEqual(result["manifest"]["status"],"BLOCKED"); self.assertTrue(result["classification_overlay"]["audit_pending"])
            overlay["claims"][0]["claim_id"]="EXTRA"; of.write_text(json.dumps(overlay),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"cover claim IDs"):
                plan(output_root,[Path("claims.json")],source_root=source_root,classification_overlay=Path("overlay.json"))
            overlay["claims"][0]["claim_id"]="A"; overlay["review_status"]="approved"; overlay["approved_at"]="2026-08-20T00:00:00Z"; of.write_text(json.dumps(overlay),encoding="utf-8")
            approved=plan(output_root,[Path("claims.json")],source_root=source_root,classification_overlay=Path("overlay.json"))
            self.assertEqual(approved["manifest"]["status"],"READY")
            self.assertEqual(approved["manifest"]["classification_overlay_digest"],approved["classification_overlay"]["digest"])
            self.assertEqual(validate_cluster_evidence(approved["claim_map"],{"anchor_claim_id":"A","member_claim_ids":["A"]},{"decisions":[]},approved["manifest"]),[])

    def test_four_claim_fixture_blocks_incomplete_identity_before_reuse_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/"claims.json"
            source.write_text(json.dumps({"topic_id":"T","claims":[
                {"claim_id":"A","statement":"same semantic fact one","predicate":"supports","subject":"tool","object":"calls","scope":"s","version":"1","time_boundary":"current","vendor":"Acme","environment":"e","population":"p","region_language":"en","risk":"medium","claim_type":"mechanism","primary_cluster_id":"K03","required_dimensions":["scope"],"execution_contract":"openai-deep-research.v1"},
                {"claim_id":"B","statement":"same semantic fact two","predicate":"supports","subject":"tool","object":"calls","scope":"s","version":"1","time_boundary":"current","vendor":"Acme","environment":"e","population":"p","region_language":"en","risk":"medium","claim_type":"mechanism","primary_cluster_id":"K03","required_dimensions":["scope"],"execution_contract":"openai-deep-research.v1"},
                {"claim_id":"C","statement":"different version fact","predicate":"supports","subject":"tool","object":"calls","scope":"s","version":"2","time_boundary":"current","vendor":"Acme","environment":"e","population":"p","region_language":"en","risk":"medium","claim_type":"mechanism","primary_cluster_id":"K03","required_dimensions":["scope"],"execution_contract":"openai-deep-research.v1"},
                {"claim_id":"D","statement":"same semantic fact one","predicate":"supports","subject":"tool","object":"calls","scope":"s","version":"1","time_boundary":"current","vendor":"Acme","environment":"e","risk":"medium","claim_type":"mechanism","primary_cluster_id":"K03","required_dimensions":["scope"],"execution_contract":"openai-deep-research.v1"}]}),encoding="utf-8")
            result=plan(root,[source])
            self.assertEqual(result["manifest"]["reuse"]["NO-REUSE"],0)
            self.assertGreaterEqual(result["manifest"]["reuse"]["undecided_candidate_count"],1)
            self.assertEqual(result["manifest"]["reuse"]["no_reuse_candidate_count"],0)
            self.assertEqual(result["manifest"]["reuse"]["audited_decision_count"],0)
            self.assertEqual(next(row for row in result["claims"] if row["claim_id"] == "D")["route"], "BLOCKED-UNCLASSIFIED")

    def test_missing_cluster_is_explicitly_unassigned_not_k01(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/"claims.json"
            source.write_text(json.dumps({"topic_id":"T","claims":[{"claim_id":"U","statement":"ambiguous claim","risk":"medium"}]}),encoding="utf-8")
            result=plan(root,[source])
            claim=result["claims"][0]
            self.assertEqual(claim["primary_cluster_id"],"K00")
            self.assertEqual(claim["evidence_class"],"UNCLASSIFIED")
            self.assertEqual(claim["route"],"BLOCKED-UNCLASSIFIED")
            self.assertNotEqual(claim["primary_cluster_id"],"K01")


if __name__ == "__main__":
    unittest.main()
