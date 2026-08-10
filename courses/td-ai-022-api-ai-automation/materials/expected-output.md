# 结果判读

| run | exit | status | 必看证据 |
|---|---:|---|---|
| baseline | 0 | PASS | 六类候选、所有 Oracle PASS |
| mutation | 1 | FAIL | `BUS-SHIPPED-REJECT`，期望 409、实际 202 |
| repair | 0 | PASS | 同一 case 恢复，输入 hash 与 Oracle 仍可追溯 |

这是离线夹具证据，不是实时服务质量或生产发布证明。
