# TD-PS12 · 稳定性 Runbook：SLO 触发后的冻结、回滚与复盘

## Research brief

业务场景是退款助手质量与延迟同时恶化：高风险退款正确率跌破基线，p95 TTFT 上升，工具调用次数翻倍，而低风险 FAQ 正常。传统做法只看全局平均或让值班人员临时讨论，容易在压力下继续放量、批准越权或回滚不完整。AI 可以生成初版时间线、聚类症状和候选修复，但不能执行生产回滚、批准 Waiver 或关闭事故。工程目标是把 SLO/错误预算、告警分级、版本冻结、只读降级、回滚、切片复验和复盘回流组织成可审计 Runbook；数值阈值必须来自目标业务承诺。

## Source pack

- Google SRE SLO：<https://sre.google/sre-book/service-level-objectives/>，支持 SLI/SLO/SLA 与错误预算关系；不提供本业务阈值。
- Google SRE alerting on SLOs：<https://sre.google/workbook/alerting-on-slos/>，支持 multi-window/multi-burn-rate 起点；参数需要按服务校准。
- Google SRE handling overload：<https://sre.google/sre-book/handling-overload/>，支持 load shedding、队列和过载保护。
- OpenTelemetry context：<https://opentelemetry.io/docs/specs/otel/context/api-propagators/>，支持 Trace/baggage 跨边界传播；不能替代事故决策记录。
- Principles of Chaos Engineering：<https://principlesofchaos.org/>，支持隔离实验、稳态假设和恢复复验。

## Evidence synthesis

事实：SLO 触发器只有在分母、窗口、风险切片、owner 和动作明确时才可操作。事实：高风险退款正确率不能被全局 FAQ 平均掩盖，越权工具调用和副作用风险应先于性能优化。工程综合：一次事故必须保存告警快照、Trace、版本账本、操作人、命令/变更、时间线、回滚结果和未解决风险，并把确认失败转为 API/UI/Eval 回归。

AI 变化是诊断摘要和复盘初稿更快；工程边界是冻结、只读、回滚和 Waiver 仍需人工授权。失败模式包括错误分母、误报导致无意义回滚、回滚漏掉 Prompt/知识库/工具版本、恢复洪峰、到期豁免不失效和复验只跑低风险 slice。当前 Runbook、GameDay 和阈值表均为 static-reviewed。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| SLO/错误预算（输入） | 输入高风险任务成功率、工具政策、p95 延迟、可用性、成本、分母和窗口；版本化并写明未知项。 |
| 告警与事故分级（门禁） | 按 Page/Ticket/Dashboard-only 分级，绑定 owner、动作、影响 slice 和是否阻断；缺分母不触发自动结论。 |
| 版本冻结（处理） | 冻结模型、Prompt、知识库、工具 schema、配置和最近部署；保存完整 Manifest，避免只冻结模型。 |
| 只读/降级（处理/证据） | 关闭高风险写工具，切只读、限流或安全 fallback；用轨迹确认无越权和用户影响停止扩大。 |
| 回滚与配置恢复（处理） | 恢复已知良好版本与路由/flag，记录操作人、时间、命令、依赖和回滚失败；禁止部分回滚假装完成。 |
| 切片回归复验（证据/门禁） | 用相同 Manifest 加一个未见 slice，验证质量、延迟、工具政策、队列、成本和 Trace completeness。 |
| 复盘与质量资产（人工决策） | 区分触发原因、放大因素、检测缺口、恢复缺口；owner 批准新增测试、阈值、Runbook 或 Waiver。 |

可执行物料是退款助手 Runbook、SLO 决策表、版本冻结清单、只读降级策略、GameDay 记录和事故复盘模板。演练顺序是告警确认、冻结、只读、回滚、连续窗口复验、回流。

## Manuscript map

从高风险切片恶化但全局平均正常的事故时间线开场。随后用决策表说明越权、质量、延迟三类触发如何采取不同动作，强调完整 Manifest 与 partial rollback 的风险。页面给出一次“只读降级→回滚→切片复验→新增回归”的具体记录格式，并把 AI 限定为摘要/候选修复。

## Editorial review

没有发明通用 SLO 数值，也没有把 Google SRE 的 alerting 模式写成组织现成政策。保留人工 owner、Waiver 到期、恢复洪峰、未见 slice 和版本账本等容易被遗漏的边界。Runbook 是可执行设计，不是已在生产值班系统完成的证明。

## Validation

当前状态：`desk-researched`，未在真实生产、Kubernetes、告警系统或值班流程执行回滚/演练。

后续可离线升级为 fixture-tested：`validate_runbook_manifest.py` 检查分母、owner、动作和版本；`simulate_slo_breach.py` 生成高风险质量/延迟告警；`freeze_manifest_fixture.py` 检查模型、Prompt、知识库和工具一起冻结；`replay_readonly_rollback.py` 验证无写工具轨迹；`run_slice_regression.py` 检查复验含新增 slice；`expire_waiver_fixture.py` 验证豁免自动失效。离线结果不能证明生产恢复耗时、告警可靠性或人员协作效果。
