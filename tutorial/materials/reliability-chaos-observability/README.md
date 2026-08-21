# AI 服务稳定性、故障注入与可观测性：学员材料

本目录从自身根目录即可运行，唯一运行时是 Python 3 标准库，不需要安装第三方包或联网。脚本用虚拟时间模拟 retrieval、model、read-only tool、队列、重试和成本；报告是教学证据，不是生产容量证明。

## 运行

```bash
cd learner-materials
python3 scripts/reliability_lab.py --config configs/baseline.json --output evidence/baseline
python3 scripts/reliability_lab.py --config configs/fault.json --output evidence/fault; test $? -eq 1
python3 scripts/reliability_lab.py --config configs/repaired.json --output evidence/repaired
python3 scripts/verify_learner_materials.py
```

预期退出码为 `0/1/0`：baseline PASS，fault 有意 FAIL，repaired PASS。每个输出目录保存可解析的 `summary.json` 与逐任务 `traces.jsonl`。故障 exit 1 是门禁检测到问题，不是脚本运行错误。

## 材料地图

- `fixtures/order-assistant-chaos.yaml`：合成订单助手、oracle、故障和观测字段。
- `fixtures/stability-gameday-report.yaml`：授权、停止条件、比较指标和证据状态模板。
- `configs/agent-trace-schema.yaml`：task 根 Trace 与 retrieval/model/tool/retry 字段。
- `guides/chaos-experiment-sop.md`：真实演练前后的授权、停止、回滚与证据要求。
- `guides/ai-observability-investigation.md`：从任务、队列到 Trace、质量、成本的调查顺序。
- `guides/refund-agent-runbook.md`：退款 Agent 的只读/沙箱故障分流 runbook。

## 生产边界

K8s/Chaos Mesh 仍是 `static-reviewed / NOT_RUN`；本目录没有执行 `kubectl`、Chaos Mesh、真实模型、真实工具、生产流量或真实退款。学员必须获得授权、替换 selector/环境/回滚命令并由负责人复核后，才能在隔离环境做真实实验。

<!-- WAVE1-OWNERS-START -->
## Wave 1 独立专项与 Owners

- TD-PS10 · 稳定性：超时、重试预算、熔断、限流与降级 · manifest: `manifests/TD-PS10.json` · owners 见 `owners.json`
- TD-PS11 · 可观测性与混沌：Trace 完整性、受控注入和恢复证据 · manifest: `manifests/TD-PS11.json` · owners 见 `owners.json`
- TD-PS12 · 安全测试：身份、授权、输入、秘密与跨租户副作用 · manifest: `manifests/TD-PS12.json` · owners 见 `owners.json`

逐页运行：

```bash
python3 scripts/specialty_lab.py --manifest manifests/TD-PS10.json --mode cycle
python3 scripts/specialty_lab.py --manifest manifests/TD-PS11.json --mode cycle
python3 scripts/specialty_lab.py --manifest manifests/TD-PS12.json --mode cycle
```

共享 runner 只执行 manifest；不得把一个页面的 Oracle、Prompt、fault 或 PASS 传播到其他页面。
<!-- WAVE1-OWNERS-END -->
