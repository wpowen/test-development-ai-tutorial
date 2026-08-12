# TD-AP08 SLO 告警事故实验指南

## 目标

先读 good-task SLI，再看 alert action 与 incident evidence；fault 会让症状不可处置。

## 工作目录

`materials/agent-load-stability`

## 三阶段

```bash
python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP08-lab.json --mode baseline
python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP08-lab.json --mode fault
python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP08-lab.json --mode repair
python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP08-lab.json --mode cycle
```

预期退出码分别为 0、1、0、0。fault 的非零退出是检测力证据，不要通过删除 gate 修复。

## 阅读顺序

1. 核对 profile、workload_version 与 configuration_hash。
2. 比较 baseline/fault/repair 的 checks 与 metrics。
3. 打开 fault/traces.jsonl，定位一条导致红灯的任务。
4. 查看 cycle-summary.json 的 fault_detected_by 与 repair_comparison。
5. 写 Evidence / Inference / Unknown，并保留边界：这是 synthetic fixture，不是生产容量。

## 停止条件

缺 manifest、缺输入、fault 未被拒绝、repair 未恢复、配置 hash 不一致或边界缺失时停止并标记 BLOCKED。

