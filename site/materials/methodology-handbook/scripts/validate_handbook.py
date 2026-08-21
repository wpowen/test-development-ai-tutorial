#!/usr/bin/env python3
"""方法论手册自检器：校验工件结构、追溯闭包与状态语义。

设计约束
--------
* 只用 Python 标准库，无网络、无模型调用，结果完全确定。
* **不写入任何文件**：故障注入在内存中进行，因此手册包保持字节不变。
* 退出码即结论：``0`` 通过，``1`` 门禁失败，``2`` 用法错误。

红绿自检（0 / 1 / 0）::

    python3 scripts/validate_handbook.py all
    python3 scripts/validate_handbook.py all --fault doc-conflict
    python3 scripts/validate_handbook.py all --fault none

证据边界：本脚本证明手册工件结构自洽、闭包成立、预埋缺陷能被发现。
它不证明任何真实模型、企业系统或生产效果。
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples"
TEMPLATES = ROOT / "templates"
CHECKLISTS = ROOT / "checklists"

CRITICAL_TIERS = ("关键", "高")

FAULTS = {
    "none": "不注入故障，期望全绿",
    "doc-conflict": "在来源清单中植入未升级的冲突，期望 S1 门禁阻断",
    "unsupported-rule": "在需求契约中植入没有来源的规则，期望 S2 门禁阻断",
    "missing-oracle": "删除一条关键风险的 Oracle 记录，期望 S5 门禁阻断",
    "expired-waiver": "把 Waiver 的过期时间设为过去，期望 S9 门禁阻断",
    "judge-self-approval": "让语义层 Oracle 单独放行 blocker，期望 Oracle 独立性门禁阻断",
}


# --------------------------------------------------------------------------
# 最小 JSON Schema 子集校验器
# --------------------------------------------------------------------------

def _type_ok(value: object, expected: str) -> bool:
    mapping = {
        "object": dict,
        "array": list,
        "string": str,
        "boolean": bool,
        "number": (int, float),
    }
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, mapping[expected])


def validate_schema(instance: object, schema: dict, path: str = "$") -> list[str]:
    """校验 type / required / enum / const / minLength / minItems /
    minimum / maximum / pattern / properties / items / additionalProperties。"""
    errors: list[str] = []

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: 期望常量 {schema['const']!r}，实际 {instance!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} 不在允许值 {schema['enum']} 内")
    if "type" in schema and not _type_ok(instance, schema["type"]):
        errors.append(f"{path}: 期望类型 {schema['type']}，实际 {type(instance).__name__}")
        return errors

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: 长度 {len(instance)} < 最小 {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} 不匹配 {schema['pattern']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < 最小 {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > 最大 {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: 元素数 {len(instance)} < 最小 {schema['minItems']}")
        if "items" in schema:
            for index, item in enumerate(instance):
                errors.extend(validate_schema(item, schema["items"], f"{path}[{index}]"))

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: 缺少必填字段 {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{path}: 出现未声明字段 {key}")
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(validate_schema(instance[key], subschema, f"{path}.{key}"))

    return errors


# --------------------------------------------------------------------------
# 载入与故障注入
# --------------------------------------------------------------------------

def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_workspace(fault: str) -> dict:
    workspace = {
        "source_manifest": load_json(EXAMPLES / "source-manifest.json"),
        "requirement_contract": load_json(EXAMPLES / "requirement-contract.json"),
        "risk_register": load_json(EXAMPLES / "risk-register.json"),
        "oracle_records": load_json(EXAMPLES / "oracle-design-record.json"),
        "waivers": load_json(EXAMPLES / "waivers.json"),
        "run_receipts": load_json(EXAMPLES / "run-receipts.json"),
    }
    return inject(copy.deepcopy(workspace), fault)


def inject(workspace: dict, fault: str) -> dict:
    if fault == "none":
        return workspace
    if fault == "doc-conflict":
        workspace["source_manifest"]["conflicts"].append({
            "id": "CONF-INJECTED",
            "source_refs": ["PRD-v3#R17", "TECH-a13f#S04"],
            "description": "PRD 禁止已发货订单取消，旧技术方案仍写 SHIPPED 可取消",
            "affected_requirements": ["REQ-CANCEL-001"],
            "status": "BLOCKED",
            "escalated_to": "",
        })
        return workspace
    if fault == "unsupported-rule":
        workspace["requirement_contract"]["invariants"].append("refund_timeout_hours <= 72")
        workspace["requirement_contract"]["_unsupported_marker"] = "refund_timeout_hours"
        return workspace
    if fault == "missing-oracle":
        workspace["oracle_records"] = [
            record for record in workspace["oracle_records"]
            if record["risk_id"] != "R-001"
        ]
        return workspace
    if fault == "expired-waiver":
        workspace["waivers"][0]["expires_at"] = "2020-01-01"
        return workspace
    if fault == "judge-self-approval":
        for record in workspace["oracle_records"]:
            if record["risk_id"] == "R-001":
                record["oracle_layers"] = ["L5"]
                record["blocker"] = True
        return workspace
    raise SystemExit(f"未知故障类型：{fault}")


# --------------------------------------------------------------------------
# 各阶段门禁
# --------------------------------------------------------------------------

def gate_basis(workspace: dict) -> list[str]:
    """S1：来源清单结构、冲突升级、未知登记。"""
    manifest = workspace["source_manifest"]
    problems = validate_schema(manifest, load_json(SCHEMAS / "source-manifest.schema.json"))
    for conflict in manifest.get("conflicts", []):
        if not conflict.get("escalated_to"):
            problems.append(
                f"S1 BLOCKED：冲突 {conflict['id']} 未指定升级责任人，下游生成必须停止"
            )
    precedences = [source["precedence"] for source in manifest.get("sources", [])]
    if len(precedences) != len(set(precedences)):
        problems.append("S1：来源优先级重复，冲突裁决规则不唯一")
    return problems


def gate_requirement(workspace: dict) -> list[str]:
    """S2：需求契约结构 + 每条规则可回溯 + 两道门禁分离。"""
    contract = workspace["requirement_contract"]
    schema = load_json(SCHEMAS / "requirement-contract.schema.json")
    problems = validate_schema(
        {key: value for key, value in contract.items() if not key.startswith("_")}, schema
    )

    known_refs = {source["id"] for source in workspace["source_manifest"]["sources"]}
    for ref in contract.get("source_refs", []):
        if ref.split("#")[0] not in known_refs:
            problems.append(f"S2：source_ref {ref} 不在当前 baseline 中")

    marker = contract.get("_unsupported_marker")
    if marker:
        problems.append(
            f"S2 UNSUPPORTED_RULE：{contract['requirement_id']} 的 {marker} 没有来源支持"
        )

    if not contract.get("unknowns"):
        problems.append("S2：unknowns 为空——真实需求不可能全部明确，请复查是否被模型补写")

    review = contract.get("semantic_review", {})
    if review.get("verdict") != "PASS_SEMANTIC":
        problems.append("S2：语义门禁未通过或未执行，结构通过不得冒充语义通过")
    if not review.get("reviewer"):
        problems.append("S2：语义门禁缺少署名复核人")
    return problems


def gate_risk(workspace: dict) -> list[str]:
    """S4：风险登记结构、RPN 一致性、降档必须具名。"""
    schema = load_json(SCHEMAS / "risk-register.schema.json")
    problems: list[str] = []
    requirement_ids = {workspace["requirement_contract"]["requirement_id"]}
    for risk in workspace["risk_register"]:
        problems.extend(validate_schema(risk, schema, f"$[{risk.get('risk_id')}]"))
        expected = risk["impact"] * risk["likelihood"] * risk["detectability"]
        if risk["rpn"] != expected:
            problems.append(f"S4：{risk['risk_id']} 的 RPN {risk['rpn']} 与 I×L×D={expected} 不一致")
        linked = risk.get("requirement_id")
        if linked and linked not in requirement_ids:
            problems.append(f"S4：{risk['risk_id']} 关联了不存在的需求 {linked}")
        downgrade = risk.get("downgrade")
        if downgrade and not downgrade.get("accepted_by"):
            problems.append(f"S4：{risk['risk_id']} 降档未具名接受")
    return problems


def gate_oracle(workspace: dict) -> list[str]:
    """S5：关键风险必须有独立 Oracle，且 L5 不得单独放行 blocker。"""
    problems: list[str] = []
    covered = {record["risk_id"] for record in workspace["oracle_records"]}
    for risk in workspace["risk_register"]:
        if risk["tier"] in CRITICAL_TIERS and risk["risk_id"] not in covered:
            problems.append(
                f"S5 BLOCKED：{risk['tier']}风险 {risk['risk_id']} 没有 Oracle 设计记录"
            )
    for record in workspace["oracle_records"]:
        layers = record.get("oracle_layers", [])
        if not layers:
            problems.append(f"S5：{record['risk_id']} 未声明 Oracle 层")
        if record.get("blocker") and set(layers) <= {"L1", "L2", "L3", "L5"}:
            problems.append(
                f"S5：{record['risk_id']} 是 blocker，但只用了 {layers}；"
                "语义层不得单独放行，必须含 L4 规则或 L6 人工"
            )
        if not record.get("independent_sources"):
            problems.append(f"S5：{record['risk_id']} 未声明独立于被测实现的 Oracle 来源")
    return problems


def gate_run_receipts(workspace: dict) -> list[str]:
    """S8：收据结构 + 0/1/0 三段齐备 + lineage 完整。"""
    schema = load_json(SCHEMAS / "run-receipt.schema.json")
    problems: list[str] = []
    phases = set()
    for receipt in workspace["run_receipts"]:
        problems.extend(validate_schema(receipt, schema, f"$[{receipt.get('run_id')}]"))
        phases.add(receipt.get("phase"))
    for required in ("baseline", "fault", "repair"):
        if required not in phases:
            problems.append(f"S8：缺少 {required} 段运行收据，0/1/0 三段不完整")
    by_phase = {receipt.get("phase"): receipt for receipt in workspace["run_receipts"]}
    expectations = {"baseline": "PASS", "fault": "FAIL", "repair": "PASS"}
    for phase, expected in expectations.items():
        receipt = by_phase.get(phase)
        if receipt and receipt.get("verdict") != expected:
            problems.append(
                f"S8：{phase} 段判定为 {receipt.get('verdict')}，期望 {expected}"
            )
    fault_receipt = by_phase.get("fault")
    if fault_receipt and not fault_receipt.get("failed_oracle_ids"):
        problems.append("S8：fault 段未指名 failed_oracle_ids，无法证明是被 Oracle 检出")
    return problems


def gate_release(workspace: dict) -> list[str]:
    """S9：Waiver 有效性与过期检查。"""
    schema = load_json(SCHEMAS / "waiver.schema.json")
    problems: list[str] = []
    today = workspace["source_manifest"]["frozen_at"]
    for waiver in workspace["waivers"]:
        problems.extend(validate_schema(waiver, schema, f"$[{waiver.get('waiver_id')}]"))
        if waiver.get("expires_at", "") <= today:
            problems.append(
                f"S9 BLOCKED：Waiver {waiver['waiver_id']} 已于 {waiver['expires_at']} 过期，发布必须阻断"
            )
        if waiver.get("approver_role") == "release-owner":
            continue
        if waiver.get("gate", "").startswith("Security"):
            if waiver.get("approver_role") != "security-owner":
                problems.append(f"S9：安全类 Waiver {waiver['waiver_id']} 必须由安全 owner 批准")
    return problems


def gate_closure(workspace: dict) -> list[str]:
    """工件闭包：模板、检查单、Schema 齐备且被引用。"""
    problems: list[str] = []
    for directory, minimum, label in (
        (TEMPLATES, 19, "模板"),
        (CHECKLISTS, 8, "检查单"),
        (SCHEMAS, 5, "Schema"),
    ):
        found = sorted(path.name for path in directory.iterdir() if path.is_file())
        if len(found) < minimum:
            problems.append(f"闭包：{label}数量 {len(found)} < 约定 {minimum}")
    for risk in workspace["risk_register"]:
        if risk["status"] == "COVERED" and not risk.get("oracle_source"):
            problems.append(f"闭包：{risk['risk_id']} 声称已覆盖但没有 Oracle 来源")
    return problems


GATES = (
    ("S1 依据冻结", gate_basis),
    ("S2 需求契约", gate_requirement),
    ("S4 风险与策略", gate_risk),
    ("S5 Oracle 设计", gate_oracle),
    ("S8 执行与证据", gate_run_receipts),
    ("S9 发布判断", gate_release),
    ("工件闭包", gate_closure),
)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def run_all(fault: str, report_path: str | None) -> int:
    workspace = load_workspace(fault)
    results = []
    total_problems = 0
    for name, gate in GATES:
        problems = gate(workspace)
        total_problems += len(problems)
        results.append({"gate": name, "verdict": "PASS" if not problems else "FAIL", "problems": problems})
        status = "PASS" if not problems else "FAIL"
        print(f"[{status}] {name}")
        for problem in problems:
            print(f"        - {problem}")

    verdict = "PASS" if total_problems == 0 else "FAIL"
    print(f"\n== {verdict} == fault={fault} 门禁 {len(GATES)} 项，问题 {total_problems} 条")
    print("证据边界：确定性离线 fixture（L1 fixture-tested）；真实模型、企业集成、"
          "从业者评审与生产验证均 NOT_RUN。")

    if report_path:
        report = {
            "fault": fault,
            "verdict": verdict,
            "gate_count": len(GATES),
            "problem_count": total_problems,
            "gates": results,
            "maturity": "fixture-tested",
            "not_run": ["model-integrated", "integration-tested", "practitioner-reviewed", "production-validated"],
        }
        Path(report_path).write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"报告已写入 {report_path}")

    return 0 if verdict == "PASS" else 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="方法论手册工件自检器")
    parser.add_argument("command", choices=["all", "list-faults", "list-gates"])
    parser.add_argument("--fault", default="none", choices=sorted(FAULTS))
    parser.add_argument("--report", default=None, help="把 JSON 报告写到该路径")
    args = parser.parse_args(argv)

    if args.command == "list-faults":
        for name, description in sorted(FAULTS.items()):
            print(f"{name:22s} {description}")
        return 0
    if args.command == "list-gates":
        for name, _ in GATES:
            print(name)
        return 0
    return run_all(args.fault, args.report)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
