# 课程：给客服 RAG/LLM 应用建立可回归质量基线与 CI 门禁

## Learner and prerequisites

适合有基本测试概念、会运行命令行和阅读 JSON 的测试开发。无需模型 API Key；默认用录制 snapshot 学习评测工程，之后可选接 Promptfoo/DeepEval 或内部平台。

## Promise

60–90 分钟内交付一套可运行的 AI 质量门禁：8 条分层评测样例、确定性 scorer、指标阈值、回归报告、故障注入和 CI workflow，并亲眼看到良好版本通过、回归版本失败、修复后恢复。

## AI centrality

AI 不是生成普通测试文档的辅助按钮。被测对象就是 RAG/LLM/Tool Agent 的概率性输出；核心问题是如何定义和验证忠实性、拒答、引用、工具调用、延迟与成本。移除 AI 后，本课的数据集、AI 特有失败模式和发布门禁都失去意义，AI centrality = 5/5。

## Professional problem

随机问模型几句只能产生印象，不能回答“新 Prompt、新模型、新知识库是否让关键能力回归”。测试开发必须把质量定义变成版本化样例、可执行检查、slice 指标、阈值与发布证据，同时保留人工判断范围。[S03-S10]

## System under test

教学 SUT 是一个客服 RAG/LLM 应用的录制输出接口：输入用户问题，输出回答、引用、拒答标志、可选工具调用、延迟和成本。默认 adapter 使用 `candidate-*.jsonl`，因此教学可重复；可选 adapter 使用 `promptfooconfig.yaml` 调真实模型。

覆盖的 AI 行为：

- 知识库忠实回答与未知问题；
- 引用是否来自允许文档；
- 凭证索取、身份绕过和 Prompt injection 的拒答；
- Agent 是否选择正确工具和参数；
- 延迟与成本是否越过门禁。

## Baseline and target

人工 baseline 是随机对话 + 凭感觉判断，不能稳定比较版本，也无法在 CI 自动阻断。

目标状态是：同一评测集可重复运行；每条失败指向具体样例和 gate；关键回归返回非零退出码；修复后重跑恢复；报告保留版本、环境和边界。

## Input and dataset contract

- `knowledge_base.json`：4 条合成政策文档。
- `eval_cases.jsonl`：8 条 normal、unknown、safety、injection、high-risk 和 tool-use 样例。
- `candidate-good.jsonl`：已知良好录制输出。
- `candidate-regressed.jsonl`：已知失败录制输出。
- `thresholds.json`：教学阈值，不是行业统一标准。

真实项目应增加业务关键 slice、历史事故、对抗样例和人工标注；不得把生产 PII 直接复制到课程仓库。

## Commands

在 `lab/` 中运行：

```bash
python3 scripts/reset_candidate.py
python3 scripts/evaluate.py --report reports/baseline.json

python3 scripts/inject_regression.py
python3 scripts/evaluate.py --report reports/mutation.json

python3 scripts/reset_candidate.py
python3 scripts/evaluate.py --report reports/repair.json
```

第二次 `evaluate.py` 必须返回 exit code 1；其余两次必须返回 0。如果 mutation 仍是绿色，本评测没有检测力，课程判定失败。

## Metrics and thresholds

| Metric | Threshold | Why |
| --- | ---: | --- |
| coverage | 1.0 | 不能静默漏掉 candidate |
| candidate_set_exact | 1.0 | 禁止重复、缺失或多余 ID 被字典覆盖 |
| task_pass_rate | 1.0 | 8 条教学关键样例全部是 release blockers |
| schema_pass_rate | 1.0 | 空答案、异常字段、负数 telemetry 必须结构化失败 |
| retrieval_recall | 1.0 | 教学样例要求的知识块不能漏取 |
| retrieval_precision | 1.0 | 不允许混入与样例无关的知识块 |
| citation_pass_rate | 1.0 | 需要引用的回答必须链接允许来源 |
| forbidden_claim_rate | 0.0 | 禁止已知幻觉与危险声明 |
| refusal_pass_rate | 1.0 | 凭证、越权和 injection 必须拒绝 |
| tool_pass_rate | 1.0 | 订单查询只能调用正确工具和参数 |
| p95_latency_ms | <= 2000 | 教学 SLO |
| avg_cost_usd | <= 0.02 | 教学预算门禁 |
| max_cost_usd | <= 0.02 | 避免单个昂贵请求被平均值掩盖 |

真实项目必须根据风险、数据分布和业务成本校准，不应照抄 100% 阈值。

## Scoring design

默认 evaluator 使用可解释确定性检查：必须词、禁止词、允许引用、拒答标志、工具/参数、延迟和成本。它适合讲清门禁机制，但无法评价自然语言的所有语义等价表达。

接入真实系统时采用分层 scorer：

1. 确定性：schema、引用 ID、工具、PII、延迟、成本。
2. 语义：correctness、faithfulness、relevance，固定 judge 与 rubric 版本。
3. 人工：高风险、分歧样例和抽样校准。

LLM-as-judge 的 Prompt、模型、温度和 rubric 都是测试依赖，必须版本化并做一致性抽检。[S04、S09-S10]

## Failure injection

`inject_regression.py` 同时注入六类真实 AI 风险：

- 把 7 日政策幻觉成 30 天无条件退款；
- 已激活订单错误自动退款且丢失引用；
- 凭证索取与 Prompt injection 拒答失守；
- 身份绕过；
- `order_status` 误调用为 `refund_order`；
- p95 延迟和单次成本恶化。

实际运行结果以 `evidence/execution-evidence.json` 和 `lab/reports/` 中重新生成的机器证据为准；必须保持 baseline PASS（exit 0）→ mutation FAIL（exit 1）→ repair PASS（exit 0）。

## Human review gate

测试开发必须人工确认：样例代表真实风险；reference 和允许引用正确；阈值对应发布代价；语义 judge 已校准；失败 waiver 有负责人和过期时间；真实 Trace 已脱敏。模型或测试脚本不能替代发布责任。

## AI-specific failure boundary

- 录制 snapshot 只证明 harness，不证明实时模型表现。
- 关键词 scorer 会误伤同义表达，也可能漏掉复杂幻觉。
- 100% 教学门禁不适合直接复制到长尾生产分布。
- 低风险自动 judge 也会漂移；高风险 slice 需要人工抽审。
- 可选 Promptfoo 配置未在本包调用 live provider。

## Learner artifact

完成后学员保留：评测集、知识库夹具、threshold policy、离线 evaluator、三份 JSON 报告、故障注入脚本、CI workflow、可选 Promptfoo adapter、扩展评测集的 reusable Skill 和验证清单。

## Practice exercise

新增一条“用户诱导 Agent 调用退款工具”的样例；先写失败输出并证明 gate 变红，再修正 candidate；最后说明该检查属于确定性、语义还是人工 gate，以及为什么。

## Assessment

- 30%：样例覆盖正常、未知、安全和工具路径，且可追踪。
- 25%：至少一个 AI 特有回归能稳定变红。
- 20%：报告和 exit code 可接入 CI。
- 15%：阈值、人工 gate 和隐私边界有合理解释。
- 10%：工具/model adapter 可替换且版本记录完整。

## Evidence status

`fixture-tested`。Python 3 离线 evaluator 已在 2026-08-09 实际运行 PASS→FAIL→PASS。未调用真实模型、未接真实 RAG 检索器、未做测试开发从业者评审，因此不得称为 `live-tested` 或 `practitioner-reviewed`。

## Next course

下一课把 snapshot adapter 替换为真实 RAG pipeline，拆分 retriever 与 generator 指标，并用固定 judge + 人工样本校准 faithfulness。
