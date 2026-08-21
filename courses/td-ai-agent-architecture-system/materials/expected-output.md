# 预期输出

| 阶段 | 退出码 | 必须可见 |
|---|---:|---|
| baseline | 0 | `verdict=PASS`、独立 Oracle 全通过、`model_evidence=NOT_RUN` |
| fault | 1 | `verdict=FAIL`、`failed_oracle_ids`、故障状态与 stop reason |
| repair | 0 | 同一合同恢复、原 Oracle 保留、未扩大权限 |

四证据环的 shadow/online 仍保持 `NOT_RUN`，不能由离线报告补写。
