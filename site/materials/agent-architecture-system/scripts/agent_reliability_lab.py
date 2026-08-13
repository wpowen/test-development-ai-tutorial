#!/usr/bin/env python3
"""Agent 测试架构 D0–D7 可运行实验室。

与 ``agent_architecture_lab.py``（边界结构自检）的分工：
本脚本**真正做计算**——Cohen's κ、位置偏置、pass@k / pass^k、Wilson 区间、
首错位置分布、步骤效率比、成本分位、三段式门禁判定。

设计约束
--------
* 只用 Python 标准库；无网络、无模型调用；结果完全确定。
* **不写入任何文件**：故障注入在内存中进行，夹具保持字节不变。
* 退出码即结论：``0`` 通过，``1`` 门禁阻断，``2`` 用法错误。

红绿自检（每个子命令都是 0 / 1 / 0）::

    python3 scripts/agent_reliability_lab.py reliability --input fixtures/run-ledger.json
    python3 scripts/agent_reliability_lab.py reliability --input fixtures/run-ledger.json --fault fake-independence
    python3 scripts/agent_reliability_lab.py reliability --input fixtures/run-ledger.json --fault none

证据边界：确定性离线 fixture（L1）。真实模型、真实 Agent、MCP/工具/队列/
交易后端、影子与在线环、从业者评审与生产效果均 NOT_RUN。
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Z95 = 1.959963984540054

# --------------------------------------------------------------------------
# 统计基元
# --------------------------------------------------------------------------


def wilson_interval(successes: int, total: int, z: float = Z95) -> tuple[float, float]:
    """Wilson score interval：小样本下比正态近似稳健。

    返回 (下界, 上界)，均已裁剪到 [0, 1]。total 为 0 时返回 (0.0, 1.0)，
    表示「完全没有信息」而不是「0%」。
    """
    if total <= 0:
        return (0.0, 1.0)
    p = successes / total
    denom = 1.0 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def cohens_kappa(pairs: list[list[str]]) -> float:
    """两名评分者的 Cohen's κ。pairs 为 [[a, b], ...] 的标签对。"""
    if not pairs:
        return 0.0
    labels = sorted({label for pair in pairs for label in pair})
    n = len(pairs)
    observed = sum(1 for a, b in pairs if a == b) / n
    expected = 0.0
    for label in labels:
        pa = sum(1 for a, _ in pairs if a == label) / n
        pb = sum(1 for _, b in pairs if b == label) / n
        expected += pa * pb
    if expected >= 1.0:
        return 1.0
    return (observed - expected) / (1 - expected)


def percentile(values: list[float], q: float) -> float:
    """最近秩百分位；空列表返回 0.0。q 取 0–100。"""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil(q / 100.0 * len(ordered)))
    return ordered[min(rank, len(ordered)) - 1]


# --------------------------------------------------------------------------
# D0-1 Judge 校准
# --------------------------------------------------------------------------


def gate_judge(data: dict) -> tuple[dict, list[str]]:
    human = data["human_labels"]          # [[标注员1, 标注员2], ...]
    judge = data["judge_labels"]          # ["好", "坏", ...] 与 human 等长
    swaps = data["position_swaps"]        # [{"ab": "甲", "ba": "甲"}, ...]
    verbosity = data["verbosity_probe"]   # [{"plain": 3, "padded": 3}, ...]
    self_pref = data["self_preference"]   # {"same_family_wins": n, "cross_family_wins": n}
    thresholds = data["thresholds"]

    kappa_human = cohens_kappa(human)
    # judge 与「人类共识」比较：只用两名标注员一致的样本，避免把人类分歧算成 judge 错
    consensus = [(pair[0], j) for pair, j in zip(human, judge) if pair[0] == pair[1]]
    kappa_judge = cohens_kappa([[a, j] for a, j in consensus])

    stable = sum(1 for s in swaps if s["ab"] == s["ba"])
    position_consistency = stable / len(swaps) if swaps else 0.0

    verbosity_gain = (
        sum(v["padded"] - v["plain"] for v in verbosity) / len(verbosity)
        if verbosity else 0.0
    )
    same = self_pref["same_family_wins"]
    cross = self_pref["cross_family_wins"]
    self_pref_gap = abs(same - cross) / max(1, same + cross)

    metrics = {
        "kappa_human_human": round(kappa_human, 4),
        "kappa_judge_human": round(kappa_judge, 4),
        "consensus_sample_size": len(consensus),
        "position_consistency": round(position_consistency, 4),
        "verbosity_mean_gain": round(verbosity_gain, 4),
        "self_preference_gap": round(self_pref_gap, 4),
        "judge_generator_same_family": data["judge_generator_same_family"],
        "judge_card_present": data["judge_card_present"],
    }

    problems: list[str] = []
    if kappa_judge < thresholds["kappa_judge_min"]:
        problems.append(
            f"D0-1/KAPPA：judge–human κ={kappa_judge:.3f} < 约定 {thresholds['kappa_judge_min']}；"
            "本轮所有下游分数无效，judge 停用并回退人审"
        )
    if kappa_human < thresholds["kappa_human_min"]:
        problems.append(
            f"D0-4/RUBRIC-AMBIGUITY：标注者间 κ={kappa_human:.3f} 过低，"
            "说明评分标准本身有歧义——先改 rubric，不要改 judge"
        )
    if position_consistency < thresholds["position_consistency_min"]:
        problems.append(
            f"D0-1/POSITION-STABILITY：交换一致率={position_consistency:.3f}，存在位置偏置"
        )
    if verbosity_gain > thresholds["verbosity_gain_max"]:
        problems.append(f"D0-1/VERBOSITY-BIAS：加入无关文字后平均分上升 {verbosity_gain:.2f}")
    if self_pref_gap > thresholds["self_preference_gap_max"]:
        problems.append(f"D0-1/SELF-PREFERENCE：同族/异族胜率差 {self_pref_gap:.3f}")
    if metrics["judge_generator_same_family"]:
        problems.append("D0-1/FAMILY-SEPARATION：judge 与 generator 属同一模型族，自偏好不可控")
    if not metrics["judge_card_present"]:
        problems.append("D0-1/JUDGE-CARD：缺少 Judge Card，换版本时无法追溯校准状态")
    return metrics, problems


# --------------------------------------------------------------------------
# D1-3 轨迹 span
# --------------------------------------------------------------------------


def gate_trajectory(data: dict) -> tuple[dict, list[str]]:
    traces = data["traces"]
    thresholds = data["thresholds"]

    first_errors: dict[str, int] = {}
    efficiency: list[float] = []
    loop_traces = 0
    unauthorized: list[str] = []

    for trace in traces:
        spans = trace["spans"]
        bad = [
            s for s in spans
            if s["tool_choice"] != "正确"
            or s["param_build"] != "正确"
            or s["observation_use"] != "正确利用"
        ]
        if bad:
            key = f"span{bad[0]['span']}"
            first_errors[key] = first_errors.get(key, 0) + 1
        effective = [s for s in spans if s["necessity"] == "有效"]
        efficiency.append(trace["optimal_steps"] / len(spans) if spans else 0.0)
        # 无效循环：同一工具连续出现 >= 3 次
        run_tool, run_len = None, 0
        for s in spans:
            run_len = run_len + 1 if s["tool"] == run_tool else 1
            run_tool = s["tool"]
            if run_len >= 3:
                loop_traces += 1
                break
        unauthorized.extend(
            f"{trace['trace_id']}#span{s['span']}:{s['tool']}"
            for s in spans if not s["authorized"]
        )
        del effective

    mean_efficiency = sum(efficiency) / len(efficiency) if efficiency else 0.0
    loop_rate = loop_traces / len(traces) if traces else 0.0

    metrics = {
        "trace_count": len(traces),
        "first_error_distribution": dict(sorted(first_errors.items())),
        "step_efficiency_mean": round(mean_efficiency, 4),
        "invalid_loop_rate": round(loop_rate, 4),
        "unauthorized_calls": unauthorized,
    }

    problems: list[str] = []
    if unauthorized:
        problems.append(
            "D1-3/STEP-AUTHORIZATION：出现未授权工具调用 "
            f"{unauthorized}；最终文本正确也不能抵消 step 层失败"
        )
    if mean_efficiency < thresholds["step_efficiency_min"]:
        problems.append(
            f"D1-3/STEP-EFFICIENCY：步骤效率比均值={mean_efficiency:.3f} < "
            f"{thresholds['step_efficiency_min']}，存在冗余步骤"
        )
    if loop_rate > thresholds["invalid_loop_rate_max"]:
        problems.append(f"D1-3/INVALID-LOOP：无效循环率={loop_rate:.3f}，成本失控的早期信号")
    if not metrics["first_error_distribution"] and any(
        not t.get("succeeded", True) for t in traces
    ):
        problems.append("D1-3/FIRST-ERROR：存在失败轨迹却没有首错位置，轨迹不完整无法归因")
    return metrics, problems


# --------------------------------------------------------------------------
# D4-1 可靠性分布
# --------------------------------------------------------------------------


def gate_reliability(data: dict) -> tuple[dict, list[str]]:
    tasks = data["tasks"]                 # [{"task_id","priority","duration_bucket","runs":[bool,...]}]
    thresholds = data["thresholds"]
    cluster_unit = data["interval"]["cluster_unit"]
    min_tasks = data["interval"]["min_tasks_for_conclusion"]

    n = len(tasks)
    at_least_one = sum(1 for t in tasks if any(t["runs"]))
    all_success = sum(1 for t in tasks if all(t["runs"]) and t["runs"])
    k_values = {len(t["runs"]) for t in tasks}

    pass_at_k = at_least_one / n if n else 0.0
    pass_pow_k = all_success / n if n else 0.0

    if cluster_unit == "task":
        lower, upper = wilson_interval(all_success, n)
        interval_basis = f"任务聚类，n={n}"
    else:
        flat_total = sum(len(t["runs"]) for t in tasks)
        flat_success = sum(sum(1 for r in t["runs"] if r) for t in tasks)
        lower, upper = wilson_interval(flat_success, flat_total)
        interval_basis = f"逐 run 展开，n={flat_total}（重复运行不独立，此口径低估不确定性）"

    buckets: dict[str, dict] = {}
    for task in tasks:
        b = buckets.setdefault(task["duration_bucket"], {"n": 0, "all": 0})
        b["n"] += 1
        b["all"] += 1 if all(task["runs"]) and task["runs"] else 0
    horizon = {
        name: {
            "tasks": b["n"],
            "pass_pow_k": round(b["all"] / b["n"], 4) if b["n"] else 0.0,
        }
        for name, b in sorted(buckets.items())
    }

    metrics = {
        "task_count": n,
        "k_values": sorted(k_values),
        "pass_at_k": round(pass_at_k, 4),
        "pass_pow_k": round(pass_pow_k, 4),
        "pass_pow_k_ci95": [round(lower, 4), round(upper, 4)],
        "interval_basis": interval_basis,
        "horizon_buckets": horizon,
        "convention": "经验口径：pass@k=|{s>=1}|/n，pass^k=|{s=k}|/n",
    }

    problems: list[str] = []
    if cluster_unit != "task":
        problems.append(
            "D4-1/CLUSTERED-CI：区间以逐 run 为单位计算。同一任务的 k 次运行高度相关，"
            "把 n×k 当独立样本会严重低估不确定性；聚类单位必须是任务"
        )
    if n < min_tasks:
        problems.append(
            f"D4-1/EVIDENCE-SUFFICIENCY：任务数 n={n} < 约定最小 {min_tasks}，"
            "结论应为 EVIDENCE-INSUFFICIENT，不得写成通过"
        )
    if len(k_values) > 1:
        problems.append(
            f"D4-1/K-CONSISTENCY：同一批次出现多个 k={sorted(k_values)}，pass^k 不可比"
        )
    if lower < thresholds["pass_pow_k_ci_lower_min"] and n >= min_tasks:
        problems.append(
            f"D4-1/RELIABILITY-GATE：pass^k 的 95% CI 下界={lower:.3f} < "
            f"{thresholds['pass_pow_k_ci_lower_min']}"
        )
    dropped = [t["task_id"] for t in tasks if len(t["runs"]) == 0]
    if dropped:
        problems.append(f"D4-1/RAW-RUN-RETENTION：任务 {dropped} 没有 raw run，失败 run 不得被删除")
    return metrics, problems


# --------------------------------------------------------------------------
# D5 安全
# --------------------------------------------------------------------------


def gate_security(data: dict) -> tuple[dict, list[str]]:
    attacks = data["attacks"]
    controls = data["controls"]

    by_layer: dict[str, int] = {}
    reached_tool = 0
    succeeded: list[str] = []
    for attack in attacks:
        layer = attack["blocked_by"]
        by_layer[layer] = by_layer.get(layer, 0) + 1
        if layer in {"none"}:
            succeeded.append(attack["attack_id"])
        if attack.get("reached_tool_layer"):
            reached_tool += 1

    surfaces = {a["surface"] for a in attacks}
    required_surfaces = set(data["required_surfaces"])

    metrics = {
        "attack_count": len(attacks),
        "blocked_by_layer": dict(sorted(by_layer.items())),
        "reached_tool_layer": reached_tool,
        "attack_success_ids": succeeded,
        "covered_surfaces": sorted(surfaces),
        "missing_surfaces": sorted(required_surfaces - surfaces),
        "note": "「模型拒绝」与「授权层拒绝」是不同安全等级，必须分开统计",
    }

    problems: list[str] = []
    if succeeded:
        problems.append(f"D5-1/ATTACK-SUCCESS：攻击成功 {succeeded}，硬红线不接受任何一次成功")
    if metrics["missing_surfaces"]:
        problems.append(
            f"D5/SURFACE-COVERAGE：攻击面未覆盖 {metrics['missing_surfaces']}；"
            "延迟触发与跨会话持久化必须单独建套件"
        )
    if not controls["tenant_isolation_enforced"]:
        problems.append("D5-3/TENANT-ISOLATION：租户隔离未在授权层强制，跨租户读取一次即 blocker")
    if not controls["manifest_hash_verified"]:
        problems.append("D5-2/MANIFEST-HASH：工具清单未做 hash 校验，rug-pull 无法察觉")
    if controls["high_risk_limit_layer"] != "tool":
        problems.append(
            f"D5-6/CONTROL-NOT-IN-TOOL-LAYER：高危限额在 "
            f"{controls['high_risk_limit_layer']} 层。提示约束在注入下可被击穿，"
            "限额必须在工具层"
        )
    if not controls["irreversible_requires_human"]:
        problems.append("D5-6/IRREVERSIBLE-CONFIRM：不可逆动作未强制人工确认")
    return metrics, problems


# --------------------------------------------------------------------------
# D6 经济性
# --------------------------------------------------------------------------


def gate_economics(data: dict) -> tuple[dict, list[str]]:
    runs = data["runs"]                  # [{"latency_ms","cost","succeeded"}]
    budget = data["budget"]

    latencies = [r["latency_ms"] for r in runs]
    costs = [r["cost"] for r in runs]
    successes = sum(1 for r in runs if r["succeeded"])
    total_cost = sum(costs)
    mean_cost = total_cost / len(costs) if costs else 0.0
    variance = (
        sum((c - mean_cost) ** 2 for c in costs) / len(costs) if costs else 0.0
    )
    cv = math.sqrt(variance) / mean_cost if mean_cost else 0.0

    metrics = {
        "run_count": len(runs),
        "latency_p95_ms": percentile(latencies, 95),
        "latency_p99_ms": percentile(latencies, 99),
        "cost_mean": round(mean_cost, 6),
        "cost_p99": round(percentile(costs, 99), 6),
        "cost_cv": round(cv, 4),
        "unit_success_cost": round(total_cost / successes, 6) if successes else None,
        "hard_budget_enforced": budget["hard_cap_enforced"],
        "note": "成本是长尾分布，报 P99 不报均值",
    }

    problems: list[str] = []
    if not budget["hard_cap_enforced"]:
        problems.append("D6-2/HARD-BUDGET：未启用单任务硬预算，失控循环无法被截断")
    elif not budget["truncation_verified"]:
        problems.append("D6-2/BUDGET-TRUNCATION：硬预算已配置但从未验证真的会截断")
    over = [r for r in runs if r["cost"] > budget["per_task_cap"]]
    if budget["hard_cap_enforced"] and over:
        problems.append(
            f"D6-2/CAP-BREACH：{len(over)} 次运行超过单任务上限 {budget['per_task_cap']}，"
            "说明截断未生效"
        )
    if successes == 0:
        problems.append("D6-2/UNIT-SUCCESS-COST：零成功任务，单位成功成本无定义")
    if cv > budget["cost_cv_max"]:
        problems.append(f"D6-2/COST-VARIANCE：成本 CV={cv:.3f} > {budget['cost_cv_max']}")
    return metrics, problems


# --------------------------------------------------------------------------
# 三段式门禁
# --------------------------------------------------------------------------


def gate_three_stage(data: dict) -> tuple[dict, list[str]]:
    redlines = data["redlines"]
    statistical = data["statistical"]
    acceptance = data["risk_acceptance"]

    redline_results = {
        name: bool(item["satisfied"]) for name, item in redlines.items()
    }
    breached = [name for name, ok in redline_results.items() if not ok]

    lower = statistical["pass_pow_k_ci"][0]
    if statistical["sample_size"] < statistical["min_sample_size"]:
        stat_verdict = "EVIDENCE-INSUFFICIENT"
    elif lower >= statistical["threshold"]:
        stat_verdict = "PASS"
    else:
        stat_verdict = "FAIL"

    metrics = {
        "stage1_redlines": redline_results,
        "stage1_breached": breached,
        "stage2_verdict": stat_verdict,
        "stage2_ci_lower": lower,
        "stage3_failure_modes": len(acceptance["failure_modes"]),
        "stage3_signed_by": acceptance.get("accepted_by") or None,
        "note": "流水线不输出「可以发布」，它输出「证据齐了，请决定」",
    }

    problems: list[str] = []
    if breached:
        problems.append(f"GATE-1/REDLINE：硬红线未满足 {breached}，阻断且无例外")
    for name, item in redlines.items():
        if item.get("evaluated_as") == "statistical":
            problems.append(
                f"GATE-1/REDLINE-NOT-STATISTICAL：红线 {name} 被做成区间判定。"
                "「发生一次即不可接受」的事件不能统计化"
            )
    if stat_verdict == "FAIL":
        problems.append(f"GATE-2/STATISTICAL：CI 下界 {lower} < 阈值 {statistical['threshold']}")
    uncovered = [
        fm["id"] for fm in acceptance["failure_modes"]
        if fm["accepted"] and not fm["guardrail_covered"]
    ]
    if uncovered:
        problems.append(
            f"GATE-3/UNCOVERED-ACCEPTANCE：失败模式 {uncovered} 无护栏覆盖却被接受；"
            "那不是接受风险，是不知道有风险"
        )
    if acceptance["failure_modes"] and not acceptance.get("accepted_by"):
        problems.append("GATE-3/UNSIGNED-ACCEPTANCE：剩余风险没有具名接受人")
    if acceptance.get("accepted_by_role") not in (None, "release-owner", "business-owner"):
        problems.append(
            f"GATE-3/WRONG-SIGNER：由 {acceptance['accepted_by_role']} 签字；"
            "接受业务风险是发布/业务 owner 的职权"
        )
    return metrics, problems


# --------------------------------------------------------------------------
# 故障注入（内存中进行，不修改夹具文件）
# --------------------------------------------------------------------------

FAULTS: dict[str, str] = {
    "none": "不注入故障，期望全绿",
    "position-bias": "judge：让成对比较在交换顺序后改变胜负",
    "same-family-judge": "judge：让 judge 与 generator 同族",
    "prohibited-call": "trajectory：把一次工具调用标为未授权",
    "insufficient-sample": "reliability：把任务数削到低于最小样本量",
    "fake-independence": "reliability：把区间聚类单位改成逐 run",
    "tenant-leak": "security：关闭授权层的租户隔离",
    "prompt-only-guard": "security：把高危限额从工具层移到提示词",
    "no-hard-budget": "economics：关闭单任务硬预算",
    "redline-statistical": "gate：把硬红线改成区间判定",
    "unsigned-acceptance": "gate：移除剩余风险的具名接受人",
}


def inject(command: str, data: dict, fault: str) -> dict:
    if fault == "none":
        return data
    value = copy.deepcopy(data)
    if fault == "position-bias" and command == "judge":
        for swap in value["position_swaps"][: max(1, len(value["position_swaps"]) // 2)]:
            swap["ba"] = "乙" if swap["ab"] == "甲" else "甲"
        return value
    if fault == "same-family-judge" and command == "judge":
        value["judge_generator_same_family"] = True
        return value
    if fault == "prohibited-call" and command == "trajectory":
        value["traces"][0]["spans"][-1]["authorized"] = False
        return value
    if fault == "insufficient-sample" and command == "reliability":
        value["tasks"] = value["tasks"][:2]
        return value
    if fault == "fake-independence" and command == "reliability":
        value["interval"]["cluster_unit"] = "run"
        return value
    if fault == "tenant-leak" and command == "security":
        value["controls"]["tenant_isolation_enforced"] = False
        return value
    if fault == "prompt-only-guard" and command == "security":
        value["controls"]["high_risk_limit_layer"] = "prompt"
        return value
    if fault == "no-hard-budget" and command == "economics":
        value["budget"]["hard_cap_enforced"] = False
        return value
    if fault == "redline-statistical" and command == "gate":
        first = next(iter(value["redlines"]))
        value["redlines"][first]["evaluated_as"] = "statistical"
        return value
    if fault == "unsigned-acceptance" and command == "gate":
        value["risk_acceptance"].pop("accepted_by", None)
        return value
    raise SystemExit(f"故障 {fault!r} 不适用于子命令 {command!r}（用 list-faults 查看对应关系）")


COMMANDS = {
    "judge": ("D0-1 评估可信：κ、位置/冗长/自偏好探针", gate_judge),
    "trajectory": ("D1-3 轨迹 span：首错位置、步骤效率、无效循环", gate_trajectory),
    "reliability": ("D4-1 可靠性分布：pass@k / pass^k / Wilson 聚类区间", gate_reliability),
    "security": ("D5 安全对抗：攻击面覆盖与拦截层分层统计", gate_security),
    "economics": ("D6 效率经济：延迟与成本分位、单位成功成本、硬预算", gate_economics),
    "gate": ("三段式门禁：硬红线 / 统计门禁 / 风险接受", gate_three_stage),
}

BOUNDARY = (
    "证据边界：确定性离线 fixture（L1 fixture-tested）。真实模型、真实 Agent、"
    "MCP/工具/队列/交易后端、影子与在线环、从业者评审与生产效果均 NOT_RUN。"
)


def run(command: str, input_path: str, fault: str, report_path: str | None) -> int:
    source = Path(input_path)
    if not source.is_absolute():
        source = ROOT / input_path
    raw = json.loads(source.read_text(encoding="utf-8"))
    data = inject(command, raw, fault)

    description, gate = COMMANDS[command]
    metrics, problems = gate(data)
    verdict = "PASS" if not problems else "FAIL"

    print(f"== {command} == {description}")
    print(f"   fault={fault}")
    for key, value in metrics.items():
        print(f"   {key}: {json.dumps(value, ensure_ascii=False)}")
    if problems:
        print("   -- 门禁问题 --")
        for problem in problems:
            print(f"   ✗ {problem}")
    print(f"== {verdict} == 问题 {len(problems)} 条")
    print(f"   {BOUNDARY}")

    if report_path:
        report = {
            "command": command,
            "fault": fault,
            "verdict": verdict,
            "problem_count": len(problems),
            "problems": problems,
            "metrics": metrics,
            "maturity": "fixture-tested",
            "not_run": [
                "model-integrated", "integration-tested",
                "practitioner-reviewed", "production-validated",
            ],
        }
        Path(report_path).write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"   报告已写入 {report_path}")

    return 0 if verdict == "PASS" else 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Agent 测试架构 D0–D7 可运行实验室")
    parser.add_argument("command", choices=[*COMMANDS, "list-faults", "list-gates"])
    parser.add_argument("--input", help="夹具路径（相对 learner-materials 根目录）")
    parser.add_argument("--fault", default="none", choices=sorted(FAULTS))
    parser.add_argument("--report", default=None)
    args = parser.parse_args(argv)

    if args.command == "list-faults":
        for name, description in sorted(FAULTS.items()):
            print(f"{name:22s} {description}")
        return 0
    if args.command == "list-gates":
        for name, (description, _) in COMMANDS.items():
            print(f"{name:12s} {description}")
        return 0
    if not args.input:
        parser.error("该子命令需要 --input")
    return run(args.command, args.input, args.fault, args.report)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
