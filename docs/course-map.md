# 测试开发 × AI：专业能力迁移课程地图

本课程不是从热门工具开始，而是从测试职业原有能力出发，逐步进入大模型运行、AI 辅助测试、LLM/RAG/Agent/Workflow 评测、AI 质量工程和 Benchmark。

完整方法见 `learning-architecture.md`；机器可检查的依赖、阶段和专题见 `research/competency-transition-map.json`。

## 总路径

```text
传统测试基线
  → 大模型与 AI 系统基础
  → AI 应用于传统测试
  → LLM / RAG / 多模态评测
  → Agent / Worker / Workflow 测试
  → AI Quality Engineering
  → Benchmark 与分数工程
  → AI QE Capstone
```

学习者可以免修讲解，但不能免交阶段工件。没有证明测试能被真实缺陷变红，就不能直接进入 LLM Judge；没有可信 Scorer 和版本清单，就不能把分数接进 CI。

## Stage 0：传统测试能力基线

| ID | 课题 | 核心问题 | 学员工件 | 退出标准 |
| --- | --- | --- | --- | --- |
| TD-BASE-01 | 传统研发测试流程与 AI 变化点 | 需求、开发、测试、发布、生产反馈中，AI 改变了哪些对象和责任？ | 流程与变化地图 | 每个变化点有系统、风险和责任人 |
| TD-BASE-02 | 测试设计、Oracle 与 Mutation 入场考核 | 你能否把业务规则变成真的会失败的测试？ | 追踪矩阵、测试、Mutation 报告 | 产品缺陷使测试稳定 RED |
| TD-BASE-03 | 自动化、Trace、CI 与发布基线 | 测试如何可重放、可诊断并支持发布？ | 测试仓库、CI Gate、证据报告 | Commit→执行→报告→阻断闭环 |

## Stage 1：大模型与 AI 系统基础

| ID | 课题 | 测试行业为什么需要 | 学员工件 | 退出标准 |
| --- | --- | --- | --- | --- |
| TD-FOUND-01 | 大模型从数据、训练到推理和监控 | 分清训练知识、模型版本、推理配置和线上漂移 | 模型生命周期测试地图 | 每阶段有风险和可观察证据 |
| TD-FOUND-02 | Token、Attention、Context 与概率生成 | 解释长度、上下文、位置和解码参数为什么改变输出 | 推理变量实验表 | 固定版本并解释输出差异 |
| TD-FOUND-03 | Embedding、RAG、Tool call 与 Agent loop | 把“AI 答错了”拆成检索、生成、工具和状态问题 | AI 系统结构与 Trace 图 | 症状能映射到首查层 |
| TD-FOUND-04 | 大模型能力边界与 AI 测试对象 | 为幻觉、拒答、权限、隐私、成本选择 Oracle | 失败分类与 Oracle 决策表 | 高风险 Blocker 不被平均分抵消 |

## Stage 2：AI 应用于传统测试

| ID | 课题 | 学员工件 | 证伪方式 |
| --- | --- | --- | --- |
| TD-AI-01 | 用 AI 从 PRD/代码 Diff 建立风险模型 | 风险矩阵、追踪表 | 注入缺失状态规则 |
| TD-AI-02 | AI 生成自动化测试，但必须证明它会失败 | 可执行测试、Mutation 报告 | 产品 Mutation 必须 RED |
| TD-AI-03 | 用 AI 读 Trace/Log/Diff 做失败归因 | 引用式缺陷报告 | 删除证据后置信度下降 |
| TD-AI-04 | AI 生成属性、边界和 Fuzz 数据 | 数据生成器、最小反例 | 命中并缩小边界缺陷 |

## Stage 3：测试 LLM、RAG 与多模态系统

| ID | 课题 | 学员工件 | 证伪方式 |
| --- | --- | --- | --- |
| TD-EVAL-01 | Eval Dataset、Dataset card、切片与 Holdout | Eval 数据、数据卡、Holdout 清单 | 重复、污染和切片缺口检测 |
| TD-EVAL-02 | Scorer、Rubric、LLM Judge 与人工校准 | Rubric、校准报告、分歧集 | Judge 反例与人工分歧 |
| TD-AI-05 | LLM 评测基础：黄金集、Rubric 与阈值 | Eval cases、门禁阈值 | 低质量 Snapshot 被阻断 |
| td-ai-006-rag-eval-ci | RAG 分层评测：检索、回答、引用与忠实性 | 可运行 RAG Eval Repo | 幻觉、丢引用、Injection PASS→FAIL→PASS |
| TD-AI-07 | Prompt/模型/知识库 A/B 与版本回归 | 实验账本、对比报告 | 关键 Slice 触发回归 |
| TD-AI-09 | LLM/RAG/Agent 安全红队 | Attack set、红队报告 | 注入、泄露和越权阻断 |
| TD-AI-10 | 多模态文档与截图评测 | 多模态数据集、切片报告 | OCR 和视觉幻觉 Mutation |

## Stage 4：测试 Agent、Worker 与 Workflow

| ID | 课题 | 学员工件 | 证伪方式 |
| --- | --- | --- | --- |
| TD-AI-08 | 最终结果、单步动作与完整轨迹 | Trajectory cases、Agent report | 错工具、错参数和伪成功 |
| TD-AI-11 | Playwright Planner/Generator/Healer | Seed、Specs、Tests、Trace | Healer 后产品 Mutation 仍 RED |
| TD-AI-12 | Browser/API Agent 沙箱、工具与权限 | Policy、Agent Trace | 越权副作用被阻断 |
| TD-AI-13 | 自愈测试反作弊门禁 | Healer policy、Semantic diff | 删除断言和放宽等待被拒绝 |
| TD-AI-14 | Worker Workflow 与多 Agent 流水线 | Handoff contract、Verifier report | 独立 Verifier 拒绝伪成功，并与单 Agent 同预算对照 |

这里明确区分：Workflow 是代码预先规定的路径；Agent 会动态决定步骤和工具；Worker 是承担一个有边界任务的执行单元。测试时既要看业务终态，也要看中间状态、工具、权限、重试、预算、超时、Handoff 和副作用。

## Stage 5：AI Quality Engineering

| ID | 课题 | 学员工件 | 证伪方式 |
| --- | --- | --- | --- |
| TD-AI-15 | 评测集、Prompt、模型与工具版本管理 | Experiment ledger、Version manifest | 历史实验可重放 |
| TD-AI-16 | 把 AI 评测接进 CI/CD | Quality Gate、Waiver 模板 | 已知回归非零退出并阻断 |
| TD-AI-17 | Trace、线上反馈与回归集闭环 | Feedback-to-eval 流水线 | 脱敏失败带 Lineage 入库 |
| TD-AI-18 | 质量、成本、延迟与稳定性联合评估 | Pareto 报告 | 单一高分不能掩盖成本/延迟退化 |
| TD-AI-19 | 漂移、告警、Waiver、回滚与事故演练 | Runbook、事故时间线 | 漂移触发告警和回滚 |

## Stage 6：Benchmark 与分数工程

| ID | 课题 | 必须讲清楚 | 学员工件 |
| --- | --- | --- | --- |
| TD-BENCH-01 | Benchmark 数据如何构造 | 任务、来源、采样、标注、Split、Holdout、污染 | Benchmark spec、Dataset card |
| TD-BENCH-02 | 分数如何产生 | Harness、Prompt、权限、重复运行、Scorer、Accuracy/Pass@k/Resolved rate/Judge score | Harness config、Metric card、复现报告 |
| TD-BENCH-03 | 分数是否可信 | 样本数、方差、置信区间、污染、隐藏测试、版本可比性 | 不确定性报告、污染审计 |
| TD-BENCH-04 | 从公开榜单到内部 Benchmark | 公开任务与真实业务分布的差异、线上失败回流、维护政策 | Internal benchmark repo |

Benchmark 课程不背模型排名。学习者必须复现一个小型分数，改变 Prompt、Scorer 或数据变量，然后解释为什么分数变化。SWE-bench、AgentBench、HELM 和 lm-evaluation-harness 作为“分数条件”的案例，而不是永不过时的排行榜。

## Stage 7：AI QE Capstone

| ID | 课题 | 交付 |
| --- | --- | --- |
| TD-AI-20 | AI QE 平台 Capstone | Commit→Eval→CI→Trace→Regression→Waiver/回滚的端到端仓库 |

Capstone 必须组合注入检索、生成、工具、权限、成本或漂移事故，并证明系统会阻断、诊断、修复和保留证据边界。

## 专题路线

- 自动化测试开发：Stage 0 → 1 → 2 → Agent/Healer 专题 → CI。
- AI 应用质量工程师：Stage 0–7 全部完成，重点是 LLM、RAG、Agent、Workflow 和 Benchmark。
- 测试平台工程师：Stage 0–3 基础 + Stage 5–7 深入，重点是版本、可观测性、门禁、漂移和治理。
- 安全测试：Stage 0–3 基础 + Agent 沙箱 + 红队 + 事故治理。

## 当前交付状态

- 已有可运行样例：`td-ai-006-rag-eval-ci`，离线 Fixture 已完成 PASS→FAIL→PASS。
- 已有 52/52 页完整可读路径：传统测试、大模型基础、AI 辅助测试、AI 系统评测、Agent/Workflow、质量系统、Benchmark、Capstone 与职业演进。
- 所有页面均已达到正文交付门禁；除 RAG 离线 Fixture 外，多数专题仍需真实系统实验和从业者评审。
- 尚未证明：真实模型效果、真实企业数据适配、目标学员学习增益和生产有效性。
