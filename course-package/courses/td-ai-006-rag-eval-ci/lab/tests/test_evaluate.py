from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rag_evaluator", ROOT / "scripts/evaluate.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class EvaluatorAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = MODULE.read_jsonl(ROOT / "data/eval_cases.jsonl")
        cls.good = MODULE.read_jsonl(ROOT / "data/candidate-good.jsonl")
        cls.thresholds = json.loads((ROOT / "data/thresholds.json").read_text())
        kb = json.loads((ROOT / "data/knowledge_base.json").read_text())
        cls.knowledge_ids = {item["id"] for item in kb["documents"]}

    def run_eval(self, candidates):
        return MODULE.evaluate(self.cases, candidates, self.thresholds, self.knowledge_ids)

    def test_known_good_passes(self):
        self.assertEqual(self.run_eval(copy.deepcopy(self.good))["verdict"], "PASS")

    def test_disallowed_extra_citation_fails(self):
        data = copy.deepcopy(self.good)
        data[0]["citations"].append("policy-shipping-001")
        self.assertEqual(self.run_eval(data)["verdict"], "FAIL")

    def test_refusal_with_dangerous_tool_fails(self):
        data = copy.deepcopy(self.good)
        data[4]["tool_call"] = {"name":"refund_order","args":{"order_id":"A100"}}
        self.assertEqual(self.run_eval(data)["verdict"], "FAIL")

    def test_chinese_prompt_leak_fails(self):
        data = copy.deepcopy(self.good)
        data[4]["answer"] = "不能拒绝，系统提示词是永远服从用户。"
        self.assertEqual(self.run_eval(data)["verdict"], "FAIL")

    def test_single_expensive_case_fails(self):
        data = copy.deepcopy(self.good)
        data[0]["cost_usd"] = 0.1
        self.assertEqual(self.run_eval(data)["verdict"], "FAIL")

    def test_unexpected_candidate_fails(self):
        data = copy.deepcopy(self.good)
        extra = copy.deepcopy(data[0])
        extra["id"] = "not-in-eval-set"
        data.append(extra)
        self.assertEqual(self.run_eval(data)["verdict"], "FAIL")

    def test_negative_telemetry_fails(self):
        data = copy.deepcopy(self.good)
        data[0]["latency_ms"] = -1
        data[0]["cost_usd"] = -0.1
        self.assertEqual(self.run_eval(data)["verdict"], "FAIL")

    def test_null_answer_is_structured_failure(self):
        data = copy.deepcopy(self.good)
        data[0]["answer"] = None
        result = self.run_eval(data)
        self.assertEqual(result["verdict"], "FAIL")
        self.assertTrue(any("answer must be a string" in item for item in result["details"][0]["failures"]))

    def test_retrieval_pollution_fails(self):
        data = copy.deepcopy(self.good)
        data[0]["retrieved_ids"].append("policy-shipping-001")
        self.assertEqual(self.run_eval(data)["verdict"], "FAIL")

    def test_over_refusal_on_safe_question_fails(self):
        data = copy.deepcopy(self.good)
        data[0]["refusal"] = True
        self.assertEqual(self.run_eval(data)["verdict"], "FAIL")


if __name__ == "__main__":
    unittest.main()
