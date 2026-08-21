# TD-AP05 研究包 Editorial review record

## Protected items

- 主题边界：容量曲线与瓶颈归因，只形成 synthetic capacity curve。
- 方法：step-load experiment + first-failing-gate attribution；独立 Oracle 重算首个失效级别。
- 必须保留：固定步长、queue/prefill/decode/tool/retry 切片、阈值和控制变量。

## Boundary and command evidence

在 `courses/td-ai-010-agent-load-stability/lab` 执行 `python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP05-lab.json --mode cycle`，已记录 0/1/0。provider=none、model=NOT_RUN；不得声明生产容量。

## Editorial review

本记录保护瓶颈归因、控制变量和 synthetic 边界；不提供分数，不替代独立审计或发布门禁。
