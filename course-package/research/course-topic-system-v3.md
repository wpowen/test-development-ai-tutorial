# 测试开发 × AI：课程知识体系与命题树 v3

这份清单不是课程正文，也不是根据工具名称拼出的目录。它先回答测试开发在 AI 时代需要负责哪些对象、质量属性和决策，再把每个能力拆成可以独立研究、教学和验收的命题。

## 课程主线

学习路径由两条主线交叉组成：

- 测试专业主线：需求与风险 → 策略与设计 → 数据与环境 → 自动化与执行 → 专项测试 → 发布 → 生产监控 → 事故回流。
- AI 系统主线：模型推理 → LLM 应用 → RAG → Agent/Workflow → Serving → Evaluation → Observability → Governance。

每个正式页面必须回答一个职业问题，并交付一个可检查的工件。一个页面如果只是在解释名词、列举工具或给出 Prompt，就只能进入“提纲”，不能标记为课程正文。

## M00 入门与路线选择

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-000 | AI 时代测试开发的责任边界 | 哪些责任保留、哪些被辅助、哪些成为新工作？ | 职业能力迁移图 |
| TD-001 | 测试对象为什么从代码扩展到 AI 系统 | 模型、Prompt、数据、检索、工具、状态和 Judge 怎样共同决定结果？ | AI 系统被测对象图 |
| TD-002 | 传统测试能力入场检查 | 没有 AI 时，学习者是否会做风险、Oracle、证据和发布判断？ | 入场能力评估表 |
| TD-003 | 三条岗位路线 | AI 辅助测试、AI 系统测试、AI 质量平台分别需要什么深度？ | 个性化学习路线 |

## M01 传统测试专业骨架

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-101 | 需求可测性与验收条件 | 如何从需求中识别歧义、约束、不变量和不可测条件？ | 需求质量审计表 |
| TD-102 | 风险驱动测试策略 | 测什么、不测什么、为什么？ | 风险—测试层级矩阵 |
| TD-103 | 用例设计与 Oracle | 等价类、边界、状态、组合、属性和探索式测试如何形成判定？ | Oracle 目录 |
| TD-104 | 测试数据与环境 | 数据、账户、时间、依赖、隔离和清理怎样影响可信度？ | 测试数据与环境契约 |
| TD-105 | 自动化分层 | 单元、组件、契约、API、UI 和 E2E 怎样分工？ | 自动化金字塔与责任图 |
| TD-106 | 执行、证据与缺陷诊断 | 一次失败怎样从日志回到组件和根因？ | 失败证据包 |
| TD-107 | 发布、Waiver 与回滚 | 哪些信号阻断发布，谁能接受例外？ | 发布门禁与回滚清单 |
| TD-108 | 生产质量闭环 | 线上事故如何转成测试和监控资产？ | Incident-to-Regression 流程 |

## M02 大模型与 AI 应用基础

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-201 | 从训练到推理 | 训练数据、对齐和推理阶段分别怎样影响测试？ | 模型生命周期图 |
| TD-202 | Token、Context 与 Attention | 为什么输入长度、位置和上下文组成会改变结果与成本？ | Token/Context 实验记录 |
| TD-203 | 概率生成与采样 | 温度、top-p、seed 和多次采样怎样改变可重复性？ | 采样敏感性报告 |
| TD-204 | Prompt 与结构化输出 | 格式约束能保证什么，不能保证什么？ | Prompt/Schema 契约 |
| TD-205 | Embedding 与向量检索 | 相似度、切分和索引怎样影响召回？ | 最小检索实验 |
| TD-206 | RAG 最小架构 | 数据进入、检索、重排、生成和引用分别在哪里失败？ | RAG 数据流图 |
| TD-207 | Tool Calling | 工具选择、参数、执行结果和副作用怎样被观测？ | Tool Contract |
| TD-208 | Agent、Worker 与 Workflow | 动态决策、固定路径和并行 Worker 有什么本质差异？ | 控制流与状态图 |
| TD-209 | Memory、State 与 Trace | 会话状态、持久状态、记忆和执行轨迹怎样区分？ | 状态与追踪模型 |
| TD-210 | AI 能力边界 | 幻觉、过时知识、Prompt 敏感、越权、延迟和成本如何进入风险模型？ | AI 风险登记册 |

## M03 AI 辅助传统测试全流程

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-301 | AI 解析 PRD | 怎样让 AI 提取规则而不发明规则？ | 需求追踪矩阵 |
| TD-302 | AI 审查架构与代码 Diff | 怎样从变更定位影响面、风险和回归范围？ | Diff 风险报告 |
| TD-303 | AI 生成测试场景 | 生成的场景怎样绑定风险、Oracle 和来源？ | 可追踪测试集 |
| TD-304 | AI 生成边界、组合与 Fuzz 数据 | 怎样证明生成数据覆盖了风险空间？ | 数据生成器与覆盖报告 |
| TD-305 | AI 生成单元与组件测试 | 怎样用 Mutation 证明不是“看起来像测试”？ | 红绿 Mutation 证据 |
| TD-306 | AI 生成 API/契约测试 | 怎样约束 Schema、状态、不变量和副作用？ | API 测试仓库 |
| TD-307 | AI 生成 UI/E2E 测试 | 怎样控制选择器、等待、数据和跨页面状态？ | 可维护 E2E 测试 |
| TD-308 | AI 测试 Agent | Planner、Generator、Healer 分别如何验收？ | Test Agent 评测集 |
| TD-309 | AI 分析失败与日志 | 怎样聚类重复失败但保留证据和未知？ | 失败聚类与根因候选报告 |
| TD-310 | AI 生成发布报告 | 怎样从测试证据形成可审计结论而非自动批准？ | 发布决策草案 |

## M04 LLM 质量工程

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-401 | LLM 测试任务定义 | 一条 Eval 的输入、参考、Rubric、切片和失败成本是什么？ | Eval Contract |
| TD-402 | 确定性与语义 Oracle | 规则、相似度、模型 Judge 和人工怎样组合？ | Composite Oracle |
| TD-403 | 事实性、相关性与完整性 | 不同质量维度怎样避免互相替代？ | 多维评分卡 |
| TD-404 | 拒答与安全边界 | 应答、拒答、升级人工分别怎样判定？ | 拒答矩阵 |
| TD-405 | Prompt/模型 A/B | 如何控制变量并解释差异？ | A/B 实验与版本清单 |
| TD-406 | 多轮与长上下文 | 记忆、指令冲突、上下文衰减怎样测试？ | 多轮状态数据集 |
| TD-407 | LLM-as-Judge 校准 | Judge 与人工不一致时怎么办？ | Judge 校准报告 |
| TD-408 | 非确定性与统计结论 | 需要重复多少次、怎样报告区间和切片？ | 统计评测报告 |

## M05 RAG 质量工程

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-501 | 知识库数据质量 | 来源、时效、重复、权限和切分怎样验收？ | Knowledge Dataset Card |
| TD-502 | 检索召回 | Recall@k、MRR、NDCG 和业务覆盖怎样选择？ | Retrieval Eval |
| TD-503 | 重排与上下文选择 | 召回正确但上下文排序错误如何发现？ | Reranker 对照实验 |
| TD-504 | 回答忠实性与引用 | 回答是否由检索证据支持？ | Answer/Citation Eval |
| TD-505 | 无答案与冲突知识 | 没有证据、证据冲突、旧政策时系统应怎样行为？ | Abstention Dataset |
| TD-506 | 多租户与权限过滤 | 相关文档和有权访问的文档为什么不是一回事？ | 权限隔离测试集 |
| TD-507 | RAG 性能与成本 | 检索、重排、生成分别贡献多少延迟和成本？ | RAG Trace 性能报告 |
| TD-508 | RAG 回归与线上反馈 | 线上失败怎样进入版本化回归集？ | RAG CI Gate |

## M06 Agent 与 Workflow 质量工程

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-601 | Agent 测试分层 | 最终结果、单步动作、轨迹和线程分别测什么？ | Agent 测试策略 |
| TD-602 | 工具选择与参数 | 选错工具、参数错误和 Schema 漂移怎样检测？ | Tool-call Dataset |
| TD-603 | 权限与副作用 | 可读、可写、审批和补偿边界怎样测试？ | 权限/副作用矩阵 |
| TD-604 | 状态与并发隔离 | 多会话、多租户和并发任务如何避免串状态？ | State Isolation Test |
| TD-605 | 循环、重试与终止 | 怎样检测死循环、重复调用和错误终止？ | Loop/Retry Gate |
| TD-606 | Handoff 与多 Agent | 委派、合并、冲突和责任边界怎样验收？ | Handoff Contract |
| TD-607 | Human-in-the-loop | 哪些节点必须人工批准，超时和拒绝如何处理？ | HITL 状态机 |
| TD-608 | Agent 安全 | Prompt injection、数据泄漏和 excessive agency 怎样进入轨迹测试？ | Agent Red-team Set |
| TD-609 | Browser/Computer-use Agent | UI 变化、等待、权限和不可逆操作怎样测试？ | Browser Agent Harness |
| TD-610 | Agent 回归与 Benchmark | 任务成功、轨迹、成本和风险怎样形成内部基准？ | Agent Benchmark |

## M07 AI API、Serving 与推理性能

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-701 | AI API 协议特点 | 流式、异步、结构化输出和工具事件怎样形成状态机？ | AI API Contract |
| TD-702 | TTFT、ITL/TPOT 与 E2E | 每个延迟指标从哪里开始、到哪里结束？ | Metric Card |
| TD-703 | Token 与请求吞吐 | 系统吞吐和单用户体验为什么可能相反？ | 吞吐—延迟曲线 |
| TD-704 | Prefill、Decode、Batch 与 KV Cache | Serving 内部阶段如何映射到外部症状？ | 瓶颈诊断图 |
| TD-705 | 工作负载建模 | Prompt/输出长度、缓存、流式、模型和到达模式怎样组合？ | Workload Manifest |
| TD-706 | LLM Serving 压测工具 | AIPerf、vLLM benchmark、k6/Locust 各自适合什么？ | 工具选择矩阵 |
| TD-707 | 容量、Goodput 与成本 | 在 SLO 内成功完成的有效吞吐怎样计算？ | 容量与成本报告 |
| TD-708 | 限流、超时、重试和降级 | 怎样避免重试风暴并验证 fallback？ | Overload Runbook |

## M08 Agent 性能与稳定性工程

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-AP01 | 为什么 Agent 压测不是 API 压测 | 一次业务任务为什么会放大为多次模型和工具调用？ | 四层性能模型 |
| TD-AP02 | Agent 指标体系 | 怎样联合任务成功、延迟、步骤、重试、成本和资源？ | Agent Metric Catalog |
| TD-AP03 | Agent 负载模型与数据集 | 任务类型、路径深度、工具时延、失败概率和并发怎样建模？ | Workload Dataset |
| TD-AP04 | Trace 与可观测数据结构 | 哪些 span、事件、版本和业务字段必须保留？ | Trace Schema |
| TD-AP05 | 压测系统架构与工具选型 | 负载发生器、Agent、依赖桩、Telemetry、分析和门禁怎样连接？ | 压测架构图 |
| TD-AP06 | Agent 压测 SOP | 基线、爬坡、容量、突发、长稳、故障和恢复怎样执行？ | 可执行测试计划 |
| TD-AP07 | 诊断队列、重试与成本放大 | 如何从症状反推模型、工具、状态、队列或策略问题？ | 瓶颈诊断报告 |
| TD-AP08 | 线上 SLO、告警与稳定性 Runbook | 怎样监控、告警、降级、回滚并把事故变成回归？ | Agent Reliability Runbook |

## M09 AI 安全、隐私与韧性

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-901 | AI 威胁建模 | 资产、信任边界、数据流和攻击者能力怎样建模？ | AI Threat Model |
| TD-902 | Prompt Injection | 直接和间接注入怎样穿过 RAG 与工具链？ | Injection Test Set |
| TD-903 | 数据泄露与隐私 | Prompt、Trace、缓存、训练和工具参数在哪里泄露？ | Data Boundary Review |
| TD-904 | Excessive Agency | 过大权限、错误工具和不可逆副作用怎样阻断？ | Authority Gate |
| TD-905 | 多租户隔离 | 数据、状态、Memory、索引和日志怎样隔离？ | Tenant Isolation Plan |
| TD-906 | 供应链与模型依赖 | 模型、包、Prompt、插件和 MCP 变更怎样进入风险？ | AI SBOM/Lineage |
| TD-907 | 安全评测与红队 | 攻击集、成功标准、重放和修复怎样组织？ | Red-team Harness |
| TD-908 | 混沌、降级与灾备 | Provider、向量库、工具或网络失败时系统怎样安全退化？ | Resilience Experiment |

## M10 Evaluation、数据、统计与 Benchmark 工程

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-1001 | 从业务风险到 Eval Task | 评测单位和失败成本怎样定义？ | Eval Spec |
| TD-1002 | 数据采样与代表性 | 数据来自哪里、覆盖哪些用户和风险切片？ | Sampling Plan |
| TD-1003 | 标注与冲突处理 | 谁标、怎样仲裁、如何记录不确定？ | Annotation Guide |
| TD-1004 | Dev、Regression 与 Holdout | 怎样避免对测试集过拟合？ | Split Manifest |
| TD-1005 | Scorer 与聚合 | 分数如何从逐条结果产生？ | Scorer Card |
| TD-1006 | 不确定性与显著性 | 小样本和随机波动怎样限制结论？ | Confidence Report |
| TD-1007 | 污染与泄漏 | 公开题、训练泄漏和调试访问怎样审计？ | Contamination Audit |
| TD-1008 | Harness 与协议敏感性 | Prompt、工具、预算、超时和重试怎样改变分数？ | Sensitivity Experiment |
| TD-1009 | 公共 Benchmark 解读 | SWE-bench、Agent benchmark、HELM 等能说明什么？ | Benchmark Review |
| TD-1010 | 企业内部 Benchmark | 怎样把真实任务、事故、成本和权限做成可维护基准？ | Internal Benchmark Repo |

## M11 AI 质量平台、CI 与生产运营

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-1101 | AI 版本与 Lineage | 模型、Prompt、数据、知识库、工具和 Judge 怎样统一版本化？ | Run Manifest |
| TD-1102 | Eval 接入 CI/CD | 快速门禁、发布评测和人工审批怎样分层？ | CI Workflow |
| TD-1103 | 质量—延迟—成本联合门禁 | 多目标怎样设硬底线与选择 Pareto 候选？ | Release Scorecard |
| TD-1104 | AI Trace 与生产反馈 | 生产 Trace 如何安全转成回归资产？ | Trace-to-Regression Pipeline |
| TD-1105 | 在线质量监控与漂移 | 没有实时答案标签时如何监控代理信号和抽样评审？ | Drift Dashboard |
| TD-1106 | 告警、Waiver 与回滚 | 告警何时调查、阻断、降级或回滚？ | Incident Runbook |
| TD-1107 | 评测平台数据模型 | Dataset、Run、Example、Score、Trace、Version 怎样关联？ | Evaluation Schema |
| TD-1108 | 质量治理与审计 | 权限、审批、证据保留和审计如何落地？ | AI Quality Policy |

## M12 专业项目与职业迁移

| ID | 命题 | 核心问题 | 学习者工件 |
| --- | --- | --- | --- |
| TD-1201 | AI 辅助测试项目 | 能否把一次真实变更变成可追踪的 AI 辅助测试闭环？ | 项目仓库 |
| TD-1202 | RAG 质量项目 | 能否让一个错误回答在 CI 中稳定变红并修复？ | RAG Eval Repo |
| TD-1203 | Agent 质量项目 | 能否联合验证结果、轨迹、权限、性能和成本？ | Agent Quality Repo |
| TD-1204 | AI 质量平台项目 | 能否连接数据、评测、Trace、发布和事故回流？ | Quality Platform MVP |
| TD-1205 | 岗位能力与作品集 | 如何用证据而不是“会用 AI”证明转型能力？ | 作品集与岗位映射 |

## 当前课程缺口判定

原 52 页只覆盖了上述体系中的一部分，并且多数页面只是摘要层。它们可以保留为早期主题地图，但不能继续作为“完整正文”对外承诺。

优先重写顺序：

1. 先完成 M08 的八页深度样章，验证调研、教材写作、可运行 Lab 和页面呈现。
2. 复用同一套门禁重写 M07、M06、M11，这三部分构成 AI 系统测试与生产质量主干。
3. 再重写 M02、M04、M05、M10，补齐知识与评测基础。
4. 最后重写 AI 辅助传统测试、专业基线、安全和 Capstone。

在一个模块没有逐页研究包、可检查工件和专业审查前，只能标记为 `outlined`，不能标记为 `desk-researched` 或“完整课程”。
