# TD-AP02 研究包 Editorial review record

## Protected items

- 主题边界：TTFT、TPOT、Queue、Retry 与 Step 指标树，不把 request 指标冒充 task 结果。
- 方法：metric-tree decomposition + denominator audit；独立 Oracle 从原始事件重算。
- 必须保留：分母、风险切片、聚合方式、good-task 与尾延迟。

## Boundary and command evidence

在 `courses/td-ai-010-agent-load-stability/lab` 执行 `python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP02-lab.json --mode cycle`，已记录 0/1/0。provider=none、model=NOT_RUN；组织阈值与真实模型未知。

## Editorial review

本记录保护指标树的主题专属性、独立重算和证据边界；不提供分数，不替代独立审计或发布门禁。
