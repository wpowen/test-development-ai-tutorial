# 测试方法论与实施方案：从阶段契约到发布决定

配套文档：仓库 `methodology/`（14 篇）。本课程把方法论中的判断规则做成一个可运行的门禁夹具，让学员先看到「规则被违反时系统真的会阻断」，再把同一套规则搬到自己的项目。

## AI centrality

课程的被测对象是**AI 变更的发布治理流程本身**。传统发布流程只需要回答「代码变了什么」；一次 LLM、RAG 或 Agent 变更却同时改动模型、Prompt、索引、工具与 Scorer 五个维度，任一维度单独回滚都会退到一个从未被测试过的组合。

移除 AI，这门课的核心问题就消失了：不再需要区分 `PASS_SCHEMA` 与 `PASS_SEMANTIC`，不再需要禁止语义层单独放行 blocker，不再需要重复运行来报告分布，也不再需要在冲突时输出 `BLOCKED` 而不是让模型挑一个更合理的说法。这五条正是本课程的门禁内容。

同时课程明确划出 AI 不能做的部分：模型可以抽取证据、生成候选工件、解释门禁失败，但不能裁决业务规则冲突、不能批准自己的输出、不能签发 Waiver、不能作出发布决定。这些权限边界被写进夹具，并由 `judge-self-approval` 故障验证。

## System under test

被测对象是一条治理流水线的工件闭包：来源清单（source-manifest）、需求契约（requirement-contract）、风险登记册（risk-register）、Oracle 设计记录、三段 Run Receipt 与 Waiver 台账。

七道门禁分别对应方法论的 S1、S2、S4、S5、S8、S9 与工件闭包。每道门禁只检查一件事，并在失败时指名具体状态词（`BLOCKED`、`UNSUPPORTED_RULE`、`UNKNOWN`），而不是返回一个笼统的「不通过」。贯穿业务场景是订单取消与退款，其中故意保留一处 PRD 与旧技术方案的冲突。

## Baseline and target

基线是当前多数团队的做法：门禁只检查结构是否合法、报表只看平均分、Waiver 写在会议纪要里没有过期时间、失败归因由人凭经验判断。这种做法能通过评审，但无法回答「已知坏版本能否被拦下」。

目标状态是：每一条判断都能指向一份可引用的文档或一条可复现的运行记录；冲突与未知显式阻断下游；语义层不得单独放行 blocker；Waiver 必须过期；发布是一份署名决定而不是流水线绿灯。

课程用同一份夹具跑出前后对照——注入缺陷前后，门禁输出从 `PASS` 变成指名了具体状态词的 `FAIL`。

## Commands

工作目录固定为 `learner-materials`。全部命令只用 Python 标准库，无网络、无模型调用、不写入任何文件（故障注入在内存中进行）。

```bash
cd learner-materials
python3 scripts/validate_handbook.py all
python3 scripts/validate_handbook.py all --fault doc-conflict
python3 scripts/validate_handbook.py all --fault none
python3 scripts/validate_handbook.py list-faults
python3 scripts/validate_handbook.py all --report reports/baseline.json
```

期望退出码依次为 `0`、`1`、`0`。这三段就是本方法论对「可运行」的定义：只有第一段的绿色不构成证据，它可能只是因为检查根本没做。

## Metrics and thresholds

课程本身度量三项：门禁项数（当前 7 项）、可注入故障数（当前 5 类）、每类故障是否被**指定的那一道**门禁拦下而不是被别的门禁顺带拦下。

方法论中出现的全部数值阈值（覆盖率、杀死率、天数、百分比）在夹具中一律为结构占位，不参与判定。定阈值的方法写在 `methodology/08-度量体系.md` 第 8.6 节：先采集 3–5 个稳定周期的实测分布，取 p50 与 p95 作为锚点，由风险 owner 决定阈值方向与超阈值动作，每季度复评。

直接照抄别人的数字，会得到一个既不阻断真问题、又天天误报的门禁。

## Failure injection

五类故障各自对应一条方法论公理，注入后门禁必须以非零退出码失败，并指名状态词：

| 故障 | 被哪道门禁拦下 | 期望输出 |
| --- | --- | --- |
| `doc-conflict` | S1 依据冻结 | 冲突未指定升级责任人，下游生成必须停止 |
| `unsupported-rule` | S2 需求契约 | `UNSUPPORTED_RULE`：规则没有来源支持 |
| `missing-oracle` | S5 Oracle 设计 | 关键风险没有 Oracle 设计记录 |
| `expired-waiver` | S9 发布判断 | Waiver 已过期，发布必须阻断 |
| `judge-self-approval` | S5 Oracle 设计 | blocker 只用了语义层，必须含规则层或人工层 |

任一故障若返回 `0`，说明门禁在这条规则上没有牙齿，属于课程本身的缺陷，不是学员操作问题。

## Human review gate

夹具能判定的只有结构、闭包与状态传播。以下判断必须由具名人类完成，课程不提供也不模拟：

业务规则冲突由产品 owner 裁决；关键金额、权限与状态的 Oracle 由领域 owner 确认；风险降档由具名接受人签字并写复评日期；Waiver 由发布 owner 批准，安全类 Waiver 由安全 owner 批准；发布决定与剩余风险接受由发布 owner 署名；回滚决定与执行由 SRE 负责。

课程要求学员在完成夹具后，填写 `materials/verification-checklist.md` 中的角色具名栏——六个关键角色都要有真实姓名，否则这套流程会在第一次冲突时崩溃。

## AI-specific failure boundary

本课程的证据只覆盖确定性离线夹具。它证明工件结构自洽、追溯闭包成立、五类预埋缺陷能被门禁发现。

它不证明任何模型的抽取准确率、跨模型与跨版本的稳定性、提示注入抗性、成本与延迟分布，也不证明企业系统集成效果、从业者认可度或生产收益。模型执行状态在夹具中固定为 `provider=none`、`model_status=NOT_RUN`。

课程中的工具类别表不构成对任何产品的推荐；组织职级、年限与晋升周期不在本课程范围，需要时填入组织适配器并保持 `INTERNAL-UNKNOWN`。

## Learner artifact

学员带走一套可直接填写的工件：19 份模板（测试策略、测试计划、测试依据清单、需求契约指南、风险登记册、方法选择矩阵、Oracle 设计记录、测试数据管理、环境登记册、缺陷分级、准入准出、RACI 与职级适配器、度量目录、发布决定书、工具选型打分表、能力矩阵、估算与排期、证据边界声明、质量周报）、8 份可逐条打勾的检查单、5 份机器可校验的 JSON Schema、6 份订单取消贯穿案例的填写样例，以及本课程使用的自检器本身。

出口标准不是「跑通了命令」，而是：能用自己的一个业务变更填出测试策略与风险登记册，并让一个已知缺陷在自己的门禁上稳定变红。

## Evidence status

`fixture-tested`（L1）。基线、五类故障与修复共七次运行的退出码与判定见 `evidence/execution-evidence.json`。

`model-integrated`、`integration-tested`、`practitioner-reviewed`、`production-validated` 四级全部为 `NOT_RUN`，不得由本课程的绿色结果推断。成熟度阶梯与各级所需的新鲜证据见 `methodology/01-公理与责任模型.md` 第 1.4 节。
