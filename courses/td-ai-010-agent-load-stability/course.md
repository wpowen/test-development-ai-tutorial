# AI Agent 性能与稳定性工程

本课把一次用户任务而不是一条 HTTP 请求作为工作单元。学习者会连接入口、队列、模型、检索、工具、状态、重试、终态和成本，形成能用于压测、诊断与生产监控的同一条证据链。

## AI centrality

被测对象本身就是 Agent：模型会动态决定工具、步骤、重试和 handoff。同样数量的用户任务可能产生完全不同的模型与工具调用量。HTTP 200、模型调用成功或低平均延迟都不能证明业务任务成功，因此必须引入轨迹、任务 verifier、Token、成本和副作用检查。

## System under test

统一场景是订单异常处置 Agent：读取任务，调用模型分类，查询订单，必要时执行退款，并写入最终状态。离线夹具用确定性时延和失败率模拟模型与工具，不接触真实资金。根 Trace 表示 task run，子 Span 表示模型、工具、attempt 和时间边界。

## Baseline and target

传统压测关注流量、延迟、错误和饱和度，这些原则继续保留。Agent 目标增加 task success、step/tool 分布、retry amplification、cost per success 和 goodput。目标不是得到一个脱离上下文的“最大并发”，而是在固定 workload、版本、到达模式和 SLO 下找到最大可持续 goodput。

## Commands

在本课程目录执行三阶段实验：

```bash
python3 lab/agent_load_lab.py --config lab/configs/baseline.json --output evidence/baseline
python3 lab/agent_load_lab.py --config lab/configs/retry-storm.json --output evidence/retry-storm
python3 lab/agent_load_lab.py --config lab/configs/repaired.json --output evidence/repaired
```

预期退出码依次为 `0 / 1 / 0`。第二步非零不是课程失败，而是故障注入能被门禁发现。

## Metrics and thresholds

报告先检查任务成功率，再检查 E2E p95 与 queue p95，然后下钻重试放大、调用放大和单位成功成本。Goodput 只统计正确完成且满足时延与成本预算的任务。教学阈值用于证明门禁机制，不能复制到生产；生产阈值需要从业务损失、用户 SLO、历史分布和容量实验共同推导。

## Failure injection

`retry-storm.json` 同时减少 worker、提高到达率、增加工具时延与失败率，并允许最多五次工具尝试。预期结果是排队和 E2E 尾延迟上升、retry amplification 超限、Goodput 下降，进程以 exit 1 结束。若它仍然 exit 0，说明负载、注入或阈值没有检测力。

## Human review gate

测试负责人必须确认 workload 是否代表目标流量，业务负责人必须确认终态与副作用 Oracle，平台负责人确认限流、费用和资源预算。AI 可以聚合 Trace 和提出候选根因，但不得自动降低阈值、批准例外或放行涉及资金的 Agent。

## AI-specific failure boundary

模型与工具可能分别成功而任务失败；重试可能提高最终成功率却扩大排队与成本；降级可能保持可用性却降低质量或扩大权限。任何结论都要保留 model、prompt、workflow、tool schema、workload、价格和阈值版本。OpenTelemetry GenAI 约定仍在演进，自定义字段应使用业务命名空间而不是臆造标准字段。

## Learner artifact

学习者交付指标字典、workload model、Trace Schema、三阶段 summary/JSONL、故障诊断记录和生产 SLO/Runbook。工件必须能从告警下钻到 Trace、版本和失败步骤，也必须能把事故样例回流到离线回归。

## Evidence status

三阶段离线夹具已经运行，退出码为 0/1/0。它证明脚本、采集、聚合、故障注入和门禁逻辑可以复现；没有调用真实模型、真实工具、GPU 服务或企业生产流量，不构成容量、费用、质量或稳定性生产证明。

## Transfer

迁移到其他 Agent 时，保持 task 作为分母、四层指标树、Trace 关联、红绿证据和人工权限边界；替换任务切片、允许终态、工具副作用、到达分布、价格表和业务阈值。先在沙箱验证一条高风险路径，再扩大到完整工作负载。
