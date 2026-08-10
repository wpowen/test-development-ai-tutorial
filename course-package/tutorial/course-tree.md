# 测试开发 × AI 课程树

## 学习路线

从传统测试生命周期开始，依次进入大模型基础、AI 辅助测试、AI 系统评测、Agent/Workflow、质量工程、Benchmark 和 Capstone。页面顺序由前置依赖决定。

## 模块

### 完整测试生命周期

从需求、策略、设计、执行到发布与生产反馈，先建立专业测试骨架

- TD-F01 · 先把传统测试开发这份工作拆开 · outlined
- TD-P01 · 需求文档解析：从自然语言变成可追踪的质量条件 · outlined
- TD-P02 · 风险策略、测试层级与用例设计 · outlined
- TD-P03 · 测试数据、环境、执行、结果收集与发布闭环 · outlined

### 传统测试专项

接口、集成、UI、数据、性能、稳定性、安全、可观测性和混沌工程

- TD-S01 · 接口、契约、集成与事件测试 · outlined
- TD-S02 · UI、兼容性、可访问性与数据质量 · outlined
- TD-S03 · 性能、负载、容量与长稳测试 · outlined
- TD-S04 · 可靠性、安全、可观测性、容灾与混沌 · outlined

### 大模型与 AI 系统基础

理解模型如何运行，以及 Token、Context、RAG、Tool 和 Agent 为什么会失败

- TD-F02 · 大模型从数据、训练到一次推理发生了什么 · outlined
- TD-F03 · Token、Attention、Context 和概率生成为什么影响测试 · outlined
- TD-F04 · 从 LLM 到 RAG、Agent 和 Workflow：测试对象怎样扩张 · outlined
- TD-T01 · 测试开发遇到 AI 后，测试对象发生了什么变化 · outlined
- TD-T02 · LLM、RAG、Agent 的最小结构 · outlined
- TD-T03 · 概率性输出为什么不能只用传统断言 · outlined
- TD-T04 · 从测试用例到评测样例、黄金集和风险切片 · outlined

### AI 帮你做传统测试

用 AI 提效，但必须证明生成结果有检测力

- TD-T05 · 从 PRD 和代码 Diff 提取风险 · outlined
- TD-T06 · AI 生成测试，但证明测试真的会失败 · outlined
- TD-T07 · 生成边界与 Fuzz 数据 · outlined
- TD-T08 · AI 做失败聚类，但必须保留证据链 · outlined

### AI 接口、性能与可靠性

测试流式协议、结构化输出、TTFT、TPOT、Goodput、容量、限流、重试和降级

- TD-A01 · AI 接口服务和普通接口到底哪里不同 · outlined
- TD-A02 · 流式、结构化输出、工具调用与异步任务怎么测 · outlined
- TD-A03 · AI 性能指标：TTFT、TPOT、ITL、Goodput 与成本 · outlined
- TD-A04 · AI 负载、容量与瓶颈实验 · outlined
- TD-A05 · 发现 AI 性能问题：从用户慢到 Queue、GPU 与 KV Cache · outlined
- TD-A06 · 限流、超时、重试、回退与降级 · outlined

### 测试 LLM 和 RAG

把概率性回答变成可重复、可审计的质量证据

- TD-T09 · 第一个 LLM 评测 · outlined
- TD-T10 · RAG 的检索质量 · outlined
- TD-T11 · 回答、引用、忠实性和拒答 · outlined
- TD-T12 · 让 RAG 的错误退款承诺在上线前变红 · outlined
- TD-T13 · Prompt、模型和知识库版本 A/B · outlined
- TD-T14 · LLM-as-judge 的校准和反例 · outlined

### 测试 Agent、Worker 与 Workflow

检查轨迹、状态、工具、权限、Handoff、副作用和自愈风险

- TD-T15 · 最终结果、单步动作和完整轨迹 · outlined
- TD-T16 · 工具选择、参数和权限 · outlined
- TD-T17 · Prompt injection、数据泄露和 Excessive Agency · outlined
- TD-T18 · Browser Agent 和 Playwright Test Agents · outlined
- TD-T19 · 自愈测试为什么会误修绿 · outlined
- TD-W01 · 先区分 Agent、Worker 和固定 Workflow · outlined
- TD-W02 · 测试状态、循环、重试、Handoff 和终止条件 · outlined
- TD-W03 · 单 Agent 与多 Agent 的公平对照 · outlined

### 建设 AI 质量系统

把评测接入 CI、生产反馈、版本与回滚体系

- TD-T20 · 把评测接入 CI · outlined
- TD-T21 · 评测集、Prompt、模型、知识库和工具版本 · outlined
- TD-T22 · Trace、生产失败和回归集闭环 · outlined
- TD-T23 · 质量、延迟和成本联合门禁 · outlined
- TD-T24 · 漂移、告警、Waiver 和回滚 · outlined

### Benchmark 与分数工程

弄清数据、协议、Scorer、聚合、污染和榜单分数如何产生

- TD-B01 · Benchmark 不是一张榜单：先拆评分流水线 · outlined
- TD-B02 · Benchmark 数据怎么来：采样、标注、Split 与 Holdout · outlined
- TD-B03 · Accuracy、Pass@k、Resolved Rate 和 Judge Score 怎么算 · outlined
- TD-B04 · Prompt、Harness、工具权限为什么会改变分数 · outlined
- TD-B05 · 不确定性、污染、隐藏测试和版本可比性 · outlined
- TD-B06 · 从 SWE-bench、AgentBench、HELM 到企业内部 Benchmark · outlined

### 专业专题与 Capstone

按岗位路线组合工件，交付端到端 AI Quality Engineering 系统

- TD-T25 · Capstone：完成一个 AI Quality Engineering 仓库 · outlined

### 职业演进

从测试执行转向质量信号、评测工程、平台工程与生产可靠性

- TD-C01 · 测试岗位不会只剩点点点：能力如何迁移 · outlined

### Agent 性能与稳定性工程

从工作负载、指标、Trace、容量压测到生产 SLO、告警与故障处置

- TD-AP01 · 为什么 Agent 压测不是把并发数调高 · desk-researched
- TD-AP02 · 建立 Agent 性能指标树：系统、模型、轨迹、成本 · desk-researched
- TD-AP03 · 设计工作负载：任务、上下文、工具与故障分布 · desk-researched
- TD-AP04 · 设计 Trace 与数据模型：让一次慢任务可下钻 · desk-researched
- TD-AP05 · 搭建压测架构：发压、夹具、观测、判定四层分离 · desk-researched
- TD-AP06 · 执行完整压测 SOP：基线、变坏、修复、容量 · fixture-tested
- TD-AP07 · 诊断压测失败：从症状反推瓶颈与反馈环 · desk-researched
- TD-AP08 · 把压测接入生产：SLO、告警、降级与 Runbook · desk-researched

## 页面状态

- 发布范围：`pilot-path`。
- 深度正文：8/60 页。
- `outlined` 表示知识位置已确定，但逐题研究和教材正文尚未通过门禁。
- `desk-researched` 表示正文和来源已整理，但没有运行目标系统。
- `fixture-tested` 表示对应离线夹具已经运行，不代表生产效果。
- 内容完成度与证据等级分开记录，不因正文完整而升级证据状态。
