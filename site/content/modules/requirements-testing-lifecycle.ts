import type { TutorialPage } from "../course.ts";

const commonBoundary = "本专题使用虚构的订单取消与退款资料包验证工件结构和离线流水线。它能证明流程可运行、冲突能阻断、预埋缺陷能被测试发现；不能证明模型能正确理解你公司的全部文档，也不能替代产品、研发、法务和发布责任人的确认。";

export const requirementsTestingLifecyclePages: TutorialPage[] = [
  {
    id: "TD-P01",
    moduleId: "TD-M00",
    order: 0,
    title: "先冻结测试依据：别让 AI 读一堆互相打架的文档",
    type: "跟做",
    status: "desk-researched",
    duration: "45 分钟",
    summary: "把 PRD、技术方案、接口契约、状态模型和术语表整理成有版本、有优先级、可引用的 Test Basis Pack。",
    why: "模型可以很快归纳多份文档，但它不知道哪份已经过期，也没有权力替团队决定冲突规则。输入版本和来源优先级不清楚，后面的测试用例越完整，返工越大。",
    prerequisites: ["TD-F01"],
    outcomes: ["建立可复现的文档输入包", "为每段内容分配稳定引用", "在冲突未解决时停止下游生成"],
    artifact: "Test Basis Pack 与 source-manifest.json",
    blocks: [
      {
        title: "先明确这次到底要测哪个版本",
        body: [
          "贯穿案例是订单取消：买家可以取消未发货订单；已支付订单取消后异步退款。这里故意放入一条冲突——PRD 禁止已发货订单取消，旧技术方案却仍写着 SHIPPED 可取消。正确结果不是让模型选一个更合理的说法，而是把该条标成 BLOCKED。",
          "最小输入包包含 PRD、技术方案、OpenAPI、状态机、业务术语表、变更范围和历史缺陷。每份文件记录版本、责任人、有效期、敏感等级和内容哈希。网页链接不能只保存当前地址，还要保存访问日期或提交版本。",
        ],
        table: {
          headers: ["输入", "必须记录", "下游用途"],
          rows: [
            ["PRD", "版本、段落 ID、产品 owner", "业务目标、范围、规则"],
            ["技术方案", "提交 SHA、接口/状态引用、技术 owner", "实现约束、依赖、副作用"],
            ["OpenAPI/事件 Schema", "规范版本、文件 hash", "请求、响应、错误和契约测试"],
            ["历史缺陷", "缺陷 ID、影响版本、复现证据", "风险权重与回归集"],
          ],
        },
      },
      {
        title: "给文档加上模型能引用的坐标",
        body: ["不要把一个 80 页 PDF 直接丢给模型。先按标题和语义段落切分，并分配不可变的 source_ref，例如 PRD-v3#R17、TECH-a13f#S04。模型输出的每条事实必须引用这些坐标。"],
        code: `{
  "baseline_id": "order-cancel-2026-08-10",
  "sources": [
    {"id":"PRD-v3","type":"prd","owner":"product-a","sha256":"…","precedence":1},
    {"id":"TECH-a13f","type":"design","owner":"tech-b","sha256":"…","precedence":2},
    {"id":"OPENAPI-v7","type":"contract","owner":"service-c","sha256":"…","precedence":3}
  ],
  "precedence_rule": "业务语义由已批准 PRD 决定；实现细节由当前技术方案和接口契约决定；任意语义冲突必须进入评审，不得自动覆盖"
}`,
        expected: "任何人拿到 manifest，都能确认模型读了哪些文件、哪个版本，以及某条结论来自哪个段落。",
      },
      {
        title: "把模型权限写进任务，不要靠一句‘请勿幻觉’",
        body: ["提取 Agent 只能做信息抽取、分类和候选冲突识别。它不能新增退款政策、性能阈值或状态转换。缺失信息输出 UNKNOWN；多源冲突输出 BLOCKED；两者都不能进入测试生成。"],
        code: `角色：需求证据提取器。你只整理已提供的资料，不决定业务规则。

输入：source-manifest、带 source_ref 的 PRD/技术方案/OpenAPI。
规则：
1. 每项事实必须给出 source_refs；没有引用则删除该事实。
2. 文档没有说明的内容写入 unknowns，不得补写。
3. 两个有效来源冲突时写入 conflicts，status=BLOCKED。
4. 只输出给定 JSON Schema；不要输出摘要、建议或测试用例。
5. 不处理任何生产密钥、真实支付账号或未脱敏个人信息。`,
        warning: "‘综合判断后采用更合理规则’会抹掉冲突，也会把模型变成没有授权的产品负责人。",
      },
      {
        title: "门禁：输入不合格时就停在这里",
        body: ["进入下一页之前，至少检查：文件可访问、版本唯一、来源坐标稳定、优先级规则已确认、敏感数据已处理。关键文件缺失或冲突责任人不明确时，状态保持 BLOCKED。"],
        code: "cd courses/td-ai-011-requirements-to-evidence/lab\npython3 pipeline.py validate-basis",
        expected: "干净夹具返回 PASS；运行 `python3 pipeline.py inject-doc-conflict` 后再次验证，返回 BLOCKED 并列出 PRD-v3#R17 与 TECH-a13f#S04。",
      },
    ],
    practice: ["把一份脱敏 PRD 和一份技术方案切成稳定 source_ref", "写出来源优先级和冲突升级责任人", "故意加入一条冲突并确认流水线停止"],
    completion: ["每份输入有版本、owner、hash 和敏感等级", "任一结论可回到具体段落", "冲突不会被模型静默合并"],
    sourceIds: ["S41", "S42", "S81", "S85"],
    evidenceBoundary: commonBoundary,
  },
  {
    id: "TD-P02",
    moduleId: "TD-M00",
    order: 0,
    title: "把自然语言变成需求契约：让下游程序能直接消费",
    type: "跟做",
    status: "desk-researched",
    duration: "55 分钟",
    summary: "用受约束的模型输出 Requirement Contract，明确角色、状态、不变量、异常、副作用、非功能要求和未知项。",
    why: "一段‘需求摘要’不能直接生成可靠测试。下游需要稳定字段、可追溯引用和停止状态，才能判断哪些规则可测、哪些规则仍待确认。",
    prerequisites: ["TD-P01"],
    outcomes: ["定义 Requirement Contract", "区分事实、推断、未知与冲突", "校验结构正确不等于语义正确"],
    artifact: "requirement-contract.json 与校验结果",
    blocks: [
      {
        title: "先定义下游需要什么，再让模型提取",
        body: ["字段不是为了让 JSON 看起来专业，而是为了支持后续风险分析、用例生成、执行和变更回归。订单取消至少要明确参与者、前置状态、触发、状态变化、拒绝路径、退款副作用、幂等不变量、接口和待确认项。"],
        code: `{
  "requirement_id": "REQ-CANCEL-001",
  "status": "ACCEPTED|UNKNOWN|BLOCKED",
  "statement": "已支付且未发货的订单允许买家取消，并创建一次退款请求",
  "actors": ["BUYER"],
  "preconditions": ["payment_status=PAID", "shipment_status=NOT_SHIPPED"],
  "trigger": "POST /orders/{order_id}/cancel",
  "state_transitions": ["PAID->CANCEL_PENDING", "CANCEL_PENDING->CANCELLED"],
  "invariants": ["refund_count<=1", "refund_total<=captured_amount"],
  "exceptions": ["SHIPPED->409", "non-owner->403"],
  "side_effects": ["emit refund.requested"],
  "nfrs": [],
  "unknowns": ["退款完成时限未定义"],
  "source_refs": ["PRD-v3#R17", "OPENAPI-v7#/cancel"]
}`,
      },
      {
        title: "结构化输出只解决格式，不保证业务语义",
        body: ["支持 JSON Schema 的模型可以减少缺字段和类型错误；它仍可能把原文理解错。提取后要运行结构校验，再由独立评审 Agent 或人工逐项核对来源。关键金额、权限和状态 Oracle 必须由领域 owner 确认。"],
        bullets: [
          "schema 校验：字段、类型、枚举、必填项是否正确",
          "引用校验：source_refs 是否存在于当前 baseline",
          "语义校验：statement 和不变量是否得到原文支持",
          "权限校验：AI 是否越权补充了业务决定",
        ],
      },
      {
        title: "可复制的提取任务",
        body: ["System Prompt 固定权限和失败语义；Task Prompt 只传当前 baseline、输出 schema 和待处理段落。不要把生成测试用例混在同一个调用里。"],
        code: `任务：从 INPUT_SOURCES 提取 RequirementContract[]。

输出要求：
- 严格遵守 REQUIREMENT_CONTRACT_SCHEMA。
- statement、preconditions、transitions、invariants、exceptions 的每一项都要绑定 source_refs。
- 文档没有定义的 SLA、重试、金额、权限、状态不得推断；放入 unknowns。
- 有效来源冲突时 status=BLOCKED，并输出 conflict_id、source_refs、impact、owner_needed。
- 不生成测试用例，不建议产品规则，不修改原文。

完成后再做一次自检：列出任何无法由引用支持的字段；若存在，将该字段删除或改为 UNKNOWN。`,
        expected: "输出可以被校验器读取；缺引用、非法状态或静默补规则都会失败。",
      },
      {
        title: "用坏契约验证门禁有牙齿",
        body: ["教学夹具先验证已批准契约，再删除一条关键 source_ref。结构仍然是合法 JSON，但证据门禁应失败。"],
        code: "python3 pipeline.py reset\npython3 pipeline.py validate-contract\npython3 pipeline.py inject-unsupported-rule\npython3 pipeline.py validate-contract",
        expected: "第一次 PASS；注入后返回 BLOCKED，并指出 REQ-CANCEL-001 的 `refund_timeout_hours` 没有来源。",
        warning: "模型能输出正确 JSON，只说明传输契约成立；不能据此宣称需求已经正确。",
      },
    ],
    practice: ["为自己的业务补一条状态转换和一条不变量", "加入一个文档未定义的字段并确认校验失败", "让产品 owner 只评审关键业务语义而不是整段模型解释"],
    completion: ["Requirement Contract 能被程序读取", "每个关键规则有来源或明确 UNKNOWN", "结构通过与业务确认被分成两道门禁"],
    sourceIds: ["S41", "S66", "S81", "S85"],
    evidenceBoundary: commonBoundary,
  },
  {
    id: "TD-P03",
    moduleId: "TD-M00",
    order: 0,
    title: "需求评审不是让 AI 总结：要把歧义、冲突和不可测项逼出来",
    type: "诊断",
    status: "desk-researched",
    duration: "45 分钟",
    summary: "让独立评审角色检查需求契约，形成带影响、责任人和关闭条件的 Review Question Pack。",
    why: "测试最早产生价值的地方，是在代码提交前发现不可测试规则。泛泛的‘建议补充异常场景’不会推动决策，问题必须指向来源、失败影响和需要谁回答。",
    prerequisites: ["TD-P02"],
    outcomes: ["识别五类可测试性缺口", "生成可关闭的评审问题", "传播 BLOCKED 而不是强行生成用例"],
    artifact: "review-questions.json 与评审决议记录",
    blocks: [
      {
        title: "五类问题要分开处理",
        body: ["评审 Agent 不复述需求，而是检查：歧义、来源冲突、缺失分支、不可观察结果和未定义非功能要求。每个问题记录严重性、影响的需求、来源、回答人和关闭证据。"],
        table: {
          headers: ["类型", "订单取消例子", "不解决的后果"],
          rows: [
            ["冲突", "SHIPPED 是否可取消", "同一版本出现相反断言"],
            ["未知", "退款最晚何时完成", "无法设计时限与告警"],
            ["不可观察", "‘取消成功’没有账本/事件定义", "只能断言 HTTP 200"],
            ["副作用缺失", "重复请求是否重复退款", "资金损失"],
            ["责任缺失", "谁批准退款例外", "Waiver 无人承担"],
          ],
        },
      },
      {
        title: "问题要能被回答和关闭",
        body: ["‘请完善需求’没有用。一个合格问题包含：问题、冲突证据、业务影响、候选选项、不得由 AI 决定的部分、责任人、截止时间和关闭后的契约变更。"],
        code: `{
  "question_id": "RQ-007",
  "requirement_ids": ["REQ-CANCEL-001"],
  "type": "SOURCE_CONFLICT",
  "question": "订单进入 SHIPPED 后是否仍允许取消？",
  "source_refs": ["PRD-v3#R17", "TECH-a13f#S04"],
  "impact": "决定 409 拒绝用例、退款副作用与仓配状态回滚",
  "owner": "product-owner-order",
  "status": "OPEN",
  "close_with": "批准后的 PRD 段落和 Requirement Contract 新版本"
}`,
      },
      {
        title: "把评审角色与提取角色分开",
        body: ["提取 Agent 容易延续自己的理解。评审角色只接收原始引用和契约，任务是找反例、缺失与越权字段。高风险问题交给产品、技术、数据或安全责任人，AI 不投票决定。"],
        code: `你是需求可测试性审查员，不负责重写需求。
逐项检查：来源冲突、状态缺口、异常与重试、幂等、副作用、权限、数据、NFR、可观察 Oracle。
输出 ReviewQuestion[]。每个问题必须包含 source_refs、impact、owner、block_level、close_with。
如果问题会改变关键 Oracle、资金、权限或发布判断，block_level=RELEASE_BLOCKER。`,
      },
      {
        title: "关闭问题后要产生新版本，不能改掉历史",
        body: ["评审决议生成新的 Requirement Contract 和 baseline_version，旧版本标成 SUPERSEDED。这样测试、执行报告和线上缺陷都能解释自己基于哪版规则。"],
        expected: "关闭 RQ-007 后，REQ-CANCEL-001 v2 明确 SHIPPED 返回 409；旧契约仍可审计，但不能被新测试包引用。",
      },
    ],
    practice: ["从自己的文档中找一条不可观察的成功条件", "把‘请完善’改成有 owner 和关闭证据的问题", "检查关键问题未关闭时下游是否确实停止"],
    completion: ["每个问题有来源、影响和责任人", "RELEASE_BLOCKER 不会被生成流程跳过", "关闭决议产生新版本而非覆盖历史"],
    sourceIds: ["S41", "S42", "S81", "S82"],
    evidenceBoundary: commonBoundary,
  },
  {
    id: "TD-P04",
    moduleId: "TD-M00",
    order: 0,
    title: "从需求契约到风险策略：决定测什么、在哪一层测",
    type: "概念",
    status: "desk-researched",
    duration: "50 分钟",
    summary: "把已确认需求映射到业务风险、测试目标、测试层级、Oracle、监控和残余风险责任人。",
    why: "AI 很容易生成几十条格式工整的用例，却不会自动知道哪项失败会造成资金损失，也不会替团队承担测试不足的风险。先做风险策略，才能控制范围和测试层级。",
    prerequisites: ["TD-P03"],
    outcomes: ["建立风险到测试的映射", "避免全部堆到 E2E", "为高风险定义测试、监控和处置"],
    artifact: "risk-test-plan.json 与测试层级决策表",
    blocks: [
      {
        title: "先写失败影响，再写测试类型",
        body: ["订单取消的主要风险不是‘接口报错’，而是重复退款、越权取消、已发货仍取消、状态和账本不一致、事件丢失。每项风险记录触发、影响、暴露面和责任人。"],
        code: `{
  "risk_id": "RISK-REFUND-DUPLICATE",
  "requirement_ids": ["REQ-CANCEL-001"],
  "failure": "重试或并发请求创建两笔退款",
  "impact": "资金损失与账务对账失败",
  "severity": "CRITICAL",
  "test_levels": ["unit", "service-integration", "contract"],
  "oracles": ["refund_count<=1", "refund_total<=captured_amount"],
  "monitoring": ["duplicate_refund_block_total", "refund_amount_mismatch_total"],
  "owner": "payments-quality-owner"
}`,
      },
      {
        title: "让测试层级承担不同证据",
        body: ["状态不变量和权限矩阵优先在单元/组件层快速覆盖；OpenAPI 和事件 Schema 用契约测试；数据库、消息和支付网关用服务集成；少量关键用户旅程进入 E2E。不要为了‘更真实’把所有组合都塞进浏览器。"],
        table: {
          headers: ["层级", "本例验证", "失败定位"],
          rows: [
            ["单元/属性", "状态机、不变量、金额边界", "业务规则"],
            ["契约", "409/403、事件字段、兼容性", "消费者/提供者契约"],
            ["集成", "事务、消息、支付重试", "依赖与一致性"],
            ["E2E", "买家取消到退款可见", "关键旅程"],
            ["生产监控", "重复退款和卡住状态", "真实分布与长尾"],
          ],
        },
      },
      {
        title: "AI 生成候选策略，人决定取舍",
        body: ["可以让模型依据契约、历史缺陷和架构生成候选风险，再由测试架构师合并、排序和选择层级。输出必须说明为什么选择、为什么不选择，以及残余风险由谁接受。"],
        code: `输入：ACCEPTED RequirementContract、架构图、历史缺陷、变更范围。
输出：RiskTestPlan[]。
要求：
- 每个 risk_id 绑定 requirement_ids 和 source_refs；
- 给出 failure、impact、test_levels、oracle、data、monitoring、owner；
- 说明未选择 E2E 或未覆盖组合的理由；
- 不编造严重性定义和阈值，缺失时标 UNKNOWN；
- 高风险没有 oracle、监控或 owner 时 status=BLOCKED。`,
      },
      {
        title: "策略门禁看覆盖关系，不看用例数量",
        body: ["至少检查：每个关键需求是否映射到风险；每个高风险是否映射到测试、Oracle、监控和处置；每个测试是否能说明自己保护什么。用例数量本身不是质量信号。"],
        warning: "‘生成 100 条测试用例’会鼓励重复和低价值组合；课程不使用数量作为完成标准。",
      },
    ],
    practice: ["为订单取消补一个安全风险和一个稳定性风险", "把一个 E2E 用例下沉到更合适的层级", "写出一项明确接受的残余风险及 owner"],
    completion: ["关键风险都有测试与 Oracle", "层级选择有理由", "高风险同时有监控和责任人"],
    sourceIds: ["S41", "S43", "S45", "S82"],
    evidenceBoundary: commonBoundary,
  },
  {
    id: "TD-P05",
    moduleId: "TD-M00",
    order: 0,
    title: "生成测试之前先固定 Oracle：否则 AI 只会生成自洽答案",
    type: "跟做",
    status: "desk-researched",
    duration: "60 分钟",
    summary: "从风险策略生成可执行测试模型，明确数据、动作、精确 Oracle、容差、清理和证据要求。",
    why: "同一个模型根据自己理解的需求生成代码和断言，错误规则也可能一起通过。关键业务结果必须依赖独立契约、状态不变量、账本或人工确认样例。",
    prerequisites: ["TD-P04"],
    outcomes: ["区分精确与概率 Oracle", "生成可追溯测试包", "用负控制证明测试有检测力"],
    artifact: "test-package.json、数据夹具和 Oracle 清单",
    blocks: [
      {
        title: "一个测试项需要的不只是步骤和预期结果",
        body: ["可执行 TestPackage 至少包含测试 ID、需求/风险映射、层级、前置数据、动作、Oracle、清理、证据和适用版本。对订单取消，HTTP 200 不是关键 Oracle；账本金额、退款次数、状态和事件才是。"],
        code: `{
  "test_id": "T-CANCEL-IDEMPOTENT-01",
  "requirement_ids": ["REQ-CANCEL-001"],
  "risk_ids": ["RISK-REFUND-DUPLICATE"],
  "fixture": {"order":"PAID_NOT_SHIPPED", "idempotency_key":"idem-001"},
  "actions": ["POST cancel", "POST cancel with same key"],
  "oracles": [
    "response[0].status=202",
    "response[1].refund_id=response[0].refund_id",
    "refund_operation_count(order_id)=1",
    "refund_total=captured_amount"
  ],
  "evidence": ["responses", "ledger_rows", "events", "trace_id"]
}`,
      },
      {
        title: "Oracle 分层，别把所有判断交给 LLM Judge",
        body: ["确定性业务规则使用精确断言、数据库不变量或契约校验。文本语义才考虑规则评分、模型 Judge 和人工抽查；Judge 要用人工标签校准，并保存版本与不确定状态。"],
        bullets: [
          "精确 Oracle：金额、状态、权限、次数、Schema、事件顺序",
          "属性/变形 Oracle：重复请求不增加副作用；输入顺序变化不改变总额",
          "统计 Oracle：失败率、延迟分位数、波动区间",
          "语义 Oracle：评分规则、独立 Judge、人工标签与 UNKNOWN 区间",
        ],
      },
      {
        title: "让模型生成候选，不让它删除证据",
        body: ["生成任务要接收已批准契约和风险计划，只生成指定层级的 TestPackage。每条测试必须说明保护的风险和所需证据；无法定义 Oracle 时输出 BLOCKED_TEST，不得退化为‘检查结果是否正确’。"],
        code: `依据 RequirementContract v2 和 RiskTestPlan 生成 TestPackage[]。
约束：
1. 每个测试绑定 requirement_ids、risk_ids、test_level。
2. 必须给出 fixture、actions、oracles、cleanup、evidence。
3. 金额、权限、状态和副作用优先使用确定性 Oracle。
4. 不得从被测实现反向推导预期结果。
5. 无独立 Oracle 时 status=BLOCKED_TEST，并说明需要哪个 owner。`,
      },
      {
        title: "先植入缺陷，再相信这组测试",
        body: ["教学实验会把已发货订单错误地改为可取消。测试包必须稳定变红，并把失败归到 REQ-CANCEL-002 与状态不变量，而不是只给一段‘可能存在业务问题’。"],
        code: "python3 pipeline.py reset\npython3 pipeline.py generate-tests\npython3 pipeline.py inject-code-defect\npython3 pipeline.py execute",
        expected: "执行返回 FAIL；T-CANCEL-SHIPPED-01 指出期望 409、实际 202，并保存 mutation_id、输入 hash 和运行日志。",
      },
    ],
    practice: ["把一个‘检查结果正确’改成可执行 Oracle", "为幂等和并发各写一条独立不变量", "植入一个错误实现并确认测试稳定失败"],
    completion: ["每个测试保护明确风险", "关键 Oracle 不依赖生成实现的同一模型", "至少一个负控制被可靠发现"],
    sourceIds: ["S41", "S45", "S87", "S07"],
    evidenceBoundary: commonBoundary,
  },
  {
    id: "TD-P06",
    moduleId: "TD-M00",
    order: 0,
    title: "把测试包接到自动化：接口、契约、集成和 UI 各自负责什么",
    type: "跟做",
    status: "desk-researched",
    duration: "65 分钟",
    summary: "把 TestPackage 转成测试骨架和适配器，并保持需求、风险、Oracle 与执行代码之间的追溯。",
    why: "直接让 AI 从 PRD 写 Playwright 脚本，往往把所有场景塞进 UI，还会基于当前页面行为生成错误断言。先有测试包，再选择执行适配器，代码才有稳定的业务依据。",
    prerequisites: ["TD-P05"],
    outcomes: ["为测试选择合适适配器", "生成后做静态与运行审查", "保留代码到契约的双向追溯"],
    artifact: "自动化测试骨架、adapter contract 与追溯索引",
    blocks: [
      {
        title: "生成代码前固定适配器边界",
        body: ["API 适配器负责请求和响应证据；数据库/事件适配器只读验证副作用；UI 适配器只覆盖用户可见关键路径。生产退款、取消和扣款等动作不得由教学 Agent 直接执行。"],
        table: {
          headers: ["适配器", "允许动作", "禁止动作"],
          rows: [
            ["API sandbox", "测试账号、幂等键、录制响应", "真实支付凭证"],
            ["DB evidence", "只读查询测试 schema", "修改生产账本"],
            ["Event probe", "订阅测试 topic", "向生产 topic 发事件"],
            ["Browser", "测试环境关键旅程", "绕过权限做副作用"],
          ],
        },
      },
      {
        title: "给代码生成 Agent 的输入必须是已批准工件",
        body: ["Playwright 的 planner、generator、healer 分工说明了计划、生成和修复可以拆开；但生成测试仍可能有错误或被跳过。课程进一步要求：生成器只接收 ACCEPTED TestPackage，不从当前实现猜预期。"],
        code: `输入：TestPackage、OpenAPI v7、adapter contract、测试环境变量清单。
输出：pytest/Playwright 测试骨架与 traceability-index.json。
要求：
- 每个测试函数标注 test_id、requirement_ids、risk_ids；
- Oracle 原样来自 TestPackage，不得根据实际响应改写；
- 失败必须保存 request_id、trace_id、响应和依赖状态；
- 禁止 skip、宽泛 try/except、固定 sleep 和删除失败断言；
- 只能调用允许的 sandbox 工具。`,
      },
      {
        title: "代码审查要找假绿模式",
        body: ["静态审查搜索空断言、只断言状态码、吞异常、自动重试后只报最终成功、条件性 skip 和 mock 自证。运行审查则植入权限、状态、重复副作用和依赖超时缺陷。"],
        bullets: [
          "断言是否来自 TestPackage，而不是复制实际返回",
          "失败是否保留原始证据和每次重试",
          "测试是否真的触发目标风险，而非只验证 mock 调用",
          "选择性执行和 skip 是否进入报告",
        ],
      },
      {
        title: "追溯索引让变更可以选择回归集",
        body: ["生成代码后保存 `test_id -> file/function -> requirement_ids -> risk_ids -> oracle_ids`。PRD、接口或实现变更时先更新影响集，再运行命中的测试；不能只按文件名猜回归范围。"],
        expected: "修改 REQ-CANCEL-001 后，可以列出受影响的契约、用例、自动化函数和上一次执行证据。",
      },
    ],
    practice: ["为一个 TestPackage 选择 API/契约/集成/UI 层", "审查一段只有 HTTP 200 的假绿测试", "生成一份 test_id 到代码函数的追溯索引"],
    completion: ["自动化代码不改变业务 Oracle", "高风险副作用只在隔离环境执行", "任一函数能回溯需求与风险"],
    sourceIds: ["S01", "S44", "S45", "S85"],
    evidenceBoundary: commonBoundary,
  },
  {
    id: "TD-P07",
    moduleId: "TD-M00",
    order: 0,
    title: "执行、收集、归因：一次绿色结果需要哪些证据",
    type: "诊断",
    status: "desk-researched",
    duration: "55 分钟",
    summary: "运行版本化测试包，保存 Run Manifest、原始日志、Trace、依赖状态、重试和失败分类。",
    why: "绿色截图无法证明测了哪个版本、是否跳过用例、是否因重试碰巧通过。执行结果只有连同输入、环境和原始证据一起保存，才能支持缺陷归因和发布判断。",
    prerequisites: ["TD-P06"],
    outcomes: ["生成可复现 Run Manifest", "区分产品失败、测试失败和环境阻塞", "禁止重试掩盖波动"],
    artifact: "run-manifest.json、原始日志与缺陷候选",
    blocks: [
      {
        title: "运行前先把版本钉住",
        body: ["Run Manifest 记录代码/镜像、需求 baseline、TestPackage、数据、依赖、模型/Prompt（如果参与）、环境和命令。任一关键版本缺失时，结果是 NOT_RUN 或 BLOCKED，不是 PASS。"],
        code: `{
  "run_id":"RUN-20260810-001",
  "code_sha":"7a31…",
  "baseline_id":"order-cancel-v2",
  "test_package_hash":"b82f…",
  "fixture_hash":"f104…",
  "environment":"local-sandbox",
  "command":"python3 pipeline.py execute",
  "retry_policy":"none",
  "selected_test_ids":["T-CANCEL-SHIPPED-01","T-CANCEL-IDEMPOTENT-01"]
}`,
      },
      {
        title: "失败先分类，修复 Agent 才能被约束",
        body: ["至少区分 PRODUCT_FAIL、TEST_FAIL、ENV_BLOCKED、DEPENDENCY_BLOCKED、UNKNOWN。没有足够证据时保持 UNKNOWN；不要让 healer 为了转绿直接改断言、加 skip 或放宽阈值。"],
        table: {
          headers: ["状态", "例子", "下一步"],
          rows: [
            ["PRODUCT_FAIL", "SHIPPED 返回 202", "建缺陷，保留 mutation/trace"],
            ["TEST_FAIL", "测试数据未创建", "修测试夹具，不改业务 Oracle"],
            ["ENV_BLOCKED", "服务未启动", "恢复环境后重跑"],
            ["UNKNOWN", "响应缺失且无 trace", "补证据，不做发布结论"],
          ],
        },
      },
      {
        title: "跑完整的 PASS → FAIL → PASS",
        body: ["离线实验使用同一份契约和测试包，先运行正常实现，再植入‘已发货可取消’缺陷，最后恢复。三次运行各自保存 manifest 和结果。"],
        code: "python3 pipeline.py reset\npython3 pipeline.py execute --report reports/baseline.json\npython3 pipeline.py inject-code-defect\npython3 pipeline.py execute --report reports/mutation.json\npython3 pipeline.py repair\npython3 pipeline.py execute --report reports/repair.json",
        expected: "baseline=PASS，mutation=FAIL，repair=PASS；mutation 报告包含测试 ID、期望 409、实际 202、代码版本和原始证据。",
      },
      {
        title: "结果收集不是生成一段总结",
        body: ["报告要保留原始结果、未运行项、重试次数、选择理由、覆盖关系和 artifact hash。AI 可以聚类相似失败、生成缺陷草稿；发布 owner 必须能打开原始证据，并知道哪些结论仍是推断。"],
        warning: "‘最终全部通过’若没有 selected tests、skipped、retry 和版本信息，只能算展示文字。",
      },
    ],
    practice: ["给一次运行补齐 code/baseline/data/test hash", "制造环境失败并确认状态是 BLOCKED 而不是 FAIL", "检查重试是否记录每次结果"],
    completion: ["运行结果可在同一夹具上复现", "失败状态不会被强制二值化", "原始证据足以支持缺陷归因"],
    sourceIds: ["S01", "S42", "S49", "S89"],
    evidenceBoundary: commonBoundary,
  },
  {
    id: "TD-P08",
    moduleId: "TD-M00",
    order: 0,
    title: "变更回归与发布判断：把整条证据链串起来",
    type: "项目",
    status: "fixture-tested",
    duration: "90 分钟",
    summary: "完成从 Test Basis、需求契约、评审、风险、测试包、执行证据到回归和发布决策的离线项目。",
    why: "这条链路的价值不在于第一次生成多少用例，而在于需求、接口、代码或模型变化后，能否知道哪些证据过期、该重跑什么、谁接受残余风险。",
    prerequisites: ["TD-P07"],
    outcomes: ["运行端到端离线证据链", "验证文档冲突与产品缺陷两类阻断", "生成有责任人与边界的发布建议"],
    artifact: "Requirements-to-Evidence Capstone 与三态运行证据",
    blocks: [
      {
        title: "你将交付的不是一份长文，而是九个可连接工件",
        body: ["依次产生 Test Basis Pack、Requirement Contract、Review Question Pack、Risk Test Plan、TestPackage、自动化代码/追溯索引、Run Manifest、Evidence Pack 和 Impact Set。每个工件都有 parent IDs、版本、owner、状态和下游消费者。"],
        code: "Test Basis -> Requirement Contract -> Review Questions\n           -> Risk Test Plan -> TestPackage -> Executable Tests\n           -> Run Manifest -> Evidence Pack -> Impact Set",
      },
      {
        title: "先证明输入冲突会阻断",
        body: ["重置后注入旧技术方案冲突。流水线必须停在需求评审之前，不能继续生成测试。"],
        code: "cd courses/td-ai-011-requirements-to-evidence/lab\npython3 pipeline.py reset\npython3 pipeline.py inject-doc-conflict\npython3 pipeline.py all",
        expected: "exit 2；status=BLOCKED；报告列出冲突来源和需要产品 owner 决定的问题；tests 目录不生成新产物。",
      },
      {
        title: "再证明测试能发现已知产品缺陷",
        body: ["恢复已批准文档，生成测试并运行正常实现；然后植入已发货可取消缺陷。"],
        code: "python3 pipeline.py reset\npython3 pipeline.py all --report reports/baseline.json\npython3 pipeline.py inject-code-defect\npython3 pipeline.py all --report reports/mutation.json",
        expected: "baseline exit 0；mutation exit 1；失败明确映射到 REQ-CANCEL-002、RISK-INVALID-STATE 和 T-CANCEL-SHIPPED-01。",
      },
      {
        title: "修复后生成发布证据，而不是自动批准",
        body: ["修复实现并重跑。Evidence Pack 汇总覆盖、失败、未决问题、环境、工件 hash 和残余风险。离线课程只输出 RELEASE_CANDIDATE；真实 Go/No-Go 仍需要具名责任人。"],
        code: "python3 pipeline.py repair\npython3 pipeline.py all --report reports/repair.json\npython3 pipeline.py evidence",
        expected: "repair exit 0；Evidence Pack 显示三态证据完整，但明确标注 synthetic fixture、not production validated、human release decision required。",
      },
      {
        title: "最后做一次变更影响分析",
        body: ["把 OpenAPI 的 409 响应 Schema 改成新版本。Impact Set 应命中需求契约、契约测试、API 自动化和发布证据；未命中的测试要保留选择理由。文件名相邻不等于业务影响。"],
        bullets: ["需求/技术文档变化：重做提取、评审和风险映射", "API/事件 Schema 变化：重做契约与消费者测试", "代码/配置变化：按依赖图选择回归集", "模型/Prompt/工具变化：旧 AI 评测证据不能自动继承"],
      },
    ],
    practice: ["完整保存 BLOCKED、FAIL、PASS 三种结果", "新增一个未授权取消的 mutation", "为一次接口契约变更生成 Impact Set"],
    completion: ["文档冲突阻断且不生成下游测试", "代码缺陷能稳定变红并正确归因", "修复后生成可审计但不越权的发布候选"],
    sourceIds: ["S41", "S42", "S66", "S81", "S82", "S07"],
    evidenceBoundary: commonBoundary,
  },
];
