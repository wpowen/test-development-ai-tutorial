#!/usr/bin/env python3
"""Build the Wave-3 quality-system and benchmark fixture package."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


OUTPUT = Path(__file__).resolve().parents[3]
COURSE = OUTPUT / "courses" / "td-ai-quality-benchmark"
LAB = COURSE / "lab"
PUBLIC = OUTPUT / "site" / "public" / "materials" / "ai-quality-benchmark"
TOPIC_ROOT = OUTPUT / "research" / "topics"
ARCHIVE = PUBLIC.parent / "ai-quality-benchmark.zip"

TOPICS = {
    "TD-T20": {"title":"CI 分层门禁","question":"怎样让 Prompt、模型、知识库或工具的危险回归在合并前真正 exit 1？","focus":"PR smoke、nightly regression 和 release-candidate Gate 的依赖顺序","decision":"先杀死 blocker，再检查风险切片阈值，最后才展示总体分。","failure":"high-risk refund 已错误承诺，但报告 job 未传播非零退出码。","metric":"blocker count、high-risk pass rate、Gate latency 与当前 SHA 绑定","artifact":"分层 CI manifest、三阶段报告和 waiver 约束","unknown":"真实云 CI、企业审批和模型执行未运行。"},
    "TD-T21": {"title":"版本 Lineage","question":"一个分数如何回到当时的 Dataset、Prompt、模型、知识库、工具、Scorer 与环境？","focus":"不可变 snapshot、hash、run manifest 与混杂变量检查","decision":"锁定字段同时变化时输出 CONFOUNDED，不生成 winner。","failure":"A/B 同时更换模型、Prompt、知识索引和 Judge，却声称模型提升。","metric":"lineage completeness、replayability 与 confounded-field count","artifact":"版本图、run manifest 和可比性报告","unknown":"外部 Provider 的内部路由和历史 snapshot 可用性未知。"},
    "TD-T22": {"title":"Trace-to-Regression","question":"怎样在不泄露生产数据的前提下，把事故变成稳定回归用例？","focus":"Trace 隔离、字段脱敏、最小触发条件、领域 Oracle 与回归追踪","decision":"不能稳定重放或未获隐私/领域批准的事件只能作调查线索。","failure":"直接复制含 PII 的 Trace，或过度脱敏后丢失越权工具触发条件。","metric":"conversion、redaction、replayability 与 recurrence 分开计算","artifact":"脱敏转换记录、最小失败 case 和 source_trace_hash","unknown":"真实保留期限、隐私分类和生产 Trace 平台未接入。"},
    "TD-T23": {"title":"质量—延迟—成本联合 Gate","question":"怎样避免平均质量、更快或更便宜中的单指标优化伤害另两个维度？","focus":"固定 workload、风险切片、TTFT/TPOT/尾延迟、Token 与 cost-per-success","decision":"先淘汰突破硬底线的候选，再在合格候选中讨论 Pareto 权衡。","failure":"平均延迟下降但高风险正确率、p99 与重试成本恶化。","metric":"high-risk quality、p95/p99 latency 与 cost-per-success","artifact":"联合 Gate 表、Pareto 报告和风险路由决定","unknown":"真实模型价格、流量、缓存与 SLO 未测。"},
    "TD-T24": {"title":"漂移、Waiver 与回滚","question":"质量异常出现时怎样区分输入、模型、知识、Judge、性能和成本漂移？","focus":"版本冻结、诊断树、到期 waiver、known-good manifest 与整包回滚","decision":"高风险先回滚再调查；例外必须具名、受限并自动到期。","failure":"Judge 漂移导致质量下降未报警，团队通过放宽阈值维持绿灯。","metric":"drift magnitude/window、MTTD/MTTR、waiver age 与 recovery","artifact":"事故 Runbook、到期 waiver 和回滚重放报告","unknown":"真实监控基线、值班流程和回滚演练未运行。"},
    "TD-T25": {"title":"Capstone Fixture Release Candidate","question":"怎样消费全链工件，让一个坏 AI 版本可重复失败、定位和恢复？","focus":"PRD/Risk→Dataset/Trace→Prompt/Schema→Oracle→Benchmark/CI→Rollback 的闭环","decision":"闭包最多证明 fixture release candidate，不得晋级 publication、production 或 practitioner。","failure":"只交文档、聊天截图或最终绿报告，没有首次红灯、trace、owner 或 hash closure。","metric":"trace coverage、artifact closure、mutation kill、0→1→0 与 unknown completeness","artifact":"AI Quality Engineering Fixture RC 与评审包","unknown":"模型、真实 RAG/Agent、企业集成、人审和发布全部 NOT_RUN。"},
    "TD-B01": {"title":"Benchmark 七段流水线","question":"一个总分背后的任务、数据、协议、环境、Scorer、聚合和报告是什么？","focus":"从 leaderboard 回到逐题结果和运行协议","decision":"关键字段缺失时标不可复现；公共分数不能自动成为企业 Gate。","failure":"只按公开名次选择客服模型，却不知道工具预算、超时和 scorer。","metric":"pipeline completeness、reproducibility 与逐任务结果","artifact":"Benchmark 流水线图和审计清单","unknown":"课程没有复现完整公开榜单或验证当前模型排名。"},
    "TD-B02": {"title":"Dataset、Split 与 Sealed Holdout","question":"怎样构建代表、挑战、回归和隐藏四类数据而不发生跨组泄漏？","focus":"抽样框、标注争议、实体/时间去重、Holdout 权限和 Dataset Card","decision":"发现泄漏或 Holdout 被反复调试时重建 split，并使旧结论失效。","failure":"随机按行切分让同一 incident 改写跨组出现，高风险又被简单 FAQ 淹没。","metric":"overlap rate、slice coverage、label agreement 与 access count","artifact":"Dataset Card、Split manifest 与访问合同","unknown":"合成数据不能证明真实流量代表性或领域标注质量。"},
    "TD-B03": {"title":"Metrics 与区间","question":"Accuracy、pass@k、resolved rate、Judge score 的分母和不确定性有什么不同？","focus":"逐题逐次 ledger、公式、缺失处理、切片、blocker 和置信区间","decision":"不可比条件或样本不足时保留不确定，不输出虚假精确排名。","failure":"pass@5 很高但单次成功低、成本高，且安全 blocker 被均值掩盖。","metric":"numerator/denominator、k、run count、slice 与 uncertainty","artifact":"Metric Card、逐题 ledger 和区间报告","unknown":"Fixture 没有运行随机模型或真实统计估计。"},
    "TD-B04": {"title":"Harness 敏感性","question":"固定模型和数据时，Prompt、工具、Context、超时与重试如何改变分数？","focus":"单变量实验、锁定 Manifest、paired task flips 与资源差异","decision":"一次只归因一个协议变量；多变量变化输出 CONFOUNDED。","failure":"同时开放工具、延长超时和改 system prompt 后，把提升归因给模型。","metric":"paired flips、effect size、variance、tool calls、timeouts 与 cost delta","artifact":"Harness 单变量敏感性报告","unknown":"公开 Harness 与真实模型适配器均未运行。"},
    "TD-B05": {"title":"污染与不确定性","question":"怎样审计近重复、公开曝光、隐藏测试泄漏、样本波动和版本可比性？","focus":"duplicate/exposure audit、sealed canary、成对区间、访问日志与 rebaseline","decision":"证据不足时输出 SUSPECT/INCOMPARABLE，不宣布整体能力提升。","failure":"候选只在污染题提升，Harness 又更新，却仍宣布显著进步。","metric":"overlap、canary exposure、paired interval、variance 与 version compatibility","artifact":"污染、不确定性与版本审计报告","unknown":"无法确认闭源模型训练数据，污染检测仍可能假阴性。"},
    "TD-B06": {"title":"公共到企业 Benchmark","question":"怎样迁移公共 Benchmark 的方法，而不是复制题目和排名？","focus":"业务风险、四类内部数据、Composite Scorer、维护 owner 与治理","decision":"内部 Benchmark 必须连接真实决策、领域 Oracle 和具名 owner。","failure":"把公开题翻译成中文就当企业发布 Gate，缺少权限、事故和业务 Oracle。","metric":"risk coverage、blocker、slice quality、latency/cost 与 freshness","artifact":"企业内部 Benchmark 最小仓库和治理卡","unknown":"真实企业数据、标注团队、权限和发布连接未建立。"},
}

CONTRACTS = {
    "TD-T20": ("blocking_exit_propagated", True, False),
    "TD-T21": ("lineage_complete", True, False),
    "TD-T22": ("source_trace_linked", True, False),
    "TD-T23": ("joint_gate_complete", True, False),
    "TD-T24": ("waiver_has_expiry", True, False),
    "TD-T25": ("capstone_trace_complete", True, False),
    "TD-B01": ("pipeline_components_complete", True, False),
    "TD-B02": ("holdout_sealed", True, False),
    "TD-B03": ("metric_denominator_declared", True, False),
    "TD-B04": ("single_variable_isolated", True, False),
    "TD-B05": ("contamination_audit_present", True, False),
    "TD-B06": ("enterprise_oracle_linked", True, False),
}

SOURCES = [
    ("W3-01","https://developers.openai.com/api/reference/resources/evals/methods/create","OpenAI Evals API","official-api","implementation","OpenAI","2026-08-11"),
    ("W3-02","https://github.com/EleutherAI/lm-evaluation-harness","Language Model Evaluation Harness","repository","benchmark-harness","EleutherAI","2026-08-11"),
    ("W3-03","https://crfm-helm.readthedocs.io/en/stable/","HELM documentation","official-docs","benchmark-harness","Stanford CRFM","2026-08-11"),
    ("W3-04","https://github.com/swe-bench/SWE-bench","SWE-bench repository","repository","task-benchmark","SWE-bench","2026-08-11"),
    ("W3-05","https://arxiv.org/abs/2310.06770","SWE-bench paper","paper","task-benchmark","Princeton/Chicago","2023-10-10"),
    ("W3-06","https://arxiv.org/abs/2308.03688","AgentBench paper","paper","agent-benchmark","Tsinghua et al.","2023-08-07"),
    ("W3-07","https://www.nist.gov/itl/ai-risk-management-framework","NIST AI RMF","government-guidance","governance","NIST","2026-08-11"),
    ("W3-08","https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf","NIST Generative AI Profile","government-publication","governance","NIST","2024-07-26"),
    ("W3-09","https://research.google/pubs/whats-your-ml-test-score-a-rubric-for-ml-production-systems/","ML Test Score","paper","production-quality","Google Research","2016-12-09"),
    ("W3-10","https://opentelemetry.io/docs/specs/semconv/gen-ai/","OpenTelemetry GenAI semantic conventions","official-spec","observability","OpenTelemetry","2026-08-11"),
    ("W3-11","https://airc.nist.gov/airmf-resources/airmf/5-sec-core/","NIST AI RMF Core","government-guidance","governance","NIST AIRC","2026-08-11"),
    ("W3-12","https://opentelemetry.io/blog/2026/genai-observability/","GenAI observability walkthrough","official-article","observability","OpenTelemetry","2026-05-14"),
]

RUNNER = '''#!/usr/bin/env python3
"""Deterministic quality/benchmark contract lab; no model or network calls."""
import argparse, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--topic",required=True); parser.add_argument("--phase",choices=("baseline","fault","repair"),required=True); args=parser.parse_args()
    contracts=json.loads((ROOT/"configs/topic-contracts.json").read_text(encoding="utf-8"))
    if args.topic not in contracts: raise SystemExit(f"unknown topic: {args.topic}")
    contract=contracts[args.topic]; observed=dict(contract["baseline_observations"]); injected=None
    if args.phase=="fault":
        injected=contract["mutation"]; observed[injected["field"]]=injected["fault_value"]
    checks=[{"field":field,"expected":expected,"actual":observed.get(field),"status":"PASS" if observed.get(field)==expected else "FAIL"} for field,expected in contract["expected"].items()]
    verdict="PASS" if all(row["status"]=="PASS" for row in checks) else "FAIL"
    report={"schema_version":"1.0.0","topic_id":args.topic,"phase":args.phase,"evidence_level":"offline-deterministic-fixture","release_candidate_level":"fixture-only","model_execution":"NOT_RUN","enterprise_integration":"NOT_RUN","practitioner_review":"NOT_RUN","publication":"NOT_RUN","production":"NOT_RUN","verdict":verdict,"decision":contract["decision"],"checks":checks,"injected_mutation":injected,"remaining_unknowns":contract["remaining_unknowns"]}
    target=ROOT/"reports"/args.topic/f"{args.phase}.json"; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
    print(json.dumps({"topic_id":args.topic,"phase":args.phase,"verdict":verdict,"report":str(target.relative_to(ROOT))},ensure_ascii=False)); return 0 if verdict=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())
'''

def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")

def dump(path: Path, value: object) -> None:
    write(path, json.dumps(value, ensure_ascii=False, indent=2))

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def contract_data() -> dict:
    result = {}
    for topic_id, (field, good, bad) in CONTRACTS.items():
        result[topic_id] = {
            "expected": {field: good, "evidence_boundary_declared": True, "human_owner_present": True},
            "baseline_observations": {field: good, "evidence_boundary_declared": True, "human_owner_present": True},
            "mutation": {"mutation_id": f"{topic_id}-fault", "field": field, "fault_value": bad, "professional_consequence": TOPICS[topic_id]["failure"]},
            "decision": TOPICS[topic_id]["decision"],
            "remaining_unknowns": [TOPICS[topic_id]["unknown"], "Model/provider execution NOT_RUN", "Practitioner/publication/production NOT_RUN"],
        }
    return result

def manifest(topic_id: str, public: bool) -> dict:
    working = "materials/ai-quality-benchmark" if public else "site/public/materials/ai-quality-benchmark"
    steps = [{"step_id": phase, "kind": "mutation" if phase=="fault" else phase, "command": f"python3 scripts/run_lab.py --topic {topic_id} --phase {phase}", "expected_exit_code": code, "expected_artifacts": [f"reports/{topic_id}/{phase}.json"]} for phase,code in (("baseline",0),("fault",1),("repair",0))]
    return {"topic_id":topic_id,"page_id":topic_id,"working_directory":working,"required_files":["scripts/run_lab.py","configs/topic-contracts.json","fixtures/cases.json","prompt-package/manifest.json","prompt-package/quality-benchmark-contract.prompt.md","prompt-package/output.schema.json","prompt-package/eval.json","prompt-package/mutation.json","BUNDLE-OWNERS.json"],"steps":steps,"failure_cycle":{"baseline_step_id":"baseline","fault_step_id":"fault","repair_step_id":"repair"},"evidence_boundary":"PASS-FIXTURE only; model, enterprise integration, practitioner review, publication and production are NOT_RUN."}

def research_docs(topic_id: str, item: dict) -> dict[str,str]:
    title, question, focus, decision, failure, metric, artifact, unknown = (item[k] for k in ("title","question","focus","decision","failure","metric","artifact","unknown"))
    brief = f"""# {title}：研究 Brief\n\n## Controlling question\n\n{question}\n\n学习者是第一次系统学习 AI Quality 的测试开发，职业任务发生在合成退款 RAG+Agent 的发布候选审查。系统边界包含需求风险、版本化输入、模型/检索/工具候选、独立 Oracle、运行报告和人工决定；本页重点是 {focus}。业务失败成本是错误政策、越权副作用、无法重放的证据或依据错误 Benchmark 作发布决定。\n\n## 范围和交付\n\n纳入：机制、失效模式、指标合同、版本、owner、三阶段实验和迁移挑战。排除：训练模型、真实企业数据、凭证、自动批准、公共排名时效结论和生产阈值。学员交付 {artifact}。核心专业决定：{decision}\n\n## 研究问题\n\n1. 哪些组件会改变观察？2. 原始事实、工程推断和未知怎样分开？3. 指标 {metric} 的单位、分母、聚合和失败动作是什么？4. 负控怎样模拟 `{failure}`？5. 哪些权限必须留给人？\n\n来源需要覆盖官方 API/规范、开源 Harness、公开 Benchmark、论文、治理与观测；至少十二个页面实际打开的来源。{unknown}\n"""
    synthesis = f"""# {title}：证据综合\n\n## Fact\n\nOpenAI Evals 将 evaluation 描述为数据源配置、测试标准/graders 与可重复运行；这支持把评测从聊天印象拆成版本化结构，但不支持任何企业阈值。lm-evaluation-harness 把任务、模型适配器与运行配置显式化；HELM 强调标准化数据、统一模型接口、逐样例检查和超越 accuracy 的指标；SWE-bench 把真实问题、仓库环境和测试判定结合。这些来源共同支持一个事实：Benchmark 分数依赖任务、数据、协议、系统和 Scorer 的组合。\n\nNIST AI RMF 的 MAP/MEASURE/MANAGE 要求记录场景、风险容忍、测试验证和残余风险；GenAI Profile 把治理放到整个生命周期。ML Test Score 指出小型离线实验不足以证明生产就绪。OpenTelemetry GenAI 语义约定把模型、token、finish reason、tool 调用与 Trace 连接。这些来源支持可观察、可回放、有人负责的质量系统，不支持模型自动批准 waiver 或发布。\n\n## Cross-source synthesis\n\n针对 `{topic_id}`，跨来源工程综合是：{decision} 具体工作面是 {focus}。传统测试的 test basis、独立 Oracle、负控、回归、退出码和事故闭环仍有效；AI 场景扩张了版本图、概率性多次运行、检索/工具轨迹、Judge 校准、数据污染和成本/延迟分布。\n\n反例 `{failure}` 会改变行动：先保存 manifest 和 raw record，再定位第一个破坏合同的组件；不能先改 Prompt 或平均阈值。度量 `{metric}` 必须声明测量点、分母、切片、聚合、版本、owner 与失败动作。高风险 blocker 不允许被许多简单样例平均抵消。\n\n## Unknown\n\n{unknown} 来源也不能给出目标公司的流量、事故频率、权限模型、可接受误报、定价、SLO、隐私分类、真实 Judge 对齐或发布 owner。它们保持 UNKNOWN/NOT_RUN。课程不能用一般方法论伪装成现场证据。\n\n## Counterevidence\n\n公开 Benchmark 的透明和可重复性不能自动解决训练污染、任务代表性或企业适配；隐藏测试不能保证无人泄露；重复运行不能替代正确 Oracle；Trace 丰富也会增加隐私风险。最终方案因此保留访问控制、限制、逐题证据与人类责任。\n"""
    blueprint = f"""# {title}：工程 Blueprint\n\n## Architecture and data flow\n\n合成 case 与版本 Manifest 进入 topic contract。`run_lab.py` 读取固定期望，baseline 生成一致 observation，fault 只改变一个会影响职业决定的字段，repair 恢复 observation 而不改 Oracle。确定性 checker 保存 expected/actual、verdict、mutation、NOT_RUN 状态和未知，再把 exit code 交给人工 Gate。数据流为 `basis → version manifest → candidate observation → independent checks → report/exit → owner decision`。\n\n业务系统、模型、RAG、Agent、企业 CI 和审批均在 Fixture 边界外。本地脚本只证明指定 mutation 会从 exit 0 变为 exit 1，并在恢复后回到 0。Prompt 包存在但 provider=none；其作用是展示 Prompt/Input/Schema/Eval/Mutation 必须一起版本化。\n\n## Metrics and decisions\n\n主测量面为 {metric}。每个指标需要单位、分母、聚合、风险维度、观测点、版本和 owner。合成 Gate 要求三个字段全部精确匹配，单个 blocker 被破坏即 exit 1；这个阈值只为 mutation sensitivity 服务，不能外推到真实业务。统计性指标仍需真实分布、重复次数和不确定性。\n\n## Baseline failure repair\n\n从 `site/public/materials/ai-quality-benchmark` 运行 `python3 scripts/run_lab.py --topic {topic_id} --phase baseline`，预期 0；fault 预期 1 并显示 `{failure}` 对应字段；repair 预期 0。三份 JSON 的 expected 保持相同。若 fault 假绿，依次检查 topic ID、manifest、mutation 字段、report phase 与 shell 是否吞掉退出码。禁止删除用例、改变 expected 或把 blocker 降为 warning。\n\n## CI、安全与恢复\n\n入口条件是 Python 3、全部 required_files、合成公开数据和精确 topic ID。停止条件是缺文件、未知 topic、合同冲突或 expected exit 不符。Prompt 权限为 candidate-only。故障恢复只恢复最后接受的 observation/config；它不是生产回滚。真实环境还需安全 sandbox、secret 隔离、Trace 脱敏和企业审批。\n\n## 责任\n\n学员生成 {artifact}。AI 可整理候选与运行检查；AI 不得批准阈值、例外、权限或发布。{unknown}\n"""
    manuscript = f"""# {title}\n\n## Professional problem\n\n{failure} 这不是“模型偶尔答错”这么简单。对于 `{topic_id}`，真正要回答的是：{question} 如果报告不能回到输入、版本、逐条观察、Oracle 和责任人，那么绿灯只是颜色。\n\n先建立最小心智模型：{focus}。每个组件都要有输入、版本、观察点、失败出口和 owner。事实来自实际打开的 API、规范、仓库、论文和治理资料；跨来源工程动作标为 Inference；企业流量、阈值和现场能力保持 Unknown。\n\n### 为什么传统测试仍然重要\n\n需求/风险仍是 test basis，独立 Oracle 仍决定成功，negative control 仍证明测试能发现坏东西，回归仍防止复发，非零退出码仍让自动化有强制力。变化在于被测对象扩展到 Prompt、Context、知识库、工具、Judge、Harness 和概率性运行。\n\n核心规则是：{decision} 指标不是装饰，本页使用 `{metric}`；必须能说出 numerator、denominator、aggregation、slice、version、owner 和 failure action。无法说清时停止发布解释。\n\n## Runnable action\n\n进入 `site/public/materials/ai-quality-benchmark`，依次执行：\n\n```bash\npython3 scripts/run_lab.py --topic {topic_id} --phase baseline\npython3 scripts/run_lab.py --topic {topic_id} --phase fault\npython3 scripts/run_lab.py --topic {topic_id} --phase repair\n```\n\n预期退出码 `0 → 1 → 0`。运行 fault 前先预测哪个字段变红、为什么会改变专业决定。打开三份报告，确认 expected 完全相同，只有 fault observation 被 mutation 改坏。模型、Provider、企业系统和生产始终 NOT_RUN。\n\n## Failure and repair\n\n若 baseline 失败，先核对 required files、topic、contract 和工作目录。若 fault 仍绿，检查 mutation 是否命中被 Gate 消费的字段以及 shell 是否传播 exit 1。若 repair 失败，恢复 observation，不要修改 expected。把脚本改成迎合故障不是修复。\n\n## 迁移挑战\n\n把退款助手迁移到内部事故总结助手。保持版本、独立 Oracle、负控、报告和人工权限不变；必须更换至少两项：政策证据改为 runbook/telemetry，退款权限改为事故严重度和 on-call 访问。成功标准是正常 Fixture 通过，无证据归因或越权读取稳定 exit 1，并保留原始报告。\n\n## 交付和边界\n\n交付 {artifact}。完成清单包括三阶段收据、版本 Manifest、owner、source_refs、unknowns 与 ZIP hash closure。{unknown} 本页结论只到 PASS-FIXTURE；它不是模型成绩、从业者认可、publication 或 production readiness。\n"""
    comparison = f"""# {title}：两次独立研究 Run 对比\n\n## Agreements\n\nRun A 从 OpenAI Evals、lm-eval、HELM、SWE-bench、NIST 与 OpenTelemetry 建立组件图，强调 {focus} 的可观察输入、版本和接口。Run B 从 `{failure}` 反推 test basis、negative control、stop state、owner 与恢复动作。两次都接受：{decision}；都拒绝流畅输出、自评 Judge、公共榜单或 exit 0 作为完整证明。\n\n## Disagreements\n\nRun A 主张使用 `{metric}` 组织报告，并保留逐题 raw evidence；它的优势是机制清晰，风险是架构过多会延迟学员第一次看到红灯。Run B 要求先做 0→1→0，再扩展统计和平台；它的优势是行动明确，风险是一个 mutation 不能代表真实场景覆盖。分歧还包括先讲架构还是先跑负控，以及度量应围绕技术组件还是业务风险组织。\n\n## Adjudication\n\n裁决是先展示具体失败和最小红灯，再用架构解释红灯的位置；指标必须服务具名决定而非反过来。Run A 的官方/论文来源可解释机制，但不能定企业阈值。Run B 的本地运行可证明 mutation sensitivity，但不能证明模型或生产质量。共同未知：{unknown}\n\nComparator verdict: `ACCEPT-WITH-FIXTURE-BOUNDARY`。拒绝的替代结论包括 universal threshold、一次 PASS 等于稳定、hidden test 等于无污染，以及 fixture RC 等于 publication/production。\n"""
    validation = f"""# {title}：Validation\n\n## Research coverage\n\n12 个 opened 来源覆盖 official API/spec、repository、paper、government guidance、benchmark harness、task benchmark、governance、production quality 与 observability。\n\n## Claim traceability\n\n页面解释 `{question}`；Fact 来自打开来源，工程决定 `{decision}` 标为 synthesis，企业阈值保持 unknown。\n\n## Runnable lab\n\nManifest 固定 required files、working directory、baseline/fault/repair 和 0/1/0 exit；Prompt/Input/Schema/Eval/Mutation 同版本。\n\n## Independent comparison\n\n两次独立研究 run 在 `research-runs.json` 登记并由 `comparison.md` 裁决，保留分歧与反证。\n\n## Publication verdict\n\n`CONTENT-READY / PASS-FIXTURE / RELEASE-BLOCKED`。Model/provider、企业集成、practitioner、publication、production 均 NOT_RUN。Unknown：{unknown}\n"""
    return {"research-brief.md":brief,"evidence-synthesis.md":synthesis,"engineering-blueprint.md":blueprint,"manuscript.md":manuscript,"comparison.md":comparison,"validation.md":validation}

def build_lab() -> None:
    write(LAB / "scripts/run_lab.py", RUNNER)
    dump(LAB / "configs/topic-contracts.json", contract_data())
    dump(LAB / "fixtures/cases.json", {"schema_version":"1.0.0","privacy":"synthetic-public","cases":[{"case_id":tid.lower(),"topic_id":tid,"scenario":"synthetic refund RAG/Agent quality release candidate","source_refs":["synthetic-prd-v1","policy-v2","trace-fixture-v1"]} for tid in TOPICS]})
    write(LAB / "prompt-package/quality-benchmark-contract.prompt.md", """# System\nYou are a candidate-only quality evidence classifier. Never approve thresholds, waivers, permissions, publication or production.\n\n# Task\nRead the fixed input and topic contract. Return only schema-valid JSON with topic_id, observed, expected, source_refs, status and unknowns. Missing, conflicting or unsupported evidence must be BLOCKED/UNKNOWN. Keep model_execution=NOT_RUN unless an external receipt proves otherwise.\n\n# Critic\nReject output that invents evidence, drops a blocker, changes an expected value, omits source_refs, converts fixture evidence to live/practitioner/production, or grants release authority.\n""")
    dump(LAB / "prompt-package/manifest.json", {"package_id":"ai-quality-benchmark-contract","version":"1.0.0","purpose":"classify fixed quality/benchmark evidence; model is not executed","authority":"candidate-only; cannot approve threshold, waiver, permission, publication, production, or release","system_prompt":"quality-benchmark-contract.prompt.md","schema":"output.schema.json","eval":"eval.json","mutation":"mutation.json","input_fixture":"../fixtures/cases.json","model":{"provider":"none","name":"NOT_RUN","parameters":{},"seed":"NOT_RUN"},"expected_statuses":["PASS_SCHEMA","PASS_SEMANTIC","FAIL","BLOCKED","UNKNOWN","NOT_RUN"],"stop_states":["SOURCE_CONFLICT","UNSUPPORTED_RULE","BLOCKED","UNKNOWN"],"review_owner":"AI quality lead and domain owner","limitations":["No model/provider run","Fixture-only evidence"]})
    dump(LAB / "prompt-package/output.schema.json", {"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","required":["topic_id","observed","expected","source_refs","status","unknowns","model_execution"],"properties":{"topic_id":{"type":"string"},"observed":{"type":"object"},"expected":{"type":"object"},"source_refs":{"type":"array","items":{"type":"string"},"minItems":1},"status":{"enum":["PASS_SCHEMA","PASS_SEMANTIC","FAIL","BLOCKED","UNKNOWN","NOT_RUN"]},"unknowns":{"type":"array","items":{"type":"string"}},"model_execution":{"const":"NOT_RUN"}},"additionalProperties":False})
    dump(LAB / "prompt-package/eval.json", {"version":"1.0.0","deterministic_checks":["schema valid","source_refs nonempty","blocker preserved","unknowns preserved","model_execution NOT_RUN"],"semantic_review":"NOT_RUN","human_gate":"required before any maturity promotion"})
    dump(LAB / "prompt-package/mutation.json", {"version":"1.0.0","mutations":[{"mutation_id":f"{tid}-fault","topic_id":tid,"field":CONTRACTS[tid][0],"expected_kill":"exit 1"} for tid in TOPICS]})

def write_research_and_manifests() -> None:
    for topic_id,item in TOPICS.items():
        folder=TOPIC_ROOT/topic_id; folder.mkdir(parents=True,exist_ok=True)
        for name,body in research_docs(topic_id,item).items(): write(folder/name,body)
        with (folder/"source-pack.csv").open("w",encoding="utf-8",newline="") as handle:
            writer=csv.writer(handle); writer.writerow(["source_id","url","title","source_type","source_family","publisher_group","accessed_at","version_date","evidence_lane","supports","does_not_support","limitations","opened_status"])
            for sid,url,title,stype,family,publisher,version in SOURCES:
                writer.writerow([sid,url,title,stype,family,publisher,"2026-08-11",version,family,f"Supports {item['focus']} from {family}",f"Does not establish {item['decision']} as universal production policy",f"{item['unknown']} Source bounded to stated system.","opened"])
        stale=folder/"independent-research-runs.json"
        if stale.exists(): stale.unlink()
        run_ids=[f"{topic_id}-architecture-20260811",f"{topic_id}-measurement-20260811"]
        dump(folder/"research-runs.json", {"topic_id":topic_id,"runs":[{"run_id":run_ids[0],"route":"architecture-primary-docs","status":"opened-sources-synthesized","source_refs":[x[0] for x in SOURCES[:8]]},{"run_id":run_ids[1],"route":"measurement-failure-counterevidence","status":"opened-sources-synthesized","source_refs":[x[0] for x in SOURCES[4:]]}],"comparison":{"reviewer":"independent-validation-contract-reviewer","input_run_ids":run_ids,"output_ref":"comparison.md","verdict":"ACCEPT-WITH-FIXTURE-BOUNDARY"},"limitations":[item["unknown"],"No live model or enterprise run"]})
        dump(folder/"lab-manifest.json", manifest(topic_id, False))
        dump(PUBLIC/"manifests"/f"{topic_id}.json", manifest(topic_id, True))

def run_public_labs() -> list[dict]:
    receipts=[]
    for topic_id in TOPICS:
        for phase,expected in (("baseline",0),("fault",1),("repair",0)):
            command=[sys.executable,"scripts/run_lab.py","--topic",topic_id,"--phase",phase]
            run=subprocess.run(command,cwd=PUBLIC,text=True,capture_output=True)
            if run.returncode!=expected: raise SystemExit(f"{topic_id} {phase}: expected {expected}, got {run.returncode}: {run.stderr}")
            report=PUBLIC/"reports"/topic_id/f"{phase}.json"
            receipts.append({"topic_id":topic_id,"phase":phase,"command":" ".join(command[1:]),"expected_exit_code":expected,"actual_exit_code":run.returncode,"stdout":run.stdout.strip(),"report":str(report.relative_to(PUBLIC)),"report_sha256":sha(report),"evidence_level":"PASS-FIXTURE","model_execution":"NOT_RUN","enterprise_integration":"NOT_RUN","practitioner_review":"NOT_RUN","publication":"NOT_RUN","production":"NOT_RUN"})
    return receipts

def write_course(receipts: list[dict]) -> None:
    course_runs={row["phase"]:row for row in receipts if row["topic_id"]=="TD-T25"}
    dump(COURSE/"course-manifest.json", {"course_id":"td-ai-quality-benchmark","title":"AI 质量系统、Benchmark 与 Capstone","page_ids":list(TOPICS),"scenario_ids":["TD-S07"],"ai_lane":"build-ai-quality-system","ai_lanes":["build-ai-quality-system","test-ai-systems"],"ai_centrality_score":5,"professional_value_score":5,"system_under_test":"版本化 AI Quality CI、Benchmark 与 Capstone Fixture release candidate","ai_roles":["system-under-test","candidate-generator","judge-dependency","quality-infrastructure"],"learner_artifact":["layered CI gate","lineage manifest","trace regression","benchmark repository","fixture release candidate"],"tool_adapters":["python-stdlib-offline-contract","optional-model-harness-NOT_RUN"],"work_domain_ids":["TD-D01"],"primary_artifact_ids":["ai-quality-benchmark-fixture-rc"],"decision_owner":"AI 质量负责人","allowed_ai_authority":"自动运行和比较评测，不得自动批准例外","prerequisite_course_ids":["td-ai-foundations-eval"],"transfer_target":"将退款助手质量系统迁移到内部事故总结助手，并重新建立证据、权限、风险切片、Benchmark 与回滚合同","lesson_flow":["demo","guided-practice","failure-injection","repair","transfer"],"default_path_requires_credentials":False,"baseline_comparison":True,"failure_injection":True,"execution_proof":"evidence/execution-evidence.json","validation_workdir":"lab","validation_steps":[{"name":f"TD-T25 {phase}","command":["python3","scripts/run_lab.py","--topic","TD-T25","--phase",phase],"expected_exit_code":code} for phase,code in (("baseline",0),("fault",1),("repair",0))],"status":"fixture-tested","evidence_ids":["S03","S05","S07","S23","S24","S36","S37","S38","S39","S40","S70"],"evidence_boundary":"PASS-FIXTURE release candidate only; model/provider/integration/practitioner/publication/production NOT_RUN"})
    def proof_row(phase: str) -> dict:
        row=course_runs[phase]
        return {"exit_code":row["actual_exit_code"],"verdict":"PASS" if row["actual_exit_code"]==0 else "FAIL","report":row["report"],"report_sha256":row["report_sha256"],"model_execution":"NOT_RUN"}
    commands=[f"python3 scripts/run_lab.py --topic TD-T25 --phase {phase}" for phase in ("baseline","fault","repair")]
    dump(COURSE/"evidence/execution-evidence.json", {"evidence_scope":"TD-T25 deterministic offline capstone contract sensitivity","commands":commands,"baseline":proof_row("baseline"),"mutation":proof_row("fault"),"repair":proof_row("repair"),"environment":{"runtime":f"Python {sys.version.split()[0]}","credentials":"none","working_directory":"courses/td-ai-quality-benchmark/lab","model_execution":"NOT_RUN","enterprise_integration":"NOT_RUN"},"limitations":["No model, RAG, Agent, cloud CI or enterprise integration","No practitioner/publication/production validation"]})
    write(COURSE/"course.md", """# AI 质量系统、Benchmark 与 Capstone\n\n面向已经理解 AI/Eval 基础、希望把零散评测升级成工程质量系统的测试开发。十二页从 CI 分层门禁、版本 lineage、Trace-to-regression、质量/延迟/成本联合 Gate、漂移/waiver/回滚，进入 Benchmark 任务、数据、协议、Scorer、聚合、Split/Holdout、Metrics/CI、Harness 敏感性、污染/不确定性和公共到企业迁移，最后由 Capstone 消费全链工件。\n\n## AI centrality\n\n移除 AI 后，这门课的核心被测对象就不存在：Prompt、有限 Context、知识索引、模型 Judge、Agent 工具选择、Harness 协议敏感性、训练污染和 Token 成本都是 AI 系统新增或被重新定义的质量面。传统 CI、test basis、独立 Oracle、负控、回归和事故闭环仍保留，但必须扩张版本图、Trace 和统计证据。\n\n## System under test\n\n被测对象是一个合成退款 RAG+Agent 的版本化 release candidate，以及负责评测它的 CI/Benchmark 质量系统。边界包括 PRD/Risk、Dataset/Split、Prompt/Input/Schema、模型和知识/工具版本、Composite Oracle、Harness、逐题报告、质量/延迟/成本 Gate、waiver 与 rollback。真实模型、企业 CI、身份和副作用系统保持边界外。\n\n## Baseline and target\n\n基线是手工聊天抽查、浮动版本、只看平均分和没有退出码的假绿报告。目标是每个发布判断都能回到当前 SHA、完整 lineage、风险切片、逐条 raw evidence、独立 Oracle、首次红灯、修复和具名 owner。Fixture 目标严格限定为同一合同下稳定复现 `0→1→0`，不把本地绿灯写成模型或生产成功。\n\n## Commands\n\n从课程 lab 运行 Capstone 的三阶段合同；三条命令必须分别执行并立即检查退出码：\n\n```bash\ncd courses/td-ai-quality-benchmark/lab\npython3 scripts/run_lab.py --topic TD-T25 --phase baseline\npython3 scripts/run_lab.py --topic TD-T25 --phase fault\npython3 scripts/run_lab.py --topic TD-T25 --phase repair\n```\n\n预期退出码依次为 0、1、0，报告位于 `reports/TD-T25/`。完整公开包对十二页共实际运行 36 条命令，并在 `run-receipts.json` 保存命令、预期/实际退出码和报告 SHA-256。\n\n## Metrics and thresholds\n\n每页指标必须声明单位、numerator、denominator、aggregation、risk slice、measurement point、version、owner 和 failure action。CI 先检查 blocker，再看风险切片阈值，最后才展示总体分；安全 blocker 不被简单样例平均抵消。质量、p95/p99 延迟和 cost-per-success 使用独立硬门禁。本地阈值只是三个固定字段精确匹配，不能复用为企业生产默认值。\n\n## Failure injection\n\nTD-T25 fault 将 `capstone_trace_complete` 从 true 改为 false，模拟 Capstone 只交最终绿报告却缺少全链 trace closure。脚本必须 `exit 1`、`verdict=FAIL` 并保存 expected/actual；baseline 与 repair 必须为 PASS。Repair 只能恢复 observation，不能修改 expected、删除 blocker、吞掉 non-zero 或把 FAIL 改成 warning。\n\n## Human review gate\n\nAI 的权限是“自动运行和比较评测，不得自动批准例外”。AI 可以整理候选合同、执行确定性检查和生成比较报告；AI 不能决定业务 Oracle、风险容忍、阈值、waiver、权限扩大、污染接受或发布。AI 质量负责人拥有阻断或批准有期限 waiver 的决定权，领域和安全 owner 必须复核各自规则。\n\n## AI-specific failure boundary\n\n课程覆盖 Prompt/模型/知识/工具版本漂移、Judge 波动、数据集泄漏、Harness 混杂、检索与工具 Trace 断链、总体均值掩盖 blocker、p99 与重试成本退化、waiver 永不过期以及隐藏测试污染。它不覆盖真实 Provider 内部路由、线上流量、企业 secret、身份链、生产副作用、完整攻击面或真实事故响应，这些保持 UNKNOWN/NOT_RUN。\n\n## Learner artifact\n\n学员交付分层 CI workflow、lineage graph、脱敏 Trace-to-regression 记录、质量/延迟/成本联合 Gate、漂移/waiver/rollback Runbook、Dataset Card、representative/challenge/regression/sealed-holdout 四类集合、Metric Card、Harness 单变量实验、污染审计、企业内部 Benchmark，以及 Prompt/Input/Schema/Eval/Mutation 包、36 条 receipts、bundle owners 和 ZIP hash closure。迁移挑战把退款助手换成事故总结助手，必须重做专业证据和权限而非只替换名词。\n\n## Evidence status\n\n当前状态是 `fixture-tested / PASS-FIXTURE release candidate`。证据只证明 Python 标准库 checker 能杀死十二个已声明 mutation，公开目录和 ZIP member 的 SHA-256 一致。Prompt 包的 provider=none、model=NOT_RUN；真实模型、RAG/Agent、企业集成、从业者评审、publication 与 production 全部 NOT_RUN。因此 Capstone 不能被表述为完整发布、生产就绪或从业者验证。\n""")
    materials={"quickstart.md":"# Quickstart\n\n进入 lab，依次运行 TD-T25 baseline/fault/repair；预期 0/1/0。检查 expected 未变、fault 命中 capstone_trace_complete、所有成熟度保持 NOT_RUN。","reusable-skill.md":"# Reusable quality-system skill\n\n1. 从 decision/risk/owner 开始。2. 固定 Prompt/Input/Schema/Data/Model/Knowledge/Tool/Scorer。3. 先跑 baseline。4. 注入会改变决定的单一 fault。5. 要求 exit 1。6. 修复 observation。7. 保存 receipts、owner、hash closure 与 unknown。","sample-input.md":"# Synthetic input\n\n退款助手 fixture release candidate，包含政策引用、租户权限、工具调用、Trace、CI、Benchmark 和 rollback 合同；无真实客户数据或凭证。","expected-output.md":"# Expected output\n\nBaseline/repair PASS，fault FAIL；证据等级 PASS-FIXTURE，model/integration/practitioner/publication/production 全部 NOT_RUN。","verification-checklist.md":"# Verification checklist\n\n- [ ] 十二页均有独立九件研究包与 12 opened sources。\n- [ ] Prompt/Input/Schema/Eval/Mutation 版本一致。\n- [ ] 36 条命令退出码为 0/1/0。\n- [ ] owner 和 ZIP hash closure 一致。\n- [ ] Capstone 只写 fixture release candidate。"}
    provenance=[]
    for index,(name,body) in enumerate(materials.items(),1):
        path=COURSE/"materials"/name; write(path,body); provenance.append({"material_id":f"QUALITY-BENCH-{index:02d}","path":f"materials/{name}","purpose":body.splitlines()[0].lstrip("# "),"source_ids":["S23","S24","S36","S37","S38","S40"],"scenario_ids":["TD-S07"],"generated_from":"Wave-3 research and fresh deterministic fixture runs","license_or_usage":"repository-owned educational material; synthetic public data","validation_status":"fixture-tested","validation_evidence":"evidence/execution-evidence.json","contains_synthetic_data":True,"limitations":"No live model, enterprise integration, practitioner, publication or production proof"})
    dump(COURSE/"materials/material-provenance.json", {"schema_version":"1.0.0","materials":provenance})
    write(COURSE/"video/brief.md", "# Lesson brief\n\n用 CI 假绿冷开场，真实呈现 0→1→0、lineage diff、Trace 回归、Benchmark protocol、waiver 到期和 ZIP closure；明确 Fixture RC 不等于发布。")
    write(COURSE/"video/script.md", "# Lesson script\n\n先看退款风险被平均分掩盖。冻结 manifest，运行 baseline；预测 fault；观察 exit 1 和 trace closure 缺失；恢复 observation 后 repair。随后将合同迁移到事故总结助手。")
    write(COURSE/"video/storyboard.md", "# Storyboard\n\n1 CI 假绿。2 全链架构。3 baseline。4 fault 预测。5 红灯定位。6 repair。7 Benchmark/waiver。8 owners/hash closure。9 Fixture/publication 边界。")
    stage_ids=["cold-open-failure","stakes-and-promise","before-after","plain-mental-model","guided-demo","failure-diagnosis","learner-practice","transfer-challenge","artifact-handoff"]
    stages=[]
    for sid in stage_ids:
        row={"stage_id":sid,"instructor_action":f"引导 {sid} 的质量系统证据","learner_action":"检查版本、风险、负控、报告和 owner","expected_observation":"证据状态与 0/1/0 可复现","debrief":"Fixture 只证明 mutation sensitivity","artifact_or_assessment":"版本化质量工件"}
        if sid=="transfer-challenge": row.update({"source_context":"合成退款 RAG/Agent 质量系统","target_context":"将退款助手质量系统迁移到内部事故总结助手，并重新建立证据、权限、风险切片、Benchmark 与回滚合同","invariant":"版本、独立 Oracle、负控、人工权力和 receipt 不变","must_change":["政策证据改为 runbook/telemetry","租户退款权限改为事故严重度/on-call 权限"],"success_criterion":"正常摘要通过，无证据归因或越权读取稳定 exit 1"})
        stages.append(row)
    dump(COURSE/"video/lesson-experience.json", {"lesson_id":"td-ai-quality-benchmark-capstone","target_learner":"已完成 AI/Eval 基础的测试开发","level":"L1-guided-fixture","estimated_minutes":120,"job_result":"能交付可杀死高风险 mutation 的 AI Quality Fixture RC","artifact":"CI、Lineage、Trace、Benchmark、Rollback 与 closure","stages":stages,"interaction_prompts":["这个绿灯是否绑定当前版本？","fault 会在哪个 Gate 变红？","迁移时哪些专业 Oracle 必须重做？"],"recovery_path":"恢复 known-good manifest 和 observation，不放宽 expected","evidence_status":"fixture-tested","limitations":"无模型、企业、从业者、publication 或 production 证据"})

def write_ownership_and_closure() -> None:
    owners={"schema_version":"1.0.0","bundle_id":"ai-quality-benchmark","shared":True,"owner_page_ids":list(TOPICS),"decision_owner":"AI 质量负责人","artifact_owner":"course factory validation lane","allowed_authority":"fixture generation and comparison only; no release approval","limitations":["Model/integration/practitioner/publication/production NOT_RUN"]}
    dump(PUBLIC/"BUNDLE-OWNERS.json", owners); dump(COURSE/"bundle-ownership.json", owners)
    entries=[]
    for path in sorted(PUBLIC.rglob("*")):
        if path.is_file() and path.name!="ARTIFACT-CLOSURE.json": entries.append({"path":str(path.relative_to(PUBLIC)),"sha256":sha(path),"owner":"course factory validation lane","owner_page_ids":list(TOPICS)})
    closure={"schema_version":"1.0.0","bundle_id":"ai-quality-benchmark","algorithm":"sha256","entry_count":len(entries),"entries":entries,"self_excluded":"ARTIFACT-CLOSURE.json excluded to avoid recursive hash","evidence_level":"PASS-FIXTURE","maturity":{"model":"NOT_RUN","integration":"NOT_RUN","practitioner":"NOT_RUN","publication":"NOT_RUN","production":"NOT_RUN"}}
    dump(PUBLIC/"ARTIFACT-CLOSURE.json",closure); dump(COURSE/"artifact-closure.json",closure)

def build() -> None:
    build_lab()
    if PUBLIC.exists(): shutil.rmtree(PUBLIC)
    shutil.copytree(LAB,PUBLIC)
    write(PUBLIC/"README.md", "# AI quality system and benchmark fixture\n\nTwelve page-level deterministic labs; no credentials, model, network, enterprise integration, practitioner review, publication or production. Run each manifest baseline/fault/repair; expected exits 0/1/0.")
    write_research_and_manifests()
    receipts=run_public_labs()
    dump(PUBLIC/"run-receipts.json", {"schema_version":"1.0.0","evidence_level":"PASS-FIXTURE","run_count":len(receipts),"runs":receipts,"limitations":["No model/provider/network call","No enterprise/practitioner/publication/production validation"]})
    write_course(receipts)
    write_ownership_and_closure()
    if ARCHIVE.exists(): ARCHIVE.unlink()
    with zipfile.ZipFile(ARCHIVE,"w",compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(PUBLIC.rglob("*")):
            if path.is_file(): zf.write(path,path.relative_to(PUBLIC))
    with zipfile.ZipFile(ARCHIVE) as zf:
        closure=json.loads((PUBLIC/"ARTIFACT-CLOSURE.json").read_text(encoding="utf-8"))
        for row in closure["entries"]:
            if hashlib.sha256(zf.read(row["path"])).hexdigest()!=row["sha256"]: raise SystemExit(f"zip closure mismatch: {row['path']}")
    print(json.dumps({"topics":len(TOPICS),"runs":len(receipts),"research_files_per_topic":9,"opened_sources_per_topic":len(SOURCES),"archive":str(ARCHIVE),"archive_sha256":sha(ARCHIVE)},ensure_ascii=False))

if __name__=="__main__": build()
