#!/usr/bin/env python3
"""Build the Wave-3 AI serving and career course assets from page contracts."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
COURSE = ROOT / "courses" / "td-ai-serving-career"
PUBLIC = ROOT / "site" / "public" / "materials" / "ai-serving-career"
TOPICS_ROOT = ROOT / "research" / "topics"


TOPICS = {
    "TD-A01": {
        "title": "普通 API 与 AI API：从确定性响应到版本化生成服务",
        "question": "怎样证明一次 AI API 结果来自哪组协议、模型、Prompt、上下文、采样、Schema、工具和区域变量，而不伪造供应商内部版本？",
        "method": "保留 HTTP、鉴权、错误和幂等共同契约，再增加生成 Manifest、行为 Oracle、Token/成本和可靠性层。",
        "oracle": "request_id 必须存在；公开版本变量齐全；不可见内部版本为 UNKNOWN；错误类别能驱动 retryable 决策。",
        "fault": "删除 request_id，并把不可见内部模型版本伪造为固定值。",
        "repair": "恢复 request_id，把内部版本改回 UNKNOWN，同时保留可见模型别名、Prompt、Schema 和 Tool 版本。",
        "artifact": "AI API 五层测试面、版本 Manifest 与错误分类表",
        "metric": "Manifest 完整率、UNKNOWN 诚实率、错误分类覆盖率",
        "expected": {"request_id": "req-fixture-001", "model.internal_version": "UNKNOWN", "error.retryable": False},
        "fault_patch": {"request_id": "", "model.internal_version": "invented-2026-08-11"},
        "unknown": "供应商内部模型修订、路由、限额和区域实现没有公开可观察证据。",
    },
    "TD-A02": {
        "title": "AI API 协议：Streaming、Structured、Tool 与 Async",
        "question": "怎样证明 streaming、structured output、tool call 和 async job 的过程与终态都合法，且取消或重试不会重复副作用？",
        "method": "为 SSE、结构化输出、工具调用、异步任务建立四个独立状态机，分别检查过程和终态。",
        "oracle": "事件顺序合法且唯一终态；Schema 与业务语义均通过；工具副作用至多一次；异步部分失败不得汇总为完成。",
        "fault": "模拟断流重试后再次执行同一工具，使 side_effect_count 从 1 变成 2。",
        "repair": "恢复幂等键和状态查询，重放同一 request_id 只读取已有终态。",
        "artifact": "四协议状态机、事件 reducer、幂等账本与重放报告",
        "metric": "非法序列数、语义不变量失败数、副作用重复数、唯一终态率",
        "expected": {"stream.terminal_count": 1, "structured.semantic_pass": True, "tool.side_effect_count": 1, "async.terminal": "completed"},
        "fault_patch": {"tool.side_effect_count": 2},
        "unknown": "真实代理缓冲、网络分片、工具服务和任务队列没有运行。",
    },
    "TD-A03": {
        "title": "AI Serving 指标：TTFT、TPOT、ITL、Goodput 与单位成功成本",
        "question": "怎样让 TTFT、TPOT、ITL、Goodput 和 cost_per_success 的时间点、分母、切片与质量条件都可重算？",
        "method": "从请求、首 Token、逐 Token 和终态时间戳计算延迟；Goodput 只计质量、安全、完整性和 SLO 同时合格的请求。",
        "oracle": "TTFT、TPOT、ITL 可由原始事件重算；Goodput 分母含所有到达；单位成功成本含失败和重试。",
        "fault": "把质量失败请求计入 Goodput，并从单位成功成本中删除失败尝试费用。",
        "repair": "恢复全部到达分母、quality_pass 条件和所有尝试成本。",
        "artifact": "指标定义卡、Token 事件夹具与单位成功成本报告",
        "metric": "TTFT、TPOT、ITL、Goodput、cost_per_success",
        "expected": {"metrics.goodput_requests": 2, "metrics.total_arrivals": 3, "metrics.cost_per_success": 0.09},
        "fault_patch": {"metrics.goodput_requests": 3, "metrics.cost_per_success": 0.04},
        "unknown": "fixture 时间戳和成本不代表任何模型、GPU、地区或供应商。",
    },
    "TD-A04": {
        "title": "AI Serving 负载与容量：从 Token 分布到 SLO 拐点",
        "question": "怎样固定到达率、Token 长度、缓存、场景和质量条件，找到 fixture 的 Goodput 拐点且不发生 coordinated omission？",
        "method": "open-loop 保持外部到达并记录 dropped arrivals；closed-loop 仅诊断单用户上限；阶梯实验每级只改到达率。",
        "oracle": "计划到达数等于完成、失败、dropped 和仍排队之和；SLO 破坏后停止；容量以 Goodput 判定。",
        "fault": "删除 dropped arrivals，并只用完成请求作为容量分母。",
        "repair": "恢复到达账本和排队项，把失败与 dropped 纳入分母。",
        "artifact": "工作负载 Manifest、阶梯实验与 fixture-only 容量报告",
        "metric": "到达守恒、Goodput 拐点、安全余量、dropped arrivals",
        "expected": {"arrivals.planned": 10, "arrivals.accounted": 10, "capacity.evidence_level": "fixture-only"},
        "fault_patch": {"arrivals.accounted": 8},
        "unknown": "没有网络、模型、GPU、调度器或生产流量，不能外推真实容量。",
    },
    "TD-A05": {
        "title": "AI Serving 瓶颈：Queue、GPU、KV Cache 与阶段诊断",
        "question": "怎样从 TTFT、TPOT、ITL 症状定位 Queue、prefill、decode、GPU、KV Cache 或工具瓶颈，并避免相关性误判？",
        "method": "先按阶段症状分流，再关联 request trace 与资源信号，最后用单变量实验确认或推翻候选根因。",
        "oracle": "高 TTFT 且 queue 占主要比例指向排队；KV 高必须伴随 eviction/preemption 或对照实验；不可见指标为 UNKNOWN。",
        "fault": "忽略 queue_time，仅因 GPU 利用率同步升高便把 root_cause 标为 gpu。",
        "repair": "恢复阶段占比判断，并用降低到达率的单变量结果确认 queue 根因。",
        "artifact": "瓶颈诊断树、Trace 对照、反证与单变量实验记录",
        "metric": "queue/prefill/decode 占比、GPU memory、KV usage、实验差异",
        "expected": {"diagnosis.root_cause": "queue", "diagnosis.single_variable_confirmed": True, "managed_internal_metrics": "UNKNOWN"},
        "fault_patch": {"diagnosis.root_cause": "gpu", "diagnosis.single_variable_confirmed": False},
        "unknown": "托管服务内部队列、GPU profiler 和真实 KV cache eviction 不可见。",
    },
    "TD-A06": {
        "title": "AI Serving 韧性：限流、Timeout、Retry、Fallback 与 Degradation",
        "question": "怎样保证 429、5xx、超时和断流下重试有界、工具副作用不重复，fallback 不会无声突破质量与安全底线？",
        "method": "先分类错误并传播 deadline；次数、总时间、Token/费用和副作用共同限制重试；fallback 必须独立评测。",
        "oracle": "429 尊重 Retry-After；attempt/time/cost 均不超预算；同一幂等键副作用至多一；fallback quality gate 通过才可使用。",
        "fault": "忽略 Retry-After，重试八次，并静默启用未通过质量门禁的 fallback。",
        "repair": "恢复三次以内、deadline/cost budget、幂等查询和安全失败；未过质量门禁则转人工。",
        "artifact": "韧性状态机、重试预算、故障矩阵与恢复证据",
        "metric": "attempt/time/token/cost budget、call amplification、fallback quality",
        "expected": {"retry.attempts": 3, "retry.respected_retry_after": True, "fallback.quality_gate": True, "tool.side_effect_count": 1},
        "fault_patch": {"retry.attempts": 8, "retry.respected_retry_after": False, "fallback.quality_gate": False},
        "unknown": "真实供应商配额、Retry-After、fallback 模型质量和生产恢复没有运行。",
    },
    "TD-C01": {
        "title": "职业能力迁移：岗位路径、自评证据与作品集边界",
        "question": "怎样把已有测试能力迁移到可验证的新责任，并用作品证明，而不承诺就业、薪资或某一岗位必然存在？",
        "method": "用 O*NET、SFIA、ISTQB、NIST 建责任基线，再按风险、代码/数据、AI Eval、Serving/Reliability、沟通治理五维自评。",
        "oracle": "岗位负责/协作/禁止边界清楚；自评分有 evidence_ref 或 UNKNOWN；90 天计划含 baseline-fault-repair；employment_guarantee=false。",
        "fault": "把证书数量当能力证据，并加入完成课程即可就业的承诺。",
        "repair": "删除就业承诺，把能力等级绑定可复验作品和 30/60/90 天复评。",
        "artifact": "岗位路径图、能力自评 JSON、90 天计划和作品集证据表",
        "metric": "有证据能力项比例、UNKNOWN 数、岗位边界完整率、红绿作品覆盖率",
        "expected": {"career.employment_guarantee": False, "career.evidence_refs_complete": True, "career.role_boundary_complete": True},
        "fault_patch": {"career.employment_guarantee": True, "career.evidence_refs_complete": False},
        "unknown": "课程不能证明招聘需求、薪资、晋升、地区机会或个体适配。",
    },
}


SOURCES = [
    ("SRC-OAS", "OpenAPI Specification", "official standard", "protocol", "openapi", "OpenAPI Initiative", "https://spec.openapis.org/oas/latest.html"),
    ("SRC-HTTP", "HTTP Semantics RFC 9110", "internet standard", "protocol", "ietf-http", "IETF", "https://www.rfc-editor.org/rfc/rfc9110.html"),
    ("SRC-SSE", "Server-sent events", "living standard", "protocol", "whatwg-sse", "WHATWG", "https://html.spec.whatwg.org/multipage/server-sent-events.html"),
    ("SRC-JSON", "JSON Schema 2020-12", "official standard", "schema", "json-schema", "JSON Schema", "https://json-schema.org/draft/2020-12"),
    ("SRC-ASYNC", "AsyncAPI Specification 3.0.0", "official standard", "async", "asyncapi", "AsyncAPI Initiative", "https://www.asyncapi.com/docs/reference/specification/v3.0.0"),
    ("SRC-CLOUD", "CloudEvents Specification", "official standard", "events", "cloudevents", "CNCF", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md"),
    ("SRC-OPENAI-STREAM", "OpenAI Responses streaming events", "official documentation", "implementation", "openai-stream", "OpenAI", "https://platform.openai.com/docs/api-reference/responses-streaming"),
    ("SRC-OPENAI-STRUCT", "Introducing Structured Outputs", "official technical article", "implementation", "openai-structured", "OpenAI", "https://openai.com/index/introducing-structured-outputs-in-the-api/"),
    ("SRC-VLLM", "vLLM production metrics", "official documentation", "metrics", "vllm-metrics", "vLLM", "https://docs.vllm.ai/en/stable/usage/metrics/"),
    ("SRC-NIM", "NVIDIA NIM LLM benchmarking metrics", "official documentation", "metrics", "nvidia-nim", "NVIDIA", "https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html"),
    ("SRC-GENAI", "GenAI-Perf README", "reference implementation", "load", "nvidia-genaiperf", "NVIDIA", "https://github.com/triton-inference-server/perf_analyzer/tree/main/genai-perf"),
    ("SRC-K6", "Open and closed load models", "official documentation", "load", "grafana-k6", "Grafana", "https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/"),
    ("SRC-SRE", "Handling Overload", "technical guidance", "reliability", "google-sre", "Google", "https://sre.google/sre-book/handling-overload/"),
    ("SRC-AWS", "Timeouts, retries, and backoff with jitter", "technical guidance", "reliability", "aws-builders-library", "AWS", "https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/"),
    ("SRC-ONET", "Software Quality Assurance Analysts and Testers", "occupational database", "career", "onet", "US Department of Labor", "https://www.onetonline.org/link/details/15-1253.00"),
    ("SRC-BLS", "Software developers, QA analysts, and testers", "government outlook", "career", "bls", "US Bureau of Labor Statistics", "https://www.bls.gov/ooh/computer-and-information-technology/software-developers.htm"),
    ("SRC-SFIA-TEST", "SFIA Testing skill", "professional framework", "career", "sfia-testing", "SFIA Foundation", "https://sfia-online.org/en/sfia-9/skills/testing"),
    ("SRC-SFIA-QA", "SFIA Quality assurance skill", "professional framework", "governance", "sfia-qa", "SFIA Foundation", "https://sfia-online.org/en/sfia-9/skills/quality-assurance"),
    ("SRC-NIST", "NIST AI RMF Core", "government framework", "governance", "nist-airc", "NIST", "https://airc.nist.gov/airmf-resources/airmf/5-sec-core/"),
    ("SRC-ISTQB", "ISTQB CTFL Syllabus 4.0.1", "professional syllabus", "testing", "istqb-ctfl", "ISTQB", "https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf"),
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def dump(path: Path, value: object) -> None:
    write(path, json.dumps(value, ensure_ascii=False, indent=2))


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def topic_sources(topic_id: str) -> list[tuple[str, ...]]:
    if topic_id == "TD-C01":
        selected = SOURCES[14:] + SOURCES[0:6] + SOURCES[8:10]
    elif topic_id in {"TD-A03", "TD-A04", "TD-A05", "TD-A06"}:
        selected = SOURCES[8:14] + SOURCES[0:6]
    else:
        selected = SOURCES[0:12]
    return selected[:12]


def research_docs(topic_id: str, item: dict) -> dict[str, str]:
    shared_boundary = "本页实验为确定性离线 fixture：没有调用模型、供应商、GPU、队列、工具或招聘系统；PASS 只证明声明的 mutation 被门禁杀死。"
    brief = f"""# {item['title']} research brief

## Controlling question

{item['question']}

专业角色是负责 AI API、Serving 或职业迁移证据的测试开发工程师。业务对象是版本化生成服务与其发布决定。失败代价包括不可归因回归、重复副作用、错误容量承诺、重试风暴和无证据职业建议。范围包括独立控制问题、方法选择、Oracle、版本化 Prompt/Input/Schema/Eval/Mutation 以及 baseline-fault-repair。范围外包括真实 Provider 能力、生产 SLO、硬件容量、就业与薪资承诺。

研究先看协议和标准，再看 Serving 实现与指标，再看可靠性反例和职业框架。核心方法：{item['method']} 学员工件：{item['artifact']}。关键 Unknown：{item['unknown']}
"""
    synthesis = f"""# {item['title']} evidence synthesis

## Fact

打开的 HTTP、OpenAPI、SSE、JSON Schema、AsyncAPI 与 CloudEvents 资料共同说明：协议形状、事件序列、终态和错误语义属于不同证据面，不能用最终文本相互替代。vLLM 与 NVIDIA 文档暴露首 Token、逐 Token、队列、缓存或请求结果等 Serving 指标，但这些定义并不自动给出某个业务的阈值。k6 的 open/closed 模型说明负载生成方式会改变观察到的到达行为。Google SRE 与 AWS 的过载、超时、重试和 jitter 指导说明恢复策略也可能放大故障。

对本页最重要的事实是：{item['oracle']} 这是可观测字段的条件，不是模型能力或生产安全证明。来源能定义协议、测量点、故障机制和责任框架；来源不能替目标组织决定错误成本、容量、安全余量、岗位设置或风险接受人。

## Cross-source synthesis

本页采用的方法是：{item['method']} 选择理由不是追求更多指标，而是让一个失败能定位到唯一或有限的责任层。普通 API 的状态码和 Schema 仍然保留；AI API 额外记录模型/Prompt/Schema/Tool 版本、流式事件、Token 和行为证据；Serving 把 queue、prefill、decode、quality 和 cost 分开；职业迁移把岗位职责、自评和 evidence_ref 分开。

控制问题“{item['question']}”落到一个可执行判断：{item['oracle']} 主指标是 {item['metric']}。每个指标必须写明分子、分母、聚合、切片、采集点、版本与 owner。fixture 中使用精确值只为证明 mutation sensitivity，不能外推为生产阈值。

反例是：{item['fault']} 如果只看最终 PASS、总延迟、GPU 利用率、证书数量或友好回答，反例会被隐藏。因此本页先运行 baseline，随后只改变声明的 fault 字段并要求 exit 1，最后恢复实现且不修改 Oracle。修复要求：{item['repair']}

职业页额外使用 O*NET、SFIA、ISTQB 与 NIST，把岗位描述、技能责任、测试基础和 AI 风险治理作为不同输入。它们支持能力映射，不支持承诺就业、薪资、晋升或某一公司岗位。Serving 页的容量数字一律写为 fixture-only。

## Unknown

{item['unknown']} 真实组织还需要确认流量分布、错误成本、数据/隐私等级、模型和硬件版本、工具权限、事件与指标可观测性、风险接受人。缺失字段保持 UNKNOWN、NOT_RUN 或 BLOCKED。{shared_boundary}
"""
    blueprint = f"""# {item['title']} engineering blueprint

## Architecture and data flow

数据流为 `approved input fixture -> page manifest -> candidate observation -> independent exact-field Oracle -> JSON evidence -> human decision`。Prompt 包包含 system、task、critic、manifest、Schema、eval 和 mutation；默认 provider 为 none，模型执行为 NOT_RUN。runner 读取本页 manifest 和 input fixture；baseline 使用批准观察，fault 只应用 `fault_patch`，repair 恢复批准观察。每个阶段都保存输入 hash、manifest hash、检查字段、预期值、实际值、退出码和边界。

架构边界至少包括客户端、协议、模型/Prompt/Tool、Serving 阶段、Telemetry、可靠性和人类 Gate。对 TD-C01，边界替换为当前能力、目标责任、证据作品、差距计划和独立招聘决定。关键决策为：{item['method']} 任何 required file 缺失、hash 漂移或 Oracle 不一致都停止，禁止模型补写 UNKNOWN。

## Metrics and decisions

指标目录：{item['metric']}。字段级 Oracle 是：{item['oracle']}。fixture 判定采用精确相等，因为它的任务是证明合同检测力；真实系统必须改为基于业务损失、历史分布、风险切片和置信度的门槛。Goodput 只计质量、安全、完整性和 SLO 同时满足的请求，单位成功成本包含失败和重试。职业能力分数必须绑定 evidence_ref，否则为 UNKNOWN。

决策次序是输入与版本完整性、确定性 blocker、协议/过程、语义或质量、成本/容量、人工 Gate。平均分不得覆盖越权、重复副作用、安全拒绝错误、到达不守恒或就业承诺。报告 owner 是 page oracle owner；真实风险接受 owner 需要目标组织重新指定。

## Baseline failure repair

工作目录为 `site/public/materials/ai-serving-career`。运行 `python3 scripts/serving_lab.py --manifest manifests/{topic_id}.json --mode baseline`，期望 exit 0；运行 fault，期望 exit 1；运行 repair，期望 exit 0；运行 cycle，外层 exit 0 且内部码严格为 `[0,1,0]`。反例：{item['fault']} 修复：{item['repair']}

诊断先检查 page_id、required files 和 hash，再检查 fault_patch 是否只改变声明字段，然后核对 expected/actual。禁止通过修改 expected、删除检查、吞掉 exit 1 或把 NOT_RUN 写成 PASS 来修复。{shared_boundary}
"""
    manuscript = f"""# {item['title']}

## Professional problem

本页从一个具体控制问题开始：{item['question']} 初学者常见错误是只保存最终文本、总耗时、GPU 百分比或证书清单，却没有可重放版本、过程事件、独立 Oracle 和决策 owner。真正的专业动作是把输入、版本、过程、结果、成本、风险和边界分开。

方法选择是：{item['method']} 独立 Oracle 为：{item['oracle']} 这使学员能解释为什么一个测试变红，而不是只复制命令。学员最终交付 {item['artifact']}，并在工件中区分 desk-researched、fixture-tested、live-tested、practitioner-reviewed 与 production-validated。

### 最小例子

baseline 观察包含本页批准字段，runner 对每个点路径做精确检查。fault 阶段注入：{item['fault']}。门禁必须产生 exit 1，并保存 expected/actual。repair 阶段执行：{item['repair']}。Oracle 和输入合同保持不变。

### 方法与边界

协议页分别检查事件序列、Schema、语义、幂等和唯一终态；指标页从原始事件重算；容量页核对计划到达守恒且只给 fixture 拐点；诊断页要求单变量反证；韧性页同时限制次数、时间、Token、成本和副作用；职业页要求 evidence_ref 和 `employment_guarantee=false`。

## Runnable action

```bash
cd outputs/test-development-ai-v2/site/public/materials/ai-serving-career
python3 scripts/serving_lab.py --manifest manifests/{topic_id}.json --mode baseline
python3 scripts/serving_lab.py --manifest manifests/{topic_id}.json --mode fault
python3 scripts/serving_lab.py --manifest manifests/{topic_id}.json --mode repair
python3 scripts/serving_lab.py --manifest manifests/{topic_id}.json --mode cycle
```

预期内部结果为 `0 -> 1 -> 0`。打开 `evidence/{topic_id}/` 下四份 JSON，核对 input hash、manifest hash、实际检查和 evidence level。先预测哪一个字段会变红，再运行；如果 fault 仍绿，立即判为测试资产无检测力。

## Failure and repair

失败：{item['fault']} 修复：{item['repair']} 修复不得降低阈值、修改 expected、删除 blocker 或把失败改成 warning。迁移到真实服务前，替换 fixture、版本、流量、阈值、owner 和回滚，同时保留 Schema、Oracle ID、mutation 和证据字段。

本页的 Remaining Unknown 是：{item['unknown']}。{shared_boundary} 对 TD-C01，岗位路径只是学习规划，不能写成就业、薪资或晋升承诺。
"""
    comparison = f"""# {item['title']} independent comparison

## Agreements

Run A 从协议、标准和实现文档出发；Run B 从故障、测量、可靠性和职业责任出发。两者同意控制问题必须落到可观察字段：{item['question']} 两者也同意方法为：{item['method']}，并要求 baseline-fault-repair 证明检测力。

两次研究都拒绝把一个流畅答案、一次延迟、一个 GPU 利用率或一个证书当完整证据。共同接受的 Oracle 是：{item['oracle']}。共同边界是 fixture-only，没有 live、practitioner 或 production 证据。

## Disagreements

Run A 更强调协议精确性和架构层次；Run B 更强调最小可执行工件、故障代价和 owner。Run A 希望先列完整指标；Run B 要求先写发布问题、错误成本和停止条件。对容量数字，Run B 进一步要求所有结果标记 fixture-only。对职业建议，Run B 要求显式 `employment_guarantee=false`。

来源也有张力：供应商文档较新但产品特定；标准和职业框架较稳定但不描述某一实现。最终不能把任一来源扩写成通用阈值、硬件承诺或就业结果。

## Adjudication

最终页先展示专业失败，再给最小机制、版本化 Prompt 包、确定性实验和迁移边界。主指标保留为 {item['metric']}，但从属于具名决策。fault 为“{item['fault']}”，repair 为“{item['repair']}”。比较 verdict 为 `ACCEPT-WITH-FIXTURE-BOUNDARY`。

未决项保持：{item['unknown']}。编辑审查确认命令、0/1/0、路径、数字、技术字段和成熟度没有被泛化正文覆盖。
"""
    validation = f"""# {item['title']} validation

## Research coverage

十二个打开来源覆盖协议、Schema、事件、实现、指标、负载、可靠性、治理和职业框架；不少于五个 lane、五个 family 和四种 source type。

## Claim traceability

协议和指标定义来自原始标准或官方文档；“{item['method']}”属于跨来源工程推论。Unknown 保留：{item['unknown']}

## Runnable lab

本页 manifest 指向版本化 Prompt/Input/Schema/Eval/Mutation 和标准库 runner。baseline/fault/repair 期望退出 0/1/0；cycle 验证内部实际码。

## Independent comparison

两次独立研究运行在 `research-runs.json` 中绑定，分歧和裁决保存在 `comparison.md`。

## Publication verdict

`CONTENT-READY / PASS-FIXTURE / RELEASE-BLOCKED`。未通过 practitioner、live、production 和出版门禁。
"""
    return {"research-brief.md": brief, "evidence-synthesis.md": synthesis, "engineering-blueprint.md": blueprint, "manuscript.md": manuscript, "comparison.md": comparison, "validation.md": validation}


RUNNER = r'''#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def digest(path): return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
def get_path(data, dotted):
    value = data
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value: return None
        value = value[part]
    return value
def set_path(data, dotted, value):
    parts=dotted.split("."); cur=data
    for part in parts[:-1]: cur=cur.setdefault(part,{})
    cur[parts[-1]]=value
def evaluate(manifest_path, mode):
    manifest=load(manifest_path); root=manifest_path.parents[1]
    fixture_path=root/manifest["input_fixture"]
    actual=copy.deepcopy(load(fixture_path)["observation"])
    if mode=="fault":
        for key,value in manifest["fault_patch"].items(): set_path(actual,key,value)
    checks=[]
    for key,expected in manifest["expected"].items():
        observed=get_path(actual,key); checks.append({"field":key,"expected":expected,"actual":observed,"pass":observed==expected})
    passed=all(x["pass"] for x in checks)
    report={"schema_version":"1.0.0","page_id":manifest["page_id"],"phase":mode,"verdict":"PASS" if passed else "FAIL","exit_code":0 if passed else 1,"evidence_level":"PASS-FIXTURE" if passed else "FAIL-FIXTURE","model_execution":"NOT_RUN","input_sha256":digest(fixture_path),"manifest_sha256":digest(manifest_path),"checks":checks,"unknowns":manifest["unknowns"],"boundary":manifest["evidence_boundary"]}
    out=root/"evidence"/manifest["page_id"]/f"{mode}.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report["exit_code"], out
def main():
    p=argparse.ArgumentParser(); p.add_argument("--manifest",required=True); p.add_argument("--mode",choices=["baseline","fault","repair","cycle"],required=True); a=p.parse_args()
    manifest_path=Path(a.manifest).resolve()
    if a.mode!="cycle":
        phase="baseline" if a.mode=="repair" else a.mode; code,out=evaluate(manifest_path,phase)
        if a.mode=="repair":
            target=out.with_name("repair.json"); out.replace(target); out=target
        print(json.dumps({"phase":a.mode,"exit_code":code,"report":str(out)},ensure_ascii=False)); raise SystemExit(code)
    codes=[]; reports={}
    for phase in ("baseline","fault","repair"):
        source="baseline" if phase=="repair" else phase; code,out=evaluate(manifest_path,source)
        if phase=="repair":
            target=out.with_name("repair.json"); out.replace(target)
        codes.append(code); reports[phase]=str(out)
    ok=codes==[0,1,0]
    manifest=load(manifest_path); root=manifest_path.parents[1]; out=root/"evidence"/manifest["page_id"]/"cycle.json"
    out.write_text(json.dumps({"page_id":manifest["page_id"],"actual_exit_codes":codes,"expected_exit_codes":[0,1,0],"verdict":"PASS" if ok else "FAIL","reports":reports,"evidence_level":"PASS-FIXTURE" if ok else "FAIL-FIXTURE","model_execution":"NOT_RUN"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"phase":"cycle","actual_exit_codes":codes,"report":str(out)},ensure_ascii=False)); raise SystemExit(0 if ok else 1)
if __name__=="__main__": main()
'''


def page_manifest(topic_id: str, item: dict, public: bool = True) -> dict:
    working = "materials/ai-serving-career" if public else "site/public/materials/ai-serving-career"
    required = [
        "owners.json", "scripts/serving_lab.py", f"fixtures/{topic_id}-input.json",
        f"prompts/{topic_id}/system-v1.md", f"prompts/{topic_id}/task-v1.md", f"prompts/{topic_id}/critic-v1.md",
        f"prompts/{topic_id}/manifest.json", f"prompts/{topic_id}/mutation.json",
        f"schemas/{topic_id}-output.schema.json", f"evals/{topic_id}-eval.json",
    ]
    steps = []
    for phase, code in (("baseline", 0), ("fault", 1), ("repair", 0), ("cycle", 0)):
        artifacts = [f"evidence/{topic_id}/{phase}.json"] if phase != "cycle" else [f"evidence/{topic_id}/{x}.json" for x in ("baseline", "fault", "repair", "cycle")]
        steps.append({"step_id": phase, "kind": "mutation" if phase == "fault" else phase, "command": f"python3 scripts/serving_lab.py --manifest manifests/{topic_id}.json --mode {phase}", "expected_exit_code": code, "expected_artifacts": artifacts})
    return {
        "schema_version": "1.0.0", "page_id": topic_id, "topic_id": topic_id, "title": item["title"],
        "working_directory": working, "input_fixture": f"fixtures/{topic_id}-input.json", "expected": item["expected"],
        "fault_patch": item["fault_patch"], "oracle": item["oracle"], "required_files": required, "steps": steps,
        "failure_cycle": {"baseline_step_id": "baseline", "fault_step_id": "fault", "repair_step_id": "repair"},
        "owners": {"content": f"{topic_id}-content-owner", "oracle": f"{topic_id}-oracle-owner", "release": "ai-serving-career-release-owner"},
        "unknowns": [item["unknown"]], "evidence_boundary": "PASS-FIXTURE only; deterministic offline input. No provider/model/GPU/live/practitioner/production evidence; capacity values are fixture-only.",
    }


def build_public_and_research() -> None:
    if PUBLIC.exists(): shutil.rmtree(PUBLIC)
    write(PUBLIC / "scripts" / "serving_lab.py", RUNNER)
    write(PUBLIC / "README.md", """# AI Serving 与职业迁移实验包

七页共用一个确定性 Python runner，但每页拥有独立 Manifest、输入、Prompt、Schema、Eval、Mutation、Oracle 和 owner。运行任一页的 cycle，内部实际退出码必须为 `0/1/0`。所有结果仅为 PASS-FIXTURE；不包含真实模型、GPU、供应商、生产流量、从业者评审或就业保证。容量数字一律 fixture-only。
""")
    owners = {"schema_version": "1.0.0", "bundle_owner": "ai-serving-career-wave-3", "runner_owner": "course-lab-engineering", "release_owner": "ai-serving-career-release-owner", "page_owners": {}}
    for topic_id, item in TOPICS.items():
        owners["page_owners"][topic_id] = {"content": f"{topic_id}-content-owner", "oracle": f"{topic_id}-oracle-owner", "prompt": f"{topic_id}-prompt-owner", "release": "ai-serving-career-release-owner"}
        fixture = {"schema_version": "1.0.0", "page_id": topic_id, "approved_at": "2026-08-11", "evidence_level": "fixture-only", "observation": {}}
        for dotted, value in item["expected"].items():
            cursor = fixture["observation"]; parts = dotted.split(".")
            for part in parts[:-1]: cursor = cursor.setdefault(part, {})
            cursor[parts[-1]] = value
        dump(PUBLIC / "fixtures" / f"{topic_id}-input.json", fixture)
        dump(PUBLIC / "schemas" / f"{topic_id}-output.schema.json", {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"urn:career-ai:{topic_id}:output:1.0.0",
            "type": "object",
            "required": ["page_id", "claims", "unknowns", "decision"],
            "properties": {
                "page_id": {"const": topic_id},
                "claims": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["claim", "source_ref", "status"],
                        "properties": {
                            "claim": {"type": "string"},
                            "source_ref": {"type": "string"},
                            "status": {"enum": ["EVIDENCE", "INFERENCE", "UNKNOWN"]},
                        },
                    },
                },
                "unknowns": {"type": "array", "items": {"type": "string"}},
                "decision": {"type": "string"},
            },
            "additionalProperties": False,
        })
        prompt_dir = PUBLIC / "prompts" / topic_id
        write(prompt_dir / "system-v1.md", f"# {topic_id} system prompt v1\n\n你是受限的测试证据候选生成器。只处理：{item['question']} 不得改写 UNKNOWN、门禁、owner、fixture-only 或就业边界。")
        write(prompt_dir / "task-v1.md", f"# {topic_id} task prompt v1\n\n读取批准的 `{topic_id}` 输入，只生成能回链 source_ref 的候选。控制问题：{item['question']} 方法：{item['method']} Oracle：{item['oracle']} 输出严格满足 Schema。")
        write(prompt_dir / "critic-v1.md", f"# {topic_id} critic prompt v1\n\n逐条检查来源、版本、独立 Oracle、Evidence/Inference/Unknown、成熟度和禁止承诺。必须拒绝：{item['fault']} 保留：{item['unknown']}")
        dump(prompt_dir / "mutation.json", {"schema_version": "1.0.0", "page_id": topic_id, "mutation_id": f"MUT-{topic_id}-01", "description": item["fault"], "fault_patch": item["fault_patch"], "expected_detection": "at least one exact-field Oracle fails"})
        dump(prompt_dir / "manifest.json", {"schema_version": "1.0.0", "version": "1.0.0", "page_id": topic_id, "provider": "none", "model_execution": "NOT_RUN", "system_prompt": "system-v1.md", "task_prompt": "task-v1.md", "critic_prompt": "critic-v1.md", "input": f"../../fixtures/{topic_id}-input.json", "schema": f"../../schemas/{topic_id}-output.schema.json", "eval": f"../../evals/{topic_id}-eval.json", "mutation": "mutation.json", "stop_states": ["UNKNOWN", "BLOCKED", "NOT_RUN"], "authority": "candidate generation only; no Gate, production, capacity or employment decision"})
        dump(PUBLIC / "evals" / f"{topic_id}-eval.json", {"schema_version": "1.0.0", "page_id": topic_id, "version": "1.0.0", "model_execution": "NOT_RUN", "deterministic_fixture_eval": {"expected": item["expected"], "fault_patch": item["fault_patch"], "required_exit_codes": [0, 1, 0]}, "professional_oracle": item["oracle"], "boundary": item["unknown"]})
        dump(PUBLIC / "manifests" / f"{topic_id}.json", page_manifest(topic_id, item, public=True))

        topic_dir = TOPICS_ROOT / topic_id
        topic_dir.mkdir(parents=True, exist_ok=True)
        for filename, body in research_docs(topic_id, item).items(): write(topic_dir / filename, body)
        with (topic_dir / "source-pack.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["source_id", "url", "title", "source_type", "source_family", "publisher_group", "accessed_at", "version_date", "evidence_lane", "supports", "does_not_support", "limitations", "opened_status"])
            for sid, title, stype, lane, family, publisher, url in topic_sources(topic_id):
                writer.writerow([sid, url, title, stype, family, publisher, "2026-08-11", "accessed-2026-08-11", lane, f"Supports definitions or constraints used to analyze {item['question']}", "Does not establish universal production thresholds, provider behavior, capacity, or employment outcomes", item["unknown"], "opened"])
        run_a = f"{topic_id}-protocol-architecture-20260811"; run_b = f"{topic_id}-failure-measurement-20260811"
        dump(topic_dir / "research-runs.json", {"topic_id": topic_id, "runs": [{"run_id": run_a, "lane": "protocol-architecture", "role": "researcher", "status": "complete", "output_ref": "source-pack.csv", "source_refs": [x[0] for x in topic_sources(topic_id)[:8]]}, {"run_id": run_b, "lane": "failure-measurement-career", "role": "independent-critic", "status": "complete", "output_ref": "evidence-synthesis.md", "source_refs": [x[0] for x in topic_sources(topic_id)[4:]]}], "comparison": {"reviewer": "independent-serving-and-career-contract-reviewer", "input_run_ids": [run_a, run_b], "output_ref": "comparison.md", "verdict": "ACCEPT-WITH-FIXTURE-BOUNDARY"}, "limitations": [item["unknown"], "No live model/provider/GPU/practitioner/production execution"]})
        dump(topic_dir / "lab-manifest.json", page_manifest(topic_id, item, public=False))
        write(topic_dir / "research-package.md", f"# {topic_id} research package\n\n九件门禁文件、十二个打开来源、两次独立研究运行和逐页实验 Manifest 的索引。控制问题：{item['question']}")
    dump(PUBLIC / "owners.json", owners)


def run_cycles() -> list[dict]:
    receipts = []
    for topic_id in TOPICS:
        command = [sys.executable, "scripts/serving_lab.py", "--manifest", f"manifests/{topic_id}.json", "--mode", "cycle"]
        run = subprocess.run(command, cwd=PUBLIC, text=True, capture_output=True)
        if run.returncode != 0: raise SystemExit(f"{topic_id} cycle failed: {run.stdout}\n{run.stderr}")
        cycle = PUBLIC / "evidence" / topic_id / "cycle.json"
        data = json.loads(cycle.read_text(encoding="utf-8"))
        if data.get("actual_exit_codes") != [0, 1, 0]: raise SystemExit(f"{topic_id} did not prove 0/1/0")
        receipts.append({"page_id": topic_id, "command": " ".join(command[1:]), "exit_code": run.returncode, "actual_exit_codes": data["actual_exit_codes"], "cycle_report": str(cycle.relative_to(PUBLIC)), "cycle_sha256": sha(cycle), "model_execution": "NOT_RUN"})
    dump(PUBLIC / "run-receipts.json", {"schema_version": "1.0.0", "evidence_level": "PASS-FIXTURE", "python": sys.version.split()[0], "runs": receipts, "limitations": ["No model/provider/GPU/network call", "No practitioner/live/production or employment validation"]})
    return receipts


def build_closure() -> None:
    files = {}
    for path in sorted(PUBLIC.rglob("*")):
        if path.is_file() and path.name != "closure-manifest.json": files[str(path.relative_to(PUBLIC))] = sha(path)
    pages = {}
    for topic_id in TOPICS:
        source_paths = [f"fixtures/{topic_id}-input.json", f"manifests/{topic_id}.json", f"prompts/{topic_id}/manifest.json"]
        material_paths = [f"schemas/{topic_id}-output.schema.json", f"evals/{topic_id}-eval.json", f"prompts/{topic_id}/mutation.json", f"evidence/{topic_id}/cycle.json"]
        pages[topic_id] = {"owner": f"{topic_id}-content-owner", "oracle_owner": f"{topic_id}-oracle-owner", "source_hashes": {p: files[p] for p in source_paths}, "material_hashes": {p: files[p] for p in material_paths}, "required_file_count": len(json.loads((PUBLIC / "manifests" / f"{topic_id}.json").read_text())["required_files"]), "evidence_boundary": "PASS-FIXTURE only"}
    dump(PUBLIC / "closure-manifest.json", {"schema_version": "1.0.0", "algorithm": "sha256", "bundle_owner": "ai-serving-career-wave-3", "file_count": len(files), "files": files, "pages": pages, "archive_excluded_from_hash_closure": "ai-serving-career.zip", "forbidden_claims": ["PASS-LIVE", "PASS-PRACTITIONER", "production capacity", "employment guarantee"]})


def build_course(receipts: list[dict]) -> None:
    for child in COURSE.iterdir():
        if child.name == "scripts": continue
        if child.is_dir(): shutil.rmtree(child)
        else: child.unlink()
    shutil.copytree(PUBLIC, COURSE / "learner-materials")
    manifest = {
        "course_id": "td-ai-serving-career", "title": "AI API、Serving 质量与职业能力迁移", "scenario_ids": ["TD-S07"],
        "ai_lane": "build-ai-quality-system", "ai_centrality_score": 5, "professional_value_score": 5,
        "system_under_test": "版本化 AI API 协议、Serving 指标/容量/瓶颈/韧性与职业证据合同",
        "ai_roles": ["system-under-test", "candidate-generator", "serving-dependency"],
        "learner_artifact": ["AI API contract", "protocol state machines", "serving metric card", "fixture capacity report", "bottleneck diagnosis", "resilience budget", "career self-assessment and portfolio plan"],
        "tool_adapters": ["python-stdlib-offline-fixture", "provider-and-GPU-adapters-NOT_RUN"], "work_domain_ids": ["TD-D03", "TD-D05"],
        "primary_artifact_ids": ["ai-serving-quality-gate", "career-evidence-map"], "decision_owner": "AI 质量负责人",
        "allowed_ai_authority": "自动运行和比较评测，不得自动批准例外", "prerequisite_course_ids": ["td-ai-foundations-eval"],
        "transfer_target": "将同一版本、协议、测量、韧性和证据合同迁移到目标组织的受控 AI 服务",
        "lesson_flow": ["demo", "guided-practice", "failure-injection", "repair", "transfer"], "default_path_requires_credentials": False,
        "baseline_comparison": True, "failure_injection": True, "execution_proof": "evidence/execution-evidence.json", "learner_materials_root": "learner-materials",
        "validation_workdir": "learner-materials", "validation_steps": [
            {"name": "TD-A01 API contract baseline", "command": ["python3", "scripts/serving_lab.py", "--manifest", "manifests/TD-A01.json", "--mode", "baseline"], "expected_exit_code": 0},
            {"name": "TD-A06 retry storm fault", "command": ["python3", "scripts/serving_lab.py", "--manifest", "manifests/TD-A06.json", "--mode", "fault"], "expected_exit_code": 1},
            {"name": "TD-C01 career boundary repair", "command": ["python3", "scripts/serving_lab.py", "--manifest", "manifests/TD-C01.json", "--mode", "repair"], "expected_exit_code": 0},
        ], "status": "fixture-tested", "evidence_ids": ["S44", "S46", "S51", "S52", "S53", "S54", "S56", "S57", "S60", "S62", "S64"],
        "topic_page_ids": list(TOPICS), "human_gate": "AI 质量负责人确认发布问题、阈值依据和风险；招聘方独立决定岗位与录用",
        "not_run": ["live provider", "real model", "GPU", "production traffic", "practitioner review", "employment outcome"],
        "shared_bundle_owners": json.loads((PUBLIC / "owners.json").read_text(encoding="utf-8")),
        "evidence_boundary": "PASS-FIXTURE only; capacity fixture-only; no employment promise.",
    }
    dump(COURSE / "course-manifest.json", manifest)
    dump(COURSE / "evidence" / "execution-evidence.json", {"evidence_scope": "Seven deterministic offline AI API/serving/career contracts", "commands": [x["command"] for x in receipts], "baseline": {"exit_code": 0, "verdict": "PASS", "report": "learner-materials/evidence/TD-A01/baseline.json"}, "mutation": {"exit_code": 1, "verdict": "FAIL", "report": "learner-materials/evidence/TD-A06/fault.json"}, "repair": {"exit_code": 0, "verdict": "PASS", "report": "learner-materials/evidence/TD-C01/repair.json"}, "environment": {"runtime": f"Python {sys.version.split()[0]}", "credentials": "none", "model_execution": "NOT_RUN"}, "limitations": ["No provider/model/GPU/network/practitioner/production execution", "Capacity numbers are fixture-only", "No employment, salary, promotion or role-availability guarantee"]})
    write(COURSE / "course.md", """# AI API、Serving 质量与职业能力迁移

这是一门从协议一路走到职业工件的完整实践课。七页不是同一篇泛化正文：TD-A01 比较普通 API 与 AI API；TD-A02 分解 Streaming、Structured、Tool、Async；TD-A03 定义 TTFT、TPOT、ITL、Goodput 与单位成功成本；TD-A04 用 open/closed 负载找 fixture 拐点；TD-A05 用阶段证据诊断 Queue/GPU/KV cache；TD-A06 设计限流、超时、重试、回退和降级；TD-C01 把既有测试能力迁移为有证据的岗位路径和作品集。

## AI centrality

移除 AI serving 后，Token 流、TTFT/TPOT/ITL、模型和 Prompt 版本、工具副作用、KV cache、fallback 质量变化等核心对象不存在。传统 HTTP、风险、Oracle、负载和可靠性知识仍然保留，但被测边界、数据结构和发布证据发生扩张。AI 可以生成候选测试与诊断假设，不能批准阈值、waiver、容量、风险或职业结论。

## System under test

被测对象是合成的 AI API 与 Serving 合同，不是某家供应商。边界从客户端、HTTP/SSE/Async、Model/Prompt/Schema/Tool 版本，经过 Queue/Prefill/Decode/GPU/KV 和 Telemetry，到 Retry/Fallback Gate 与人工决定。职业页的系统边界是当前能力、目标责任、证据作品、差距计划和招聘组织的独立决定。

## Baseline and target

baseline 是只看最终文本、总耗时、GPU 百分比或证书数量。目标是每页有独立控制问题、方法理由、Oracle、版本化 Prompt/Input/Schema/Eval/Mutation、0/1/0 报告、owner 和 hash closure。所有容量只到 fixture，所有职业建议明确 `employment_guarantee=false`。

## Commands

从公开学习包根目录运行逐页完整 cycle。以下命令不需要网络、密钥、模型或 GPU；外层 exit 0 仅在内部实际退出码严格为 `0/1/0` 时成立。

```bash
cd learner-materials
python3 scripts/serving_lab.py --manifest manifests/TD-A01.json --mode cycle
python3 scripts/serving_lab.py --manifest manifests/TD-A06.json --mode cycle
python3 scripts/serving_lab.py --manifest manifests/TD-C01.json --mode cycle
```

## Metrics and thresholds

协议页看事件顺序、唯一终态、Schema+语义和副作用账本；性能页看 TTFT、TPOT、ITL、Goodput、cost_per_success；容量页看计划到达守恒与 Goodput 拐点；诊断页看 queue/prefill/decode、GPU/KV 与单变量实验；韧性页看 attempt/time/token/cost budget 和 fallback 质量；职业页看 evidence_ref、UNKNOWN 和岗位边界完整率。fixture 的精确值只为杀死 mutation，不是行业或生产阈值。

## Failure injection

每页 fault 只改变 manifest 声明的字段。例如 TD-A06 把重试次数从 3 改为 8、忽略 Retry-After，并令 fallback quality gate 失败。预期进程 exit 1、报告 verdict=FAIL，且 exact-field Oracle 显示 expected/actual。若 fault 不变红，立即判定测试资产无检测力；修复只能恢复实现观察，不能删除检查或修改 expected。

## Human review gate

AI 质量负责人确认发布问题、指标分母、风险切片、阈值依据、owner 和残余风险。协议或副作用 blocker 不能被平均分覆盖。容量必须在真实模型、硬件、流量和故障环境重新验证。招聘、薪资、晋升、地区机会与个体适配由具体组织独立决定，本课程不承诺任何结果。

## AI-specific failure boundary

模型候选可能发明内部版本、把最终文本当工具事实、隐藏 dropped arrivals、从 GPU 相关性推导根因、建议无限重试或写出就业承诺。Prompt 包默认 provider=none、model_execution=NOT_RUN。Schema 通过不等于业务正确，fixture 红绿不等于 live、practitioner 或 production 通过。

## Learner artifact

学员交付七份独立 manifest 与 evidence：AI API 五层测试面、四协议状态机、指标卡、fixture-only 容量报告、瓶颈诊断树、韧性预算，以及包含岗位负责/协作/禁止边界、evidence_ref、UNKNOWN、30/60/90 天计划和 baseline-fault-repair 作品的自评 JSON。

## Evidence status

当前为 `fixture-tested`。Python 标准库 runner 已实际证明七页各自 `baseline -> fault -> repair = 0/1/0` 并写入逐页 hash。真实 Provider、模型、GPU、网络、生产流量、从业者评审和就业结果均为 NOT_RUN；出版仍由上层门禁决定。
""")
    write(COURSE / "materials" / "quickstart.md", "# Quickstart\n\n进入 `learner-materials`，选择一个 page manifest 运行 cycle；打开对应 evidence 四份报告并核对 0/1/0、hash、UNKNOWN 和 boundary。")
    write(COURSE / "materials" / "reusable-skill.md", "# Reusable skill\n\n1. 写控制问题和风险决定。2. 固定 Input/Version/Owner。3. 选择独立 Oracle。4. 版本化 Prompt/Schema/Eval/Mutation。5. 运行 baseline-fault-repair。6. 保留 Unknown。7. 真实迁移时重定阈值和责任。")
    write(COURSE / "materials" / "sample-input.md", "# Sample input\n\n使用 `learner-materials/fixtures/TD-A06-input.json`：三次有界重试、尊重 Retry-After、fallback quality gate 通过、工具副作用一次。")
    write(COURSE / "materials" / "expected-output.md", "# Expected output\n\ncycle 外层退出 0，内部码 `[0,1,0]`。fault 报告至少一项 exact-field Oracle 为 false；repair 不修改 expected。")
    write(COURSE / "materials" / "verification-checklist.md", "# Verification checklist\n\n- required files 存在\n- prompt/input/schema/eval/mutation 版本化\n- baseline/fault/repair 为 0/1/0\n- owner 与 hash closure 完整\n- capacity=fixture-only\n- employment_guarantee=false\n- live/practitioner/production 均未冒充")
    provenance = []
    material_specs = [
        ("M-SERVE-01", "materials/quickstart.md", "复现逐页 0/1/0 实验", ["S44", "S51"], "fixture-tested", "离线 fixture，不含真实服务"),
        ("M-SERVE-02", "materials/reusable-skill.md", "迁移控制问题、Oracle 与故障链", ["S44", "S46"], "static-reviewed", "真实阈值和 owner 必须重定"),
        ("M-SERVE-03", "materials/sample-input.md", "解释有界重试和回退输入", ["S46", "S51"], "fixture-tested", "合成输入，不代表供应商配额"),
        ("M-SERVE-04", "materials/expected-output.md", "判读机器报告与内部退出码", ["S44", "S51"], "fixture-tested", "只证明声明 mutation 的检测力"),
        ("M-SERVE-05", "materials/verification-checklist.md", "复核成熟度、容量与职业边界", ["S60", "S64"], "static-reviewed", "没有 practitioner 或就业结果验证"),
        ("M-SERVE-06", "learner-materials/README.md", "公开实验入口、限制与复跑方法", ["S44", "S51", "S60"], "fixture-tested", "模型、GPU、网络和生产流量均 NOT_RUN"),
    ]
    for material_id, path, purpose, sources, status, limitations in material_specs:
        provenance.append({"material_id": material_id, "path": path, "purpose": purpose, "source_ids": sources, "scenario_ids": ["TD-S07"], "generated_from": ["Wave-3 research synthesis", "scripts/build_assets.py"], "license_or_usage": "项目原创教学材料，可在内部学习与受控演练中修改复用", "validation_status": status, "validation_evidence": ["evidence/execution-evidence.json" if status == "fixture-tested" else "course.md"], "contains_synthetic_data": status == "fixture-tested", "limitations": limitations})
    dump(COURSE / "materials" / "material-provenance.json", {"course_id": "td-ai-serving-career", "materials": provenance})
    write(COURSE / "video" / "brief.md", "# Video brief\n\n用一次断流重复工具副作用做冷开场，沿协议、指标、容量、诊断、韧性和职业证据推进。静态脚本，视频未制作。")
    write(COURSE / "video" / "script.md", "# Video script\n\n先看最终回答似乎成功，再打开 side-effect ledger 看见重复执行。随后逐层展示七页工件和 0/1/0 证据。结尾重申容量 fixture-only、职业无就业承诺。")
    write(COURSE / "video" / "storyboard.md", "# Storyboard\n\n1 冷开场失败。2 普通 API 与 AI API 对照。3 四协议状态机。4 Token 时间线。5 到达守恒。6 Queue/GPU/KV 诊断。7 Retry/Fallback。8 作品集证据。")
    stage_specs = [
        ("cold-open-failure", "展示最终回答正常但工具被重复执行的红灯账本", "判断能否发布并写下缺失的过程证据", "最终文本不能证明副作用只发生一次", "过程 Oracle 与结果 Oracle 必须分开", "初始发布判断和未知项"),
        ("stakes-and-promise", "展示七页工件、0/1/0 和 hash closure", "把每个文件映射到输入、检查、证据或决定", "可复用结果是一条证据链而不是提示词清单", "版本、owner 和失败出口共同构成可审计交付", "材料到决策步骤映射表"),
        ("before-after", "对比普通 API 断言与 AI API 五层测试面", "标出协议、生成变量、行为、Serving 和可靠性", "AI API 扩张证据面但不废弃普通 HTTP 合同", "共同面和新增面应分别验证", "普通 API 与 AI API 对照图"),
        ("plain-mental-model", "用排队、首 Token、逐 Token 和终态解释 Serving", "从时间线手算 TTFT、TPOT 和 ITL", "总延迟不能定位 queue、prefill 与 decode", "指标必须能回到原始事件和分母", "指标定义卡和手算记录"),
        ("guided-demo", "运行 TD-A04 cycle 并打开到达守恒报告", "核对 planned 与 accounted 以及 fixture-only 标签", "baseline 通过且容量结论没有外推硬件", "Goodput 与到达账本共同限制容量解释", "经字段核对的 TD-A04 报告"),
        ("failure-diagnosis", "运行 TD-A06 fault 展示重试放大与回退质量失败", "沿 attempts、Retry-After、cost 和 quality 字段定位", "fault 以 exit 1 变红且保留 expected/actual", "修复不能靠吞掉错误或放宽 Oracle", "韧性 fault 根因记录"),
        ("learner-practice", "提供新的 429 与工具超时组合但不提供答案", "设计有界重试、幂等状态查询和安全失败", "同一副作用至多一次且预算不被突破", "四类预算和 fallback Gate 必须同时成立", "新增故障矩阵与 repair 报告"),
        ("transfer-challenge", "将合成服务替换为目标组织的受控 AI 服务", "重新固定模型、硬件、流量、阈值、owner 和回滚", "方法保留但 fixture 数字和岗位假设不得复制", "迁移的是证据合同而不是教学阈值", "真实项目差距与适配清单"),
        ("artifact-handoff", "展示公开包、课程包、owners 与 closure", "独立复跑七页并列出所有 NOT_RUN", "学员能区分 fixture、live、practitioner 和 production", "职业自评只支持学习规划且不承诺就业", "复跑证据与 30/60/90 天计划"),
    ]
    stages = [{"stage_id": x[0], "instructor_action": x[1], "learner_action": x[2], "expected_observation": x[3], "debrief": x[4], "artifact_or_assessment": x[5]} for x in stage_specs]
    stages[7].update({"source_context": "离线合成 AI API、Serving 与职业自评 fixture", "target_context": "目标组织的受控 AI 服务", "invariant": "版本化输入、独立 Oracle、0/1/0、owner、hash 和成熟度边界", "must_change": ["目标模型、硬件、流量分布、阈值和发布 owner", "工具权限、数据等级、回滚策略和岗位责任"], "success_criterion": "健康路径 exit 0，声明 fault exit 1，repair 回到 exit 0，且容量和职业结论不越界"})
    dump(COURSE / "video" / "lesson-experience.json", {"lesson_id": "td-ai-serving-career-l01", "target_learner": "掌握普通 API 测试、需要进入 AI Serving 质量与职业迁移的测试开发工程师", "level": "L2-guided-workflow", "estimated_minutes": 45, "job_result": "能为 AI API 和 Serving 建立可执行证据链，并产出无就业承诺的能力自评", "artifact": "七页 Prompt/Manifest/Oracle/0-1-0 evidence、容量报告和职业作品计划", "stages": stages, "interaction_prompts": ["最终文本正确时，哪种过程证据仍可能阻断发布？", "为什么 Goodput 不能只用完成请求作分母？", "迁移到目标组织时哪些合同保留、哪些阈值和责任必须重取证？"], "recovery_path": "从 learner-materials 根目录重跑 cycle；若 required file、hash 或环境异常，保留 NOT_RUN/BLOCKED，不手改报告", "evidence_status": "fixture-tested", "limitations": "离线合成 fixture 已验证；真实 Provider、模型、GPU、生产流量、学习效果、从业者评审和就业结果均未验证"})


def archive() -> None:
    target = PUBLIC.parent / "ai-serving-career.zip"
    if target.exists(): target.unlink()
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(PUBLIC.rglob("*")):
            if path.is_file(): zf.write(path, path.relative_to(PUBLIC))


def main() -> None:
    build_public_and_research()
    receipts = run_cycles()
    build_closure()
    build_course(receipts)
    archive()
    print(json.dumps({"pages": list(TOPICS), "cycles": len(receipts), "public": str(PUBLIC), "course": str(COURSE)}, ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
