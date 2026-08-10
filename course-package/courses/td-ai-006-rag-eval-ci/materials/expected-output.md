# Expected output

Baseline 和 repair：`verdict=PASS`，exit code 0，8/8 case 通过，schema、retrieval、引用、拒答和工具门禁 100%，forbidden claim 0%，p95 820ms，max cost 0.006 美元。

Mutation：`verdict=FAIL`，exit code 1；retrieval recall/precision 50%，citation 20%，forbidden claim 100%，并列出幻觉、检索污染、引用缺失、拒答失守、错误工具、latency 和单请求 cost gate 失败。保存于 `lab/reports/mutation.json`。
