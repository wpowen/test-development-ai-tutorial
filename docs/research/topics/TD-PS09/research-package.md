# TD-PS09 · AI 性能指标：TTFT、TPOT、Goodput 与单位成功成本

## Research brief

业务场景是客服 Agent：先检索政策，再生成回答，退款长对话可能查询订单和调用工具。传统性能报告只给 QPS、平均响应时间或单次模型延迟，无法解释长输入、工具 fan-out、队列、首 token、尾延迟、质量和成本的联合变化。AI 变化是模型/工具链路动态放大，性能工作量必须按 task slice 固定；AI 可以辅助生成 workload 和解释曲线，不能选择风险阈值或忽略失败请求成本。工具选型为 k6/到达率、vLLM 或 provider 可见指标、Prometheus histogram 和 Trace；托管服务内部 GPU 指标保持未知。

## Source pack

- vLLM production metrics：<https://docs.vllm.ai/en/stable/usage/metrics/>，提供 queue、TTFT、inter-token latency/TPOT、E2E、token 和 cache 指标；版本/硬件会影响定义。
- NVIDIA GenAI-Perf metrics：<https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_benchmark/genai-perf-README.html>，支持生成式推理性能指标与负载测量；不提供业务成功 Oracle。
- k6 scenarios：<https://grafana.com/docs/k6/latest/using-k6/scenarios/>，区分 closed 与 arrival-rate/open workload；入口负载不等于 Agent 任务容量。
- Prometheus histograms：<https://prometheus.io/docs/practices/histograms/>，支持可聚合分位数；bucket 必须按 SLO 设计。

## Evidence synthesis

事实：TTFT 是到首 token，TPOT/ITL 描述生成节奏，E2E 包含队列、模型、工具和客户端路径；它们不能互换。事实：Goodput 是本地决策指标，只有同时满足任务质量、SLO 和安全条件的任务进入分子；`cost_per_success` 应包含失败、重试和工具放大成本。工程综合：任何 p50/p95/p99 都要带 slice、分母、模型/Prompt/知识库版本、到达率和缓存状态。

传统平均值会掩盖退款长对话尾延迟和高风险失败。AI 变化是动态 tool fan-out、retry 和长上下文使 workload 不再是单一 prompt；工程边界是不能从 vendor 的公开指标推断内部 GPU/KV 状态。失败模式包括 coordinated omission、吞吐上涨但 good-task 下降、重试风暴让成本翻倍、缓存命中掩盖新鲜度问题。当前材料仅为 `static-reviewed`，不包含目标模型运行结果。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| Workload/到达率（输入） | 固定 FAQ/退款长对话 slice、token 长度、到达率、并发、工具比例、缓存和合成数据；保存 workload hash。 |
| 队列与调度（处理） | 记录 admission、queue wait、并发、拒绝、优先级和 backpressure；open-loop 与 closed-loop 分开报告。 |
| Prefill/TTFT（证据） | 记录首 token 时间并按输入 token、队列、模型版本切片；provider 不可见内部字段标 `UNKNOWN`。 |
| Decode/TPOT（证据） | 记录 token gap、TPOT/ITL、输出长度、stream completion 和断流；不把完整响应时间替代阶段指标。 |
| 工具与检索（处理） | 记录 retrieval/tool latency、fan-out、retry、cache state 和失败；结果必须回链 task。 |
| 质量/Goodput（门禁） | 以任务正确、权限/副作用安全、延迟和拒答规则计算 good-task；安全/质量越界优先于速度。 |
| 成本与容量门禁（人工决策） | 汇总 token、工具、重试和成功任务成本；候选进入 Pareto 后由业务/平台 owner 决定适用流量与回退。 |

可执行物料是 AI workload YAML、指标字典、Prometheus bucket 配置、阶段 Trace schema 和容量决策表。先固定基线，再比较路由/批处理，最后做限流、工具超时和队列饱和。

## Manuscript map

用“平均延迟下降但退款长对话 p99 与错误率上升”的反例说明 slice 和 Goodput。页面逐一解释 TTFT、TPOT、E2E、Goodput、`cost_per_success` 的分母，展示 open-loop 与 closed-loop 的差异，并将性能、质量、成本放在同一个 trace。AI 只负责候选 workload/诊断草稿。

## Editorial review

没有给出未经目标系统测量的通用阈值，也没有把 vLLM 指标扩展成所有托管模型的内部真相。保留容量未知、切片、尾延迟、重试和质量底线；“Pareto”作为决策组织方式而非自动选型结论。材料和脚本均标为后续 fixture 路径。

## Validation

当前状态：`desk-researched`，未在目标模型、硬件、provider 或真实客服 workload 上压测。

后续可离线升级为 fixture-tested：`validate_ai_workload.py` 检查 slice、分母和版本 manifest；`replay_stage_timing.py` 生成 queue/TTFT/TPOT/E2E；`compute_goodput_cost.py` 以失败和重试计入成本；`inject_tool_fanout.py` 验证放大告警；`compare_histogram_slices.py` 检查分位数报告。离线 fixture 不能证明生产容量、GPU 利用率或供应商价格。
