# 快速开始

从 `learner-materials/` 根目录执行三条实验命令：baseline、fault、repaired：

```bash
cd learner-materials
python3 scripts/reliability_lab.py --config configs/baseline.json --output evidence/baseline
python3 scripts/reliability_lab.py --config configs/fault.json --output evidence/fault; test $? -eq 1
python3 scripts/reliability_lab.py --config configs/repaired.json --output evidence/repaired
```

它们分别应退出 0、1、0，并在对应目录保存 `summary.json` 与 `traces.jsonl`。实验使用虚拟时间，运行很快且无网络。

阅读顺序是 `task_success_rate` → `queue_p95_ms`/`e2e_p95_ms` → `retry_amplification`/`call_amplification` → `cost_per_success`。exit 1 表示门禁正确检测故障，不表示脚本自身失败。
