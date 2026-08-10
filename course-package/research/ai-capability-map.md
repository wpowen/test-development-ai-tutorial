# 测试开发 × AI capability map

## `use-ai-for-work`

| Professional task | AI role | Learner proof | AI-specific failure | Course |
| --- | --- | --- | --- | --- |
| 从 PRD/代码 diff 建风险模型 | assistant | 风险项能追溯到输入，且人工删改有记录 | 臆造规则、忽略隐式状态 | TD-AI-01 |
| 生成并审计自动化测试 | assistant | 代码实际执行且能抓住 mutation | 脆弱 locator、错误 oracle、只测 happy path | TD-AI-02 |
| 从 trace/log/diff 做失败归因 | assistant | 结论链接证据，错误归因可被反例推翻 | 把相关性当因果 | TD-AI-03 |
| 生成边界、属性和 fuzz 数据 | assistant | 生成器命中预埋边界缺陷 | 无效数据、泄露生产数据 | TD-AI-04 |

## `test-ai-systems`

| System under test | AI role | Learner proof | Failure modes | Course |
| --- | --- | --- | --- | --- |
| LLM/RAG 应用 | system-under-test + judge | 评测集、分层指标、红绿回归 | 幻觉、引用缺失、检索污染 | TD-AI-05/06 |
| Prompt/模型版本 | system-under-test | A/B 差异与阈值门禁 | 回归、评测器漂移 | TD-AI-07 |
| Tool-using Agent | system-under-test | 最终结果、单步、轨迹三层评分 | 错工具、错参数、越权、循环 | TD-AI-08 |
| AI 安全边界 | red-team target | 攻击语料与阻断报告 | injection、泄露、过度代理权 | TD-AI-09 |
| 多模态模型 | system-under-test | 图像/文档输入的结构化评测 | OCR 错误、视觉幻觉 | TD-AI-10 |

## `agentize-work`

| Workflow | AI role | Learner proof | Guardrail | Course |
| --- | --- | --- | --- | --- |
| Playwright planner/generator/healer | agent | seed/spec/test/trace 与 mutation | 人审 spec、限制自愈范围 | TD-AI-11 |
| Browser/API Agent 执行探索 | agent | 完整轨迹、截图、网络证据 | 沙箱、白名单、只读凭证 | TD-AI-12 |
| 失败修复 Agent | agent | 修复前红、修复后绿且产品 mutation 仍能被抓 | 禁止把断言删掉“修绿” | TD-AI-13 |
| 多 Agent 测试流水线 | agent swarm | 任务交接与独立验证 | 最小权限、预算、停止条件 | TD-AI-14 |

## `build-ai-quality-system`

| Platform capability | AI role | Learner proof | Failure modes | Course |
| --- | --- | --- | --- | --- |
| 数据集/Prompt/模型版本 | infrastructure | 可重放实验 ledger | 数据泄露、不可重现 | TD-AI-15 |
| CI 质量门禁 | infrastructure | 回归阻断和 waiver 记录 | 阈值过拟合、flaky judge | TD-AI-16 |
| Trace 与线上反馈回归 | infrastructure | 线上失败转入评测集 | 采样偏差、PII | TD-AI-17 |
| 成本/延迟/质量联合决策 | infrastructure | Pareto 报告与发布选择 | 只优化单指标 | TD-AI-18 |
| 漂移与事故响应 | infrastructure | 告警、回滚和复盘演练 | 告警疲劳、未知漂移 | TD-AI-19 |
| AI QE 平台 capstone | infrastructure | 从 commit 到生产反馈的完整链路 | 权限和治理缺失 | TD-AI-20 |
