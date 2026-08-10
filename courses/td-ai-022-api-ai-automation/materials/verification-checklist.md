# 验证清单

- [ ] Spec 版本、Schema dialect、输入 hash 已记录。
- [ ] 候选由 Spec 生成，业务 Oracle 在独立规则中维护。
- [ ] contract/schema/permission/business/idempotency/async/SSE 均有 case。
- [ ] 非 owner 无副作用；SHIPPED 不可取消；重复请求只有一次副作用。
- [ ] 异步状态合法，SSE 只有一个终态。
- [ ] mutation 红、repair 绿，未改断言、未 skip 失败。
- [ ] `BLOCKED`、`UNKNOWN`、`NOT_RUN` 未被包装成 PASS。
- [ ] 真实接入前完成数据脱敏、租户隔离、kill switch、预算和 owner 审核。
