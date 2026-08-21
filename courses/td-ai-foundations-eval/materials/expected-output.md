# Expected output

Baseline 和 repair 报告显示 `verdict=PASS`、`model_execution=NOT_RUN`，三个字段均匹配。Fault 报告显示 `verdict=FAIL`、`acl_denied expected=true actual=false`，进程 exit 1。该结果只证明确定性合同杀死指定 mutation。
