# AI API、Serving 质量与职业能力迁移

这是一门从协议一路走到职业工件的完整实践课。七页不是同一篇泛化正文：TD-A01 比较普通 API 与 AI API；TD-A02 分解 Streaming、Structured、Tool、Async；TD-A03 定义 TTFT、TPOT、ITL、Goodput 与单位成功成本；TD-A04 用 open/closed 负载找 fixture 拐点；TD-A05 用阶段证据诊断 Queue/GPU/KV cache；TD-A06 设计限流、超时、重试、回退和降级；TD-C01 把既有测试能力迁移为有证据的岗位路径和作品集。

## AI centrality

移除 AI serving 后，Token 流、TTFT/TPOT/ITL、模型和 Prompt 版本、工具副作用、KV cache、fallback 质量变化等核心对象不存在。传统 HTTP、风险、Oracle、负载和可靠性知识仍然保留，但被测边界、数据结构和发布证据发生扩张。AI 可以生成候选测试与诊断假设，不能批准阈值、waiver、容量、风险或职业结论。

## System under test

被测对象是合成的 AI API 与 Serving 合同，不是某家供应商。边界从客户端、HTTP/SSE/Async、Model/Prompt/Schema/Tool 版本，经过 Queue/Prefill/Decode/GPU/KV 和 Telemetry，到 Retry/Fallback Gate 与人工决定。职业页的系统边界是当前能力、目标责任、证据作品、差距计划和招聘组织的独立决定。

## Baseline and target

baseline 是只看最终文本、总耗时、GPU 百分比或证书数量。目标是每页有独立控制问题、方法理由、Oracle、版本化 Prompt/Input/Schema/Eval/Mutation、0/1/0 报告、owner 和 hash closure。所有容量只到 fixture，所有职业建议明确 `employment_guarantee=false`。

## Commands

从公开学习包根目录运行逐页完整 cycle。以下命令不需要网络、密钥、模型或 GPU；外层 exit 0 仅在内部实际退出码严格为 `0/1/0` 时成立。

```bash
cd learner-materials
python3 scripts/serving_lab.py --manifest manifests/TD-A01.json --mode cycle
python3 scripts/serving_lab.py --manifest manifests/TD-A06.json --mode cycle
python3 scripts/serving_lab.py --manifest manifests/TD-C01.json --mode cycle
```

## Metrics and thresholds

协议页看事件顺序、唯一终态、Schema+语义和副作用账本；性能页看 TTFT、TPOT、ITL、Goodput、cost_per_success；容量页看计划到达守恒与 Goodput 拐点；诊断页看 queue/prefill/decode、GPU/KV 与单变量实验；韧性页看 attempt/time/token/cost budget 和 fallback 质量；职业页看 evidence_ref、UNKNOWN 和岗位边界完整率。fixture 的精确值只为杀死 mutation，不是行业或生产阈值。

## Failure injection

每页 fault 只改变 manifest 声明的字段。例如 TD-A06 把重试次数从 3 改为 8、忽略 Retry-After，并令 fallback quality gate 失败。预期进程 exit 1、报告 verdict=FAIL，且 exact-field Oracle 显示 expected/actual。若 fault 不变红，立即判定测试资产无检测力；修复只能恢复实现观察，不能删除检查或修改 expected。

## Human review gate

AI 质量负责人确认发布问题、指标分母、风险切片、阈值依据、owner 和残余风险。协议或副作用 blocker 不能被平均分覆盖。容量必须在真实模型、硬件、流量和故障环境重新验证。招聘、薪资、晋升、地区机会与个体适配由具体组织独立决定，本课程不承诺任何结果。

## AI-specific failure boundary

模型候选可能发明内部版本、把最终文本当工具事实、隐藏 dropped arrivals、从 GPU 相关性推导根因、建议无限重试或写出就业承诺。Prompt 包默认 provider=none、model_execution=NOT_RUN。Schema 通过不等于业务正确，fixture 红绿不等于 live、practitioner 或 production 通过。

## Learner artifact

学员交付七份独立 manifest 与 evidence：AI API 五层测试面、四协议状态机、指标卡、fixture-only 容量报告、瓶颈诊断树、韧性预算，以及包含岗位负责/协作/禁止边界、evidence_ref、UNKNOWN、30/60/90 天计划和 baseline-fault-repair 作品的自评 JSON。

## Evidence status

当前为 `fixture-tested`。Python 标准库 runner 已实际证明七页各自 `baseline -> fault -> repair = 0/1/0` 并写入逐页 hash。真实 Provider、模型、GPU、网络、生产流量、从业者评审和就业结果均为 NOT_RUN；出版仍由上层门禁决定。
