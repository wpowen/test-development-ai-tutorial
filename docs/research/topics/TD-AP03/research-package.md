# TD-AP03 研究包 Editorial review record

## Protected items

- 主题边界：Trace 语义与因果证据，必须覆盖 task root、generation、tool、attempt、handoff、finalize。
- 方法：causal trace reconstruction + schema-closure audit；独立 Oracle 检查 root closure。
- 必须保留：parent_id、schema version、脱敏状态和缺证据原因。

## Boundary and command evidence

在 `courses/td-ai-010-agent-load-stability/lab` 执行 `python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP03-lab.json --mode cycle`，已记录 0/1/0。provider=none、model=NOT_RUN；provider 默认 trace 完整性未知。

## Editorial review

本记录保护 Trace 因果链、隐私边界和方法理由；不提供分数，不替代独立审计或发布门禁。
