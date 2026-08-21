# 从需求文档到执行证据

本课用虚构的订单取消场景，串起测试依据、需求契约、评审问题、风险策略、测试包、执行证据和变更回归。AI 负责提取、质疑和生成候选工件；产品、技术、测试和发布责任人负责业务语义、关键 Oracle、残余风险和发布决定。

## AI centrality

课程不是普通需求分析加一段提示词。模型参与多文档抽取、冲突发现、风险候选、测试设计和失败聚类；因此新增了结构正确但语义错误、静默补规则、同模型自证、healer 误修绿和版本漂移等失败。移除 AI 后，权限划分、Structured Output、独立 Critic 和生成资产验证都失去核心问题。

AI 不能决定退款政策、权限和发布结论。所有无法从来源支持的字段进入 `UNKNOWN`，有效来源冲突进入 `BLOCKED`。这两个状态不能被自动转成 PASS/FAIL。

## System under test

场景包含已支付未发货订单、已发货订单、买家权限、取消接口和异步退款副作用。PRD 规定 SHIPPED 不可取消；OpenAPI 定义 409；旧技术方案被用作冲突负控制。健康实现拒绝已发货订单、阻止越权并对重复请求保持幂等。

离线夹具不调用真实模型或支付网关。它模拟 AI 生产线的中间工件和门禁，重点验证输入冲突、无来源规则、独立 Oracle、负控制和执行证据。

## Baseline and target

常见基线是把 PRD、技术方案和接口文档一起发给模型，要求直接生成测试。输出可能有标题、步骤和预期结果，却没有版本、引用、未知项或下游数据契约。

目标链路是：

```text
Test Basis Pack
  -> Requirement Contract
  -> Review Question Pack
  -> Risk Test Plan
  -> TestPackage
  -> Executable Tests
  -> Run Manifest
  -> Evidence Pack
  -> Impact Set
```

每个工件保留父工件、版本、owner、状态、来源引用和下游消费者。关键输入缺失、来源冲突或 Oracle 未定义时，流水线停止。

## Direct-use Prompt Kit

课程同时交付八套可以直接复制到通用 AI Agent 的 Prompt，而不是只给抽象方法名：

1. P01 冻结测试依据和生命周期入口；
2. P02 进行需求评审、需求解析和验收标准整理；
3. P03 解析技术文档中的组件、接口、状态、重试、幂等、恢复和可观测性；
4. P04 从风险和输入形态选择测试方法与层级；
5. P05 固定独立 Oracle 后生成测试点和测试用例；
6. P06 审查用例并适配 API、契约、组件、UI 或数据自动化；
7. P07 固定运行证据、归因失败并生成可复现缺陷；
8. P08 分析变更影响、选择回归集并使过期 PASS 失效。

先读 `lab/DIRECT-USE-GUIDE.md`，再复制 `lab/page-prompts/<页面 ID>/prompt-v1.md` 的“直接复制到 AI Agent”代码块。迁移到自己的业务前填写 `lab/ADAPTATION-CARD.md`。每套 Prompt 都包含准备项、输入粘贴区、可改字段、预期输出、自检和 BLOCKED 条件；结构合同已验证，真实模型执行仍为 `NOT_RUN`。

## Commands

在本课程 `lab/` 目录运行三态实验：

```bash
python3 pipeline.py reset
python3 pipeline.py all --report reports/baseline.json
python3 pipeline.py inject-code-defect
python3 pipeline.py all --report reports/mutation.json
python3 pipeline.py repair
python3 pipeline.py all --report reports/repair.json
```

预期退出码为 `0 / 1 / 0`。文档冲突实验为：

```bash
python3 pipeline.py reset
python3 pipeline.py inject-doc-conflict
python3 pipeline.py all
```

预期退出码为 `2`，状态是 `BLOCKED`，且不得生成新的下游测试包。

## Metrics and thresholds

本课不用“生成用例数”作为指标。门禁检查：关键规则引用完整率 100%；冲突静默合并数 0；无来源 ACCEPTED 字段数 0；高风险测试有独立 Oracle；已知 mutation 检出率 100%；运行报告包含输入 hash、选择集、skip、retry 和实际结果。

这些是教学夹具的结构门槛，不是生产阈值。真实项目还要根据业务损失、历史缺陷、系统层级、数据政策和发布责任确定严重性与覆盖。

## Failure injection

第一种失败发生在上游：`inject-doc-conflict` 让 PRD 与旧技术方案对 SHIPPED 订单给出相反规则。正确结果是退出 2，并把问题交给产品 owner。

第二种失败发生在产品实现：`inject-code-defect` 把已发货订单错误改为允许取消。`T-CANCEL-SHIPPED-01` 期望 409，实际得到 202，执行退出 1。报告同时记录 `REQ-CANCEL-002`、`RISK-INVALID-STATE`、mutation ID 和输入 hash。

若冲突仍继续生成测试，或 mutation 仍返回 PASS，本课直接失败。调整断言、删除测试或放宽规则不属于修复。

## Human review gate

产品 owner 确认业务语义和冲突决议；技术 owner 确认当前接口、状态与副作用；测试负责人确认风险、层级、Oracle 与 mutation；发布 owner 接受或拒绝残余风险。

AI 可以生成候选问题和缺陷草稿，但不能替上述责任人签字。金额、权限、状态和不可逆副作用的 Oracle 必须来自批准契约、账本不变量或领域样例，而不是从被测实现反推。

## AI-specific failure boundary

Structured Outputs 只约束 JSON 形状；字段值仍可能错误。模型也可能混合过期文档、补出退款 SLA、把 skip 当修复、根据实际响应修改 expected，或在没有环境证据时输出结论。

课程通过 source_ref、source precedence、`UNKNOWN/BLOCKED`、独立 Critic、适配器权限、mutation 和 Run Manifest 约束这些失败。它仍不能证明模型在真实文档分布上的准确率，也不能覆盖所有未知业务规则。

## Learner artifact

学习者交付 Test Basis Pack、Requirement Contract、Review Question Pack、Risk Test Plan、TestPackage、自动化追溯索引、baseline/mutation/repair 三份报告、Evidence Pack 和一次 Impact Set。

每个工件必须能回答：输入来自哪里；谁批准；AI 做了什么；哪个字段被下游消费；什么条件会阻断；哪个版本变化会使证据过期。

## Evidence status

确定性离线夹具已经运行：baseline PASS、代码 mutation FAIL、repair PASS；文档冲突返回 BLOCKED。该证据证明脚本、工件和门禁可复现，不证明真实模型抽取准确率、真实支付行为、企业缺陷发现率、学员效果或生产发布安全。

## Transfer

迁移到登录、结算、物流或审批时，保留版本化测试依据、段落引用、冲突传播、独立 Oracle、负控制和执行证据；替换业务状态机、接口、历史缺陷、权限、数据和责任人。先在隔离环境验证一条高风险路径，再扩大覆盖。不要直接把教学订单规则复制到真实系统。
