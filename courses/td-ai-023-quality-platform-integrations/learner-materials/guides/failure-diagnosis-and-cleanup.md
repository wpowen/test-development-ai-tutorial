# 失败诊断、回滚与清理

按 `failed_oracle_ids` 诊断：`INBOX-DEDUPE` 看 inbox key，`SHA-BINDING` 对比 run/head，`JUNIT-COMPLETE` 查报告与 artifact，`K8S-BOUNDARY` 查 Role/namespace/TTL，回写重复查 fingerprint。回滚先冻结新的成功状态、保留失败工件和 outbox，再修复或 supersede，按 owner+TTL 清理 namespace，最后写 `rollback_requested/cleanup_completed` 审计；不能通过手工评论伪造 PASS。
