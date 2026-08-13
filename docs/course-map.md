# 测试开发 × AI：Canonical 课程地图

更新时间：2026-08-11

本地图只描述内部课程目录和依赖，不声明公开课程已经完成。Canonical 目录包含 117 个主题：105 个既有专业命题，加 12 个主动审计发现的高风险缺口。46 个旧课程合同和 107 个站点 ID 均保留在迁移表中作为 alias，不再作为独立完成事实。

## 依赖主线

`职业责任 → AI 基础 → 测试生命周期 → Eval 数据/Oracle/统计 → AI 辅助测试 → LLM/RAG → Agent + 安全 → Serving/性能 → 质量平台/生产/Benchmark → Capstone`

任何阶段都必须通过工件退出考核；观看页面、静态渲染、共享 Fixture 或旧 alias 状态不能跳过前置能力。

## CAT-00：职业责任、入场检查与路线

| 顺序 | Canonical ID | 主题 | 前置 | Delivery | Evidence maturity |
| ---: | --- | --- | --- | --- | --- |
| 1 | TD-000 | AI 时代测试开发的责任边界 | — | outlined | fixture-tested |
| 2 | TD-001 | 测试对象为什么从代码扩展到 AI 系统 | TD-000 | outlined | fixture-tested |
| 3 | TD-002 | 传统测试能力入场检查 | TD-000 | outlined | fixture-tested |
| 4 | TD-003 | 三条岗位路线 | TD-001；TD-002 | outlined | fixture-tested |

## CAT-01：AI 系统基础

| 顺序 | Canonical ID | 主题 | 前置 | Delivery | Evidence maturity |
| ---: | --- | --- | --- | --- | --- |
| 5 | TD-201 | 从训练到推理 | TD-003 | outlined | fixture-tested |
| 6 | TD-202 | Token、Context 与 Attention | TD-201 | outlined | fixture-tested |
| 7 | TD-203 | 概率生成与采样 | TD-202 | outlined | fixture-tested |
| 8 | TD-204 | Prompt 与结构化输出 | TD-203 | planned | unmeasured |
| 9 | TD-205 | Embedding 与向量检索 | TD-204 | outlined | fixture-tested |
| 10 | TD-206 | RAG 最小架构 | TD-205 | outlined | fixture-tested |
| 11 | TD-207 | Tool Calling | TD-206 | outlined | fixture-tested |
| 12 | TD-208 | Agent、Worker 与 Workflow | TD-207 | outlined | fixture-tested |
| 13 | TD-209 | Memory、State 与 Trace | TD-208 | outlined | fixture-tested |
| 14 | TD-210 | AI 能力边界 | TD-209 | outlined | fixture-tested |
| 15 | TD-X602 | 训练、Fine-tuning 与模型更新质量 | TD-210 | outlined | fixture-tested |

## CAT-02：测试生命周期与专业基线

| 顺序 | Canonical ID | 主题 | 前置 | Delivery | Evidence maturity |
| ---: | --- | --- | --- | --- | --- |
| 16 | TD-101 | 需求可测性与验收条件 | TD-210 | outlined | fixture-tested |
| 17 | TD-102 | 风险驱动测试策略 | TD-101 | outlined | fixture-tested |
| 18 | TD-103 | 用例设计与 Oracle | TD-102 | outlined | fixture-tested |
| 19 | TD-104 | 测试数据与环境 | TD-103 | planned | unmeasured |
| 20 | TD-105 | 自动化分层 | TD-104 | outlined | fixture-tested |
| 21 | TD-106 | 执行、证据与缺陷诊断 | TD-105 | outlined | fixture-tested |
| 22 | TD-107 | 发布、Waiver 与回滚 | TD-106 | outlined | fixture-tested |
| 23 | TD-108 | 生产质量闭环 | TD-107 | outlined | fixture-tested |
| 24 | TD-X101 | 静态测试、架构、代码与依赖质量 | TD-108 | outlined | fixture-tested |
| 25 | TD-X102 | 数据库、数据管道与迁移质量 | TD-X101 | outlined | desk-researched |
| 26 | TD-X103 | Web 兼容、可访问性与本地化质量 | TD-X102 | outlined | desk-researched |
| 27 | TD-X104 | Android 质量工程 | TD-X103 | outlined | desk-researched |
| 28 | TD-X105 | iOS 质量工程 | TD-X104 | outlined | desk-researched |

## CAT-03：Evaluation、数据与统计基础

| 顺序 | Canonical ID | 主题 | 前置 | Delivery | Evidence maturity |
| ---: | --- | --- | --- | --- | --- |
| 29 | TD-1001 | 从业务风险到 Eval Task | TD-X105 | outlined | fixture-tested |
| 30 | TD-1002 | 数据采样与代表性 | TD-1001 | outlined | fixture-tested |
| 31 | TD-1003 | 标注与冲突处理 | TD-1002 | outlined | fixture-tested |
| 32 | TD-1004 | Dev、Regression 与 Holdout | TD-1003 | outlined | fixture-tested |
| 33 | TD-1005 | Scorer 与聚合 | TD-1004 | outlined | fixture-tested |
| 34 | TD-1006 | 不确定性与显著性 | TD-1005 | outlined | fixture-tested |
| 35 | TD-1007 | 污染与泄漏 | TD-1006 | outlined | fixture-tested |
| 36 | TD-1008 | Harness 与协议敏感性 | TD-1007 | outlined | fixture-tested |

## CAT-04：AI 辅助测试全生命周期

| 顺序 | Canonical ID | 主题 | 前置 | Delivery | Evidence maturity |
| ---: | --- | --- | --- | --- | --- |
| 37 | TD-301 | AI 解析 PRD | TD-1004 | outlined | fixture-tested |
| 38 | TD-302 | AI 审查架构与代码 Diff | TD-301 | outlined | fixture-tested |
| 39 | TD-303 | AI 生成测试场景 | TD-302 | outlined | fixture-tested |
| 40 | TD-304 | AI 生成边界、组合与 Fuzz 数据 | TD-303 | outlined | fixture-tested |
| 41 | TD-305 | AI 生成单元与组件测试 | TD-304 | outlined | fixture-tested |
| 42 | TD-306 | AI 生成 API/契约测试 | TD-305 | outlined | fixture-tested |
| 43 | TD-307 | AI 生成 UI/E2E 测试 | TD-306 | outlined | fixture-tested |
| 44 | TD-308 | AI 测试 Agent | TD-307 | outlined | fixture-tested |
| 45 | TD-309 | AI 分析失败与日志 | TD-308 | outlined | fixture-tested |
| 46 | TD-310 | AI 生成发布报告 | TD-309 | outlined | fixture-tested |

## CAT-05：LLM、RAG 与多模态质量

| 顺序 | Canonical ID | 主题 | 前置 | Delivery | Evidence maturity |
| ---: | --- | --- | --- | --- | --- |
| 47 | TD-401 | LLM 测试任务定义 | TD-1008 | outlined | fixture-tested |
| 48 | TD-402 | 确定性与语义 Oracle | TD-401 | outlined | fixture-tested |
| 49 | TD-403 | 事实性、相关性与完整性 | TD-402 | outlined | fixture-tested |
| 50 | TD-404 | 拒答与安全边界 | TD-403 | outlined | fixture-tested |
| 51 | TD-405 | Prompt/模型 A/B | TD-404 | outlined | fixture-tested |
| 52 | TD-406 | 多轮与长上下文 | TD-405 | planned | unmeasured |
| 53 | TD-407 | LLM-as-Judge 校准 | TD-406 | outlined | fixture-tested |
| 54 | TD-408 | 非确定性与统计结论 | TD-407 | outlined | fixture-tested |
| 55 | TD-501 | 知识库数据质量 | TD-206；TD-408 | outlined | fixture-tested |
| 56 | TD-502 | 检索召回 | TD-501 | outlined | fixture-tested |
| 57 | TD-503 | 重排与上下文选择 | TD-502 | outlined | fixture-tested |
| 58 | TD-504 | 回答忠实性与引用 | TD-503 | outlined | fixture-tested |
| 59 | TD-505 | 无答案与冲突知识 | TD-504 | outlined | fixture-tested |
| 60 | TD-506 | 多租户与权限过滤 | TD-505 | outlined | fixture-tested |
| 61 | TD-507 | RAG 性能与成本 | TD-506 | outlined | fixture-tested |
| 62 | TD-508 | RAG 回归与线上反馈 | TD-507 | outlined | fixture-tested |
| 63 | TD-X501 | 多模态 AI 评测 | TD-408 | outlined | fixture-tested |
| 64 | TD-X502 | 多语言、可访问性与包容性 AI 评测 | TD-X501 | outlined | fixture-tested |

## CAT-06：Agent、Workflow 与安全

| 顺序 | Canonical ID | 主题 | 前置 | Delivery | Evidence maturity |
| ---: | --- | --- | --- | --- | --- |
| 65 | TD-601 | Agent 测试分层 | TD-208；TD-408 | outlined | fixture-tested |
| 66 | TD-602 | 工具选择与参数 | TD-601 | outlined | fixture-tested |
| 67 | TD-901 | AI 威胁建模 | TD-602 | outlined | fixture-tested |
| 68 | TD-902 | Prompt Injection | TD-901 | outlined | fixture-tested |
| 69 | TD-903 | 数据泄露与隐私 | TD-901 | outlined | fixture-tested |
| 70 | TD-904 | Excessive Agency | TD-901 | outlined | fixture-tested |
| 71 | TD-905 | 多租户隔离 | TD-903；TD-904 | planned | unmeasured |
| 72 | TD-906 | 供应链与模型依赖 | TD-901 | planned | unmeasured |
| 73 | TD-907 | 安全评测与红队 | TD-902；TD-903；TD-904；TD-906 | outlined | fixture-tested |
| 74 | TD-908 | 混沌、降级与灾备 | TD-907 | outlined | fixture-tested |
| 75 | TD-603 | 权限与副作用 | TD-602；TD-901 | outlined | fixture-tested |
| 76 | TD-604 | 状态与并发隔离 | TD-603 | outlined | fixture-tested |
| 77 | TD-605 | 循环、重试与终止 | TD-604 | outlined | fixture-tested |
| 78 | TD-606 | Handoff 与多 Agent | TD-605 | outlined | fixture-tested |
| 79 | TD-607 | Human-in-the-loop | TD-606 | outlined | fixture-tested |
| 80 | TD-608 | Agent 安全 | TD-907 | planned | unmeasured |
| 81 | TD-609 | Browser/Computer-use Agent | TD-603；TD-605；TD-608 | outlined | fixture-tested |
| 82 | TD-610 | Agent 回归与 Benchmark | TD-609 | outlined | fixture-tested |
| 83 | TD-X601 | 公平性、伤害与人类监督有效性 | TD-907 | outlined | fixture-tested |
| 84 | TD-X603 | 长期 Memory、个性化与语义缓存质量 | TD-604；TD-903 | outlined | fixture-tested |
| 85 | TD-X604 | 模型路由、Provider Fallback 与工具协议漂移 | TD-602；TD-906；TD-908 | outlined | fixture-tested |

## CAT-07：Serving、性能与稳定性

| 顺序 | Canonical ID | 主题 | 前置 | Delivery | Evidence maturity |
| ---: | --- | --- | --- | --- | --- |
| 86 | TD-701 | AI API 协议特点 | TD-207；TD-408；TD-X604 | outlined | fixture-tested |
| 87 | TD-702 | TTFT、ITL/TPOT 与 E2E | TD-701 | outlined | fixture-tested |
| 88 | TD-703 | Token 与请求吞吐 | TD-702 | outlined | fixture-tested |
| 89 | TD-704 | Prefill、Decode、Batch 与 KV Cache | TD-703 | outlined | fixture-tested |
| 90 | TD-705 | 工作负载建模 | TD-704 | outlined | fixture-tested |
| 91 | TD-706 | LLM Serving 压测工具 | TD-705 | outlined | fixture-tested |
| 92 | TD-707 | 容量、Goodput 与成本 | TD-706 | outlined | fixture-tested |
| 93 | TD-708 | 限流、超时、重试和降级 | TD-707 | outlined | fixture-tested |
| 94 | TD-AP01 | 为什么 Agent 压测不是 API 压测 | TD-610；TD-708 | outlined | fixture-tested |
| 95 | TD-AP02 | Agent 指标体系 | TD-AP01 | outlined | fixture-tested |
| 96 | TD-AP03 | Agent 负载模型与数据集 | TD-AP02 | outlined | fixture-tested |
| 97 | TD-AP04 | Trace 与可观测数据结构 | TD-AP03 | outlined | fixture-tested |
| 98 | TD-AP05 | 压测系统架构与工具选型 | TD-AP04 | outlined | fixture-tested |
| 99 | TD-AP06 | Agent 压测 SOP | TD-AP05 | outlined | fixture-tested |
| 100 | TD-AP07 | 诊断队列、重试与成本放大 | TD-AP06 | outlined | fixture-tested |
| 101 | TD-AP08 | 线上 SLO、告警与稳定性 Runbook | TD-AP07 | outlined | fixture-tested |

## CAT-08：质量平台、Benchmark 与生产运营

| 顺序 | Canonical ID | 主题 | 前置 | Delivery | Evidence maturity |
| ---: | --- | --- | --- | --- | --- |
| 102 | TD-1101 | AI 版本与 Lineage | TD-508；TD-610；TD-708 | outlined | fixture-tested |
| 103 | TD-1102 | Eval 接入 CI/CD | TD-1101 | outlined | fixture-tested |
| 104 | TD-1103 | 质量—延迟—成本联合门禁 | TD-1102 | outlined | fixture-tested |
| 105 | TD-1104 | AI Trace 与生产反馈 | TD-1103 | outlined | fixture-tested |
| 106 | TD-1105 | 在线质量监控与漂移 | TD-1104 | outlined | fixture-tested |
| 107 | TD-1106 | 告警、Waiver 与回滚 | TD-1105 | outlined | fixture-tested |
| 108 | TD-1107 | 评测平台数据模型 | TD-1106 | outlined | fixture-tested |
| 109 | TD-1108 | 质量治理与审计 | TD-1107 | outlined | fixture-tested |
| 110 | TD-1009 | 公共 Benchmark 解读 | TD-1105；TD-1008 | outlined | fixture-tested |
| 111 | TD-1010 | 企业内部 Benchmark | TD-1009 | outlined | fixture-tested |
| 112 | TD-X805 | 在线实验、Canary 与人工抽样评审 | TD-1105；TD-1006 | outlined | fixture-tested |

## CAT-09：Capstone、作品集与职业迁移

| 顺序 | Canonical ID | 主题 | 前置 | Delivery | Evidence maturity |
| ---: | --- | --- | --- | --- | --- |
| 113 | TD-1201 | AI 辅助测试项目 | TD-310；TD-1106 | planned | unmeasured |
| 114 | TD-1202 | RAG 质量项目 | TD-508；TD-1106 | planned | unmeasured |
| 115 | TD-1203 | Agent 质量项目 | TD-610；TD-AP08；TD-1106 | planned | unmeasured |
| 116 | TD-1204 | AI 质量平台项目 | TD-1010；TD-X805 | outlined | fixture-tested |
| 117 | TD-1205 | 岗位能力与作品集 | TD-1201；TD-1202；TD-1203；TD-1204 | outlined | fixture-tested |

## 状态边界

- `planned`：有 canonical 学习合同，但没有独立正文。
- `outlined`：存在旧页面或别名材料，但 canonical topic 的九文件研究包和页面门禁尚未通过。
- `gap`：证据显示能力可能重要，但尚未完成研究裁决。
- `fixture-tested` 只描述指定 alias 的离线执行证据，不升级 canonical topic 的内容完成度。
- 当前 117 个 canonical topic 的 `content_gate` 全部保持 `blocked`；TD-P02 的 Fixture 证据单独保留，不外推到 TD-301 全命题或整课。
