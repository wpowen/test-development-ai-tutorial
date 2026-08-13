# Agent 性能与稳定性：完整离线实验包

本包覆盖 TD-AP01～TD-AP08：工作负载模型、指标树、Trace 语义、开放/封闭负载、容量与瓶颈、超时/重试/降级、长稳/泄漏、SLO/告警/事故证据。

## 运行

从站点公开材料根目录进入：

```bash
cd materials/agent-load-stability
python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP01-lab.json --mode cycle
```

把 `TD-AP01` 换成 `TD-AP02`～`TD-AP08` 可运行其余专题。每个 cycle 实际执行 baseline、fault、repair，预期阶段退出码为 `0/1/0`，cycle 自身在模式匹配时退出 `0`。

兼容旧版单场景材料仍保留 `agent_load_lab.py`、`configs/baseline.json`、`configs/retry-storm.json`、`configs/repaired.json`；其独立阶段同样预期 `0 / 1 / 0`。新版八页教学以 `scripts/agent_performance_lab.py` 与逐页 manifest 为准。

## 目录

- `profiles/`：版本化 workload、gate 与 mutation。
- `manifests/`：精确命令、cwd、required files、退出码和工件。
- `prompts/`：每页 Prompt/Input/Schema/Eval/Mutation v1.0.0；provider=none、model=NOT_RUN。
- `guides/`：逐页阅读顺序、排错和停止条件。
- `reports/`：已保存的三阶段 Trace、摘要、cycle 与总 execution evidence。

## 证据边界

这是 deterministic synthetic fixture，只证明本包的采集、故障检测和修复门禁可运行。它没有调用真实模型或生产工具，没有 practitioner review，也不代表生产容量、SLA 或供应商性能。
