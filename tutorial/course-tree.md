# 测试开发 × AI 课程树

## 学习路线

从传统测试生命周期开始，依次进入大模型基础、AI 辅助测试、AI 系统评测、Agent/Workflow、质量工程、Benchmark 和 Capstone。页面顺序由前置依赖决定。

## 模块

### 完整测试生命周期

从需求、策略、设计、执行到发布与生产反馈，先建立专业测试骨架

- TD-F01 · 先重建测试开发这份工作，再判断 AI 应该改哪里 · fixture-tested
- TD-P01 · 先冻结测试依据：别让 AI 读一堆互相打架的文档 · fixture-tested
- TD-P02 · 把自然语言变成需求契约：让下游程序能直接消费 · fixture-tested
- TD-P03 · 解析技术文档：把组件、接口、状态与失败恢复变成可测试契约 · fixture-tested
- TD-P04 · 从需求契约到风险策略：决定测什么、在哪一层测 · fixture-tested
- TD-P05 · 生成测试之前先固定 Oracle：否则 AI 只会生成自洽答案 · fixture-tested
- TD-P06 · 把测试包接到自动化：接口、契约、集成和 UI 各自负责什么 · fixture-tested
- TD-P07 · 执行、收集、归因：一次绿色结果需要哪些证据 · fixture-tested
- TD-P08 · 变更回归与发布判断：把整条证据链串起来 · fixture-tested

### 传统测试专项

接口、集成、UI、数据、性能、稳定性、安全、可观测性和混沌工程

- TD-PS01 · API 业务契约：从 HTTP 结果到可验证副作用 · desk-researched
- TD-PS02 · OpenAPI Schema 与属性测试：让坏请求和破坏性变更变红 · desk-researched
- TD-PS03 · 契约、事件与鉴权：测试跨服务边界的真实兼容性 · desk-researched
- TD-PS04 · Web UI 关键旅程：隔离、定位器、网络控制与跨浏览器 · desk-researched
- TD-PS05 · Web UI 兼容性、无障碍与视觉回归 · desk-researched
- TD-PS06 · Android 自动化：生命周期、同步、权限与设备矩阵 · desk-researched
- TD-PS07 · iOS 自动化：可访问性标识、权限、签名与状态残留 · desk-researched
- TD-PS08 · 数据与迁移：Schema 演进、回填、CDC 与回滚对账 · desk-researched
- TD-PS09 · 性能与容量：到达率、尾延迟、Goodput 与单位成功成本 · desk-researched
- TD-PS10 · 稳定性：超时、重试预算、熔断、限流与降级 · desk-researched
- TD-PS11 · 线上可观测性：把 AI 质量、Trace、成本和 SLO 接成一条链 · desk-researched
- TD-PS12 · 安全测试：身份、授权、输入、秘密与跨租户副作用 · desk-researched
- TD-X101 · 静态、架构、代码与依赖供应链门禁 · fixture-tested

### 大模型与 AI 系统基础

理解模型如何运行，以及 Token、Context、RAG、Tool 和 Agent 为什么会失败

- TD-FP01 · Prompt 小白第一课：从一句指令到可验证 Prompt Package · fixture-tested
- TD-F02 · 模型生命周期：一次错误究竟来自哪里 · fixture-tested
- TD-F03 · Token、Context 与非确定性：为什么一次 PASS 不够 · fixture-tested
- TD-F04 · 从 LLM 到 RAG、Agent 与 Workflow：被测边界如何扩张 · fixture-tested
- TD-T01 · Eval Contract：先写发布问题，再选指标 · fixture-tested
- TD-T02 · Dataset、Slice 与 Holdout：让评测不会越调越假 · fixture-tested
- TD-T03 · Composite Oracle：规则、语义 Judge 与人工如何组合 · fixture-tested
- TD-T04 · 重复运行与统计：从一次结果到可解释分布 · fixture-tested

### AI 帮你做传统测试

用 AI 提效，但必须证明生成结果有检测力

- TD-T05 · 从冻结 Basis 与代码 Diff 提取可追溯风险 · fixture-tested
- TD-T06 · AI 生成测试候选，用 Mutation 证明检测力 · fixture-tested
- TD-T07 · 按失败模型选择 Boundary、Combination、Property 与 Fuzz · fixture-tested
- TD-T08 · AI 聚类失败，但原始证据和 UNKNOWN 不能丢 · fixture-tested

### AI 接口、性能与可靠性

测试流式协议、结构化输出、TTFT、TPOT、Goodput、容量、限流、重试和降级

- TD-A01 · 普通 API 与 AI API：从确定性响应到版本化生成服务 · fixture-tested
- TD-A02 · AI API 协议：Streaming、Structured、Tool 与 Async · fixture-tested
- TD-A03 · AI Serving 指标：TTFT、TPOT、ITL、Goodput 与单位成功成本 · fixture-tested
- TD-A04 · AI Serving 负载与容量：从 Token 分布到 SLO 拐点 · fixture-tested
- TD-A05 · AI Serving 瓶颈：Queue、GPU、KV Cache 与阶段诊断 · fixture-tested
- TD-A06 · AI Serving 韧性：限流、Timeout、Retry、Fallback 与 Degradation · fixture-tested

### 测试 LLM 和 RAG

把概率性回答变成可重复、可审计的质量证据

- TD-T09 · RAG 语料治理：来源、版本、分块与权限 · fixture-tested
- TD-T10 · 检索评测：Recall、Ranking 与查询切片 · fixture-tested
- TD-T11 · Faithfulness 与 Citation：回答真的被证据支持吗 · fixture-tested
- TD-T12 · 无答案、权限与端到端 RAG Gate · fixture-tested
- TD-X501 · 多模态关系与独立 Oracle 评测 · fixture-tested
- TD-X502 · 多语言、可访问与包容性 AI 任务验收 · fixture-tested
- TD-T13 · Prompt、模型和知识库版本 A/B · fixture-tested
- TD-T14 · LLM-as-judge 的校准和反例 · fixture-tested

### 测试 Agent、Worker 与 Workflow

检查轨迹、状态、工具、权限、Handoff、副作用和自愈风险

- TD-T15 · 最终结果、单步动作和完整轨迹 · fixture-tested
- TD-T16 · 工具选择、参数和权限 · fixture-tested
- TD-T17 · Prompt injection、数据泄露和 Excessive Agency · fixture-tested
- TD-T18 · Browser Agent 和 Playwright Test Agents · fixture-tested
- TD-T19 · 自愈测试为什么会误修绿 · fixture-tested
- TD-W01 · 先区分 Agent、Worker 和固定 Workflow · fixture-tested
- TD-W02 · 测试状态、循环、重试、Handoff 和终止条件 · fixture-tested
- TD-W03 · 单 Agent 与多 Agent 的公平对照 · fixture-tested
- TD-X603 · 长期 Memory、个性化与语义缓存治理 · fixture-tested
- TD-X604 · 模型路由、Fallback 与工具协议漂移测试 · fixture-tested

### 建设 AI 质量系统

把评测接入 CI、生产反馈、版本与回滚体系

- TD-X602 · 训练、Fine-tuning 与模型更新的版本化验收 · fixture-tested
- TD-X601 · 公平、伤害与 HITL 有效性门禁 · fixture-tested
- TD-T20 · CI 分层门禁：让坏 AI 版本真的停下来 · fixture-tested
- TD-T21 · Lineage：每个分数都能回到当时的版本 · fixture-tested
- TD-T22 · Trace-to-Regression：把生产失败变成不会复发的用例 · fixture-tested
- TD-T23 · 质量、延迟与成本：联合 Gate 而不是一个综合分 · fixture-tested
- TD-T24 · 漂移、Waiver 与回滚：质量系统的恢复闭环 · fixture-tested
- TD-X805 · 在线实验、Canary 与人工抽样发布门禁 · fixture-tested

### Benchmark 与分数工程

弄清数据、协议、Scorer、聚合、污染和榜单分数如何产生

- TD-B01 · Benchmark 流水线：总分背后有七个可变组件 · fixture-tested
- TD-B02 · Dataset、Split 与 Sealed Holdout：防止越调越假 · fixture-tested
- TD-B03 · Metrics 与区间：Accuracy、Pass@k、Resolved Rate 不能混讲 · fixture-tested
- TD-B04 · Harness 敏感性：固定模型，一次只改一个协议变量 · fixture-tested
- TD-B05 · 污染与不确定性：隐藏测试也不是万能证明 · fixture-tested
- TD-B06 · 公共到企业：把 Benchmark 方法迁移到业务风险 · fixture-tested

### 专业专题与 Capstone

按岗位路线组合工件，交付端到端 AI Quality Engineering 系统

- TD-QP01 · Jira 需求事件：从 Basis Gate 到人工批准 · fixture-tested
- TD-QP02 · GitLab MR 与 Pipeline：把 JUnit 证据绑定到当前 SHA · fixture-tested
- TD-QP03 · Kubernetes 临时测试环境：隔离、回收与审计 · fixture-tested
- TD-QP04 · 跨系统事件总线：幂等、重放、脱敏通知与审计闭环 · fixture-tested
- TD-T25 · Capstone：交付 AI Quality Fixture Release Candidate · fixture-tested

### 职业演进

从测试执行转向质量信号、评测工程、平台工程与生产可靠性

- TD-C01 · 职业能力迁移：岗位路径、自评证据与作品集边界 · fixture-tested
- TD-C02 · 责任证据梯：从跟做测试到质量治理 · fixture-tested
- TD-C03 · 能力自评与 30/60/90 天证据计划 · fixture-tested
- TD-C04 · 组织职级适配器：P5–P9 不能由 Skill 猜 · fixture-tested
- TD-F05 · AI 任务族与指标选择：先问任务，再选 F1 或 QPS · fixture-tested
- TD-T26 · AI 生成测试用例提效：用 Mutation 证明不是批量幻觉 · fixture-tested
- TD-R01 · 资源与学习路线：会更新的索引，不是盲目书单 · fixture-tested

### Agent 性能与稳定性工程

从工作负载、指标、Trace、容量压测到生产 SLO、告警与故障处置

- TD-AP01 · 先建工作负载模型：Task 不是 HTTP Request · fixture-tested
- TD-AP02 · 建立指标树：TTFT、TPOT、Queue、Retry、Step · fixture-tested
- TD-AP03 · 锁定 Trace 语义：从 Task Root 到 Tool Attempt · fixture-tested
- TD-AP04 · 对照开放与封闭负载：识别 Coordinated Omission · fixture-tested
- TD-AP05 · 寻找容量边界并归因瓶颈：只报告 Synthetic Goodput · fixture-tested
- TD-AP06 · 约束超时与重试：压力下安全降级 · fixture-tested
- TD-AP07 · 运行长稳测试：识别资源泄漏与漂移 · fixture-tested
- TD-AP08 · 把结果接入 SLO、告警与事故证据 · fixture-tested

### Agent 测试架构

从 D0 评估可信到 D7 业务治理，用四证据环验证轨迹、协作、安全、可靠性与成本

- TD-AG-00 · Agent 测试架构总览：先画边界，再选测试 · fixture-tested
- TD-AG-01 · D0 评估可信：先测试 Judge，再相信分数 · fixture-tested
- TD-AG-02 · D1 轨迹 span：从最终结果追到首个错误 · fixture-tested
- TD-AG-03 · D2 编排：交接、隔离、级联和熔断 · fixture-tested
- TD-AG-04 · D3 人机协同：中断、接管与确认疲劳 · fixture-tested
- TD-AG-05 · D4 可靠性分布：pass@k、pass^k 与长时程衰减 · fixture-tested
- TD-AG-06 · D5 持续安全：注入、MCP 投毒、委托、沙箱与爆炸半径 · fixture-tested
- TD-AG-07 · D6 经济性：任务、步骤、尾延迟与成本预算 · fixture-tested
- TD-AG-08 · D7 业务治理：规则、审计、四维版本与 ROI · fixture-tested
- TD-AG-09 · 四证据环与三段门禁：从 CI 走到持续评估 · fixture-tested
- TD-AG-10 · 高风险适配器：交易/金融 Agent 的时效、执行与能力沙箱 · fixture-tested

## 页面状态

- 发布范围：`pilot-path`。
- 同步页面：103 页。
- 深度正文状态：103/103 页。
- `desk-researched` 表示正文和来源已整理，但没有运行目标系统。
- `fixture-tested` 表示对应离线夹具已经运行，不代表生产效果。
- 内容完成度与证据等级分开记录，不因正文完整而升级证据状态。
