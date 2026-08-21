#!/usr/bin/env python3
"""Regression tests for the deterministic author-draft extractor."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from extract_claim_list_author import (
    AUTHOR_PENDING,
    build_draft,
    run,
    split_atomic_sentences,
)


class ExtractClaimListAuthorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "topics"
        (self.root / "TD-A").mkdir(parents=True)
        (self.root / "TD-B").mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, topic: str, name: str, text: str) -> None:
        path = self.root / topic / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_compound_sentence_is_split_into_atomic_candidates_with_exact_locator(self) -> None:
        self.write("TD-A", "manuscript.md", "# Heading\n系统必须记录 owner，并且系统必须记录 version。\n")
        draft = build_draft("TD-A", self.root / "TD-A", ["manuscript.md"])
        statements = [row["statement"] for row in draft["claims"]]
        self.assertEqual(statements, ["系统必须记录 owner", "系统必须记录 version。"])
        self.assertEqual([row["source_locations"] for row in draft["claims"]], [["topic:manuscript.md:L2-L2"]] * 2)

    def test_markdown_list_and_table_cells_are_extracted_independently(self) -> None:
        self.write("TD-A", "table.md", "- 系统必须记录 owner。\n| rule | evidence |\n| --- | --- |\n| 系统必须冻结版本 | 证据必须可回链 |\n")
        draft = build_draft("TD-A", self.root / "TD-A", ["table.md"])
        self.assertEqual([claim["statement"] for claim in draft["claims"]], [
            "系统必须记录 owner。", "系统必须冻结版本", "证据必须可回链",
        ])
        self.assertEqual([claim["source_locations"][0] for claim in draft["claims"]], [
            "topic:table.md:L1-L1", "topic:table.md:L4-L4", "topic:table.md:L4-L4",
        ])

    def test_heading_and_code_are_not_silently_claimed_but_prose_is_retained(self) -> None:
        self.write("TD-A", "source.md", "## A heading\n```python\nassert False\n```\n这是一条可供作者复核的事实。\n")
        draft = build_draft("TD-A", self.root / "TD-A", ["source.md"])
        self.assertEqual(len(draft["claims"]), 1)
        self.assertEqual(draft["claims"][0]["source_locations"], ["topic:source.md:L5-L5"])
        self.assertEqual(draft["unmapped_propositions"]["count"], None)
        self.assertEqual(draft["unmapped_propositions"]["status"], AUTHOR_PENDING)

    def test_duplicate_text_at_distinct_locations_is_preserved_for_auditor(self) -> None:
        self.write("TD-A", "source.md", "系统必须记录 owner。\n系统必须记录 owner。\n")
        draft = build_draft("TD-A", self.root / "TD-A", ["source.md"])
        self.assertEqual(len(draft["claims"]), 2)
        self.assertNotEqual(draft["claims"][0]["claim_id"], draft["claims"][1]["claim_id"])
        self.assertEqual([x["source_locations"][0] for x in draft["claims"]], ["topic:source.md:L1-L1", "topic:source.md:L2-L2"])

    def test_stable_ids_and_serialization_are_deterministic(self) -> None:
        self.write("TD-A", "z.md", "系统必须记录 version。\n")
        self.write("TD-A", "a.md", "系统必须记录 owner。\n")
        first = build_draft("TD-A", self.root / "TD-A", ["z.md", "a.md"])
        second = build_draft("TD-A", self.root / "TD-A", ["a.md", "z.md"])
        self.assertEqual(first, second)
        self.assertEqual(first["source_files"][0]["path"], "a.md")
        self.assertTrue(first["source_files"][0]["sha256"].startswith("sha256:"))

    def test_path_escape_is_rejected_for_source_and_output(self) -> None:
        self.write("TD-A", "source.md", "系统必须记录 owner。\n")
        with self.assertRaises(ValueError):
            build_draft("TD-A", self.root / "TD-A", ["../TD-B/source.md"])
        with self.assertRaises(ValueError):
            run(self.root, ["TD-A"], ["source.md"], [], "../outside.json", False, False)

    def test_batch_dry_run_does_not_write_and_overwrite_is_fail_closed(self) -> None:
        self.write("TD-A", "source.md", "系统必须记录 owner。\n")
        self.write("TD-B", "source.md", "系统必须记录 version。\n")
        result = run(self.root, None, ["source.md"], [], "claim-list.author.json", True, False)
        self.assertEqual([item["topic_id"] for item in result], ["TD-A", "TD-B"])
        self.assertFalse((self.root / "TD-A" / "claim-list.author.json").exists())
        run(self.root, ["TD-A"], ["source.md"], [], "claim-list.author.json", False, False)
        with self.assertRaises(ValueError):
            run(self.root, ["TD-A"], ["source.md"], [], "claim-list.author.json", False, False)
        run(self.root, ["TD-A"], ["source.md"], [], "claim-list.author.json", False, True)
        saved = json.loads((self.root / "TD-A" / "claim-list.author.json").read_text(encoding="utf-8"))
        self.assertFalse(saved["independent_review"])
        self.assertNotEqual(saved["unmapped_propositions"], 0)

    def test_default_batch_sources_are_curated_and_do_not_sweep_audit_outputs(self) -> None:
        self.write("TD-A", "research-brief.md", "研究范围必须冻结。\n")
        self.write("TD-A", "claim-list.audit.md", "审计文字不应被默认重新当成课程源。\n")
        result = run(self.root, ["TD-A"], [], [], "claim-list.author.draft.json", True, False)
        self.assertEqual(result[0]["source_count"], 1)

    def test_default_manifest_covers_formal_topic_surfaces_and_excludes_research_package(self) -> None:
        for name, text in {
            "research-brief.md": "研究范围必须冻结。\n",
            "source-pack.csv": "fact,Source evidence is opened\n",
            "research-runs.json": '{"status": "Research receipt is pending"}\n',
            "evidence-synthesis.md": "证据必须回链来源。\n",
            "engineering-blueprint.md": "The blueprint records an owner.\n",
            "manuscript.md": "页面必须保留边界。\n",
            "comparison.md": "The comparison records a disagreement.\n",
            "lab-manifest.json": '{"description": "The fixture is deterministic"}\n',
            "validation.md": "验证结果必须可复现。\n",
            "projection-ledger.json": '{"status": "Projection is pending"}\n',
            "research-package.md": "这份旧摘要不应默认进入正式源面。\n",
        }.items():
            self.write("TD-A", name, text)
        draft = build_draft("TD-A", self.root / "TD-A", [])
        self.assertEqual([item["path"] for item in draft["source_files"]], [
            "comparison.md", "engineering-blueprint.md", "evidence-synthesis.md",
            "lab-manifest.json", "manuscript.md", "projection-ledger.json",
            "research-brief.md", "research-runs.json", "source-pack.csv", "validation.md",
        ])

    def test_controlled_source_manifest_is_hash_bound_and_exact(self) -> None:
        self.write("TD-A", "brief.md", "研究范围必须冻结。\n")
        self.write("TD-A", "facts.csv", "kind,The source is opened\n")
        self.write("TD-A", "source-manifest.json", json.dumps({"source_files": ["facts.csv", "brief.md"]}) + "\n")
        draft = build_draft("TD-A", self.root / "TD-A", [], "source-manifest.json")
        self.assertEqual([item["path"] for item in draft["source_files"]], ["brief.md", "facts.csv"])
        self.assertEqual(draft["source_manifest"]["path"], "source-manifest.json")
        self.assertTrue(draft["source_manifest"]["sha256"].startswith("sha256:"))
        with self.assertRaises(ValueError):
            build_draft("TD-A", self.root / "TD-A", ["brief.md"], "source-manifest.json")

    def test_json_csv_and_typescript_strings_have_line_and_character_offsets(self) -> None:
        self.write("TD-A", "facts.json", '{"rule": "The rule is versioned"}\n')
        self.write("TD-A", "facts.csv", "kind,The CSV source is opened\n")
        self.write("TD-A", "facts.ts", 'export const note = "The TypeScript source is frozen";\n')
        draft = build_draft("TD-A", self.root / "TD-A", ["facts.json", "facts.csv", "facts.ts"])
        self.assertEqual(len(draft["claims"]), 3)
        for claim in draft["claims"]:
            offset = claim["character_offset"]
            self.assertIsInstance(offset["start"], int)
            self.assertGreater(offset["end"], offset["start"])

    def test_same_line_duplicate_sentences_have_distinct_offsets_and_ids(self) -> None:
        self.write("TD-A", "source.md", "系统必须记录 owner。系统必须记录 owner。\n")
        draft = build_draft("TD-A", self.root / "TD-A", ["source.md"])
        self.assertEqual(len(draft["claims"]), 2)
        self.assertNotEqual(draft["claims"][0]["character_offset"], draft["claims"][1]["character_offset"])
        self.assertNotEqual(draft["claims"][0]["claim_id"], draft["claims"][1]["claim_id"])

    def test_split_fragments_are_rechecked_and_unmapped_stays_pending(self) -> None:
        self.write("TD-A", "source.md", "规则必须冻结，并且。\n")
        draft = build_draft("TD-A", self.root / "TD-A", ["source.md"])
        self.assertEqual(len(draft["claims"]), 1)
        self.assertEqual(draft["unmapped_propositions"]["status"], AUTHOR_PENDING)
        self.assertTrue(draft["unmapped_propositions"]["items"])

    def test_empty_source_and_zero_candidate_are_blocked(self) -> None:
        self.write("TD-A", "empty.md", "\n")
        with self.assertRaises(ValueError):
            build_draft("TD-A", self.root / "TD-A", ["empty.md"])
        self.write("TD-A", "heading.md", "# only heading\n")
        with self.assertRaises(ValueError):
            build_draft("TD-A", self.root / "TD-A", ["heading.md"])

    def test_output_must_be_claim_list_author_json_and_never_input(self) -> None:
        self.write("TD-A", "source.md", "系统必须记录 owner。\n")
        with self.assertRaises(ValueError):
            run(self.root, ["TD-A"], ["source.md"], [], "claims.json", False, False)
        with self.assertRaises(ValueError):
            run(self.root, ["TD-A"], ["source.md"], [], "claim-list.author-source.md", False, False)

    def test_unmapped_field_is_strictly_pending_and_bytes_are_stable(self) -> None:
        self.write("TD-A", "source.md", "系统必须记录 owner。\n残片并且。\n")
        run(self.root, ["TD-A"], ["source.md"], [], "claim-list.author.json", False, False)
        path = self.root / "TD-A" / "claim-list.author.json"
        first_bytes = path.read_bytes()
        first = json.loads(first_bytes.decode("utf-8"))
        self.assertEqual(first["schema_version"], "claim-list.author.v1")
        self.assertEqual(first["reviewed_by"], AUTHOR_PENDING)
        self.assertIs(first["independent_review"], False)
        self.assertIsInstance(first["unmapped_propositions"], dict)
        self.assertEqual(first["unmapped_propositions"]["status"], AUTHOR_PENDING)
        self.assertIsNone(first["unmapped_propositions"]["count"])
        self.assertNotEqual(first["unmapped_propositions"], 0)
        run(self.root, ["TD-A"], ["source.md"], [], "claim-list.author.json", False, True)
        self.assertEqual(first_bytes, path.read_bytes())

    def test_sentence_splitter_keeps_non_compound_sentence_intact(self) -> None:
        self.assertEqual(split_atomic_sentences("A versioned source is required."), ["A versioned source is required."])
        self.assertEqual(split_atomic_sentences("A source is required, and an owner is recorded."), ["A source is required", "an owner is recorded."])

    def test_fenced_code_is_pending_and_later_offsets_round_trip(self) -> None:
        text = "# Heading\n```bash\npython3 run.py --phase fault\n```\n系统必须记录当前版本。\n"
        self.write("TD-A", "manuscript.md", text)
        draft = build_draft("TD-A", self.root / "TD-A", ["manuscript.md"])
        command = next(item for item in draft["unmapped_propositions"]["items"] if item.get("evidence_kind") == "fenced-code-or-command")
        self.assertEqual(command["language"], "bash")
        self.assertEqual(text[command["char_start"]:command["char_end"]], command["text"])
        claim = next(item for item in draft["claims"] if item["statement"] == "系统必须记录当前版本。")
        span = claim["character_offset"]
        self.assertEqual(text[span["start"]:span["end"]], claim["statement"])

    def test_structured_non_string_fields_are_not_silently_dropped(self) -> None:
        self.write("TD-A", "contract.json", '{\n  "expected_exit_code": 0,\n  "enabled": false,\n  "description": "系统必须记录 owner。"\n}\n')
        draft = build_draft("TD-A", self.root / "TD-A", ["contract.json"])
        structured = [item for item in draft["unmapped_propositions"]["items"] if item.get("evidence_kind") == "structured-non-string-field"]
        self.assertEqual(len(structured), 2)
        self.assertTrue(any("expected_exit_code" in item["text"] for item in structured))
        self.assertTrue(any("enabled" in item["text"] for item in structured))

    def test_single_quoted_chinese_ts_string_is_preserved(self) -> None:
        self.write("TD-A", "source.ts", "export const note = '中文规则必须冻结';\n")
        draft = build_draft("TD-A", self.root / "TD-A", ["source.ts"])
        self.assertEqual([item["statement"] for item in draft["claims"]], ["中文规则必须冻结"])

    def test_duplicate_topic_ids_are_rejected(self) -> None:
        self.write("TD-A", "research-brief.md", "系统必须记录 owner。\n")
        with self.assertRaisesRegex(ValueError, "duplicates"):
            run(self.root, ["TD-A", "TD-A"], [], [], "claim-list.author.json", True, False)

    def test_cross_root_manifest_is_allowlisted_and_hash_bound(self) -> None:
        external = Path(self.tmp.name) / "canonical"
        external.mkdir()
        canonical = external / "page.ts"
        canonical.write_text("export const note = '页面结论必须绑定当前来源';\n", encoding="utf-8")
        import hashlib
        digest = "sha256:" + hashlib.sha256(canonical.read_bytes()).hexdigest()
        self.write("TD-A", "source-manifest.json", json.dumps({"source_files": [
            {"root_alias": "canonical", "path": "page.ts", "sha256": digest}
        ]}))
        draft = build_draft(
            "TD-A", self.root / "TD-A", [], "source-manifest.json", {"canonical": external}
        )
        self.assertEqual(draft["source_files"][0]["root_alias"], "canonical")
        self.assertEqual(draft["claims"][0]["source_locations"], ["canonical:page.ts:L1-L1"])
        with self.assertRaisesRegex(ValueError, "unknown source root"):
            build_draft("TD-A", self.root / "TD-A", [], "source-manifest.json")

    def test_every_pending_locator_round_trips_raw_excerpt(self) -> None:
        text = '"source_id","说明"\n"A",false\n"B","系统必须记录当前版本。"\n'
        self.write("TD-A", "facts.csv", text)
        draft = build_draft("TD-A", self.root / "TD-A", ["facts.csv"])
        for item in draft["unmapped_propositions"]["items"]:
            self.assertEqual(text[item["char_start"]:item["char_end"]], item["source_excerpt"])


if __name__ == "__main__":
    unittest.main()
