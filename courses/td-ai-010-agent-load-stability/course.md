# AI Agent 性能与稳定性工程

本课把“一项用户任务是否以正确、及时、安全、可控成本结束”作为性能与稳定性的核心工作单元。入口 HTTP 2xx、单次模型成功和最大并发都不能替代任务证据。

## AI centrality

移除 AI 后，本课的被测对象不再存在：Agent 的任务终态、模型生成、工具路径、上下文长度、重试与轨迹共同决定性能和稳定性。传统压测仍保留，但必须按 task、step、tool、retry 和风险切片观察，而不是只看入口请求。

## System under test

被测对象是订单异常处置 Agent 的离线合成版本：工作负载经过到达调度、模型/工具模拟、任务终态和 task-rooted trace，再进入版本化 evaluator。真实模型、资金工具、生产流量和组织 SLO 不在本夹具边界内。

## Baseline and target

基线只看 HTTP 2xx、平均延迟和最大并发；目标是用 workload version、业务终态、队列/尾延迟、重试成本、资源斜率和完整 trace 支撑放行或阻断。目标只证明 fixture 的证据链可复现，不推导生产容量。

## 完整学习链

1. **TD-AP01 工作负载模型**：用 task type、token bucket、tool path、allowed terminal state、failure mix 和 provenance 建联合分布。
2. **TD-AP02 指标树**：连接 queue、TTFT、TPOT/ITL、E2E、retry、step、task success 与 goodput。
3. **TD-AP03 Trace 语义**：一项 task 一个 root，generation/tool/attempt/handoff/finalize 为子证据；锁定语义版本与隐私策略。
4. **TD-AP04 开放/封闭负载**：用 open arrival rate 观察容量与排队，用 closed concurrency 观察受限用户；识别 coordinated omission。
5. **TD-AP05 容量与瓶颈**：阶梯加压，报告第一个门禁失效点和 synthetic goodput，再用控制变量归因 queue/prefill/decode/tool/retry。
6. **TD-AP06 超时/重试/降级**：跨 gateway、SDK、Agent、Tool 统一 deadline 与 attempt budget，为写操作定义只读、人工与对账终态。
7. **TD-AP07 长稳/泄漏**：分热身、稳态、恢复窗口，联合检查资源斜率、平台期、cleanup、尾延迟与快照差分。
8. **TD-AP08 SLO/告警/事故**：以 good task 为 SLI，用多窗口 burn-rate 告警连接 owner、止血、恢复和事故样例回流。

## 统一系统与证据链

订单异常处置 Agent 是确定性离线夹具：四类任务经过到达调度、模型、订单工具、退款/人工终态和 evaluator。每页拥有独立 profile、Prompt/Input/Schema/Eval/Mutation、Lab Manifest 和 baseline/fault/repair 证据。

```text
workload fixture → arrival scheduler → Agent/model/tool simulator
       → task-rooted traces + metrics → versioned evaluator/gate → evidence card
```

## 运行八页实验

## Commands

在 `lab` 目录执行：

```bash
python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP01-lab.json --mode cycle
```

把页面 ID 替换为 TD-AP02～TD-AP08。每个 cycle 真正运行 baseline、fault、repair；阶段退出码必须为 `0 / 1 / 0`，cycle 只有观察到该模式才退出 0。也可把 `--mode` 改成 baseline、fault、repair 单独复现。

## 如何读报告

## Metrics and thresholds

每个指标必须记录单位、分母、聚合方式、风险切片、测量点、版本、owner 和失败动作。先检查业务 blocker，再检查尾延迟、队列、重试、资源与成本；禁止以平均值或入口成功覆盖关键任务失败。

1. 核对 page_id、workload_version、configuration_hash 与 fixture 边界。
2. 先看业务 task success / good-task gate，再看 queue、TTFT、TPOT、retry、step、资源与成本。
3. 从 fault 的 `traces.jsonl` 找一项红灯任务，不只引用汇总。
4. 检查 repair 改的是实现/配置，不是删除或放宽 gate。
5. 把结论写成 Evidence / Inference / Unknown；真实容量、组织 SLO、外部依赖和 practitioner sign-off 保持 Unknown。

## Prompt 包

## Failure injection

fault 会删减任务切片、制造重试/队列/资源或 trace 证据缺口，预期阶段退出码为 1 且 verdict=FAIL。repair 只能恢复实现或配置，不得删除阈值、放宽 Oracle 或吞掉非零退出码。

每页 Prompt v1.0.0 都绑定固定 Input、JSON Schema、Eval 和 Mutation，manifest 保存 SHA-256、权限、停止状态与 provider/model 状态。当前 provider=none、model=NOT_RUN：Prompt 已定义并静态验证，不代表 live model evaluation 已运行。

## 人工责任边界

## Human review gate

测试负责人确认 workload 与 gate；业务负责人确认允许终态、副作用和损失预算；平台/SRE 确认资源、限流、值班和恢复；安全/合规确认遥测内容与保留期。AI 可以聚合证据和提出候选根因，不能自动降低阈值、批准例外或放行真实资金操作。

## Evidence status

TD-AP01～TD-AP08 的 deterministic fixture 均实际观察到 0/1/0。状态是 **PASS-FIXTURE**：证明脚本、采集、故障检测与修复比较可复现。每一条结论都必须同时保存命令、观察到的退出码、报告哈希和边界说明；缺少其中任一项就保持 BLOCKED/UNKNOWN，而不是把静态内容升级为 live 证据。没有真实模型、生产工具、GPU 集群、企业流量或 practitioner review，因此不构成 PASS-LIVE、PASS-PRACTITIONER 或 production capacity。

## AI-specific failure boundary

本课覆盖 workload、指标、trace、开放/封闭负载、容量瓶颈、重试降级、长稳泄漏和 SLO 事故闭环；不覆盖供应商内部路由、真实 GPU/网络、生产副作用、组织阈值或从业者判断。

## Learner artifact

学员提交 workload model、metric dictionary、trace schema、负载模型比较、容量曲线、retry/degrade policy、soak report、SLO/incident runbook，以及八页实验的输入、评估、mutation、报告和证据边界。

## Transfer challenge

把同一 workload/metric/trace/gate 链迁移到另一个有状态工具 Agent，并重新定义任务终态、工具权限、风险切片和 owner；不得只替换产品名称。

TD-AP01～TD-AP08 的 deterministic fixture 均实际观察到 0/1/0。状态是 **PASS-FIXTURE**：证明脚本、采集、故障检测与修复比较可复现。没有真实模型、生产工具、GPU 集群、企业流量或 practitioner review，因此不构成 PASS-LIVE、PASS-PRACTITIONER 或 production capacity。
