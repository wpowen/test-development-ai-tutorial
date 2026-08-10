# 验证清单

- [ ] HMAC 使用原始 body，重复事件只产生一次副作用。
- [ ] AI candidate 有 reviewer、model、prompt hash，不能自批准。
- [ ] run/pipeline/JUnit/artifact 均绑定当前 commit SHA。
- [ ] namespace 非 default，Role 不含 cluster-admin，TTL 和 owner 存在。
- [ ] Jira 缺陷按 fingerprint 幂等，GitLab status 只写当前 SHA。
- [ ] 通知无 token/secret，audit 为 append-only hash chain。
- [ ] 外部适配统一标 `static-reviewed/NOT_RUN`，不把配置当运行证据。
