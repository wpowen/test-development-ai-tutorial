# TD-AP08 研究包 Editorial review record

## Protected items

- 主题边界：SLO、告警与事故证据，必须围绕 good-task SLI。
- 方法：good-task SLI + multi-window burn-rate incident loop；独立 Oracle 重算 numerator/denominator。
- 必须保留：窗口、burn-rate、owner、止血、恢复和事故样例回流。

## Boundary and command evidence

在 `courses/td-ai-010-agent-load-stability/lab` 执行 `python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP08-lab.json --mode cycle`，已记录 0/1/0。provider=none、model=NOT_RUN；组织 SLO 与生产告警策略未知。

## Editorial review

本记录保护 SLI、告警闭环和成熟度边界；不提供分数，不替代独立审计或发布门禁。
