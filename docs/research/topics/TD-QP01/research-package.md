# TD-QP01 · Jira 需求事件、Basis Gate、AI 候选与人工批准

## Research brief

业务场景是订单取消需求：Jira 更新验收条件，但旧技术方案仍保留冲突状态规则。质量平台接收 Jira issue webhook 后，必须回读当前 issue/changelog/权限，构建有版本和引用坐标的 Basis Pack；Basis Gate 通过后，AI 才能输出带 source_refs、模型标识、提示词哈希和 schema 版本的候选。最终的需求语义、风险、测试范围和执行批准由有权限的人决定。

研究对象是事件验签与去重、Jira REST 回读、冲突/缺失阻断、AI provenance、人工评审、supersede 和审计。Webhook 不是事实来源；Jira 评论、ChatOps 表情和模型输出都不等于批准。页面与研究包状态为 `desk-researched`/`static-reviewed`；真实 Jira 租户、真实模型和组织审批流明确 `NOT_RUN`。

## Source pack

- [Jira Cloud REST API v3 introduction](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)：支持 REST v3、ADF、认证、权限和分页边界；目标租户 scope 仍需回读验证。
- [Jira issue REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/)：覆盖 issue、changelog、transition、comment 和 link 操作；不能替代业务批准规则。
- [Jira Cloud webhooks](https://developer.atlassian.com/cloud/jira/software/webhooks/)：支持 HTTPS、JQL、HMAC、生命周期和续期约束；事件仍需 API reconciliation。
- [CloudEvents specification](https://github.com/cloudevents/spec)：提供事件 ID/source/type 等信封语义；不定义 Jira 业务状态或人工批准。
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)：支持约束结构化输出；结构有效不等于需求语义已获批准。

## Evidence synthesis

事实：Jira webhook 只提供触发通知；当前需求、变更历史、字段、权限和 transition 必须由 Jira API 回读。事实：结构化输出可以降低字段和类型错误，但不能确认 source_ref 是否真实、冲突规则采用哪一条或 reviewer 是否同意。事实：旧 revision 不能继续驱动新的执行请求。

工程综合：用 Inbox 去重、Basis Gate、source snapshot hash、AI provenance 和 review decision 把候选与批准隔离。缺字段、有效来源冲突、来源不可读、权限失败或模型输出无引用时，结果必须为 BLOCKED/NOT_RUN；不能把“AI 给了答案”写成通过。

未知项：目标 Jira 项目字段、issue type、transition ID、OAuth/Forge/Connect scopes、webhook 续期实现、真实评审角色和模型质量尚未验证。任何租户字段和批准时延都不能从官方文档推断。

## Engineering blueprint

七节点架构与 TD-QP01 页面一致：

| 节点 | 实施与可审计输出 |
|---|---|
| Jira 需求与变更（输入） | 保存 issue key、revision、changelog、owner、敏感等级和 source snapshot hash；需求变化使旧 revision superseded。 |
| Webhook Gateway/Inbox（处理） | 验签、时间窗、防重放、source/event 去重、快速 2xx；记录接收和 duplicate_suppressed。 |
| Jira REST 回读（证据） | 分页读取 issue/changelog/permissions/transitions；保存响应引用和读取时间。 |
| Basis Gate/Source Pack（门禁） | 校验版本唯一、来源存在、字段完整、冲突责任人和敏感边界；失败为 BLOCKED。 |
| AI 候选与 provenance（处理） | 生成风险、测试、假设和 unknowns；每项带 source_refs、model、prompt hash、schema version。 |
| Review Console/人工批准（人工决策） | 记录 reviewer、scope、decision、reason、policy version、时间和 approved revision。 |
| Orchestrator/审计与执行请求（结果） | 只有 approved revision 可产生执行请求；审计关联 actor、action、resource、event、trace 和版本。 |

材料计划是 `basis_gate_and_candidate_review.py`、`jira-basis-gate.yaml`、`jira-requirement-event.json` 和 `td-qp01-jira-review-sop.md`，均使用页面规定的 `materials/quality-platform-integrations/learner-materials/...` 前缀；当前交付只创建页面和研究包，不创建 courses 或材料文件。

## Manuscript map

先用“PRD 已更新、旧技术方案未更新”的冲突需求说明为什么 webhook payload 不能直接生成测试。随后按事件验签/去重、Jira 回读、Basis Gate、AI provenance、人工批准和 supersede 展开。用一个缺少 source_ref 的 AI 候选和一次 reviewer reject 说明候选与批准的边界；再给出指标、故障注入、审计字段、回滚和 NOT_RUN 语句。

页面应保留三类明确结论：事实来自 Jira 回读和版本化输入；AI 只能生成 proposed；人工批准才允许执行。不得用通用“本页完成后”模板，也不得把真实租户结果写成已运行。

## Editorial review

保留 Jira issue/changelog/permission/transition 的具体边界，以及产品、技术、测试 reviewer 的职责差异。没有把 Jira webhook、ADF 或 structured output 描述成业务正确性或审批保证；没有把评论、表情或模型摘要当作批准。`sourceIds` 复用站点现有来源 ID，直接官方 URL 保存在本包 Source pack 中。

风险提示：Jira Cloud 文档、权限和项目字段会变化；本包不假设具体租户、许可证、认证方案、模型版本或审批 SLA。`static-reviewed` 只代表材料结构与研究边界已审阅，不代表真实集成通过。

## Validation

状态：`desk-researched`；真实 Jira 租户、真实 webhook、REST 回读、AI 调用、人工批准和 audit API 查询均为 `NOT_RUN`。

静态验证范围：页面包含 5 个实质 blocks、7 个 architecture nodes、至少 3 个 sourceIds、3 个 outcomes/practice/completion 项，并链接一个脚本、配置、夹具和指南计划文件。后续真实验收必须在隔离 Jira project 验证签名、续期、字段、权限、冲突阻断、review audit、supersede 和回滚。
