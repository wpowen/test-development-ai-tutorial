# 可复用方法：质量控制平面门禁

将每次跨系统运行固化为 `source_event_id/correlation_id/commit_sha/run_id/artifact_hash/policy_version`，把 AI 输出限定为 candidate，把确定性 Oracle 和人工审批放在门禁前。先验签、去重、回读事实，再执行、聚合、回写、通知和清理；任何缺失报告、旧 SHA、越权或重复副作用都 fail-closed。
