# Agent 负载与重试风暴离线实验

这个实验用本地模拟器演示三件事：正常负载能满足 SLO；无边界重试会放大调用量并触发成本、尾延迟和成功率门禁；限制重试、增加退避和并发保护后恢复。

不需要 API Key，也不会访问生产服务。

```bash
python3 agent_load_lab.py --config configs/baseline.json --output reports/baseline
python3 agent_load_lab.py --config configs/retry-storm.json --output reports/retry-storm
python3 agent_load_lab.py --config configs/repaired.json --output reports/repaired
```

预期退出码为 `0 / 1 / 0`。不要只看 RPS；同时比较成功任务数、p95、每个成功任务的模型调用数、重试放大系数和预算消耗。

脚本会自动创建每个输出目录，并写入 `summary.json` 与 `traces.jsonl`。

教学脚本模拟的是可控依赖，不代表某个模型供应商或真实 Agent 平台的容量。迁移到真实系统时，需要替换请求适配器、工作负载、价格、SLO 和 Trace 采集。
