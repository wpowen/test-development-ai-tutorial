---
status: superseded
superseded_at: 2026-08-16
replacement: human-review/11-测试开发专家全量质量审计与修订计划-2026-08-16.md
reason: 33-page course snapshot; it predates the current 103-page canonical catalog and evidence-governance contract.
---

> **历史快照（已废弃）**：本文只保留修复前缺口的来历，不得作为当前课程、晋级或发布依据。请读取 [`11-测试开发专家全量质量审计与修订计划-2026-08-16.md`](11-测试开发专家全量质量审计与修订计划-2026-08-16.md)。

# 测试开发 × AI 完整方案审计（历史）

审计结论：不通过“完整方案”门禁。当前内容可以作为内部研究样稿和离线实验集合，不能再以“测试开发 × AI 完整课程”“生产可用质量平台”或“从入门到专业级完整体系”对外承诺。

## 方案单元

| 方案单元 | 当前页面 | 已有内容 | 还缺什么 |
|---|---|---|---|
| 需求到发布证据链 | TD-F01、TD-P01～P08 | 需求依据、契约、风险、Oracle、执行归因、离线红绿实验 | Jira/Confluence/Git 真实权限与版本流；评审状态机；真实回写；跨 API/UI/数据/事件追踪；审批、豁免、升级和回滚责任 |
| API 与服务质量 | TD-PS01～PS03、PS09 | OpenAPI、业务副作用、契约、事件、AI 性能指标和离线脚本 | OAuth/mTLS/租户、真实端点、限流与重试、消息队列、最终一致性、Pact/Schemathesis/k6、CI required check、真实清理和回滚 |
| Web、Android、iOS 自动化 | TD-PS04～PS08 | 定位器、业务 Oracle、权限、设备矩阵、自愈约束和离线契约实验 | 真实浏览器、模拟器和真机；签名、系统弹窗、后台恢复；设备农场；Flaky 治理；AI repair precision、false repair、unsafe repair 和人工接受率 |
| 稳定性、性能与 Agent 压测 | TD-PS10～PS12、TD-AP01～AP08 | SLO、Trace、重试风暴、工作负载、指标树、离线压测和 Runbook | 真实 Provider/队列/工具；开放与闭环负载；GPU、KV Cache、连接池和队列饱和；长稳与容量拐点；告警触发、On-call、RTO/RPO、GameDay、灾备和恢复证据 |
| 质量平台集成 | TD-QP01～QP04 | Jira、GitLab、Kubernetes、事件总线、SHA 绑定、幂等和审计的离线状态机 | Webhook 验签；真实 429/5xx；protected branch；K8s RBAC/NetworkPolicy/Admission；不可变证据库；DLQ 运维；真实回写、通知、保留和成本 |
| AI 系统评测与治理 | 目前主要停留在内部课程目录 | LLM、RAG、Agent、Benchmark、CI、漂移等主题标题 | 公开学习路径、独立研究包、数据卡、Holdout、污染与漂移、统计置信度、Judge 校准、安全红队、集成实验、持续评测和版本弃用方案 |

## 完整性结论

现有 33 个公开页面不等于 6 个完整方案。页面层已经有职业问题、材料和局部流程，但方案层尚未完成以下闭环：

`业务结果 → 需求与质量属性 → 架构决策 → 系统/数据/接口设计 → 实现与环境 → 测试评测 → 运行证据 → 安全/性能/可靠性 → 发布回滚 → 运维接管 → 人工批准 → 版本演进`

下一版必须逐方案评审 25 个维度，不能用增加页面或延长正文补偿缺失项。任何维度没有负责人、证据、决策或明确 `not-applicable` 理由，都保持 `partial` 或 `gap`。

## 运行证据

当前最强证据是确定性离线 Fixture 的 `PASS → FAIL → PASS`。它证明部分门禁脚本有检测力，但不证明：

- 真实 Jira、GitLab、Kubernetes、浏览器、Android、iOS 或模型服务已经接通；
- 真实认证、租户、网络、消息、设备、集群、生产数据分布和故障条件已经覆盖；
- 性能阈值、SLO、成本预算、容量余量、RTO/RPO 适用于真实环境；
- 从业者已经批准设计与验收结论。

因此方案级 `execution_status` 最高只能按实际单元分别标记为 `desk-researched` 或 `fixture-tested`，不能写成 `integration-tested`、`live-tested` 或 `production-validated`。

## 架构与决策

每个方案单元还必须补齐六张可渲染、可追溯的架构图：系统上下文、组件责任、运行时序、部署拓扑、数据流、信任边界。每张图都要包含失败路径、证据采集点、人工接管和对应 ADR，不能继续使用“五个节点的装饰图”代替工程设计。

关键 ADR 至少覆盖：默认离线与真实适配器如何分层；AI 可以执行和禁止执行什么；数据如何脱敏、保留和删除；阈值由谁按什么分母批准；失败时如何冻结、降级、回滚；何时需要重新评测和废弃旧版本。

## 缺口与风险

当前最高风险不是“主题不够多”，而是已公开页面与方案成熟度没有分开。用户容易把资料审阅、离线 Fixture、真实集成和生产验证混为一谈。

第二个风险是材料虽存在，但多个专业单元还没有真实环境、真实适配器、运维接管和从业者盲审。继续批量生成正文只会扩大表面完成度，不能提高专业可信度。

第三个风险是运行回执可以被手写。后续必须在 CI 中实际执行命令，保存 stdout/stderr、输入与配置哈希、断言观测值、红灯、修复、绿灯和环境版本；静态 JSON 不作为独立证明。

## 发布门禁

从本次 Skill 升级开始：

- `pilot`：25 个维度完成、六类架构图完成、至少 Fixture 实测、资深测试开发/AI QE 完成评审；
- `public`：在试点条件上增加真实集成环境、从业者批准、安全评审、回滚证据和全部验收门禁通过；
- `production-validated`：必须有真实生产或等价环境的保留回执，不从离线或集成结果推断；
- 每个公开页面都必须追溯到 coverage cell、topic、scenario、仓库物料、精确命令、运行回执、考核和人工 Gate；
- 公开包必须包含哈希固定的 `SOLUTION-MANIFEST.json`，且覆盖全部公开页面。

当前项目尚未生成并通过 `research/solution-architecture.json`。所以下一版 GitHub 和 ChatGPT Site 发布应保持阻断，直到完整方案机器契约通过；现有线上版本只能视为旧版研究预览，不视为新标准下的完整交付。
