# 测试开发 × AI 课程树

## 学习路线

从传统测试生命周期开始，依次进入大模型基础、AI 辅助测试、AI 系统评测、Agent/Workflow、质量工程、Benchmark 和 Capstone。页面顺序由前置依赖决定。

## 模块

### 完整测试生命周期

从需求、策略、设计、执行到发布与生产反馈，先建立专业测试骨架

- TD-F01 · 测试开发职业责任与 AI 授权边界 · fixture-tested
- TD-P01 · 测试依据冻结：来源版本、权威与冲突门禁 · fixture-tested
- TD-P02 · 需求契约建模与结构化 Schema · fixture-tested
- TD-P03 · 技术文档解析与可测试技术契约 · fixture-tested
- TD-P04 · 风险分析与测试层级策略 · fixture-tested
- TD-P05 · 独立 Oracle 设计与测试用例生成 · fixture-tested
- TD-P06 · Test Package 与自动化执行分层 · fixture-tested
- TD-P07 · 测试执行、证据收集与失败归因 · fixture-tested
- TD-P08 · 影响分析、回归选择与发布证据链 · fixture-tested

### 传统测试专项

接口、集成、UI、数据、性能、稳定性、安全、可观测性和混沌工程

- TD-PS01 · API 业务契约与副作用验证 · desk-researched
- TD-PS02 · OpenAPI Schema 与属性测试 · desk-researched
- TD-PS03 · 跨服务契约、事件与鉴权测试 · desk-researched
- TD-PS04 · Web UI 关键旅程：隔离、定位器、网络控制与跨浏览器 · desk-researched
- TD-PS05 · Web UI 兼容性、无障碍与视觉回归 · desk-researched
- TD-PS06 · Android 自动化：生命周期、同步、权限与设备矩阵 · desk-researched
- TD-PS07 · iOS 自动化：可访问性标识、权限、签名与状态残留 · desk-researched
- TD-PS08 · 数据与迁移：Schema 演进、回填、CDC 与回滚对账 · desk-researched
- TD-PS09 · 性能与容量：到达率、尾延迟、Goodput 与单位成功成本 · desk-researched
- TD-PS10 · 稳定性：超时、重试预算、熔断、限流与降级 · desk-researched
- TD-PS11 · 线上可观测性：质量、Trace、成本与 SLO 链路 · desk-researched
- TD-PS12 · 安全测试：身份、授权、输入、秘密与跨租户副作用 · desk-researched
- TD-X101 · 静态、架构、代码与依赖供应链门禁 · fixture-tested

### 大模型与 AI 系统基础

理解模型如何运行，以及 Token、Context、RAG、Tool 和 Agent 为什么会失败

- TD-FP01 · Prompt Package 入门：从指令到可验证评测单元 · fixture-tested
- TD-F02 · 大模型生命周期与失败归因 · fixture-tested
- TD-F03 · Token、Context 与采样非确定性 · fixture-tested
- TD-F04 · LLM、RAG、Agent 与 Workflow 的测试边界 · fixture-tested
- TD-T01 · Eval Contract 与指标选择 · fixture-tested
- TD-T02 · Eval Dataset、Slice 与 Holdout · fixture-tested
- TD-T03 · Composite Oracle：规则、Judge 与人工评审组合 · fixture-tested
- TD-T04 · 重复运行、统计与结果分布 · fixture-tested

### AI 帮你做传统测试

用 AI 提效，但必须证明生成结果有检测力

- TD-T05 · 冻结 Basis 与代码 Diff 的可追溯风险提取 · fixture-tested
- TD-T06 · AI 测试候选生成与 Mutation 检测力验证 · fixture-tested
- TD-T07 · 测试方法选择：Boundary、Combination、Property 与 Fuzz · fixture-tested
- TD-T08 · 失败聚类与原始证据保留 · fixture-tested

### AI 接口、性能与可靠性

测试流式协议、结构化输出、TTFT、TPOT、Goodput、容量、限流、重试和降级

- TD-A01 · 普通 API 与 AI API：确定性响应与版本化生成服务 · fixture-tested
- TD-A02 · AI API 协议：Streaming、Structured、Tool 与 Async · fixture-tested
- TD-A03 · AI Serving 指标：TTFT、TPOT、ITL、Goodput 与单位成功成本 · fixture-tested
- TD-A04 · AI Serving 负载与容量：从 Token 分布到 SLO 拐点 · fixture-tested
- TD-A05 · AI Serving 瓶颈：Queue、GPU、KV Cache 与阶段诊断 · fixture-tested
- TD-A06 · AI Serving 韧性：限流、Timeout、Retry、Fallback 与 Degradation · fixture-tested

### 测试 LLM 和 RAG

把概率性回答变成可重复、可审计的质量证据

- TD-T09 · RAG 语料治理：来源、版本、分块与权限 · fixture-tested
- TD-T10 · 检索评测：Recall、Ranking 与查询切片 · fixture-tested
- TD-T11 · Faithfulness 与 Citation 评估 · fixture-tested
- TD-T12 · RAG 端到端门禁：无答案与权限 · fixture-tested
- TD-X501 · 多模态关系与独立 Oracle 评测 · fixture-tested
- TD-X502 · 多语言、可访问与包容性 AI 任务验收 · fixture-tested
- TD-T13 · 版本化 A/B：Prompt、模型与知识库 · fixture-tested
- TD-T14 · LLM-as-Judge 校准与反例集 · fixture-tested

### 测试 Agent、Worker 与 Workflow

检查轨迹、状态、工具、权限、Handoff、副作用和自愈风险

- TD-T15 · Agent 结果、步骤与轨迹评估 · fixture-tested
- TD-T16 · Agent 工具调用：选择、参数与权限 · fixture-tested
- TD-T17 · Agent 安全：Prompt Injection、数据泄露与 Excessive Agency · fixture-tested
- TD-T18 · Browser Agent 与 Playwright Test Agents · fixture-tested
- TD-T19 · 自愈测试的误修绿风险 · fixture-tested
- TD-W01 · Agent、Worker 与固定 Workflow 的边界 · fixture-tested
- TD-W02 · Workflow 状态、循环、重试、Handoff 与终止条件 · fixture-tested
- TD-W03 · 单 Agent 与多 Agent 对照评估 · fixture-tested
- TD-X603 · 长期 Memory、个性化与语义缓存治理 · fixture-tested
- TD-X604 · 模型路由、Fallback 与工具协议漂移测试 · fixture-tested

### 建设 AI 质量系统

把评测接入 CI、生产反馈、版本与回滚体系

- TD-X602 · 训练、Fine-tuning 与模型更新的版本化验收 · fixture-tested
- TD-X601 · 公平、伤害与 HITL 有效性门禁 · fixture-tested
- TD-T20 · CI 分层质量门禁 · fixture-tested
- TD-T21 · 模型与评测 Lineage 追踪 · fixture-tested
- TD-T22 · Trace-to-Regression：生产失败到回归用例 · fixture-tested
- TD-T23 · 质量、延迟与成本联合门禁 · fixture-tested
- TD-T24 · 漂移、Waiver 与回滚闭环 · fixture-tested
- TD-X805 · 在线实验、Canary 与人工抽样发布门禁 · fixture-tested

### Benchmark 与分数工程

弄清数据、协议、Scorer、聚合、污染和榜单分数如何产生

- TD-B01 · Benchmark 流水线：七个可变组件 · fixture-tested
- TD-B02 · Benchmark 数据集：Split 与 Sealed Holdout · fixture-tested
- TD-B03 · Benchmark 指标：Accuracy、Pass@k、Resolved Rate 与置信区间 · fixture-tested
- TD-B04 · Harness 敏感性与控制变量实验 · fixture-tested
- TD-B05 · Benchmark 污染与不确定性 · fixture-tested
- TD-B06 · Benchmark 方法的企业化迁移 · fixture-tested

### 专业专题与 Capstone

按岗位路线组合工件，交付端到端 AI Quality Engineering 系统

- TD-QP01 · Jira 需求事件、Basis Gate 与人工批准 · fixture-tested
- TD-QP02 · GitLab MR、Pipeline 与证据 SHA 绑定 · fixture-tested
- TD-QP03 · Kubernetes 临时测试环境：隔离、回收与审计 · fixture-tested
- TD-QP04 · 跨系统事件总线：幂等、重放、脱敏通知与审计闭环 · fixture-tested
- TD-T25 · Capstone：AI Quality Fixture Release Candidate · fixture-tested

### 职业演进

从测试执行转向质量信号、评测工程、平台工程与生产可靠性

- TD-C01 · 职业能力迁移：岗位路径、自评证据与作品集边界 · fixture-tested
- TD-C02 · 测试开发责任证据阶梯 · fixture-tested
- TD-C03 · 能力自评与 30/60/90 天证据计划 · fixture-tested
- TD-C04 · 组织职级适配：P5–P9 能力映射 · fixture-tested
- TD-F05 · AI 任务族与指标选择 · fixture-tested
- TD-T26 · AI 测试用例生成提效与 Mutation 验证 · fixture-tested
- TD-R01 · 资源与学习路线索引 · fixture-tested

### Agent 性能与稳定性工程

从工作负载、指标、Trace、容量压测到生产 SLO、告警与故障处置

- TD-AP01 · Agent 工作负载模型：Task、切片与 Oracle · fixture-tested
- TD-AP02 · Agent 性能指标树：TTFT、TPOT、Queue、Retry、Step · fixture-tested
- TD-AP03 · Agent Trace 语义：Task Root 到 Tool Attempt · fixture-tested
- TD-AP04 · 开放与封闭负载对照与 Coordinated Omission · fixture-tested
- TD-AP05 · 容量边界、瓶颈归因与 Synthetic Goodput · fixture-tested
- TD-AP06 · 超时、重试预算与安全降级 · fixture-tested
- TD-AP07 · 长稳测试：资源泄漏与漂移 · fixture-tested
- TD-AP08 · Agent SLO、告警与事故证据闭环 · fixture-tested

### Agent 测试架构

从 D0 评估可信到 D7 业务治理，用四证据环验证轨迹、协作、安全、可靠性与成本

- TD-AG-00 · Agent 测试架构总览：D0–D7 与四证据环 · fixture-tested
- TD-AG-01 · D0 评估可信度：Judge 校准 · fixture-tested
- TD-AG-02 · D1 轨迹 Span 归因 · fixture-tested
- TD-AG-03 · D2 编排：交接、隔离、级联与熔断 · fixture-tested
- TD-AG-04 · D3 人机协同：中断、接管与确认疲劳 · fixture-tested
- TD-AG-05 · D4 可靠性分布：pass@k、pass^k 与长时程衰减 · fixture-tested
- TD-AG-06 · D5 持续安全：注入、MCP 投毒、委托、沙箱与爆炸半径 · fixture-tested
- TD-AG-07 · D6 经济性：任务、步骤、尾延迟与成本预算 · fixture-tested
- TD-AG-08 · D7 业务治理：规则、审计、四维版本与 ROI · fixture-tested
- TD-AG-09 · 四证据环与三段门禁 · fixture-tested
- TD-AG-10 · 高风险适配器：交易/金融 Agent 的时效、执行与能力沙箱 · fixture-tested

## 页面状态

- 发布范围：`pilot-path`。
- 同步页面：103 页。
- 深度正文状态：103/103 页。
- `desk-researched` 表示正文和来源已整理，但没有运行目标系统。
- `fixture-tested` 表示对应离线夹具已经运行，不代表生产效果。
- 内容完成度与证据等级分开记录，不因正文完整而升级证据状态。
