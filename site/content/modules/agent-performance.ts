import type { TutorialPage } from "../course.ts";

const commonSources = ["S47", "S48", "S67", "S68", "S69", "S70", "S72", "S75"];

export const agentPerformancePages: TutorialPage[] = [
  {
    id: "TD-AP01", moduleId: "TD-M11", order: 0,
    title: "为什么 Agent 压测不是把并发数调高",
    type: "概念", status: "desk-researched", duration: "45 分钟",
    summary: "先建立正确的被测系统模型：一次 Agent 任务可能包含多轮模型调用、检索、工具、状态读写、重试和人工交接，HTTP 成功不等于任务成功。",
    why: "普通接口通常把一次请求视为一个工作单元；Agent 的一个用户任务会动态展开成多步有状态工作流。如果仍只看 QPS 和接口 p95，你可能得到全绿的网关曲线，同时用户任务超时、重复扣费、成本失控或执行了错误副作用。",
    prerequisites: [],
    outcomes: ["画出 Agent 任务的完整关键路径", "区分请求成功、步骤成功与业务任务成功", "解释开环和闭环负载何时会掩盖问题"],
    artifact: "Agent 压测对象与失败模型",
    blocks: [
      {
        title: "先定义真正的工作单元：Task，而不是 HTTP Request",
        body: [
          "假设用户让报销 Agent 完成“读取发票、核对政策、创建报销单”。入口 API 可能 200 返回一个 task_id，但后台还要完成 OCR、两次模型判断、政策检索、财务系统写入和最终确认。入口 200 只能证明受理成功，不能证明任务正确结束。",
          "压测报告因此至少保留三层分母：收到多少用户任务、启动多少 Agent 运行、内部产生多少模型/工具调用。任何百分比都必须写明分母，否则 99.9% 的‘成功率’没有可比较含义。",
        ],
        table: {
          headers: ["观察层", "工作单元", "典型成功", "典型假绿"],
          rows: [
            ["入口服务", "HTTP 请求", "2xx/受理", "任务随后超时或进入死循环"],
            ["Agent 运行", "一次 task/run", "终态正确且在时限内", "最终文本正常但工具副作用错误"],
            ["模型层", "一次 generation", "生成成功", "多轮重试后才成功，成本被放大"],
            ["工具层", "一次 tool call", "返回成功", "重复调用、幂等失效或写错对象"],
          ],
          caption: "压测结论必须逐层汇总，不能用入口成功率代替业务成功率。",
        },
      },
      {
        title: "Agent 的负载为什么会动态放大",
        body: [
          "传统服务的扇出通常由代码路径决定；Agent 会受模型决策、上下文、工具失败和重试策略影响。同样 100 个用户任务，可能产生 200 次模型调用，也可能在异常时产生 900 次模型调用。这个比值就是调用放大系数。",
          "排队会进一步形成反馈环：依赖变慢 → Agent 超时并重试 → 下游流量增加 → 排队更长。Google SRE 把重试和队列列为级联故障的重要放大器。Agent 系统还多了一层模型循环和工具循环，因此必须为步骤数、重试数、总时长和总成本设硬预算。",
        ],
        code: "call_amplification = (model_calls + tool_calls) / accepted_tasks\nretry_amplification = total_attempts / first_attempts\ngoodput = successful_tasks_meeting_latency_and_cost_slo / test_duration",
        expected: "你能说明吞吐不是完成量：只有正确、及时、成本合格的任务才进入 goodput。",
      },
      {
        title: "选择负载模型：开环发现容量，闭环模拟受限用户",
        body: [
          "闭环模型维持固定并发：一个虚拟用户完成后才发下一个请求。系统变慢时，发压端也会自动降速，可能掩盖过载。开环模型按到达率持续注入任务，更适合验证突发流量、排队和拒绝策略。",
          "工程上通常两者都要：用闭环回答‘固定 50 个并发用户体验如何’，用开环回答‘每秒 20 个任务到来时系统是否保持 SLO’。再加入突发、长短任务混合、依赖变慢和限流场景，才能接近真实流量。",
        ],
        table: { headers: ["模型", "控制量", "适合回答", "主要风险"], rows: [["闭环", "并发用户数", "固定并发下的体验与资源占用", "系统变慢时注入率下降，产生协调遗漏"], ["开环", "任务到达率", "容量边界、排队、限流和突发", "需控制队列，避免无限积压"], ["回放", "真实到达间隔与任务分布", "已知业务形态下的回归", "历史流量未必覆盖未来峰值"]] },
      },
      {
        title: "本专题使用的业务场景",
        body: [
          "后续七页统一使用“订单异常处置 Agent”：读取工单，调用模型分类，查询订单工具，必要时调用退款工具，并写入处理结果。这样指标、Trace、压测和告警可以在同一条业务链上串起来。",
          "教学实验不调用真实模型和支付系统，而使用确定性夹具模拟模型、工具、限流和重试。它能验证测量方法与门禁逻辑，不能证明某家模型或你的生产容量。",
        ],
        warning: "不要直接对生产写接口做压测。退款、发信、建单等副作用必须使用沙箱、幂等键和清理脚本。",
      },
    ],
    practice: ["画出一个真实 Agent 从入口到终态的所有步骤和依赖", "分别写出入口成功、任务成功和业务正确的判定", "为模型调用、工具调用、重试和总时长设置初始预算"],
    completion: ["图中包含队列、模型、工具、状态和外部依赖", "所有成功率都注明分母", "能解释为何闭环压测可能掩盖过载"],
    sourceIds: ["S47", "S48", "S68", "S72", "S75", "S77"],
    evidenceBoundary: "来源支持负载模型、级联故障与 Agent Trace 的通用机制；具体容量、调用放大和预算必须由目标系统实测。",
  },
  {
    id: "TD-AP02", moduleId: "TD-M11", order: 0,
    title: "建立 Agent 性能指标树：系统、模型、轨迹、成本",
    type: "参考", status: "desk-researched", duration: "60 分钟",
    summary: "把传统 Golden Signals、生成式模型延迟、Agent 轨迹质量和单位成功成本连接成可计算的指标树。",
    why: "单一平均延迟无法解释首字等待、逐 Token 卡顿、工具等待、队列积压和重试放大。指标树必须同时回答：快不快、对不对、稳不稳、贵不贵，以及慢在哪里。",
    prerequisites: ["TD-AP01"], outcomes: ["区分 TTFT、TTFO、TPOT/ITL 和 E2E", "计算任务 Goodput 与单位成功成本", "为每个指标指定维度、窗口和行动"], artifact: "Agent 性能指标字典",
    blocks: [
      {
        title: "第一层：服务是否承受住流量",
        body: ["沿用 SRE 四类信号，但必须按成功/失败请求、任务类型和依赖拆维度。平均值只适合看总量，发布门禁使用分位数和错误预算。"],
        table: { headers: ["指标", "定义", "它回答什么", "异常时先看"], rows: [["Traffic", "tasks/s、requests/s、tokens/s", "来了多少工作", "任务类型与输入长度分布"], ["Latency", "queue、service、E2E 的 p50/p95/p99", "用户等多久", "成功与失败延迟分开"], ["Errors", "超时、限流、依赖、解析、业务错误率", "哪里失败", "错误码与失败步骤"], ["Saturation", "CPU/GPU、KV cache、连接池、队列深度", "资源是否接近极限", "等待任务与排队时间"]] },
      },
      {
        title: "第二层：生成式模型的等待发生在哪里",
        body: [
          "TTFT 是请求发出到第一个生成 Token 的时间，通常包含排队和 Prefill；TPOT 或 ITL 描述首 Token 后的生成节奏；E2E 是完整请求耗时。推理模型还可能先生成不可见的推理 Token，AIPerf 因此区分首 Token 与首可见输出（TTFO）。",
          "测试时必须记录输入/输出 Token 长度，因为长上下文会增加 Prefill，长输出会增加生成时间。只比较总延迟而不控制长度，无法判断版本真的变慢还是工作负载变了。",
        ],
        table: { headers: ["指标", "近似计算", "用户感知", "常见根因"], rows: [["TTFT", "first_token_at - request_at", "等待开始响应", "排队、长 Prompt、Prefill"], ["TTFO", "first_visible_output_at - request_at", "推理模型首次可见内容", "隐藏推理阶段过长"], ["ITL/TPOT", "相邻 Token 间隔/生成阶段每 Token 时间", "流式是否卡顿", "Decode 调度与资源争用"], ["E2E", "completed_at - request_at", "完整完成时间", "输出长度、重试、工具等待"]] },
      },
      {
        title: "第三层：Agent 是否用合理路径完成任务",
        body: ["性能不能以牺牲正确性换取。轨迹指标把最终结果与过程成本连接起来；LangSmith 的 Agent 评测也区分最终响应、轨迹和单步决策。"],
        table: { headers: ["指标", "计算", "防止什么假绿"], rows: [["Task success", "正确到达允许终态 / 总任务", "HTTP 200 但业务失败"], ["Step count", "每任务 span/tool/model 数", "无意义循环"], ["Tool precision", "正确工具调用 / 全部工具调用", "乱调工具但最终文本看似正常"], ["Retry amplification", "总尝试 / 首次尝试", "靠重试掩盖不稳定"], ["Goodput", "成功且满足延迟、成本、轨迹预算的任务 / 秒", "吞吐高但质量或成本不合格"]] },
      },
      {
        title: "第四层：成本必须按成功任务归一化",
        body: [
          "总 Token 与总费用只能回答账单规模。工程决策更关心每个成功任务成本，以及不同任务切片的成本尾部。失败重试同样消耗 Token，不能从分母中删除。",
          "建议同时保存 model_input_tokens、model_output_tokens、model_calls、tool_calls、retry_count、estimated_cost 和 task_success，再计算 cost_per_success。价格属于外部配置，报告要记录价格表版本。",
        ],
        code: "cost_per_success = total_cost / successful_tasks\nquality_adjusted_cost = total_cost / tasks_meeting_quality_latency_budget\n# 不要用 total_cost / accepted_tasks 掩盖失败和超时",
      },
      {
        title: "指标不是列表，而是触发行动的契约",
        body: ["每个指标必须补齐单位、分母、聚合窗口、分位数、标签基数、数据源、阈值、负责人和超限动作。没有行动映射的指标只能做探索面板，不能做告警。"],
        expected: "一条合格定义示例：checkout_agent/task_e2e_ms，成功任务 p95，5 分钟滚动，按 workflow_version 和 task_type 分组；连续 3 个窗口 > 12s 则停止放量并检查 queue/model/tool 三段耗时。",
      },
    ],
    practice: ["为一个 Agent 写出不少于 15 个指标并归入四层", "给每个百分比补充分母", "选择 5 个指标写出阈值超限后的具体动作"], completion: ["同时覆盖正确性、延迟、容量、轨迹和成本", "能从 E2E 下钻到 queue/model/tool", "至少一个门禁使用 Goodput 而不是裸吞吐"], sourceIds: ["S47", "S51", "S67", "S69", "S73", "S74"], evidenceBoundary: "指标语义来自官方文档和 SRE 方法；阈值示例仅作教学，不能直接用于生产。",
  },
  {
    id: "TD-AP03", moduleId: "TD-M11", order: 0,
    title: "设计工作负载：任务、上下文、工具与故障分布",
    type: "参考", status: "desk-researched", duration: "55 分钟",
    summary: "从真实流量构造可解释的 workload model，而不是用同一个 Prompt 循环一万次。",
    why: "Agent 性能高度依赖输入长度、任务复杂度、工具扇出、缓存命中和失败重试。如果测试分布与生产不同，容量数字即使精确也没有决策价值。",
    prerequisites: ["TD-AP02"], outcomes: ["把生产流量切成任务类别", "建立输入与路径联合分布", "设计稳态、突发、浸泡和故障场景"], artifact: "版本化工作负载模型",
    blocks: [
      { title: "从业务任务切片，不从 Prompt 文案切片", body: ["先按业务风险和执行路径分类，再统计每类任务的占比、上下文长度、预期工具链、允许终态和成本预算。相同 Prompt 长度可能走完全不同的工具路径。"], table: { headers: ["切片", "占比示例", "路径", "主要风险"], rows: [["只读查询", "55%", "model → order_lookup → model", "高频、缓存与限流"], ["退款判断", "25%", "model → policy → order → refund", "副作用与幂等"], ["信息不足", "15%", "model → ask_user", "长会话与状态"], ["人工升级", "5%", "model → handoff", "队列与终态正确"]] } },
      { title: "控制四类决定性能的变量", body: ["至少控制输入 Token 分布、输出 Token 上限、步骤/工具扇出、依赖延迟与错误率。还要记录缓存热度、模型版本、区域和限流配额。"], bullets: ["长度：短/中/长上下文，不要只测平均长度", "复杂度：一步任务、三步任务、可能循环的任务", "依赖：工具 p50/p95、超时、429、5xx 和空结果", "状态：冷启动、热缓存、长会话、并发写冲突"] },
      { title: "四种测试各回答一个问题", body: ["容量测试逐级增加到 SLO 首次失败；突发测试观察队列与恢复；浸泡测试发现泄漏、缓存膨胀和漂移；故障测试验证限流、重试、熔断和降级。不要用一次十分钟的峰值测试替代全部。"], table: { headers: ["场景", "负载形状", "停止条件", "主要产物"], rows: [["基线", "低负载固定分布", "指标稳定", "无竞争时的服务时间"], ["容量", "阶梯/恒定到达率", "SLO 或资源门限首次失败", "最大可持续 goodput"], ["突发", "短时 3–10 倍", "队列恢复或拒绝失控", "恢复时间和降载行为"], ["浸泡", "60 分钟以上稳态", "资源/成本持续漂移", "泄漏和尾延迟趋势"], ["故障", "依赖慢/错/限流", "安全降级失败", "韧性与错误预算消耗"]] } },
      { title: "给数据集加上可回放字段", body: ["每条任务保存 task_type、risk_slice、input_token_bucket、expected_tools、allowed_terminal_states、latency_budget_ms、cost_budget 和 fixture_version。敏感生产输入必须脱敏或合成，并保留分布依据。"], code: "{\n  \"task_id\": \"refund-long-007\",\n  \"task_type\": \"refund_decision\",\n  \"input_token_bucket\": \"8k-16k\",\n  \"expected_tools\": [\"policy_lookup\", \"order_lookup\", \"refund\"],\n  \"allowed_terminal_states\": [\"refunded\", \"handoff\"],\n  \"latency_budget_ms\": 12000,\n  \"cost_budget\": 0.08,\n  \"fixture_version\": \"workload-2026-08-v1\"\n}" },
    ],
    practice: ["抽样至少 30 条脱敏 Trace 建立任务切片", "生成一份不含生产 PII 的回放数据集", "设计基线、容量、突发、浸泡和故障五个场景"], completion: ["工作负载包含联合分布而非单一平均值", "每条任务有允许终态和预算", "能解释样本与生产流量之间的偏差"], sourceIds: ["S68", "S77", "S47", "S75"], evidenceBoundary: "工作负载建模原则可迁移；示例比例是教学数据，真实比例必须来自脱敏生产 Trace 或业务预测。",
  },
  {
    id: "TD-AP04", moduleId: "TD-M11", order: 0,
    title: "设计 Trace 与数据模型：让一次慢任务可下钻",
    type: "参考", status: "desk-researched", duration: "60 分钟",
    summary: "用一次 task 一个根 Trace、模型/工具/检索/队列为子 Span 的结构，把质量、性能和成本放在同一证据链。",
    why: "只有最终延迟和日志文本时，无法回答慢在排队、模型、工具还是重试。结构化 Trace 是压测诊断、线上监控和离线评测复用同一证据的基础。",
    prerequisites: ["TD-AP03"], outcomes: ["设计 Agent Span 树", "定义低基数指标与高维 Trace 的边界", "写出可关联的结果表结构"], artifact: "Agent 可观测性 Schema",
    blocks: [
      { title: "一条任务 Trace 应该长什么样", body: ["OpenTelemetry GenAI 约定正在快速演进，推荐采用通用 OTel 字段并把供应商字段放入命名空间。根 Span 表示 invoke_agent，子 Span 表示 generation、tool、retrieval、handoff 和状态读写。"], code: "invoke_agent task_id=... workflow.version=v12\n├─ queue.wait duration_ms=...\n├─ gen_ai.chat model=... input_tokens=... output_tokens=...\n├─ execute_tool tool.name=order_lookup retry=0\n├─ gen_ai.chat model=...\n├─ execute_tool tool.name=refund idempotency_key=...\n└─ task.finalize terminal_state=refunded success=true" },
      { title: "Span、Metric、Log 各自负责什么", body: ["Metric 用于低成本聚合和告警；Trace 用于单任务因果下钻；Log 记录离散事件和调试上下文。不要把 user_id、prompt 全文或 task_id 作为 Prometheus 标签，否则会制造高基数与隐私风险。"], table: { headers: ["信号", "适合", "不适合"], rows: [["Metric", "速率、分位数、错误预算、资源", "高基数 task_id 与完整输入"], ["Trace", "跨模型/工具关键路径、重试和因果", "无限期保存全部敏感正文"], ["Log", "错误事件、审计和调试", "代替结构化耗时聚合"]] } },
      { title: "最小字段集必须支持五类问题", body: ["字段设计从问题反推：哪个版本、哪类任务、慢在哪一步、为什么重试、成本如何产生。输入正文默认不采集；需要调试时使用哈希、脱敏摘要或受控采样。"], table: { headers: ["实体", "关键字段"], rows: [["task_run", "task_id, trace_id, task_type, workflow_version, started_at, terminal_state, success"], ["span", "span_id, parent_span_id, kind, dependency, start/end, status, error_type"], ["generation", "model, prompt_version, input/output_tokens, ttft_ms, finish_reason"], ["tool_call", "tool_name, attempt, timeout_ms, idempotency_key_hash, side_effect"], ["evaluation", "quality_score, policy_pass, trajectory_pass, scorer_version"], ["cost", "price_version, estimated_cost, currency"]] } },
      { title: "用关键路径而不是简单相加定位 E2E", body: ["并行工具调用的耗时不能全部相加。先按 parent-child 和时间戳重建关键路径，再计算 queue、model、tool、orchestration overhead。若 E2E 大于关键路径各段之和，差额通常来自调度、序列化、网络或未埋点等待。"], expected: "选一条 p99 慢 Trace，能指出关键路径、重试分支、最长依赖和未归因时间，而不是只说‘模型慢’。" },
      { title: "隐私与采样是设计的一部分", body: ["Prompt、检索文档和工具参数可能含 PII、密钥或业务机密。生产默认保存长度、哈希、版本和分类标签；错误或慢请求可提高 Trace 采样率，但正文访问需要权限、保留期和审计。"], warning: "不要为了可观测性把 Authorization、原始用户输入或完整工具结果写入公开日志。" },
    ],
    practice: ["为一条 Agent 任务画根 Span 与子 Span", "将当前日志字段分配到 Metric/Trace/Log", "从一条慢 Trace 计算未归因时间"], completion: ["Trace 能跨入口、模型、工具和终态关联", "指标标签无 task_id 等高基数字段", "敏感字段有默认关闭、采样和保留策略"], sourceIds: ["S49", "S70", "S71", "S72", "S80"], evidenceBoundary: "OTel GenAI 语义约定仍在演进，落地前需锁定版本并做兼容层；Schema 示例不是法规合规意见。",
  },
  {
    id: "TD-AP05", moduleId: "TD-M11", order: 0,
    title: "搭建压测架构：发压、夹具、观测、判定四层分离",
    type: "概念", status: "desk-researched", duration: "50 分钟",
    summary: "设计可替换真实模型或离线夹具的测试架构，并按测试对象选择 k6、AIPerf、Trace 平台和自定义校验器。",
    why: "没有分层架构时，团队常用一个 HTTP 发压工具承担任务生成、业务判定、模型指标和诊断，最后只能得到吞吐曲线，无法验证 Agent 是否正确完成任务。",
    prerequisites: ["TD-AP04"], outcomes: ["设计四层压测架构", "按对象选工具而不是找万能工具", "隔离副作用并保存版本证据"], artifact: "Agent 压测系统架构图",
    blocks: [
      { title: "四层架构各自只有一个责任", body: ["发压层控制到达模式；被测与夹具层提供真实/模拟依赖；观测层收集指标和 Trace；判定层把质量、延迟、成本和安全条件合成门禁。它们通过 run_id、task_id 和版本 Manifest 关联。"], code: "workload driver ──task──> Agent gateway ──> queue/orchestrator\n      │                         ├─> model endpoint/fixture\n      │                         └─> tools/sandbox fixtures\n      └─ run manifest           └─> OTel collector ─> metrics/traces\n                                             └─> evaluator ─> gate report" },
      { title: "工具按层组合", body: ["k6 擅长 HTTP 场景、阈值和开闭环负载；AIPerf/GenAI-Perf 专注模型端点 Token 与延迟；vLLM 暴露服务内部调度指标；OpenTelemetry 贯通 Agent Trace；Phoenix、Langfuse 或 LangSmith 可承载追踪与评测。工具文档证明功能存在，不证明它适合你的规模。"], table: { headers: ["任务", "候选工具", "必须补的能力"], rows: [["入口/API 负载", "k6/Locust/JMeter", "任务终态轮询与业务 Oracle"], ["模型端点", "AIPerf/GenAI-Perf", "Agent 工具链和终态"], ["服务内部", "vLLM metrics/Prometheus", "端到端用户任务"], ["跨步骤追踪", "OpenTelemetry + Phoenix/Langfuse/LangSmith", "负载生成和容量判定"], ["质量判定", "自定义 evaluator/Promptfoo/DeepEval", "系统资源与排队"]] } },
      { title: "测试环境必须保护真实副作用", body: ["所有写工具先走沙箱；每个调用携带幂等键；夹具要模拟延迟、错误码、429 和超时，而不只是永远成功。对真实外部模型压测前确认额度、限流政策和费用上限。"], bullets: ["run_id 隔离测试数据和清理范围", "工具权限最小化，禁止真实付款/群发", "全局预算：最大任务数、Token、费用和运行时长", "失败即停：错误放大、队列失控或预算接近上限"] },
      { title: "每次运行都生成 Manifest", body: ["没有版本记录的两次压测不可比较。Manifest 至少包含代码提交、workflow/prompt/model/tool schema、workload、价格、环境、资源规格、限流和阈值版本。"], code: "run_id: ap-load-20260810-001\nworkflow_version: refund-agent-v12\nworkload_version: workload-v3\nmodel_endpoint: fixture-v1\ntool_schema_version: tools-v8\nthreshold_version: slo-v4\nprice_version: 2026-08-10\nseed: 42" },
    ],
    practice: ["画出四层架构和数据流", "为每层选择一个工具并写明缺口", "列出所有有副作用的工具及隔离方案"], completion: ["架构能替换真实依赖与夹具", "判定层同时检查质量、性能、成本和安全", "每次运行可由 Manifest 回放"], sourceIds: ["S52", "S67", "S70", "S77", "S78", "S79"], evidenceBoundary: "工具能力来自官方文档或项目仓库；没有在目标企业网络、数据量和合规环境中完成对比基准。",
  },
  {
    id: "TD-AP06", moduleId: "TD-M11", order: 0,
    title: "执行完整压测 SOP：基线、变坏、修复、容量",
    type: "跟做", status: "fixture-tested", duration: "75 分钟",
    summary: "运行离线 Agent 压测夹具，亲眼看到重试风暴如何让排队、p95、成本和 Goodput 同时恶化，再用预算与退避修复。",
    why: "看懂指标不等于能验证系统。这个实验强制经历绿色基线、故障注入红灯和修复复跑，证明门禁真的能发现问题。",
    prerequisites: ["TD-AP05"], outcomes: ["执行三阶段压测", "读取 JSONL Trace 和汇总报告", "用证据解释门禁为何红/绿"], artifact: "三阶段 Agent 压测证据包",
    blocks: [
      { title: "实验测什么", body: ["离线脚本模拟订单处置 Agent 的模型和工具步骤。retry-storm 场景提高工具失败率并允许激进重试；repaired 场景加入重试预算、退避和队列保护。随机种子固定，因此结果可复现。"], bullets: ["任务层：成功率、E2E p95、Goodput", "链路层：queue p95、model/tool calls、重试放大", "成本层：总成本、每成功任务成本", "门禁：质量、延迟、成本和放大系数同时满足"] },
      { title: "第一步：运行健康基线", body: ["在发布包根目录执行："], code: "python3 courses/td-ai-010-agent-load-stability/lab/agent_load_lab.py \\\n  --config courses/td-ai-010-agent-load-stability/lab/configs/baseline.json \\\n  --output courses/td-ai-010-agent-load-stability/evidence/baseline", expected: "退出码 0；gate_pass=true。报告包含 summary.json 和 traces.jsonl。" },
      { title: "第二步：注入重试风暴", body: ["坏版本应该稳定失败；非零退出码是预期证据。"], code: "python3 courses/td-ai-010-agent-load-stability/lab/agent_load_lab.py \\\n  --config courses/td-ai-010-agent-load-stability/lab/configs/retry-storm.json \\\n  --output courses/td-ai-010-agent-load-stability/evidence/retry-storm", expected: "退出码 1；至少 retry_amplification、task_success_rate、e2e_p95_ms 或 cost_per_success 超限。" },
      { title: "第三步：应用保护并复跑", body: ["修复不是删除阈值，而是限制重试、加入退避并在队列压力下拒绝或降级。"], code: "python3 courses/td-ai-010-agent-load-stability/lab/agent_load_lab.py \\\n  --config courses/td-ai-010-agent-load-stability/lab/configs/repaired.json \\\n  --output courses/td-ai-010-agent-load-stability/evidence/repaired", expected: "退出码 0；gate_pass=true。与坏版本相比，调用放大、排队和单位成功成本下降。" },
      { title: "第四步：按固定顺序读报告", body: ["先确认 workload 与版本相同，再看任务正确率和 Goodput，然后看 E2E/queue 分位数，再下钻 model/tool/retry，最后看资源和成本。不能先看到 CPU 不高就宣布系统健康。"], warning: "故障场景失败是测试通过；如果坏版本也绿，说明阈值、负载或故障注入没有检测力。" },
    ],
    practice: ["完成 baseline → retry-storm → repaired", "从 traces.jsonl 找出一条重试最多的任务", "修改一个阈值并解释它会防止哪类业务损失"], completion: ["三次运行退出码为 0/1/0", "报告保留相同 seed 和 workload", "能用 Trace 解释红灯而不是只引用总分"], sourceIds: commonSources, evidenceBoundary: "已运行确定性离线模拟器，证明采集、聚合和门禁机制；不调用真实模型、真实工具，也不代表生产容量。",
  },
  {
    id: "TD-AP07", moduleId: "TD-M11", order: 0,
    title: "诊断压测失败：从症状反推瓶颈与反馈环",
    type: "诊断", status: "desk-researched", duration: "60 分钟",
    summary: "用队列、TTFT、ITL、工具耗时、放大系数和资源信号区分容量不足、长上下文、工具慢、重试风暴与 Agent 循环。",
    why: "‘p95 变差’只是症状。错误归因会导致盲目加机器、降低阈值或增加重试，反而扩大成本和故障。",
    prerequisites: ["TD-AP06"], outcomes: ["按症状树定位根因候选", "识别协调遗漏和重试反馈环", "设计一次只改一个变量的验证实验"], artifact: "性能故障诊断记录",
    blocks: [
      { title: "先做相关，再做因果验证", body: ["把失败窗口与健康窗口按相同 workload 比较，定位从哪一层开始偏移。Trace 只能提供强线索；通过控制变量、依赖夹具或资源隔离复跑，才能提高因果置信度。"], table: { headers: ["症状组合", "优先假设", "下一步验证"], rows: [["queue↑, TTFT↑, GPU高", "模型容量/调度饱和", "固定长度，降低到达率或增加副本"], ["TTFT↑, 输入Token↑, queue平", "长上下文 Prefill", "按长度桶比较并裁剪上下文"], ["ITL↑, queue平, GPU高", "Decode 竞争", "固定输出长度与并发"], ["tool p95↑, retries↑, model平", "工具依赖慢并触发重试", "夹具固定工具延迟/错误率"], ["step count↑, tool/model均平", "Agent 循环或路由退化", "对比 workflow/prompt 与轨迹"], ["入口RPS平, 内部calls↑", "调用放大/重试风暴", "限制 attempts 并观察恢复"]] } },
      { title: "避免 Coordinated Omission", body: ["固定并发压测中，系统越慢，客户端完成越少，实际到达率随之下降。这会漏记用户本应在等待期间继续到达的请求。用开环到达率、记录计划发送时间，并报告队列等待，才能看见真实过载。"], expected: "同一系统用闭环和开环各跑一次；若闭环 p95 较好但吞吐下降，不能据此宣称容量更高。" },
      { title: "重试必须有总预算", body: ["单层 3 次重试看似合理；如果网关、Agent、SDK 和工具各重试 3 次，最坏尝试数会乘法增长。优先让最接近失败的一层重试，并遵守 Retry-After 或指数退避加抖动。失败请求也消耗限流额度和费用。"], code: "retry_budget_per_task: 2\nmax_total_task_ms: 12000\nrespect_retry_after: true\nbackoff: exponential_with_jitter\nretryable: [429, 502, 503]\nnon_retryable: [400, 401, 403, policy_violation]" },
      { title: "修复顺序：止血、定位、容量、长期预防", body: ["先停止放量并限制反馈环；再用 Trace 定位；然后选择扩容、缓存、裁剪上下文、并行工具、超时预算或降级；最后把事故样例加入 workload 和回归门禁。"], warning: "增加无限队列只会把错误变成更长等待；增加无限重试只会把局部失败变成全局过载。" },
    ],
    practice: ["从 retry-storm 报告写出三条证据链", "设计一个控制变量实验排除错误假设", "画出网关、SDK、Agent、工具四层重试乘法"], completion: ["诊断区分症状、假设和验证", "没有用平均延迟掩盖尾部", "修复没有删除质量或成本门禁"], sourceIds: ["S48", "S51", "S57", "S67", "S68", "S75"], evidenceBoundary: "诊断树基于公开指标语义与 SRE 机制，是优先级启发式；真实根因仍需目标系统 Trace、资源和变更证据。",
  },
  {
    id: "TD-AP08", moduleId: "TD-M11", order: 0,
    title: "把压测接入生产：SLO、告警、降级与 Runbook",
    type: "项目", status: "desk-researched", duration: "75 分钟",
    summary: "把一次性压测结果转成线上稳定性体系：多维 SLO、错误预算、分层告警、自动保护和可执行 Runbook。",
    why: "上线前压测只能证明某个环境、版本和工作负载下的表现。模型、Prompt、工具、流量和价格持续变化，生产必须持续监测质量、性能、成本与轨迹。",
    prerequisites: ["TD-AP07"], outcomes: ["定义多维 Agent SLO", "设计症状告警与原因面板", "写出限流、熔断、降级和回滚 Runbook"], artifact: "Agent 生产稳定性方案",
    blocks: [
      { title: "SLO 以用户任务为中心", body: ["建议把可用性定义为‘任务正确完成且满足时延、成本和安全预算’，并为高风险切片单独设 SLO。模型调用 99.9% 可用不能替代业务任务 SLO。"], code: "Task SLI = good_tasks / eligible_tasks\ngood_task = correct_terminal_state\n         && e2e_ms <= latency_budget(task_type)\n         && cost <= cost_budget(task_type)\n         && policy_pass\n         && no_duplicate_side_effect" },
      { title: "告警先报用户症状，再关联原因", body: ["Page 级告警用于需要立即行动的用户症状或错误预算快速燃烧；资源、TTFT、队列和工具延迟进入原因面板，除非它们本身有明确处置。使用快慢两个窗口可兼顾突发和持续劣化。"], table: { headers: ["级别", "信号", "触发示例", "动作"], rows: [["P1", "高风险任务错误/重复副作用", "任何确认事件或快速燃烧", "停止写工具、回滚/切人工"], ["P2", "Task SLO/Goodput", "5m 与 1h 窗口同时超预算", "停止放量、启用降级"], ["诊断", "queue/TTFT/tool/retry/cost", "与症状窗口关联", "定位容量或依赖"], ["趋势", "成本、长度、步骤漂移", "日/周趋势异常", "容量和 Prompt/流程优化"]] } },
      { title: "保护机制必须提前设计终态", body: ["限流、队列上限、超时、熔断、负载削减和降级不是简单返回错误。对 Agent 要定义：哪些任务可拒绝、哪些改成只读、哪些切小模型、哪些进入人工队列，以及已执行副作用如何补偿。"], bullets: ["入口：token bucket/并发配额，返回可重试信息", "Agent：最大步骤、最大模型调用、总时长和总费用", "依赖：每工具 timeout、circuit breaker、bulkhead", "降级：关闭非关键工具、缩短上下文、切只读或人工", "恢复：逐级放量，不在依赖刚恢复时瞬间重放全部积压"] },
      { title: "Runbook 必须能由当班人员执行", body: ["每条告警链接到：影响判定、首查面板、三条安全止血动作、回滚条件、数据查询、负责人和复盘资产。把一条真实慢 Trace 的查找命令写进去，而不是只写‘联系研发排查’。"], code: "alert: agent_goodput_burn_rate\ncheck:\n  - compare task_type/workflow_version/model_version\n  - inspect queue_p95, retry_amplification, dependency_p95\n  - open 3 slow/error trace_ids\nmitigate:\n  - freeze rollout\n  - cap retries and queue\n  - route risky write tasks to human\nrecover:\n  - verify 3 healthy windows\n  - canary 5% -> 25% -> 100%\npostmortem:\n  - add incident trace to workload and regression gate" },
      { title: "形成发布前后闭环", body: ["离线压测发现容量边界，预发布复跑候选版本，线上 SLO 发现分布漂移，事故 Trace 回流为新切片。四者共用指标字典、Trace Schema、workload 版本和门禁定义，才能避免压测与监控各说各话。"], expected: "最终方案能从一条线上告警追溯到 Trace、版本、离线回归样例和负责人。" },
    ],
    practice: ["定义一个高风险和一个普通任务 SLO", "为重试风暴写告警与三步止血 Runbook", "把实验中的坏 Trace 加入回归 workload"], completion: ["SLO 分母和 good task 条件明确", "告警对应具体人和动作", "降级不会扩大权限或重复副作用", "事故能回流为可复现回归"], sourceIds: ["S47", "S48", "S70", "S71", "S75", "S76"], evidenceBoundary: "SLO 与 Runbook 模板来自通用 SRE 和 GenAI 可观测性实践；业务影响等级、阈值、值班责任和合规要求必须由组织确认。",
  },
];
