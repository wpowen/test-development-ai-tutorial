# AI 服务稳定性、故障注入与可观测性

这是一门面向测试开发工程师与 AI 服务质量负责人的可运行课程。学习者最终交付一份可回放的 workload、任务级指标报告、故障注入证据和修复后的稳定性门禁。默认实验只使用 Python 标准库和虚拟时间，不访问模型、工具、集群或网络。

## 学习者与前置条件

适合已经会读 JSON、运行 Python unittest、理解 HTTP 请求/响应和基本 SLO 的学习者。无需 API key、Docker、Kubernetes 或第三方包。前置课程是 AI 系统测试基础与 Agent 负载稳定性；本课重点从“请求是否 200”推进到“被接纳的用户任务是否在正确、及时、成本和副作用约束内完成”。

## AI centrality

AI 不是装饰性例子，而是被测系统的内部放大器：一次用户任务会产生检索、模型 generation、工具调用和重试 attempt。模型/工具失败会改变任务终态、队列等待、尾延迟、调用放大和成本；因此移除 AI 调用链，课程的核心问题就不存在。业务 oracle 仍由人定义，AI 不能自行批准发布或决定真实工具副作用。

## System under test

实验把一个合成的 AI 任务服务建模为 admission → bounded worker queue → retrieval → model → tool → task terminal state。每个任务具有 `task_id`、`trace_id`、终态、调用 attempt、延迟和成本；每个模型/工具事件都作为 Trace 子事件保存到 `traces.jsonl`。模型和工具是确定性 stub，故障配置只改变虚拟时延、失败率、重试上限和到达速率。

## Baseline and target

基线固定 `seed=42`、120 个 admitted tasks、任务到达间隔、worker 数、服务版本和阈值。目标不是让平均 QPS 好看，而是同时满足 task success、E2E p95、queue p95、retry amplification、call amplification 与 cost per success。基线与修复应为 PASS；中间故障必须至少有一个门禁变红。阈值是教学 gate，不是跨模型或生产容量常数。

## Input and output contract

输入是 `lab/configs/*.json`：workload、seed、延迟、失败率、attempt 上限、成本和阈值。输出目录必须包含 `summary.json` 与逐任务 `traces.jsonl`。`summary.json` 的 `metrics` 至少包括任务成功率、E2E p95、queue p95、retry amplification、call amplification、总成本、每成功任务成本和 goodput；`checks` 是布尔门禁，`gate_pass=false` 时进程退出 1。

## Commands

从本课程目录运行：

```bash
python3 lab/reliability_lab.py --config lab/configs/baseline.json --output evidence/baseline
python3 lab/reliability_lab.py --config lab/configs/latency-retry-fault.json --output evidence/latency-retry-fault; test $? -eq 1
python3 lab/reliability_lab.py --config lab/configs/repaired.json --output evidence/repaired
python3 -m unittest discover -s lab -p 'test_*.py'
```

命令使用 Python 标准库，不需要安装依赖。K8s 示例位于 `lab/k8s/`，只允许静态审查：可以检查 selector、duration、direction 和 `externalTargets`，不能在本课程默认路径 apply。真实演练前必须由授权 owner 在隔离 namespace 执行 dry-run、确认 selector、停止条件与回滚。

## Metrics and thresholds

`task_success_rate = 通过业务 oracle 的任务 / admitted tasks`；`e2e_p95_ms` 从 admission 到任务终态；`queue_p95_ms` 是 admission 到 worker 开始；`retry_amplification = 所有 model/tool attempts / admitted tasks`；`call_amplification = retrieval + model + tool calls / admitted tasks`；`cost_per_success = 总合成成本 / 成功任务`。p95 采用固定排序插值，避免均值掩盖尾部。诊断顺序是先查任务终态和队列，再查模型/工具事件、重试和成本；不要由 HTTP 200 推断成功。

## Failure injection

`latency-retry-fault.json` 同时模拟 provider latency、tool transient failure、5 次工具重试和高到达率。预期观察到 queue p95、E2E p95、retry amplification 或 task success 超过阈值，进程以 exit 1 结束，报告 `gate_pass=false`；这是一种可观测的红结果，不是实验器崩溃。学习者应从 `traces.jsonl` 找出 `tool status=error` → retry attempt → queue/e2e 变大的顺序，并写出 `symptom → hypothesis → confirming evidence → controlled rerun`。

## Repair

`repaired.json` 恢复较低到达率与足够 worker，模型只允许单次尝试，工具只保留有界重试，并使用更长但明确的 backoff。它不是通过删除断言或放宽阈值造绿，而是切断重试反馈环并恢复 admission/容量边界。复跑同一 seed 后应 exit 0、`gate_pass=true`；还需比较三份 JSON 的任务成功率、p95、调用放大、成本与队列。

## Human review gate

真实服务接入前，负责人必须确认实验授权、namespace/selector、SUT 与观测版本、最大持续时间、自动停止条件、脱敏策略、幂等键和回滚命令。高风险写工具必须路由到 sandbox；用户 prompt、token、PII 和原始 tool arguments 不进入高基数指标。Kubernetes/Chaos Mesh YAML 仅为静态形状示例，不证明 CRD、权限、PDB、节点压力或恢复行为；必须由具备集群权限的人按当前版本文档复核。

## AI-specific failure boundary

本夹具覆盖“任务分母、队列、尾延迟、重试/调用放大、成本、逐任务 Trace 与红绿 gate”的可回放行为，不覆盖真实 tokenizer、SSE 首 token/流中断、GPU 饱和、provider 429 计费、检索相关性、Agent 工具权限、OTel Collector 丢失或真实 Chaos Mesh 恢复。OpenTelemetry GenAI 字段和 provider API 版本会演进；接入时必须版本化 schema 与成本表，不能把本地数值写成生产阈值。

## Learner artifact

学习者提交：三份 `summary.json` 与 `traces.jsonl`、一张五层指标字典、一次故障诊断表、一个修复决策和迁移到另一 AI 网关的 gate 提案。评分 100 分：任务/调用分母 20，基线可回放 15，故障确实变红 20，Trace 根因证据 15，修复后 0/1/0 证据 15，权限/隐私/生产边界 10，迁移时至少两处必须修改 5。不得用“报告看起来合理”替代退出码和 JSON 字段。

## Evidence status

状态为 `PASS-FIXTURE` / `fixture-tested`：本包的标准库脚本、unittest、三阶段报告和 YAML 静态文件已在本机运行/审查。它证明教学夹具能 baseline → fault → repair，不能证明真实模型质量、企业工作负载、生产容量、费用、SLO、Chaos Mesh 执行或恢复时间。生产验证仍是 `UNKNOWN`，不得伪造为 `PASS-LIVE`。

<!-- WAVE1-SPECIALTIES-START -->
## Wave 1 独立专业专项

### TD-PS10 · 稳定性：超时、重试预算、熔断、限流与降级

- 控制问题：怎样证明每层 deadline 和 retry budget 有界，过载时安全拒绝或只读降级，恢复后不会产生洪峰与重复副作用？
- 方法选择：deadline 传播控制等待，指数退避+jitter 降低同步重试，retry budget 限制放大，熔断和 load shedding 保护容量，只读 fallback 保护资金副作用
- 独立 Oracle：端到端 deadline 不小于子调用但总链有界；call amplification 不超过预算；过载拒绝不产生退款写操作；恢复窗口队列与错误率回到基线
- Prompt：读取依赖图、deadline、retry policy、队列和副作用规则，生成故障矩阵与降级断言；禁止建议无限重试或放宽写权限
- Failure cycle：baseline → 模型 429 与工具超时叠加 → repair
- Unknown：目标供应商 Retry-After、真实队列容量和业务降级文案

### TD-PS11 · 可观测性与混沌：Trace 完整性、受控注入和恢复证据

- 控制问题：怎样让 symptom、fault event、跨服务 Trace、质量切片和恢复检查属于同一证据链，并在 telemetry 缺失时保持 UNKNOWN？
- 方法选择：OTel/W3C 传播连接任务，版本字段区分变化，trace completeness 先验证观测能力，Chaos Experiment Card 固定授权和 blast radius，单变量注入支持归因
- 独立 Oracle：task trace 覆盖 gateway retrieval model tool 和 terminal；敏感输入不进入默认 telemetry；fault start/end 与异常窗口可关联；停止回滚后同一切片恢复且无残留
- Prompt：读取 Trace schema、脱敏策略、实验授权和 SLO，输出单变量实验卡、观测字段、停止条件与复验；生产 selector 缺失时必须 BLOCKED
- Failure cycle：baseline → collector 丢 span → repair
- Unknown：目标 collector 采样、生产权限、托管模型内部 span 和真实恢复时间

### TD-PS12 · 安全测试：身份、授权、输入、秘密与跨租户副作用

- 控制问题：怎样从 threat model 和权限矩阵构建确定性安全 Oracle，并证明拒绝发生在工具边界且没有跨租户读取或写副作用？
- 方法选择：ASVS/WSTG 提供控制目录，威胁建模映射资产与信任边界，身份/对象/功能级权限矩阵构造负例，输入验证和工具 allowlist 强制策略，审计 Trace 提供拒绝证据
- 独立 Oracle：无效过期或错 audience token 被拒绝；跨租户对象读取和退款写入均为零；Prompt 内容不能扩大工具 allowlist；日志报告不含 token PII 或支付秘密
- Prompt：读取 threat model、角色权限、API/工具 schema 与数据分类，生成 abuse case、独立 Oracle 和证据要求；不得生成真实攻击生产命令或自动批准风险
- Failure cycle：baseline → 替换 order_id 做 BOLA → repair
- Unknown：目标 IdP 策略、真实密钥管理、渗透授权范围和剩余风险接受人

共享 bundle 只复用 runner；页级 manifest、owner、Oracle、Prompt、fault 和证据互不继承。
<!-- WAVE1-SPECIALTIES-END -->
