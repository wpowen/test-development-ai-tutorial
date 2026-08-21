# TD-AP06 研究包 Editorial review record

## Protected items

- 主题边界：超时、重试、降级与副作用安全终态。
- 方法：deadline propagation + retry-budget state machine；独立 Oracle 检查预算、幂等和副作用类别。
- 必须保留：deadline、attempt budget、read-only/人工/对账终态和 retry-storm mutation。

## Boundary and command evidence

在 `courses/td-ai-010-agent-load-stability/lab` 执行 `python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP06-lab.json --mode cycle`，已记录 0/1/0。provider=none、model=NOT_RUN；真实写操作与生产策略未知。

## Editorial review

本记录保护预算传播、降级边界和人工责任；不提供分数，不替代独立审计或发布门禁。
