# Agent 测试架构维度文档

> 本目录是 `methodology/dimensions/agent-testing-architecture/` 的学习者投影，内容与仓库正文同源。

| 文件 | 内容 |
| --- | --- |
| [00-research-and-adjudication.md](00-research-and-adjudication.md) | 五个失效点、v1→v2 结构变更、证据分级与数值使用纪律 |
| [01-architecture-overview-8-domains.md](01-architecture-overview-8-domains.md) | 8 域 36 维完整明细、域间依赖、不适用情况、最小起步 |
| [02-d0-evaluation-trust.md](02-d0-evaluation-trust.md) | judge 校准七步、三类偏置探针、Judge Card、混合范式 |
| [03-d1-single-agent-capability.md](03-d1-single-agent-capability.md) | span 四类标签、首错位置、步骤效率比、无效循环率、三层 Oracle |
| [04-d2-orchestration.md](04-d2-orchestration.md) | handoff 契约、信息衰减链路、职责边界矩阵、三重熔断 |
| [05-d3-human-agent-interaction.md](05-d3-human-agent-interaction.md) | 中断、接管、确认疲劳、可解释 ≠ 可控 |
| [06-d4-reliability-distribution.md](06-d4-reliability-distribution.md) | pass@k / pass^k 数学、Wilson 聚类区间、horizon 衰减、统计回归 |
| [07-d5-security-adversarial.md](07-d5-security-adversarial.md) | 六类攻击面矩阵、MCP 投毒与 rug-pull、信任边界、爆炸半径 |
| [08-d6-efficiency-economics.md](08-d6-efficiency-economics.md) | 成本长尾、P99、单位成功成本、可复现五要素 |
| [09-d7-business-governance.md](09-d7-business-governance.md) | 四维版本、哨兵集、审计证据链、ROI 的诚实算法 |
| [10-four-ring-execution-model.md](10-four-ring-execution-model.md) | 环 1–4 的触发、覆盖、门禁性质与环间不可冒充 |
| [11-three-stage-gate.md](11-three-stage-gate.md) | 硬红线 / 统计门禁 / 风险接受三段判定 |
| [12-high-risk-adapter.md](12-high-risk-adapter.md) | 交易与金融场景五条落地要点与爆炸半径具体化 |
| [13-migration-roadmap.md](13-migration-roadmap.md) | P0 止血 → P4 常态化，各阶段准出与失败信号 |
| [14-evidence-boundary.md](14-evidence-boundary.md) | 本维度成熟度声明、未运行清单、引用时的正确表述 |

## 配套可运行工件

```bash
python3 scripts/agent_reliability_lab.py list-gates     # 六个可计算门禁
python3 scripts/agent_reliability_lab.py list-faults    # 十一类可注入故障
```

模板位于 `templates/`，夹具位于 `fixtures/`，Prompt 包位于 `prompts/AG-DIM/`，维度级设计图位于 `visuals/AG-DIM-*.svg`。

## 证据边界

全部内容成熟度为 `fixture-tested`（L1）。真实模型、真实 Agent、MCP/工具/队列/交易后端、
影子与在线环、从业者评审与生产效果均 `NOT_RUN`。所有阈值为结构占位，必须按你的业务实测重设。
