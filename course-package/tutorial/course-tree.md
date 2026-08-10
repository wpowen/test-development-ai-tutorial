# 测试开发 × AI 教程知识树

## 学习路线

默认路线不再直接从“AI 测试对象”开始，而是先确认传统测试职业基线，再理解大模型运行机制，最后进入评测实操：

`传统测试能力 → 模型生命周期 → Token/Attention/Context/生成 → LLM/RAG/Agent/Workflow 结构 → AI 测试对象 → Eval 数据与 Oracle → RAG 门禁 → Agent/Workflow → AI 质量系统 → Benchmark → Capstone`

首条已交付路径：

`TD-F01 → F02 → F03 → F04 → T01 → T02 → T03 → T04 → T09 → T10 → T11 → T12`

可以通过阶段考核免修讲解，但不能跳过职业基线、AI 系统结构、Oracle、评测数据和故障注入工件。

## 模块

### 模块零：传统测试能力迁移

1. TD-F01：传统测试开发的流程、方法、工具、工件和质量责任。

### 模块一：大模型与 AI 系统基础

2. TD-F02：模型从数据、训练到推理和监控。
3. TD-F03：Token、Attention、Context、Logits 与概率生成。
4. TD-F04：LLM、RAG、Agent、Worker 和 Workflow 的结构差异。
5. TD-T01：AI 进入后，测试对象发生什么变化。
6. TD-T02：LLM、RAG、Agent 的最小结构与 Trace。
7. TD-T03：概率性输出与组合 Oracle。
8. TD-T04：Eval case、黄金集和风险切片。

### 模块二：AI 帮你做传统测试

9. 从 PRD 和代码 Diff 提取风险。
10. AI 生成测试，但证明测试真的会失败。
11. 生成边界与 Fuzz 数据。
12. AI 做失败聚类，但必须保留证据链。

### 模块三：测试 LLM 和 RAG

13. 第一个 LLM 评测。
14. RAG 检索质量。
15. 回答、引用、忠实性和拒答。
16. RAG 错误退款承诺 PASS→FAIL→PASS。
17. Prompt、模型和知识库版本 A/B。
18. LLM-as-judge 校准和反例。

### 模块四：测试 Agent、Worker 与 Workflow

19. 最终结果、单步动作和完整轨迹。
20. 工具选择、参数和权限。
21. Prompt injection、数据泄露和 excessive agency。
22. Browser Agent 和 Playwright Test Agents。
23. 自愈测试为什么会误修绿。
24. Agent、Worker 和固定 Workflow 的区别。
25. 状态、循环、重试、Handoff 和终止条件。
26. 单 Agent 与多 Agent 的同预算对照。

### 模块五：建设 AI 质量系统

27. 把评测接入 CI。
28. 数据、Prompt、模型、知识库、工具和 Scorer 版本。
29. Trace、生产失败和回归集闭环。
30. 质量、延迟、成本和稳定性联合门禁。
31. 漂移、告警、Waiver 和回滚。

### 模块六：Benchmark 与分数工程

32. Benchmark 评分流水线。
33. 数据来源、采样、标注、Split 与 Holdout。
34. Accuracy、Pass@k、Resolved rate 和 Judge score。
35. Prompt、Harness 和工具权限对分数的影响。
36. 不确定性、污染、隐藏测试和版本可比性。
37. 从公开 Benchmark 到企业内部 Benchmark。

### 模块七：专业 Capstone

38. 完成一个从 Commit 到 CI、Trace、Regression、Benchmark 和回滚的 AI Quality Engineering 仓库。

## 页面状态

- `TD-F01` 至 `TD-F04`：`desk-researched`，具备完整讲解、练习、工件和完成检查，未做真实模型实验。
- `TD-T01` 至 `TD-T04`、`TD-T09` 至 `TD-T11`：`desk-researched`。
- `TD-T12`：`fixture-tested`，离线实验已运行 PASS→FAIL→PASS。
- 其余 26 页：`planned`，只定义知识位置、依赖、工件和学习结果，不冒充完成。

状态含义：

- `planned`：知识位置和依赖已确定；
- `desk-researched`：正文由已打开来源支持，尚未运行目标系统；
- `fixture-tested`：离线夹具和验证器已运行；
- `live-tested`：真实外部模型或系统已运行；
- `practitioner-reviewed`：相关从业者已审；
- `production-validated`：真实生产工作流提供效果证据。
