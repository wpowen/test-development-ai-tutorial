# TD-QP04 · 跨系统事件总线、幂等/重放、回写、脱敏通知与审计闭环

## Research brief

业务场景是一次质量运行跨 Jira、GitLab、Kubernetes、artifact store 和 ChatOps：Jira 需求事件触发 GitLab MR/Pipeline，Kubernetes 执行测试，结果聚合后回写 Jira 缺陷和 GitLab 当前 SHA 状态，再发送脱敏摘要并回收环境。目标是让重复、乱序、漏投、部分成功、API 限流和敏感数据事件都能被去重、补偿、诊断和审计。

研究范围是 CloudEvents 风格信封、Inbox/Outbox/DLQ、source_event_id/correlation/causation/trace、幂等 fingerprint、API reconciliation、Jira/GitLab 回写、通知 allowlist/脱敏、W3C Trace Context 和跨系统 append-only audit。真实租户、集群、事件总线、通知频道和审计后端投递/重放均为 `NOT_RUN`。

## Source pack

- [CloudEvents specification](https://github.com/cloudevents/spec)：提供 `id`、`source`、`type`、`subject` 等跨系统事件上下文；不定义业务幂等或回写策略。
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)：定义 `traceparent`/`tracestate` 传播；不应承载业务身份、Token 或 PII。
- [Jira issue REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/)：支持缺陷、评论、链接、transition 等回写；必须按目标项目权限和状态回读。
- [GitLab Pipelines API](https://docs.gitlab.com/api/pipelines/) 与 [commit status API](https://docs.gitlab.com/api/commits/#post-the-build-status-to-a-commit)：支持 Pipeline 查询和 SHA 状态回写；旧 SHA 不得覆盖当前 HEAD。
- [Kubernetes auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)：提供集群动作审计；需要与平台 run/trace 关联而非复制 Secret。

## Evidence synthesis

事实：事件的唯一 ID、来源、因果链和当前外部状态是不同证据；重复投递必须不会产生第二个缺陷、第二个 status 副作用或第二次环境回收。事实：Webhook 不保证事实完整，必须用 Jira/GitLab/K8s API reconciliation 修复漏事件和乱序。事实：通知是下游消费者，通知失败不能改变质量 gate。

工程综合：Gateway 验签、时间窗、租户/项目 allowlist 后写 Inbox；Orchestrator 用状态机和 Outbox 驱动幂等副作用；超过重试上限进入 DLQ；恢复时以当前 revision/SHA/environment 回读为准。事件 payload 只带 artifact_ref 和脱敏字段，完整日志/JUnit 由授权 API 读取。

故障模型包括响应丢失导致的重复写入、旧事件覆盖新状态、乱序 gate/result、API 429/403、通知超时、DLQ 堵塞、K8s cleanup 延迟和 PII 泄露。AI 只能分类、聚类和起草脱敏摘要，不能直接写入系统事实、发送敏感通知或批准 waiver。

## Engineering blueprint

七节点架构与 TD-QP04 页面一致：

| 节点 | 实施与可审计输出 |
|---|---|
| Jira/GitLab/K8s 上游事件（输入） | 产生需求、MR/Pipeline、环境/结果/cleanup 事件；事件带 source、id、revision/SHA/environment 关联。 |
| Event Gateway/验签去重（处理） | 校验签名、时间窗、tenant/project/type/schema，写 Inbox，快速 2xx；拒绝和重复都有 audit。 |
| Inbox/Outbox/DLQ（处理） | Inbox 保障入站去重；Outbox 保障副作用重试；DLQ 保留超限失败和人工处理上下文。 |
| Quality Orchestrator/状态机（处理） | 以当前 revision/SHA/environment 为事实，建立 causation graph，阻止旧事件覆盖新状态。 |
| Jira/GitLab/K8s 适配器（处理/证据） | 通过 fingerprint、SHA、environment owner 做幂等回写/清理；写前回读权限和当前状态。 |
| Artifact/脱敏通知（证据/输出） | artifact_ref 指向不可变 JUnit/log/provenance；通知只发送 allowlist 脱敏摘要，失败不改 gate。 |
| Reconciliation/Trace/审计 Sink（人工决策） | 对账补偿漏事件；W3C trace 和外部 audit 引用闭合一次 run；人工复核不可自动补偿的冲突。 |

材料计划是 `event_replay_and_reconcile.py`、`event-gateway-policy.yaml`、`quality-event-envelope.json` 和 `td-qp04-event-audit-sop.md`，均为页面指定的材料路径；当前交付不创建这些课程材料文件。

## Manuscript map

开篇用“Jira 缺陷创建请求已发送但响应丢失”说明为什么不能盲目创建第二个 issue；再用重复/乱序/旧 SHA 事件拆 Inbox、Outbox、DLQ 和 reconciliation。随后描述 Jira/GitLab 回写、K8s cleanup、脱敏通知和 trace/audit graph。故障注入需包含重复 webhook、旧签名、429、通知超时、含 PII payload 和对账修复。

结尾明确人类决策、回滚和 `NOT_RUN`：冻结新 success、恢复上一版 adapter/policy、保留原始队列和审计、按当前事实补偿；未在真实租户/集群投递或重放时，不能声称 delivery guarantee、幂等或审计闭环已验证。

## Editorial review

保留跨系统关联字段和各适配器的事实边界，没有把 CloudEvents 或 Trace Context 描述成消息可靠性、业务幂等或隐私合规的自动保证。通知与事实来源分离；Jira/GitLab/K8s 回写均要求当前状态/权限回读；部分成功必须有独立状态而不是一个模糊失败。

官方/GitHub URL 直接放入 Source pack，页面 `sourceIds` 复用站点已有来源 ID。`static-reviewed` 只表示研究设计和材料计划已审阅；真实网络、签名、投递、重放、脱敏效果和 audit retention 仍待隔离环境验证。

## Validation

状态：`desk-researched`；真实 Jira/GitLab 租户、Kubernetes 集群、事件总线、通知频道、artifact store、DLQ、reconciliation worker 和审计 backend 均为 `NOT_RUN`。

静态验证范围：页面有 5 个实质 blocks、7 个 architecture nodes、至少 3 个 sourceIds、3 个 outcomes/practice/completion 项，并链接脚本、配置、夹具和指南计划文件。后续真实验收必须覆盖重复/乱序/旧事件、响应丢失、429/403、DLQ、通知脱敏、K8s 回收、跨系统 trace/audit graph 和 rollback。
