# API Run Manifest：让一次“通过”可重放

Run Manifest 是本次执行的身份证。没有它，绿色日志无法回答“跑了什么版本、选择了哪些用例、用了哪个 Oracle、是否跳过、能否重放”。

## 最小字段

```json
{
  "run_id": "RUN-20260810T000000Z",
  "status": "PASS",
  "evidence_status": "fixture-tested",
  "command": "python3 scripts/api_automation.py baseline --report reports/baseline.json",
  "runtime": "CPython 3.x standard library",
  "inputs": {
    "order_openapi_sha256": "...",
    "payment_openapi_sha256": "...",
    "checkout_events_sha256": "...",
    "mutation_catalog_sha256": "...",
    "oracle_sha256": "..."
  },
  "selected_case_ids": ["CONTRACT-ORDER-OPERATIONS", "BUS-SHIPPED-REJECT"],
  "mutation_id": null,
  "skipped": [],
  "results": [],
  "not_run": ["Schemathesis", "Pact", "k6", "GitLab CI"]
}
```

## 运行前

1. 固定 Spec、事件 fixture、mutation catalog 和 Oracle 的版本或 hash。
2. 记录工作目录、完整命令、Python/工具版本、环境与数据边界。
3. 明确用例选择集、seed、预算、破坏性 endpoint allowlist 和 stop condition。
4. 缺少关键输入、owner 或独立 Oracle 时标记 `BLOCKED`；工具未执行时标记 `NOT_RUN`。

## 运行后

1. 保存进程退出码、每个 case 的 expected/actual、失败类别和最小 replay。
2. 明确 skip、retry、timeout、未解析依赖和不稳定重跑，不能只留最终 PASS。
3. 把 mutation ID 与检测 case 绑定；若已知 mutation 未变红，整个测试资产判为无检测力。
4. 报告由 CI 上传，但发布决定仍由具名 owner 承担。

## 本材料的停止规则

- `0`：全部必需 Oracle 通过。
- `1`：可执行检查发现产品、契约或事件缺陷。
- `2`：输入/环境/责任人不足，无法形成有效结论；不得降级为 PASS。

本课程脚本当前只产生 `0/1`，因为所需离线输入均随包提供。外部工具仍是 `static-reviewed/NOT_RUN`，不会在报告中伪装成执行成功。
