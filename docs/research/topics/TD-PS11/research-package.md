# TD-PS11 · 线上可观测性：把 AI 质量、Trace、成本和 SLO 接成一条链

## Research brief

业务场景是生产客服 Agent：高风险退款正确率下降，但 Judge 分数未变。可能原因是知识库索引过期、输入分布变化、工具错误、Judge 漂移或观测丢失。传统做法只看平均延迟和模型日志，无法把用户任务、检索版本、tool span、token 成本、质量切片和发布版本关联；过度采集又会泄露 PII/凭证。AI 可以总结 Trace、聚类症状和生成调查问题，不能删除证据、静默换 Judge、放宽阈值或自动回滚。工具选型为 OpenTelemetry + Prometheus/日志 + 版本 Manifest，GenAI semconv 仍需按版本核对。

## Source pack

- OpenTelemetry signals：<https://opentelemetry.io/docs/concepts/signals/>，定义 traces、metrics、logs 等信号边界；采集到不等于数据合规。
- OpenTelemetry GenAI semantic conventions：<https://opentelemetry.io/docs/specs/semconv/gen-ai/>，提供 GenAI 观测字段方向；页面仍演进，不应当作跨厂商稳定 schema。
- OpenTelemetry Collector 官方仓库：<https://github.com/open-telemetry/opentelemetry-collector>，支持 telemetry pipeline 组件；不提供业务质量 Oracle。
- W3C Trace Context：<https://www.w3.org/TR/trace-context/>，支持跨 HTTP 边界的 trace context 传播。
- Google SRE monitoring：<https://sre.google/sre-book/monitoring-distributed-systems/>，支持 golden signals、黑盒/白盒监控和分层观察。

## Evidence synthesis

事实：一个可诊断的 AI Trace 至少要能关联 task/request/trace、模型/Prompt/Scorer/知识库版本、风险 slice、检索 IDs、工具摘要、阶段延迟、token、终态和人工结果。事实：trace completeness 本身是可靠性指标；没有 Trace 不能把“无异常”写成“质量正常”。工程综合：敏感数据采用最小化、哈希、脱敏、访问控制和保留期限，默认 Dashboard 不放原文/凭证。

AI 变化是日志摘要和异常聚类加速，但工程边界是 AI 只能提出假设，必须保存 confirming 与 disconfirming evidence。失败模式包括 Judge 分数稳定掩盖真实错误、cardinality 爆炸、PII 入日志、collector 失联、版本字段缺失、成本因重试被隐藏。页面不宣称已接入生产 telemetry。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| 用户请求/风险切片（输入） | 记录 task/request ID、风险等级、输入分布摘要、租户和脱敏规则；不默认保存原文。 |
| Gateway 与 Trace（处理） | 传播 trace context，生成 manifest、model/prompt/scorer/index 版本和采样决策；缺 trace 标记不完整。 |
| 模型/检索/工具 Span（处理） | 记录检索 IDs、工具名/参数摘要、阶段延迟、错误分类和重试；敏感参数只存 hash/分类。 |
| 日志与指标（证据） | 分层记录任务成功、拒答、TTFT/p95、token、cost、检索 freshness、tool policy 和 completeness。 |
| 质量/成本评测（处理/门禁） | 按风险 slice 做人工/Judge/引用/业务 Oracle 对照；Judge drift 或分母改变不得静默通过。 |
| 告警与版本冻结（门禁） | 告警包含分母、窗口、owner、动作和阻断性；高风险异常先冻结完整 Manifest。 |
| 回归集与发布门禁（人工决策） | 脱敏失败样例进入回归；owner 决定回滚/修复/豁免，保留操作和证据，不由 AI 自动关闭。 |

可执行物料是 Agent Trace schema、脱敏策略、Dashboard 字段表、告警样例、调查树和回归 case。诊断固定为 symptom→hypothesis→evidence→controlled rerun。

## Manuscript map

以“Judge 没变、退款正确率下降”展示单指标监控的盲区。页面逐层构造最小 Trace，解释版本、检索、工具、性能、成本与业务结果的关联，并展示 PII/凭证不得进默认 Dashboard。最后给出告警到冻结、调查、回归回流的闭环，AI 只做聚类和调查草稿。

## Editorial review

明确区分 OTel 信号、GenAI 字段草案和业务质量 Oracle；没有把 span 数量或 Judge 分数写成质量证明。保留 semconv 演进、敏感数据、collector 失联和托管模型内部不可见字段的未知状态。字段设计和调查流程为 static-reviewed。

## Validation

当前状态：`desk-researched`，未接入生产 Collector、Dashboard、真实 Trace、PII 审批或告警系统。

后续可离线升级为 fixture-tested：`validate_agent_trace_schema.py` 检查必填字段和版本；`redact_trace_fixture.py` 检查邮箱、电话、凭证和支付原文不出现在默认输出；`propagate_trace_context.py` 模拟 gateway/tool 关联；`compute_trace_completeness.py` 统计缺失 span；`replay_alert_fixture.py` 验证高风险切片告警能冻结版本并生成回归 case。离线测试不能证明生产采样、权限和吞吐表现。
