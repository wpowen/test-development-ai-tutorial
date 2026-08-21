# TD-AP04 研究包 Editorial review record

## Protected items

- 主题边界：开放/封闭负载模型与 coordinated omission，不把两种执行器压成一个吞吐数字。
- 方法：open-vs-closed controlled comparison；独立 Oracle 判断任务终态与 queue evidence。
- 必须保留：offered rate、achieved rate、queue、p99 和调度器声明。

## Boundary and command evidence

在 `courses/td-ai-010-agent-load-stability/lab` 执行 `python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP04-lab.json --mode cycle`，已记录 0/1/0。provider=none、model=NOT_RUN；生产负载选择未知。

## Editorial review

本记录保护负载模型对比和 omission 边界；不提供分数，不替代独立审计或发布门禁。
