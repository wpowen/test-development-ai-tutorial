# 测试开发 × AI

- Career ID: `test-development-ai`
- Audience: 有测试基础的初中级测试开发；懂 Python/JSON/命令行更佳
- Source status: multi-platform desk research + local fixture test
- Last verified: 2026-08-10

## Role reality

测试开发的专业价值不是“多生成几条用例”，而是把模糊风险变成可重复的检查、证据和发布决策。AI 进入产品和研发流程后，测试对象从确定性软件扩大到概率性模型、检索链路、工具调用 Agent 与持续变化的提示词/模型版本；测试方法也必须从单次断言扩大到数据集、rubric、统计阈值、轨迹、红队和生产反馈。

## Four AI lanes

1. `use-ai-for-work`：用模型/Agent 辅助风险分析、自动化代码、失败归因和测试资产维护。
2. `test-ai-systems`：测试 LLM、RAG、Agent、多模态应用的正确性、忠实性、安全性与稳定性。
3. `agentize-work`：让受控 Agent 规划、生成、执行和修复测试，同时保留可审计轨迹和人工批准。
4. `build-ai-quality-system`：建设评测集、实验记录、CI 门禁、Tracing、线上监控和回归闭环。

## AI transformation thesis

差异化课程不以“会用某个 AI 工具”为目标，而以“能定义 AI 质量、运行评测、证明检测有效、把结果接入工程流程”为目标。每门课必须产出可运行或可审计的职业物料，并通过一次有意义的故障注入。

## Professional capability transition

完整课程采用八层路径，而不是直接从工具或 RAG 实验开始：

1. 传统测试能力基线；
2. 大模型与 AI 系统运行基础；
3. AI 应用于传统测试；
4. LLM、RAG 与多模态评测；
5. Agent、Worker 与 Workflow 测试；
6. AI Quality Engineering；
7. Benchmark 与分数工程；
8. AI QE Capstone。

学习者可以通过入场考核免修传统测试讲解，但不能跳过风险、Oracle、数据、Mutation、Trace 和 CI 的工件验收。AI 质量方向必须分别学习 LLM、RAG、Agent、Workflow 和 Benchmark，不能把它们压成一门“AI 测试工具课”。

## Boundaries

- 离线 snapshot 能证明评测逻辑和回归敏感性，不能证明真实模型质量。
- LLM-as-judge 是一个可版本化的评测器，不是客观真理；关键发布门禁需要确定性检查或人工抽审。
- 浏览器 Agent 的自愈不能替代断言正确性；修复 locator 后仍需证明测试能发现产品缺陷。
- 生产数据、Prompt、Trace 和用户对话需要权限、脱敏、留存与审计策略。
