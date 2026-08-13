# TD-AP01 研究包 Editorial review record

## Protected items

- 主题边界：工作负载模型与任务终态，不外推生产容量。
- 方法：workload modeling + task-oracle decomposition；独立 Oracle 不读取 evaluator verdict。
- 必须保留：task 分母、tool path、allowed terminal state、Evidence/Inference/Unknown 分类。

## Boundary and command evidence

在 `courses/td-ai-010-agent-load-stability/lab` 执行 `python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP01-lab.json --mode cycle`，已记录 baseline/fault/repair=0/1/0。provider=none、model=NOT_RUN；live、practitioner、production capacity 均未知。

## Editorial review

本记录只保护主题专属性、方法理由、命令可复现性和成熟度边界；不提供分数，不替代独立审计或发布门禁。
