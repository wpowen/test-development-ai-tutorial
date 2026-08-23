# 测试开发 × AI 课程树

## 文档导航

可按任务、主题或文档类型进入：Learn、Do、Look up、Understand、Report / Decide。页面的前置关系只表达局部依赖，不构成规定的使用顺序。

## 模块

### 完整测试生命周期

从需求、策略、设计、执行到发布与生产反馈，先建立专业测试骨架

- TD-F01 · 测试开发如何与 AI 协作，以及哪些发布责任必须由人承担 · fixture-tested
- TD-P01 · PRD 和技术方案如何整理成可追溯的测试依据 · fixture-tested
- TD-P02 · 需求如何拆成可验证的角色、状态和业务规则 · fixture-tested
- TD-P03 · 技术方案如何变成可测试契约：接口、事件和状态要写清什么 · fixture-tested
- TD-P04 · 测试该做到哪一层：从业务风险反推测试策略 · fixture-tested
- TD-P05 · 为测试用例设计独立、可复核的预期结果（Oracle） · fixture-tested
- TD-P06 · 测试包如何生成自动化骨架，并保留需求追溯关系 · fixture-tested
- TD-P07 · 测试失败后，如何保留证据并定位责任层 · fixture-tested
- TD-P08 · 用一条完整证据链做回归选择和发布判断 · fixture-tested

### 传统测试专项

接口、集成、UI、数据、性能、稳定性、安全、可观测性和混沌工程

- TD-PS01 · 如何验证 API 的业务规则和真实副作用 · desk-researched
- TD-PS02 · 不止验证 Schema：用属性测试发现 API 测试盲区 · desk-researched
- TD-PS03 · 跨服务事件为什么会出错：契约、鉴权与补偿测试 · desk-researched
- TD-PS04 · 写出稳定的 Web UI 测试：从定位器到网络控制 · desk-researched
- TD-PS05 · Web 页面兼容性怎么测：无障碍、响应式和视觉回归 · desk-researched
- TD-PS06 · 排查 Android 自动化不稳定：生命周期、权限与设备差异 · desk-researched
- TD-PS07 · 排查 iOS 自动化失败：标识、权限、签名与状态清理 · desk-researched
- TD-PS08 · 数据库迁移怎么测：从 Schema 演进到回滚对账 · desk-researched
- TD-PS09 · AI 系统性能怎么测：尾延迟、Goodput 与单位成功成本 · desk-researched
- TD-PS10 · 超时和过载时，服务如何安全退化 · desk-researched
- TD-PS11 · 如何用 Trace、质量和成本看懂线上 AI 系统 · desk-researched
- TD-PS12 · 为 AI 助手建立可执行的安全测试门禁 · desk-researched
- TD-X101 · 代码合并前，如何用架构和供应链证据做门禁 · fixture-tested

### 大模型与 AI 系统基础

理解模型如何运行，以及 Token、Context、RAG、Tool 和 Agent 为什么会失败

- TD-FP01 · 把一段 Prompt 变成可运行、可评测的版本化包 · fixture-tested
- TD-F02 · 大模型回答是怎么产生的，以及测试开发应在哪些环节排查失效 · fixture-tested
- TD-F03 · 为什么同一个 Prompt 会得到不同结果 · fixture-tested
- TD-F04 · LLM、RAG、Agent、Worker 和 Workflow 的测试边界 · fixture-tested
- TD-T01 · Eval Contract 要写什么，才能让评测结果可审计 · fixture-tested
- TD-T02 · 评测数据集怎么切：风险 Slice、去重与封存 Holdout · fixture-tested
- TD-T03 · 规则、模型评审器和人工复核如何组成可靠判定标准（Oracle） · fixture-tested
- TD-T04 · 评测为什么要重复运行：如何用分布、差异和阻断规则判断结果 · fixture-tested

### AI 帮你做传统测试

用 AI 提效，但必须证明生成结果有检测力

- TD-T05 · 从需求和代码 Diff 提取可追溯的测试风险 · fixture-tested
- TD-T06 · 用变异测试（Mutation）验证 AI 生成测试的检测力 · fixture-tested
- TD-T07 · 边界值、组合、属性还是 Fuzz：测试方法怎么选 · fixture-tested
- TD-T08 · 相似失败不等于同一根因：保留原始证据再聚类 · fixture-tested

### AI 接口、性能与可靠性

测试流式协议、结构化输出、TTFT、TPOT、Goodput、容量、限流、重试和降级

- TD-A01 · 普通 API 与 AI API 的测试重点有什么不同 · fixture-tested
- TD-A02 · AI API 怎么测：流式输出、结构化结果与工具调用 · fixture-tested
- TD-A03 · AI 服务性能怎么看：延迟、吞吐和成本指标怎么选 · fixture-tested
- TD-A04 · AI 服务能扛多少负载：从 Token 分布找到容量拐点 · fixture-tested
- TD-A05 · 定位 AI 服务延迟瓶颈：排队、GPU、KV Cache 与下游依赖 · fixture-tested
- TD-A06 · AI 服务出错后如何限流、重试和安全降级 · fixture-tested

### 测试 LLM 和 RAG

把概率性回答变成可重复、可审计的质量证据

- TD-T09 · RAG 检索前先管好语料：版本、分块、权限和删除 · fixture-tested
- TD-T10 · RAG 为什么没检索到：用 Recall、排序和查询切片定位 · fixture-tested
- TD-T11 · 回答有引用就可信吗？检查引用对齐与回答忠实度 · fixture-tested
- TD-T12 · RAG 发布前要检查什么：拒答、权限隔离和检索质量门禁 · fixture-tested
- TD-X501 · 多模态回答是否可信：验证跨模态关系与独立 Oracle · fixture-tested
- TD-X502 · 多语言 AI 能否完成真实任务：从语言区域到可访问性 · fixture-tested
- TD-T13 · 如何公平比较 Prompt、模型和知识库版本 · fixture-tested
- TD-T14 · 模型 Judge 什么时候可信：校准、偏差与反例集 · fixture-tested

### 测试 Agent、Worker 与 Workflow

检查轨迹、状态、工具、权限、Handoff、副作用和自愈风险

- TD-T15 · Agent 评测不能只看最终答案：结果、步骤与轨迹 · fixture-tested
- TD-T16 · Agent 调错工具怎么办：验证选择、参数、权限和副作用 · fixture-tested
- TD-T17 · 如何测试 Agent 的注入、泄露和过度代理风险 · fixture-tested
- TD-T18 · 用 Playwright Test Agents 生成测试后，怎样独立验收 · fixture-tested
- TD-T19 · 自愈测试如何掩盖失败：识别错误修复并设置审批边界 · fixture-tested
- TD-W01 · Agent、Worker 和固定 Workflow 的边界在哪里 · fixture-tested
- TD-W02 · 长流程如何避免丢状态、重复执行和无限循环 · fixture-tested
- TD-W03 · 多 Agent 真的更好吗？用对照实验判断 · fixture-tested
- TD-X603 · 长期 Memory 会记错什么：个性化、隔离与删除治理 · fixture-tested
- TD-X604 · 模型或工具切换后，哪些契约必须重新验证 · fixture-tested

### 建设 AI 质量系统

把评测接入 CI、生产反馈、版本与回滚体系

- TD-X602 · 模型更新怎么验收：锁定数据、训练配置和回滚目标 · fixture-tested
- TD-X601 · 公平与人工复核不是口号：怎样做成可审计门禁 · fixture-tested
- TD-T20 · AI 质量检查如何分层接入 CI，并阻断危险变更 · fixture-tested
- TD-T21 · 评测运行要记录哪些版本：数据、Prompt、模型、知识库、工具和 Scorer · fixture-tested
- TD-T22 · 把生产 Trace 变成可重复的回归用例 · fixture-tested
- TD-T23 · 质量、延迟和成本冲突时，怎样选择发布版本 · fixture-tested
- TD-T24 · AI 系统发生漂移后，如何管理 Waiver 并整包回滚 · fixture-tested
- TD-X805 · 离线评测如何走到 Canary，并安全渐进发布 · fixture-tested

### Benchmark 与分数工程

弄清数据、协议、Scorer、聚合、污染和榜单分数如何产生

- TD-B01 · Benchmark 分数到底由哪些因素决定 · fixture-tested
- TD-B02 · 为企业 Benchmark 设计数据集和封存 Holdout · fixture-tested
- TD-B03 · Benchmark 分数怎么算：Accuracy、Pass@k 与置信区间 · fixture-tested
- TD-B04 · 分数变化来自模型还是 Harness？用控制变量拆解 · fixture-tested
- TD-B05 · Benchmark 分数为什么会失真：污染、样本量和版本差异 · fixture-tested
- TD-B06 · 把公开 Benchmark 方法迁移到企业真实任务 · fixture-tested

### 专业专题与 Capstone

按岗位路线组合工件，交付端到端 AI Quality Engineering 系统

- TD-QP01 · 从 Jira 需求事件生成可审批的测试依据 · fixture-tested
- TD-QP02 · 把 GitLab 测试证据绑定到同一个 commit SHA · fixture-tested
- TD-QP03 · 为每个 MR 建立可回收、可审计的 Kubernetes 测试环境 · fixture-tested
- TD-QP04 · 用事件总线串起 Jira、GitLab 和 Kubernetes 证据链 · fixture-tested
- TD-T25 · 如何交付可审计的 AI 质量候选发布版本 · fixture-tested

### 职业演进

从测试执行转向质量信号、评测工程、平台工程与生产可靠性

- TD-C01 · 传统测试能力如何映射到 AI Quality 岗位并形成证据 · fixture-tested
- TD-C02 · 职业成长不看年限：用责任和证据判断能力层级 · fixture-tested
- TD-C03 · 把能力自评变成 30/60/90 天证据计划 · fixture-tested
- TD-C04 · 如何把公共能力模型映射到组织职级 · fixture-tested
- TD-F05 · 面对不同 AI 任务，指标应该怎么选 · fixture-tested
- TD-T26 · AI 生成的测试是否真的提效：用 Mutation 和对照实验验证 · fixture-tested
- TD-R01 · AI 测试资源怎么选：用途、版本和替代路径索引 · fixture-tested

### Agent 性能与稳定性工程

从工作负载、指标、Trace、容量压测到生产 SLO、告警与故障处置

- TD-AP01 · Agent 性能测试前，先定义什么是工作负载 · fixture-tested
- TD-AP02 · 拆解 Agent 等待时间：排队、首 Token、工具调用与重试指标 · fixture-tested
- TD-AP03 · Agent Trace 怎么设计，才能定位每一步耗时和失败 · fixture-tested
- TD-AP04 · 为什么闭环压测会掩盖过载：开放与封闭负载对照 · fixture-tested
- TD-AP05 · Agent 容量边界在哪里：逐级加压并归因瓶颈 · fixture-tested
- TD-AP06 · 给 Agent 设定统一的超时、重试预算和安全降级 · fixture-tested
- TD-AP07 · 长稳测试如何区分缓存热身、漂移和资源泄漏 · fixture-tested
- TD-AP08 · Agent 上线后如何用 SLO 告警和事故复盘闭合运行证据 · fixture-tested

### Agent 测试架构

从 D0 评估可信到 D7 业务治理，用四证据环验证轨迹、协作、安全、可靠性与成本

- TD-AG-00 · Agent 测试架构怎么搭：D0–D7 与四个证据环 · fixture-tested
- TD-AG-01 · Judge 评估器如何校准：人工金标、偏差探针和回退链 · fixture-tested
- TD-AG-02 · Agent 第一步错在哪里：用 Span 和轨迹定位 · fixture-tested
- TD-AG-03 · 多 Agent 交接如何避免信息衰减和级联失败 · fixture-tested
- TD-AG-04 · 人能否随时接管 Agent：如何测试中断、确认和控制权 · fixture-tested
- TD-AG-05 · Agent 可靠性不能只看一次成功：用 pass@k 与 pass^k 比较重复运行 · fixture-tested
- TD-AG-06 · 持续验证 Agent 安全：注入、MCP 投毒与能力沙箱 · fixture-tested
- TD-AG-07 · Agent 值不值得运行：任务成功、延迟和成本预算 · fixture-tested
- TD-AG-08 · Agent 业务规则、版本和审计责任如何关联 · fixture-tested
- TD-AG-09 · 从离线 CI 到线上评估：搭建四证据环门禁 · fixture-tested
- TD-AG-10 · 交易 Agent 如何安全上线：时效、执行隔离和分钟级回滚 · fixture-tested

## 页面状态

- 发布范围：`validated-subset`。
- 同步页面：103 页。
- 深度正文状态：103/103 页。
- `desk-researched` 表示正文和来源已整理，但没有运行目标系统。
- `fixture-tested` 表示对应离线夹具已经运行，不代表生产效果。
- 内容完成度与证据等级分开记录，不因正文完整而升级证据状态。
