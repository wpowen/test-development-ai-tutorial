# 验收清单

- [ ] baseline 退出 0 且 `gate_pass=true`
- [ ] retry-storm 退出 1 且至少一个门禁变红
- [ ] repaired 退出 0 且调用放大、排队或成本恢复
- [ ] 三次运行使用可比较的任务定义与固定 seed
- [ ] 能从 `traces.jsonl` 找到具体失败步骤与 attempt
- [ ] 报告明确标注 fixture，不声明生产容量
