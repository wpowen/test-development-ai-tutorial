# 期望结果

`baseline.json` 和 `repair.json` 为 `PASS/0`；`mutation.json` 为 `FAIL/1` 且 stale SHA 的失败 Oracle 是 `SHA-BINDING`。其他 mutation 应分别指向 `INBOX-DEDUPE`、`K8S-BOUNDARY`、`JUNIT-COMPLETE`。报告中的 state 是可审计快照，不是生产系统事实。
