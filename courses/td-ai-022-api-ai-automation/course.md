# AI时代接口自动化：从契约到可审计门禁

## 一句话结果

学员会把一份 OpenAPI 变成候选测试清单，再用独立 Oracle 检查契约、Schema、权限、业务状态、幂等、异步任务和 SSE 事件；最后用同一份证据链证明 `baseline -> mutation -> repair = 0/1/0`。AI 扩大探索空间，但没有合并权限。

## 学员与前置

目标学员是能读 HTTP/JSON、会运行 Python 测试的测试开发工程师（L2）。前置是状态码、请求头、JSON Schema 基础；不会 Python 的学员可先阅读脚本中的 `service`、`check_schema` 和 `run` 三个函数。默认实验仅使用 Python 3 标准库，无网络、无密钥、无生产数据。

## AI centrality

传统“多写几条 HTTP 请求”会漏掉跨资源状态、重复副作用、异步乱序和流式终态。AI 能从批准的 Spec、需求与失败 trace 生成候选操作、边界与属性，并聚类失败；但生成的断言可能把实现当 Oracle、忽略权限或把 HTTP 202 当业务成功。移除 AI 候选层后，本课的核心问题——如何审查候选、固定独立 Oracle 并把结果送进 fail-closed 门禁——不成立，因此 AI 中心性为 5/5。

## System under test

被测系统是合成的订单取消与支付意图 API，包括同步请求、202 异步任务、SSE 事件流、调用者权限、幂等键和副作用账本。公开包同时提供订单与支付 OpenAPI、checkout 事件、mutation catalog 和 AI 性能 workload。默认实现完全离线，不连接真实支付服务；Spec 生成候选 case，批准的业务规则和事件状态机充当独立 Oracle。

## Baseline and target

传统 baseline 是为每个 endpoint 手写几个请求，只验证状态码和响应字段；它无法稳定证明跨状态行为、consumer 兼容、重复投递、唯一终态或 AI 工具调用副作用。目标状态是从版本化 Spec 生成候选，经独立 Oracle 审查后进入确定性门禁，并保存输入 hash、case ID、mutation ID、退出码和 replay 证据。健康、缺陷、修复三次运行必须稳定得到 `0 / 1 / 0`。

## 架构：九层证据链

```text
OpenAPI / JSON Schema / 事件规则
  -> normalize + operation/state graph
  -> candidate cases（AI 可生成，必须可追溯）
  -> independent Oracle catalog（业务 owner/规则，不从实现反推）
  -> deterministic contract/schema/permission checks
  -> state + idempotency + async/SSE reducers
  -> sandbox service + side-effect ledger
  -> mutation/replay + machine report
  -> CI gate（任一必需门禁失败即停止）
```

普通 JSON 的断言是 `request -> status/header/schema/invariant`；异步和 AI 接口必须扩展为 `submit -> queued -> events/tool calls -> terminal -> side-effect ledger`。OpenAPI 解决形状和协议，不单独证明消费者使用方式、权限、金额守恒或副作用；Pact、状态机和业务 Oracle 是互补层。

## SOP：从 Spec 到门禁

1. 固定 Spec 版本、OAS minor、Schema dialect、环境、seed、测试预算与破坏性 endpoint allowlist。
2. 解析并规范化 `learner-materials/fixtures/` 中两份 OpenAPI，建立 operation graph；生成器只能产生候选，不得写入 required gate。
3. 让独立 Oracle 审查每个候选：来源、前置状态、允许角色、期望状态码、状态转移、幂等语义、事件终态与副作用策略。
4. 先跑契约/schema，再跑权限和业务状态；随后检查重复请求、异步合法转移、SSE 事件顺序和唯一终态。
5. 每次运行保存输入 hash、候选 ID、Oracle 版本、实际结果、mutation ID、退出码和 replay 命令。
6. 用 learner-materials 的 `mutation` 模式注入 SHIPPED 错误接受，确认同一测试变红；再运行 `repair`，不修改 Oracle、不跳过失败。
7. CI 按 `spec -> diff -> contract -> smoke -> state/property -> stream/async/tool -> security/perf -> gate` 顺序执行；任一必需门禁失败即停止。

## 默认实验输入与输出

公开输入位于 `learner-materials/fixtures/` 和 `configs/`，包含订单取消、支付意图、checkout 事件、mutation catalog 与 AI 性能 workload。业务夹具包括 `PAID_NOT_SHIPPED`、`SHIPPED`、owner/non-owner、重复取消、任务状态和重复事件。输出是 `learner-materials/reports/baseline.json`、`mutation.json`、`repair.json`。

## Commands

```bash
cd /Volumes/MACSSD/owen-home/Documents/Codex/2026-08-07/ai-1-2-skill-3-ai-2/outputs/test-development-ai-v2/courses/td-ai-022-api-ai-automation/learner-materials
python3 scripts/api_automation.py baseline --report reports/baseline.json  # exit 0
python3 scripts/api_automation.py mutation --report reports/mutation.json  # exit 1，必须红
python3 scripts/api_automation.py repair --report reports/repair.json      # exit 0
python3 -m unittest discover -s tests -v                                  # exit 0
```

## Metrics and thresholds

教学门禁要求：候选包含 contract/business/permission/idempotency/async/sse 六类；契约 operationId 可解析；响应具备 `status/refund_count/state`；非 owner 必须 403；SHIPPED 必须 409 且无退款；重复请求只能一次副作用；异步状态严格为 `QUEUED -> CANCEL_PENDING -> COMPLETED`；SSE 事件为 `task.accepted -> order.cancelled` 且只有一个 terminal。阈值是教学夹具的可解释门槛，不是生产 SLA；生产阈值应由业务损失、历史分布、权限风险和容量数据决定。

## Failure injection

`python3 scripts/api_automation.py mutation --report reports/mutation.json` 会注入 `MUT-ORDER-SHIPPED-ACCEPTED`，令服务错误接受 SHIPPED 取消。可观察失败必须是进程 `exit 1`、报告状态 `FAIL`，并由 `BUS-SHIPPED-REJECT` 显示 `status expected 409, actual 202`。修复只能恢复实现状态检查，不能调整 Oracle、删除 case 或跳过失败。若 mutation 仍为 exit 0，应立即判定测试资产没有检测力；若输入不足则保持 `BLOCKED/NOT_RUN`，不得伪装成 PASS。

## Human review gate

契约失败表示实现与版本化接口不一致；Schema 失败表示形状或类型不满足；权限失败表示角色越权；业务失败表示状态或不变量错误；幂等失败表示重复请求产生重复副作用；协议失败表示异步或 SSE 事件轨迹非法。AI 质量负责人依据分切片证据阻断合并或批准有期限的 waiver；产品和 API owner 确认状态、权限与副作用 Oracle。AI 可自动运行和比较评测，但不得自动批准例外、降低阈值、接触真实资金或作出发布决定。

## 官方工具适配（static-reviewed / NOT_RUN）

本包没有安装或运行下列工具，以下仅为按官方文档核对过的适配边界：

| 工具 | 适配位置 | 运行状态与边界 |
|---|---|---|
| Schemathesis | 用 OpenAPI 做 property/stateful 生成；把 `case_id`、seed、缩减序列回写 evidence | `static-reviewed/NOT_RUN`；必须 pin 版本并本地验证 OAS dialect，不把文档支持矩阵当运行证据 |
| Pact | 为真实消费者交互增加 consumer/provider contract；与 OAS provider conformance 互补 | `static-reviewed/NOT_RUN`；本夹具没有 broker、真实 consumer 或 provider |
| k6 | 将 checks 作为观测、thresholds 作为失败门禁；补充 p95、TTFT、流式完成时间 | `static-reviewed/NOT_RUN`；本包无压测服务与生产阈值 |
| GitLab CI | 编排 parse/diff/contract/runtime/gate，上传 JSON/JUnit，并以非零退出阻断 merge | `static-reviewed/NOT_RUN`；需由项目管理员配置 protected branch、artifact 和 merge queue 规则 |

## 迁移 SOP

迁移到真实服务时保留 case schema、Oracle ID、状态机、幂等键和 evidence 字段；替换订单状态、角色、事件 envelope、数据隔离、依赖 stub、阈值和 owner。先用隔离租户与 dry-run ledger 验证一条高风险路径，再扩展；不要复制本夹具的订单规则。AI 输入只能是脱敏且批准的 Spec/需求/失败 trace，所有候选在静态校验、sandbox、mutation 和人工审核后才能升级为 required。

## AI-specific failure boundary

AI 生成的 case 可能引用不存在的 operationId、从实现反推 expected、忽略权限、重复已有测试或把 HTTP 202 当业务完成。Schema 通过不等于业务正确；SSE snapshot 不证明真实网络分片；fake async 不证明真实队列；候选数量不证明缺陷发现增益；LLM judge 也不是独立 Oracle。所有候选必须经过静态校验、sandbox、mutation 和人工审查后才能升级为 required gate。

## Learner artifact

学员新增一个“重复 webhook + 取消竞态” case：写出允许状态序列、幂等副作用与签名失败 Oracle；先注入重复副作用让报告变红，再修复并恢复绿。交付 OpenAPI、候选清单、Oracle catalog、三份 JSON 报告、unittest 输出、适配评审记录和验证清单。下一课可接入真实 Pact consumer 与受控 Schemathesis stateful run，但必须重新锁版本、环境、seed 和生产责任边界。

## Evidence status

当前课程状态是 `fixture-tested`：Python 标准库公开包已经从 learner-materials 根目录实际跑出 baseline PASS/exit 0、mutation FAIL/exit 1、repair PASS/exit 0，并通过复制隔离测试。Schemathesis、Pact、k6、GitLab CI、live endpoint、真实模型、真实消费者和生产流量均为 `static-reviewed/NOT_RUN`；这些未运行项不会被描述为 live evidence、容量结论或生产安全证明。

<!-- WAVE1-SPECIALTIES-START -->
## Wave 1 独立专业专项

### TD-PS01 · API 业务契约：从 HTTP 结果到可验证副作用

- 控制问题：怎样证明 202 响应、订单状态、退款账本和事件消费属于同一次合法取消，而不是只证明 HTTP 成功？
- 方法选择：分层使用 HTTP 语义、OpenAPI Schema、领域状态机、副作用账本和 Trace；因为任一单层都无法证明异步资金结果
- 独立 Oracle：响应错误模型与状态码一致；非法状态和非 owner 请求零副作用；同一 Idempotency-Key 的退款计数增量最多一；request trace event ledger 可关联
- Prompt：从 OpenAPI、状态机和账本夹具生成带 source_ref 的四层 API 测试包；未知规则输出 UNKNOWN，冲突输出 BLOCKED
- Failure cycle：baseline → 服务端提交后客户端超时 → repair
- Unknown：目标支付网关幂等窗口、真实账本可查询性和业务延迟阈值

### TD-PS02 · OpenAPI Schema 与属性测试：让坏请求和破坏性变更变红

- 控制问题：怎样证明 Schema 生成的用例具备业务检测力，而不是生成大量合法 JSON？
- 方法选择：Schema 正反例负责结构，属性测试负责不变量，固定 seed 与 shrink 负责复现，mutation 负责检测力；四者职责不能合并
- 独立 Oracle：amount 必须大于零且币种受商户支持；客户只能操作自己的支付意图；过期意图不能确认且状态不变；删除 required 或放宽金额必须杀死 mutation
- Prompt：读取 OpenAPI 和历史缺陷，只输出风险约束、最小正反例、固定 seed 与 mutation 映射；不得把 Schema 通过写成业务通过
- Failure cycle：baseline → 删除 merchant_id required → repair
- Unknown：目标生成器对 OAS dialect 的实现差异和生产商户配置

### TD-PS03 · 契约与集成：事件兼容、租户边界和补偿

- 控制问题：怎样在部署前证明消费者字段兼容，并在运行时证明租户、幂等、死信和补偿没有静默失败？
- 方法选择：消费者契约验证使用字段，AsyncAPI/CloudEvents 固定事件 envelope，权限矩阵验证租户，回放器验证重复乱序，Trace 验证补偿
- 独立 Oracle：provider 变更满足所有活跃消费者；跨租户事件被拒绝且零副作用；重复 event_id 只产生一次支付意图；失败事件进入具名 dead-letter 或补偿终态
- Prompt：根据消费者读取字段、事件规范和策略夹具生成兼容矩阵与回放序列；禁止自动授予权限或更改事件语义
- Failure cycle：baseline → 删除消费者字段 → repair
- Unknown：目标 broker 投递保证、策略引擎版本和补偿 owner

### TD-PS08 · 数据与迁移：Schema 演进、回填、CDC 与回滚对账

- 控制问题：怎样证明迁移前后行数、键、金额、状态语义和 CDC offset 一致，并在部分失败时安全停止或回滚？
- 方法选择：expand-contract 降低兼容风险，约束与 checksum 验证静态完整性，分片回填和高水位验证进度，CDC 对账处理并发变化，影子读比较语义
- 独立 Oracle：主键集合与关键行数按分片守恒；金额汇总和状态语义映射一致；CDC 高水位前后的变更无丢失可容忍去重；旧新读路径差异低于零容忍 blocker
- Prompt：读取 DDL、数据字典、约束、回填计划和 CDC manifest，输出前置检查、分片 Oracle、停机条件、回滚与对账 SQL；不得建议直接 DROP 生产列
- Failure cycle：baseline → 回填跳过一个分片 → repair
- Unknown：目标数据规模、锁等待、复制延迟、业务可接受停机窗口

### TD-PS09 · 性能与容量：到达率、尾延迟、Goodput 与单位成功成本

- 控制问题：怎样在不发生 coordinated omission 的前提下测量队列、TTFT、TPOT、E2E、任务质量与成本，并给出容量而非单次速度？
- 方法选择：open-loop arrival 保持外部到达，closed-loop 诊断单用户上限，分阶段 Trace 定位 queue/model/tool，风险切片阻止均值掩盖，Goodput 将质量安全纳入容量
- 独立 Oracle：到达率与 dropped iterations 可核对；每任务阶段时间相加可解释 E2E；只有质量安全延迟同时合格进入 Goodput；失败重试和工具调用计入 cost_per_success
- Prompt：从 workload、任务切片、SLO 和成本模型生成 open/closed 场景、阶段指标和容量判定；禁止发明通用阈值或忽略失败成本
- Failure cycle：baseline → 工具 fan-out 翻倍 → repair
- Unknown：目标模型硬件、provider 内部队列、真实流量分布和价格

共享 bundle 只复用 runner；页级 manifest、owner、Oracle、Prompt、fault 和证据互不继承。
<!-- WAVE1-SPECIALTIES-END -->
