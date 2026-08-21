import json
import tempfile
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator

from build_claim_source_manifest import build, validate_freshness


class ClaimSourceManifestTests(unittest.TestCase):
    def test_build_is_page_exact_and_hash_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "research/topics/P-1").mkdir(parents=True)
            (root / "research/topics/P-1/manuscript.md").write_text("A claim.\n", encoding="utf-8")
            (root / "site/content").mkdir(parents=True)
            (root / "site/content/course.ts").write_text('id: "P-1"\n', encoding="utf-8")
            (root / "research/catalog-manifest.json").write_text(json.dumps({"release_scope": {"promised_page_ids": ["P-1"]}}), encoding="utf-8")
            out = root / "research/claim-source-manifest.json"
            doc = build(root, root / "research/catalog-manifest.json", out)
            self.assertEqual(doc["page_count"], 1)
            self.assertEqual(doc["catalog_manifest"]["page_ids"], ["P-1"])
            self.assertTrue(any(item["root_alias"] == "topic" for item in doc["pages"][0]["source_files"]))
            self.assertTrue(any(item["root_alias"] == "site" for item in doc["pages"][0]["source_files"]))
            self.assertTrue(out.is_file())
            schema = json.loads((Path(__file__).resolve().parents[1] / "assets/schemas/claim-source-manifest.v1.schema.json").read_text())
            self.assertEqual(list(Draft202012Validator(schema).iter_errors(doc)), [])
            self.assertEqual(validate_freshness(doc, root), [])
            (root / "site/content/course.ts").write_text('id: "P-1"\nchanged: true\n', encoding="utf-8")
            self.assertTrue(any("source hash mismatch" in item for item in validate_freshness(doc, root)))


if __name__ == "__main__":
    unittest.main()
