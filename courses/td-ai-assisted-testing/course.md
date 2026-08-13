# AI 辅助传统测试：从变更风险到失败证据

这门课不教“把 PRD 贴给模型，让它写很多测试”。学习者要完成一条可审计链：冻结测试依据与代码 Diff，生成有引用的风险候选，用独立 Oracle 和 mutation 证明测试有检测力，按风险选择边界/组合/property/fuzz 方法，最后让 AI 聚类失败但保留原始事件与 `UNKNOWN`。

## Learner and prerequisites

面向能读基础 PRD、Diff、JSON 和测试结果的初级测试开发。前置能力是需求可测性、测试 Oracle、状态与组合测试的基本概念；不要求模型 API、云账号或第三方包。

## AI centrality

AI 能快速阅读变更、提出风险、生成测试、建议数据维度和压缩大量失败，但新增四类风险：无来源猜测、同模型自证 Oracle、表面覆盖却杀不死 mutation、以及把相似失败写成未经验证的根因。移除 AI 后，这些权限、Prompt/Schema/Eval/Mutation 与独立验证问题也随之消失，因此 AI 是核心工作流而不是装饰。

## System under test

```text
Frozen Basis + Code Diff
  -> cited risk candidates
  -> human-owned risk decision + independent oracle
  -> generated test candidates
  -> baseline / mutation / repair evidence
  -> selected boundary-combination-property-fuzz data
  -> raw failure events + candidate clusters
  -> controlled experiment
  -> PASS / FAIL / UNKNOWN / BLOCKED decision
```

每个中间工件有版本、来源、owner、状态和下游消费者。关键来源冲突时停止；模型提出的测试只有在 mutation 中杀死预埋业务缺陷后，才能进入回归候选集。

## Baseline and target

传统基线是工程师分别阅读 PRD、查看 Diff、手写测试数据并逐条排查失败；常见结果是引用链断裂、弱断言和归因不可复核。本课目标不是用 AI 替代这些专业判断，而是让候选生成更快，同时以引用闭合、独立 Oracle、预埋 mutation、最小反例和原始事件引用建立更严格的完成条件。教学目标限定为四页确定性 fixture 全部形成 baseline/fault/repair 证据；真实项目目标和阈值必须重新建立。

## Inputs, prompts, schemas and independent Oracle

`lab/fixtures/basis.json` 冻结 PRD 条款、当前代码 Diff、来源权威、业务不变量和责任人。四个 `lab/page-prompts/<page-id>/` 分别保存 Prompt、固定 Input、输出 Schema、Eval、Mutation 和 provider/model 配置。离线运行不调用模型，`model_evidence` 保持 `NOT_RUN`。

`fixtures/oracles.json` 独立于生成 Prompt，来源是冻结 basis 中已接受的不变量与批准样例。候选生成器不能修改这个文件，也不能根据被测实现当前输出倒推 expected。

## Commands

从 `courses/td-ai-assisted-testing/lab` 运行：

```bash
python3 ai_assisted_lab.py verify-packages
python3 ai_assisted_lab.py suite --phase baseline
python3 ai_assisted_lab.py suite --phase fault
python3 ai_assisted_lab.py suite --phase repair
```

预期退出码依次为 `0 / 0 / 1 / 0`。`suite --phase fault` 汇总四页故障，其中 TD-T05 与 TD-T08 的正确停止状态为 `BLOCKED/UNKNOWN`，TD-T06 与 TD-T07 的预埋产品缺陷为 `FAIL`；套件把这些红结果视为已观察到的负控制并统一退出 1。

## Metrics and thresholds

- 风险引用完整率：教学夹具要求 100%，来源点为 risk matrix；缺失时 `BLOCKED`。
- 高风险 mutation 检出率：教学夹具选定 mutation 要求 100%，来源点为 mutation report；survived 必须有处置，不把分数外推为生产阈值。
- 失败样例可重放率：保存 seed、输入、system version 和最小反例；目标是已保存样例 100% 可重放。
- 聚类证据闭合率：每个簇至少两个原始 event ref，且 commit/environment 一致；不满足时为 `UNKNOWN`。

这些阈值只用于合成场景的工件完整性，不证明真实项目的缺陷发现率、效率或根因准确率。

## Failure injection and repair

TD-T05 删除一个 Diff 引用，风险候选必须阻断；TD-T06 反转“已激活数字商品不可自动退款”的条件，独立测试必须变红；TD-T07 关闭幂等保护，固定 seed 必须找到并缩减双退款反例；TD-T08 混合不同 commit 的事件并删除 trace 引用，根因必须降级为 `UNKNOWN`。Repair 恢复输入或实现并重新运行，不允许删除断言、改 expected 或让模型批准自身结论。

## Human review gate

产品 owner 确认退款规则，研发 owner 确认 Diff 与部署版本，测试负责人选择风险与方法、批准独立 Oracle，故障 owner 批准根因和行动。AI 只生成候选。真实 PRD、源码、日志和 Trace 进入模型前必须脱敏并遵守组织的数据边界。

## AI-specific failure boundary

模型可能发明未提供的 SLA，把实现当前输出复制成 expected，用高覆盖掩盖弱断言，推荐无授权 fuzz，或把相似异常写成根因。四类门禁分别要求引用存在、Oracle 外置、mutation 能被杀死、缺 trace/混合版本保持 `UNKNOWN`。同一模型不得同时生成候选和批准 Oracle；任何自动 repair 不得删除断言、改写业务规则或覆盖原始证据。当前模型调用为 `NOT_RUN`，因此课程只证明防线形状和离线 runner，不证明生成质量。

## Learner artifact and assessment

学习者提交四份报告、四个版本化 Prompt 包、三个阶段的运行收据和一份迁移说明。验收重点不是数量，而是能否从 source ref 走到风险、方法、Oracle、case、result，并在证据不足时保留 `UNKNOWN/BLOCKED`。

## Evidence status and limits

确定性 Python 标准库夹具已运行 baseline/fault/repair。它证明仓库内工件、状态传播、负控制和命令可复现；没有运行真实模型、代码托管平台、真实测试框架、生产日志或从业者评审，因此不能写成 live、practitioner 或 production。

## Transfer

迁移到订阅续费时，保留来源冻结、AI 权限、独立 Oracle、mutation、seed/replay、原始事件与实验验证；必须替换状态机、金额与时间边界、渠道组合、幂等键、日志字段、owner 和风险阈值。成功标准是新场景的预埋重复扣费缺陷稳定变红，证据不足的失败仍保持 `UNKNOWN`。
