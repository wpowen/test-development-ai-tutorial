# TD-AP07 研究包 Editorial review record

## Protected items

- 主题边界：长稳、资源漂移与泄漏，必须区分 warmup、steady、recovery。
- 方法：windowed soak + snapshot-diff diagnosis；独立 Oracle 检查窗口完整性和资源斜率。
- 必须保留：资源 slope、cleanup diff、p99、错误重试和 recovery 证据。

## Boundary and command evidence

在 `courses/td-ai-010-agent-load-stability/lab` 执行 `python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP07-lab.json --mode cycle`，已记录 0/1/0。provider=none、model=NOT_RUN；真实平台泄漏未知。

## Editorial review

本记录保护分窗 soak、快照差分和稳定性边界；不提供分数，不替代独立审计或发布门禁。
