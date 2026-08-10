# TD-PS02 · OpenAPI Schema 与属性测试：让坏请求和破坏性变更变红

## Research brief

业务场景是支付意图 API，字段包括金额、币种、商户、客户和回跳地址。传统做法生成少量合法 JSON，再检查 `2xx` 和字段类型；它会漏掉金额为零、币种与商户配置不符、客户越权和过期意图重复确认。AI 可以阅读 Schema 并提出边界组合或解释契约 diff，但不能把“合法 JSON”判为“合法支付业务”。工程目标是把 Schema、跨字段属性、状态前置和 mutation 检测力连接起来，工具选型为 OpenAPI + JSON Schema + Schemathesis/Hypothesis，服务执行仍需隔离租户和合成支付数据。

## Source pack

- OpenAPI Specification：<https://spec.openapis.org/oas/v3.2.0.html>，定义参数、请求体、响应和 Schema 语义；跨字段业务规则需要额外 Oracle。
- JSON Schema Draft 2020-12：<https://json-schema.org/draft/2020-12>，支持类型、组合、边界和条件约束；工具实现仍需锁定 dialect。
- Schemathesis 文档：<https://schemathesis.readthedocs.io/en/stable/>，支持从 API schema 生成 property-based 测试和报告；生成量不等于业务覆盖。
- Hypothesis stateful testing：<https://hypothesis.readthedocs.io/en/latest/stateful.html>，支持状态序列和规则式属性；不应替代简单、可读的固定用例。

## Evidence synthesis

事实：Schema 能表达 required、类型、枚举和部分数值边界，但通常不能独立表达“客户只能访问自己的意图”“过期意图不可确认”这类业务条件。事实：mutation 是测试检测力证据，删除 `merchant_id` required 或放宽 `amount > 0` 后，若套件仍绿，说明 Oracle 不足。工程综合：每条生成输入都要带 case ID、风险、预期错误模型和最小重放。

传统随机数据容易产生大量无意义失败，例如不存在的商户或无法解释的网络错误。AI 变化是根据字段语义、历史缺陷和错误日志生成候选边界；工程边界是候选先过 schema/数据工厂，再由固定属性断言裁决。失败模式包括空值与缺省混淆、额外字段被静默接收、错误码漂移、随机 seed 无法复现和 mutation 未被捕获。页面只做 static-reviewed 设计。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| OpenAPI 版本（输入） | 固定规范 commit、Schema dialect、操作 ID、examples 和 mutation 版本；保存规范 hash。 |
| 例生成器（处理） | 生成合法、缺字段、非法枚举、边界金额、错误 Content-Type 和最小跨字段组合；固定 seed。 |
| Schema 校验器（门禁） | 先判 request/response 结构；结构失败与服务业务拒绝分开编号，不把网络异常混入产品失败。 |
| 业务属性 Oracle（处理/证据） | 校验金额、币种、归属、过期状态、错误模型和状态不变式；每条属性带 requirement_ref。 |
| 被测 API（处理） | 在合成支付租户运行，记录请求、响应、状态快照和 side-effect ledger；禁止真实扣款。 |
| Mutation 控制器（输入/处理） | 注入删除 required、放宽范围、改错误码和删除跨字段规则；输出预期失败 ID。 |
| 报告与门禁（证据/人工决策） | 汇总属性覆盖、mutation 发现率和最小复现；阻断项自动失败，规则冲突由测试 owner 审查。 |

可执行物料是支付意图 OpenAPI、属性清单、mutation YAML、固定 seed 和错误模型目录。先做 Schema 静态验证，再执行服务，最后对每个红色 mutation 生成最小请求。

## Manuscript map

开篇展示一个 `amount: 0` 的合法 JSON 如何穿过类型检查。接着用“约束—风险—Oracle”表区分 Schema 与业务属性，再介绍受控正反例和 mutation。页面应展示一次删除 required 后预期变红的报告格式，并把 AI 生成限制在候选组合和失败解释。结尾给出最小重放记录，而不是样例数量排行榜。

## Editorial review

避免把 property-based testing 描述成随机覆盖万能方案；保留 seed、最小化、业务状态和 mutation 发现率。每个工具都有明确职责：Schema 负责结构，生成器负责空间，属性负责语义，mutation 负责检测力。没有把教学 fixture 的发现率写成真实支付 API 的覆盖率，也没有伪造执行结果。

## Validation

当前状态：`desk-researched`，未在目标支付服务或真实商户配置上运行生成测试。

后续可离线升级为 fixture-tested：`validate_payment_schema.py` 校验 OpenAPI 与错误模型；`generate_payment_cases.py --seed <固定值>` 产生可复现输入；`run_property_oracle.py` 用内存支付状态机检查属性；`apply_schema_mutation.py` 注入四类契约变化并要求至少一项 gate 失败；`shrink_case.py` 输出最小 JSON。离线结果只证明生成与门禁逻辑，不证明供应商支付行为。
