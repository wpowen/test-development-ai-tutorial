# TD-QP04 事件重放、对账与审计 SOP

事件 Gateway 只接受通过 HMAC、时间窗和 schema 校验的 envelope；重复事件返回可重试的成功语义但不重复副作用。Orchestrator 以 correlation/causation/trace 关联，并在 Jira/GitLab 回写前重新读取事实；失败写入 outbox/dead-letter，恢复后 reconciliation。通知只发脱敏摘要，审计追加 principal、action、resource、decision、source_event_id、trace_id、policy_version、before_hash、after_hash，禁止凭据。
