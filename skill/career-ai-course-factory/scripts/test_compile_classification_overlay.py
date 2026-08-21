import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from compile_classification_overlay import compile_overlay


class ClassificationOverlayCompilerTests(unittest.TestCase):
    def test_compiles_pending_k00_overlay_with_reproducible_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            topic = root / "TD-X"
            topic.mkdir()
            draft = {"schema_version": "claim-list.author.v1", "independent_review": False, "claims": [
                {"claim_id": "TD-X-C1", "statement": "qzx"},
                {"claim_id": "TD-X-C2", "statement": "repository validator hash is checked"},
            ]}
            (topic / "claim-list.author.draft-2026-08-20.json").write_text(json.dumps(draft), encoding="utf-8")
            output = root / "overlay.json"
            result = compile_overlay(root, output)
            self.assertEqual(result["claim_count"], 2)
            document = json.loads(output.read_text())
            self.assertEqual(document["review_status"], "pending")
            self.assertFalse(document["independent_review"])
            self.assertEqual(document["normalization_version"], "nfkc-casefold-punct-space.v1")
            self.assertEqual(document["claims"][0]["primary_cluster_id"], "K00")
            self.assertEqual(document["claims"][0]["subject"], "UNKNOWN-EXPLICIT")
            self.assertEqual(document["claims"][0]["claim_type_family"], "UNKNOWN-EXPLICIT")
            self.assertEqual(document["claims"][0]["execution_contract"], "openai-deep-research.v1")
            schema = json.loads((Path(__file__).resolve().parents[1] / "assets/schemas/classification-overlay.v1.schema.json").read_text())
            self.assertEqual(list(Draft202012Validator(schema).iter_errors(document)), [])

    def test_negative_target_status_does_not_route_to_target_evidence(self):
        from compile_classification_overlay import classify
        self.assertNotEqual(classify("没有调用供应商 API，不证明真实模型行为")[2], "TARGET-EVIDENCE")
        self.assertEqual(classify("当前生产系统返回 202 Accepted")[2], "TARGET-EVIDENCE")
        for statement in [
            "排除真实凭据、外部 API 与生产 SLO",
            "当前仅证明静态研究到页面的投影，不证明 provider 行为",
            "Condensed into the page evidence boundary with live limits preserved",
            "12 个 opened 来源覆盖 official API/spec 与 repository",
        ]:
            self.assertNotEqual(classify(statement)[2], "TARGET-EVIDENCE", statement)
        self.assertNotEqual(classify("Projected to the named learner-facing section")[2], "TEACHING-VALIDATION")
        self.assertEqual(classify("NIST 把风险测量放进治理语境")[0], "K07")
        self.assertNotEqual(classify("局限是这些文档不提供真实用户的效果数据")[2], "TARGET-EVIDENCE")

    def test_local_runtime_and_material_status_are_not_external_or_target_research(self):
        from compile_classification_overlay import classify
        self.assertEqual(classify("Outbox 记录发送意图，回读 adapter receipt 记录平台实际接受")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("当前运行只服务课程工程化，所有结果都是离线合成 fixture")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("fault report contains verdict=FAIL")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("learner/public material closure includes the model-config artifact at both copied paths")[2], "LOCAL-VERIFY")

    def test_incomplete_fragment_and_provider_contract_are_not_overclaimed(self):
        from compile_classification_overlay import classify
        self.assertEqual(classify("all live platform model")[2], "BLOCKED-UNCLASSIFIED")
        self.assertNotEqual(classify("每个 Provider 记录能力、Schema、权限、区域和成本合同")[2], "TARGET-EVIDENCE")

    def test_projection_maturity_and_eval_artifacts_stay_local(self):
        from compile_classification_overlay import classify
        for statement in [
            "研究中的判断维度被压缩为页面中的真实表格",
            "TD-T08 eval 集覆盖八类",
            "course evidence-boundary owner",
            "保留 deferred，待命题级研究与正式综合完成后绑定真实 manuscript/page target",
            "只有真实集成、从业者复核和发布后读回完成，状态才可能继续提升",
            "本包不声称 live-tested、practitioner-reviewed 或 production-validated",
            "README 预期退出码为 0",
        ]:
            self.assertEqual(classify(statement)[2], "LOCAL-VERIFY", statement)

    def test_method_and_evaluation_claims_are_not_blocked(self):
        from compile_classification_overlay import classify
        self.assertEqual(classify("禁止动作数量优先于最终文本得分")[0], "K04")
        self.assertEqual(classify("这个推断必须用 mutation 发现率、失败可定位性和人工审查结果验证")[0], "K04")

    def test_target_route_requires_current_observation_and_generic_eval_stays_external(self):
        from compile_classification_overlay import classify
        self.assertEqual(classify("当前生产系统返回 202 Accepted")[2], "TARGET-EVIDENCE")
        self.assertEqual(classify("对不可逆动作使用 pass@k 会因为允许重试而高估真实能力")[2], "EXTERNAL-RESEARCH")
        self.assertNotEqual(classify("范围外包括真实 Provider 能力、生产 SLO、硬件容量、就业与薪资承诺")[2], "TARGET-EVIDENCE")
        self.assertEqual(classify("PR smoke、nightly regression 和 release-candidate Gate 的依赖顺序")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("evidence/TD-C04/repair.json")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("courses/td-t08/learner-materials/page-prompts/manifest.json")[2], "LOCAL-VERIFY")

    def test_workflow_and_contract_fragments_are_not_left_unclassified(self):
        from compile_classification_overlay import classify
        self.assertNotEqual(classify("Workflow owner 仅在重复消息无重复写……时批准流程。")[2], "BLOCKED-UNCLASSIFIED")
        self.assertNotEqual(classify("save expected versus actual")[2], "BLOCKED-UNCLASSIFIED")
        self.assertNotEqual(classify("compare the same field")[2], "BLOCKED-UNCLASSIFIED")
        self.assertEqual(classify("research-runs.json#/comparison")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("The prompt's available input fields are oracle_ref...")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("10 个 opened 来源与 0→1→0 支持离线供应链合同")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("practitioner was run")[2], "TARGET-EVIDENCE")

    def test_final_boundary_samples_remain_local_or_external(self):
        from compile_classification_overlay import classify
        self.assertEqual(classify("ensure repair kept the same expected values.")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("研究分两次独立 run，至少打开十个来源……")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("repair 恢复 canonical state 并预期退出 0。")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("执行层只运行标准库 fixture，不连接模型、浏览器、网络、队列或企业系统。")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("Supports ... rebaseline from production-quality")[2], "EXTERNAL-RESEARCH")

    def test_last_audit_samples_route_to_local_or_teaching(self):
        from compile_classification_overlay import classify
        self.assertEqual(classify("Entry conditions: Python 3, repository files present")[2], "LOCAL-VERIFY")
        self.assertNotEqual(classify("LLM Judge 的人工双标、顺序翻转、事实反例校准")[2], "BLOCKED-UNCLASSIFIED")
        self.assertEqual(classify("用确定性 runner 验证控制契约")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("LLM/RAG/Agent 指标和 pytest 集成")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("research/topics/TD-T07/source-pack.csv:L5")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("选择传统测试到 AI 质量迁移的一项能力，写 Dataset/Eval/Trace/权限或生产反馈工件")[2], "TEACHING-VALIDATION")
        self.assertEqual(classify("模型、企业系统、真实支付、生产部署和从业者盲评均不在本页证据内")[2], "LOCAL-VERIFY")

    def test_final_boundary_samples_two_route_to_local_and_model_semantics(self):
        from compile_classification_overlay import classify
        self.assertEqual(classify("模型更新不是替换一个名称")[0], "K03")
        self.assertEqual(classify("expected exit 0 with the same expected contract")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("cycle 预期 0 / 1 / 0，核对 risk trace、后端状态和 mutation report")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("course reusable-artifact owner")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("TD-T07 eval 包含 unauthorized 用例")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("再画工件链：风险地图 → 生产回归资产")[2], "LOCAL-VERIFY")
        self.assertEqual(classify("run_lab.py 读取 baseline_observations 的静态字段，不读取五次真实随机运行记录")[2], "LOCAL-VERIFY")


if __name__ == "__main__":
    unittest.main()
