# 可复用 Skill：Agent D0-D7 证据卡

```text
输入：风险切片、Agent/工具边界、版本 manifest、脱敏 trace、业务 Oracle、owner 与 rollback。
输出：Evidence/Inference/Unknown 分栏、独立 Oracle、failed_oracle_ids、stop_state、候选修复和复用限制。
允许：整理固定输入、生成测试草稿、聚合 span、提出 repair 候选。
禁止：模型自批 Oracle/waiver，删除断言，扩大权限，解除 blocker，访问真实资金或写入生产。
门禁：先 baseline，再注入单一命名故障，最后恢复同一合同；退出码必须是 0/1/0。
```

提示词不能发明版本、阈值、owner 或生产效果；缺任一关键证据就返回 `BLOCKED` 或 `UNKNOWN`。
