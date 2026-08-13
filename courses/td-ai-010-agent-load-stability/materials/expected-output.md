# 预期输出与页面门禁

| 页面 | Fault 必须暴露 | Repair 必须恢复 |
|---|---|---|
| TD-AP01 | workload slice、business Oracle 缺失 | 切片与 Oracle 完整 |
| TD-AP02 | TTFT、TPOT、queue、retry、step 超限 | 五类指标回到固定 gate |
| TD-AP03 | orphan span / trace incomplete | task-rooted parent 关联 |
| TD-AP04 | closed load 协调遗漏、到达失真 | open arrival 可解释 |
| TD-AP05 | goodput/queue 失败且瓶颈未知 | synthetic goodput 与归因恢复 |
| TD-AP06 | timeout/retry 风暴、任务失败 | 总预算与安全降级恢复 |
| TD-AP07 | 资源正斜率、cleanup 失败 | 斜率和 cleanup 同时恢复 |
| TD-AP08 | good-task、告警动作、事故证据缺失 | SLI、action、evidence 完整 |

每个 `cycle-summary.json` 应显示 `cycle_pass=true`、observed `0/1/0` 和 repair_comparison。结果只能标为 fixture-tested，不代表生产容量。

