# TD-PS10 · 故障注入：从单点失败到重试风暴与级联故障

## Research brief

业务场景是订单 AI 助手：可以查订单和解释退款政策，但没有二次确认不得退款。传统做法只测依赖正常时的成功路径，或在没有授权、blast radius 和停止条件时随机打坏环境。AI 可以从 Trace 提出工具超时、429、检索空结果和重试风暴实验候选，不能向生产注入故障、修改停止阈值或判断资金副作用安全。工程目标是用 Chaos Experiment Card 把假设、单变量注入、SLI、副作用 Oracle、恢复和复验接起来；工具选型为 Chaos Mesh/Kubernetes、Toxiproxy、k6 和受控 provider gateway。

## Source pack

- Principles of Chaos Engineering：<https://principlesofchaos.org/>，支持 steady-state hypothesis、真实变量、blast radius 和持续实验；原则不是目标系统恢复证明。
- Chaos Mesh Pod faults：<https://chaos-mesh.org/docs/simulate-pod-chaos-on-kubernetes/>，支持 Pod 级故障实验；selector、CRD 和权限必须按集群版本验证。
- Chaos Mesh network faults：<https://chaos-mesh.org/docs/simulate-network-chaos-on-kubernetes/>，支持 delay、loss、partition 等网络变量；不涵盖全部节点/GPU 故障。
- Google SRE cascading failures：<https://sre.google/sre-book/addressing-cascading-failures/>，支持 deadline、队列、重试放大和级联控制。
- Toxiproxy 官方仓库：<https://github.com/Shopify/toxiproxy>，适合测试环境的 TCP 延迟、断连和超时注入。

## Evidence synthesis

事实：故障实验必须先定义稳态、授权、blast radius、停止条件、观察人、回滚和清理；否则实验本身不可审计。事实：多层各重试会产生乘法放大，最终成功率尚可也不能掩盖队列、成本和副作用恶化。工程综合：验证顺序是健康基线、单变量故障、传播指标、立即恢复、同 Manifest 回归。

AI 变化是实验设计和诊断候选更快，但不会替代授权和实时止损。失败模式包括工具超时后越权退款、429 无限重试、队列无界、重复消息、错误 Feature Flag、残留数据和恢复后观测仍失联。真实 K8s/生产未运行，所有实验物料是 static-reviewed。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| 实验授权/隔离命名空间（输入/门禁） | 输入 owner、目标 selector、合成账户、blast radius、开始/停止条件和回滚命令；缺任一关键字段保持 `BLOCKED`。 |
| 注入器（处理） | 只注入一个变量：工具 timeout、provider 429、检索空结果、网络 delay 或非关键 Pod kill；记录 fault start/end。 |
| 模型/工具/检索依赖（处理） | 返回可分类 transient/permanent/overload/policy 结果，保留 Retry-After、错误 schema 和调用次数。 |
| Agent 重试与降级（门禁） | 验证 bounded retry、jitter、retry budget、只读 fallback、max steps 和 policy stop；越权/无限重试直接红。 |
| 订单 API/队列（证据） | 检查 admitted task、queue、订单状态、死信和副作用计数；验证没有真实退款。 |
| SLI/Trace/副作用（证据） | 保存错误率、延迟、good-task、retry/call amplification、trace、注入事件和恢复时间。 |
| 自动停止与回滚（人工决策） | 触发 stop_if 自动恢复；授权负责人确认清理、复验和是否新增门禁，AI 不可自行关闭实验。 |

可执行物料是订单助手实验卡、Chaos YAML、provider fault map、stop condition、恢复清单和复盘报告。先做工具 timeout，再做 429/重试风暴，最后才考虑级联。

## Manuscript map

从“助手返回解释成功但实际调用退款工具”的单点失败开始，介绍实验卡字段和隔离门禁。随后解释重试反馈环、队列、降级、副作用 Oracle 和 Trace。页面应对比单变量与级联实验、基线与修复后同一回归集，并明确未运行 K8s 时只能审查设计。

## Editorial review

没有把 Chaos Mesh 文档能力写成目标服务已恢复，也没有提供可直接指向生产的破坏性命令。每个实验有停止、回滚、清理和人工授权边界；保留工具 timeout、429、网络和 Pod 故障的适用范围差异。结论不超出 desk research。

## Validation

当前状态：`desk-researched`，未在 K8s、Chaos Mesh、生产 provider 或真实订单助手执行故障注入。

后续可离线升级为 fixture-tested：`validate_chaos_card.py` 检查授权、blast radius、stop_if 和 rollback；`simulate_retry_storm.py` 计算调用/重试放大；`assert_read_only_fallback.py` 检查工具超时不产生退款；`replay_recovery_manifest.py` 比较注入前后 SLI；`check_cleanup_fixture.py` 检查队列、flag 和合成数据清理。离线结果不能证明真实集群恢复时间或节点故障韧性。
