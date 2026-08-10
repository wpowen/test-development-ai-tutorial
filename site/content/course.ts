export type TutorialBlock = {
  title: string;
  body: string[];
  bullets?: string[];
  code?: string;
  expected?: string;
  warning?: string;
};

export type TutorialPage = {
  id: string;
  moduleId: string;
  order: number;
  title: string;
  type: "概念" | "跟做" | "诊断" | "参考" | "项目";
  status: "planned" | "desk-researched" | "fixture-tested";
  duration: string;
  summary: string;
  why: string;
  prerequisites: string[];
  outcomes: string[];
  artifact: string;
  blocks: TutorialBlock[];
  practice: string[];
  completion: string[];
  sourceIds: string[];
  evidenceBoundary: string;
};

export const modules = [
  { id: "TD-M01", title: "先建立共同语言", subtitle: "理解 AI 为什么改变测试对象、断言和测试数据" },
  { id: "TD-M02", title: "AI 帮你做传统测试", subtitle: "用 AI 提效，但必须证明生成结果有检测力" },
  { id: "TD-M03", title: "测试 LLM 和 RAG", subtitle: "把概率性回答变成可重复、可审计的质量证据" },
  { id: "TD-M04", title: "测试 Agent", subtitle: "检查轨迹、工具、权限、安全与自愈风险" },
  { id: "TD-M05", title: "建设 AI 质量系统", subtitle: "把评测接入 CI、生产反馈、版本与回滚体系" },
] as const;

const planned = (
  id: string,
  moduleId: string,
  order: number,
  title: string,
  type: TutorialPage["type"],
  summary: string,
  artifact: string,
  prerequisites: string[],
): TutorialPage => ({
  id,
  moduleId,
  order,
  title,
  type,
  status: "planned",
  duration: "待细化",
  summary,
  why: "本页已进入知识树，但尚未达到可交付内容门禁。",
  prerequisites,
  outcomes: [summary],
  artifact,
  blocks: [],
  practice: [],
  completion: [],
  sourceIds: [],
  evidenceBoundary: "只有学习目标和知识位置，不代表页面已经完成。",
});

export const pages: TutorialPage[] = [
  {
    id: "TD-T01",
    moduleId: "TD-M01",
    order: 1,
    title: "测试开发遇到 AI 后，测试对象发生了什么变化",
    type: "概念",
    status: "desk-researched",
    duration: "18 分钟",
    summary: "区分确定性软件检查与概率性 AI 质量判断，知道哪些旧方法仍然有效、哪些地方必须换思路。",
    why: "如果仍把 AI 当作普通接口，只断言状态码和固定字符串，就会漏掉幻觉、拒答失守、引用错误、工具越权和质量漂移。",
    prerequisites: [],
    outcomes: [
      "说清普通软件与 AI 系统在输出、依赖和失败模式上的三个差异",
      "把一条 AI 失败归类为结构、行为、语义、安全或运行质量问题",
      "为同一个输出选择确定性检查、语义评测或人工审核",
    ],
    artifact: "AI 测试对象五层检查表",
    blocks: [
      {
        title: "先看一个真实工作差异",
        body: [
          "普通退款接口收到合法请求后，通常返回一个确定结构：状态码、订单状态和退款编号。测试开发可以对字段做精确断言。",
          "客服 AI 面对“会员已经激活，还能自动退款吗？”时，可能用不同句子表达同一正确答案，也可能语言很流畅却错误承诺退款。此时只检查 JSON 合法或回答非空远远不够。",
        ],
        bullets: [
          "结构正确不等于业务正确",
          "一次回答正确不等于版本稳定",
          "最终答案正确也不等于 Agent 的工具调用安全",
        ],
      },
      {
        title: "AI 测试对象的五层模型",
        body: ["把一次 AI 请求拆成五层，测试时从下往上看，定位会比只盯最终文本更清楚。"],
        bullets: [
          "输入层：用户问题、上下文、语言、身份和攻击载荷是否被正确处理",
          "检索层：应该取到的知识是否取到，是否混入无关或过期材料",
          "生成层：回答是否正确、忠实、相关、引用充分，是否应该拒答",
          "行动层：Agent 是否选择正确工具、参数和权限，是否需要人工确认",
          "运行层：延迟、成本、失败率、版本和 Trace 是否可观测",
        ],
      },
      {
        title: "旧测试方法哪些还能用",
        body: [
          "Schema、权限、工具参数、引用 ID、PII、延迟和成本依然可以做确定性断言；这些检查便宜、稳定，应当优先使用。",
          "自然语言正确性、忠实性和帮助程度通常需要规则、语义模型和人工样本组合。不要因为引入了大模型，就把所有判断都交给另一个大模型。",
        ],
        warning: "最危险的误区是“回答看着挺好”。测试开发需要的是可重复证据，而不是一次对话印象。",
      },
      {
        title: "最小例子：这条失败属于哪一层",
        body: ["用户只询问订单状态，Agent 却调用了 refund_order，并传入订单号。最终回复说“正在查询”，表面上没有错误。"],
        bullets: [
          "最终文本：看似正常",
          "行动层：错误工具，属于高风险失败",
          "权限层：若工具实际执行，可能产生不可逆业务影响",
          "正确 oracle：工具名、参数、权限策略和人工确认状态的确定性检查",
        ],
        expected: "你应该得出结论：不能只测试最终答案，还必须保存并检查 Agent 轨迹。",
      },
    ],
    practice: [
      "把“答案引用了不存在的政策文档”归类到检索层和生成层，并分别写出可观察信号。",
      "把“回答正确但耗时 12 秒”归类到运行层，写出至少一个门禁指标。",
      "从你自己的项目选一个 AI 功能，按五层模型列出每层至少一个检查。",
    ],
    completion: [
      "能解释为什么 JSON Schema 通过不代表 AI 质量通过",
      "能为至少三类失败选择不同 oracle",
      "已经完成一份五层检查表，而不是只阅读概念",
    ],
    sourceIds: ["S23", "S24", "S32"],
    evidenceBoundary: "本页是基于职业标准、AI 测试体系和生产就绪研究的概念综合；没有证明某个企业应采用统一指标或阈值。",
  },
  {
    id: "TD-T02",
    moduleId: "TD-M01",
    order: 2,
    title: "LLM、RAG、Agent 的最小结构",
    type: "概念",
    status: "desk-researched",
    duration: "22 分钟",
    summary: "画出模型、检索、工具和轨迹的最小结构，并知道每个部件应该留下什么测试证据。",
    why: "系统结构决定故障位置。分不清检索、生成和工具执行，就只能看到“AI 回答错了”，无法定位谁错、怎么复现。",
    prerequisites: ["TD-T01"],
    outcomes: ["画出 LLM、RAG 和 Agent 三种最小流程", "为每个节点标出输入、输出、版本和可观察证据", "根据症状选择先查哪一层"],
    artifact: "AI 系统结构与证据图",
    blocks: [
      {
        title: "三个系统，一句话讲懂",
        body: [
          "LLM：根据输入和上下文生成下一个最合适的内容。",
          "RAG：先从外部知识中找材料，再让 LLM 基于材料回答。",
          "Agent：让模型在多步过程中选择工具、读取结果、继续判断，直到完成任务或交给人工。",
        ],
        code: "LLM:    user -> prompt -> model -> answer\nRAG:    user -> retriever -> context -> model -> answer + citation\nAgent:  goal -> model -> tool call -> tool result -> ... -> final answer",
      },
      {
        title: "测试开发要保存的最小证据",
        body: ["每次运行只保存最终文本，会让大量故障无法复现。最小 Trace 至少包含下面这些字段。"],
        bullets: [
          "request_id、样例 ID、时间和环境",
          "Prompt、模型、参数、知识库与工具版本",
          "检索文档 ID、排序和得分",
          "每次工具调用的名称、参数、返回值和权限判定",
          "最终答案、引用、拒答标志、延迟、token 和成本",
        ],
        code: '{\n  "case_id": "refund-out-window",\n  "retrieved_ids": ["policy-refund-001"],\n  "answer": "超过 7 日且已激活的订阅不能自动退款，需要人工复核。",\n  "citations": ["policy-refund-001"],\n  "tool_call": null,\n  "latency_ms": 820\n}',
      },
      {
        title: "用症状倒推检查顺序",
        body: ["同一句错误回答可能来自不同根因，因此不能只修改 Prompt。"],
        bullets: [
          "正确文档没检索到：先查数据切片、召回、过滤和索引版本",
          "文档正确但回答捏造：查忠实性、Prompt、上下文截断和模型版本",
          "答案正确但引用错：查 citation 映射与后处理",
          "调用了危险工具：查工具选择、参数、权限和人工确认策略",
        ],
        warning: "“调一下 Prompt”不是通用修复。没有结构证据时，它只是碰运气。",
      },
      {
        title: "自己画一张证据图",
        body: ["选一个你熟悉的 AI 功能，用箭头画出数据流；在每个箭头旁写下可以保存的输入和输出。"],
        expected: "图中至少包含用户输入、版本、检索或工具证据、最终输出和业务决策人。",
      },
    ],
    practice: ["分别画出纯 LLM、RAG、可调用退款工具的 Agent", "在图中圈出一个不可逆动作", "写明不可逆动作由谁批准"],
    completion: ["能在不提框架品牌的情况下解释三种结构", "结构图包含版本与 Trace", "能根据四种常见症状选择首查节点"],
    sourceIds: ["S09", "S10", "S23"],
    evidenceBoundary: "结构图是跨框架最小模型；不同供应商的实际字段、工具协议和 Trace 格式需要按当前版本适配。",
  },
  {
    id: "TD-T03",
    moduleId: "TD-M01",
    order: 3,
    title: "概率性输出为什么不能只用传统断言",
    type: "概念",
    status: "desk-researched",
    duration: "25 分钟",
    summary: "学会按风险选择确定性断言、规则评分、语义 Judge 和人工评审，而不是寻找一个万能分数。",
    why: "同一正确答案可以有很多表达，同一流畅回答也可能严重错误。Oracle 选错，比阈值调错更根本。",
    prerequisites: ["TD-T02"],
    outcomes: ["识别四类 oracle 的适用边界", "为高风险 slice 设计组合 oracle", "解释 LLM-as-judge 为什么也要测试和校准"],
    artifact: "风险到 Oracle 决策表",
    blocks: [
      {
        title: "不要把“不能精确匹配”理解成“无法测试”",
        body: [
          "AI 输出不是完全随机，而是存在可观察约束。订单号格式、工具名、引用 ID、拒答标志和 PII 都可以精确检查。",
          "只有当问题涉及语义正确、帮助程度或表达质量时，才需要规则、embedding、LLM Judge 或人工。",
        ],
      },
      {
        title: "四类 Oracle",
        body: ["按稳定性和风险从左到右组合，而不是从一开始就使用最昂贵的方法。"],
        bullets: [
          "确定性：schema、正则、集合、工具/参数、引用白名单、延迟和成本",
          "规则评分：必须包含、禁止声明、关键词组、业务状态机",
          "语义评测：正确性、相关性、忠实性、风格，必须固定 rubric 与 judge 版本",
          "人工评审：高风险、分歧样例、新失败和抽样校准",
        ],
      },
      {
        title: "一个高风险退款样例如何组合",
        body: ["问题：已激活数字商品是否可以自动退款？"],
        bullets: [
          "确定性：不得调用 refund_order；引用必须来自 policy-refund-001",
          "规则：不得出现“已自动退款”“保证退款”等禁止声明",
          "语义：回答是否忠实表达“需要人工复核”",
          "人工：法务或业务负责人确认政策解释和例外情形",
        ],
        expected: "任何高风险确定性 gate 失败都应先阻断，不应被平均语义分数抵消。",
      },
      {
        title: "LLM-as-judge 也属于被测依赖",
        body: [
          "Judge 会受到 Prompt、模型、温度、上下文顺序和 rubric 的影响。同一批样例换模型后，分数可能变化。",
          "最低要求是准备人工标注的小校准集，检查 judge 与人工的一致率，并保存分歧样例。",
        ],
        warning: "不要用一个未校准的模型分数，替代业务负责人对高风险行为的决策。",
      },
    ],
    practice: ["为“泄露手机号”“回答不够礼貌”“调用错误工具”各选一种主 oracle", "设计一个不能被平均分掩盖的 blocker", "写出三条 judge 校准样例"],
    completion: ["每种 oracle 都能举出适用例子", "能说明高风险为何使用组合检查", "知道 judge 的版本与 rubric 必须进入测试依赖"],
    sourceIds: ["S04", "S10", "S13", "S23"],
    evidenceBoundary: "本页给出选择方法，不声称任何 Judge 或通用指标在所有业务上可靠；真实一致性必须用本业务人工样本测量。",
  },
  {
    id: "TD-T04",
    moduleId: "TD-M01",
    order: 4,
    title: "从测试用例到评测样例、黄金集和风险切片",
    type: "跟做",
    status: "desk-researched",
    duration: "35 分钟",
    summary: "把业务风险写成可重复执行的评测样例，并形成一个能扩展的小型黄金集。",
    why: "没有版本化评测数据，模型、Prompt 或知识库变更只能靠人随机试问，无法比较和回归。",
    prerequisites: ["TD-T03"],
    outcomes: ["写出包含输入、期望和证据的 eval case", "用 slice 表达业务风险而不是只分正负例", "避免黄金集污染和不一致"],
    artifact: "最小黄金集与数据卡",
    blocks: [
      {
        title: "评测样例比普通测试用例多什么",
        body: ["除了输入和预期，它还要记录允许的多种结果、证据来源、风险 slice、oracle、版本和人工争议。"],
        code: '{\n  "id": "refund-out-window",\n  "prompt": "我 30 天前买的订阅已经激活，能自动退款吗？",\n  "slice": "grounded-answer",\n  "expected_retrieved_ids": ["policy-refund-001"],\n  "allowed_citations": ["policy-refund-001"],\n  "forbidden_terms": ["自动退款成功", "一定能退"],\n  "expected_tool": null\n}',
      },
      {
        title: "从风险而不是问题清单开始",
        body: ["先列失败代价，再设计样例。一个可用的首版数据集至少覆盖下面六种切片。"],
        bullets: [
          "正常已知问题",
          "知识库未知或证据不足",
          "高风险政策解释",
          "身份、凭证和隐私",
          "Prompt injection 与越权",
          "工具选择、参数和人工确认",
        ],
      },
      {
        title: "黄金集不是永远正确的真理",
        body: [
          "黄金集是当前经确认的发布依据，必须记录谁确认、何时确认、引用哪版政策。政策变化后，旧标签可能变成错误答案。",
          "把训练数据、开发调试集和最终回归集分开，避免开发者反复针对同一批样例调参导致过拟合。",
        ],
        warning: "如果样例没有 source、owner 和 updated_at，它只能叫样例集合，不能叫可治理的黄金集。",
      },
      {
        title: "完成你的 8 条最小数据集",
        body: ["使用上面的 schema，分别写 2 条正常、1 条未知、2 条高风险、1 条隐私、1 条 injection、1 条工具样例。"],
        expected: "每条样例都有唯一 ID、风险 slice、至少一个 oracle 和证据负责人；高风险样例不可只写自然语言参考答案。",
      },
    ],
    practice: ["将一条生产失败脱敏后转成 eval case", "为每条样例标注阻断级别", "让另一位同事在不看你解释的情况下判断期望是否清楚"],
    completion: ["至少 8 条样例覆盖 6 类风险", "所有高风险样例有确定性 blocker", "数据卡记录 owner、版本、来源和限制"],
    sourceIds: ["S03", "S04", "S23"],
    evidenceBoundary: "页面提供数据结构和风险覆盖方法；8 条教学样例不能代表真实生产分布，也不能用于计算业务质量水平。",
  },
  planned("TD-T05", "TD-M02", 5, "从 PRD 和代码 Diff 提取风险", "跟做", "产出有业务依据的风险矩阵和追踪表", "风险矩阵", ["TD-T04"]),
  planned("TD-T06", "TD-M02", 6, "AI 生成测试，但证明测试真的会失败", "跟做", "用 mutation 证明 AI 生成测试具有检测力", "自动化测试与 mutation 报告", ["TD-T05"]),
  planned("TD-T07", "TD-M02", 7, "生成边界与 Fuzz 数据", "跟做", "让生成器命中预埋边界缺陷并保存最小失败样例", "失败种子", ["TD-T06"]),
  planned("TD-T08", "TD-M02", 8, "AI 做失败聚类，但必须保留证据链", "诊断", "生成可回到 Trace、Log 和 Diff 的候选归因", "引用式归因报告", ["TD-T07"]),
  {
    id: "TD-T09",
    moduleId: "TD-M03",
    order: 9,
    title: "第一个 LLM 评测",
    type: "跟做",
    status: "fixture-tested",
    duration: "40 分钟",
    summary: "运行一组固定样例和 scorer，得到第一份可比较、可失败、可保存的 AI 质量报告。",
    why: "本页把前四页的概念变成最小执行闭环：数据集、candidate、scorer、阈值、报告和退出码。",
    prerequisites: ["TD-T04"],
    outcomes: ["解释最小评测 harness 的五个部件", "运行 baseline 并读取报告", "证明坏版本会返回非零退出码"],
    artifact: "评测数据集、阈值和 baseline 报告",
    blocks: [
      {
        title: "准备环境",
        body: ["课程仓库使用 Python 3 标准库，不需要模型 Key。进入 RAG 课程 lab 目录后运行。"],
        code: "cd courses/td-ai-006-rag-eval-ci/lab\npython3 scripts/reset_candidate.py\npython3 scripts/evaluate.py --report reports/baseline.json",
        expected: "命令退出码为 0，终端显示 verdict: PASS，并生成 reports/baseline.json。",
      },
      {
        title: "最小评测 harness 的五个部件",
        body: ["只要能清楚回答这五个问题，你就拥有一个可以演进的评测起点。"],
        bullets: [
          "Dataset：测试什么风险",
          "Candidate：哪个模型、Prompt、知识库或录制输出",
          "Scorer：怎样判断每条样例",
          "Threshold：什么时候阻断",
          "Report：留下什么版本和失败证据",
        ],
      },
      {
        title: "读取 baseline 报告",
        body: ["不要只看 PASS。检查样例数、candidate 是否一一对应、关键 slice、失败列表和环境信息。"],
        code: 'python3 -m json.tool reports/baseline.json\necho $?',
        expected: "coverage、candidate_set_exact、task_pass_rate 均为 1.0；退出码为 0。",
      },
      {
        title: "证明评测不是摆设",
        body: ["运行故障注入并再次评测。一个不能让已知坏版本变红的评测，没有资格进入 CI。"],
        code: "python3 scripts/inject_regression.py\npython3 scripts/evaluate.py --report reports/mutation.json\necho $?",
        expected: "verdict 为 FAIL，evaluate.py 返回 1；报告中至少出现任务、引用、拒答、工具或运行质量失败。",
        warning: "mutation 仍然 PASS 时，不要降低要求庆祝通过；应检查 candidate 是否真的被替换、样例是否执行、阈值是否绑定。",
      },
    ],
    practice: ["新增一条禁止声明并让 baseline 先失败", "修正 candidate 后恢复 PASS", "在报告中写入你自己的版本标识"],
    completion: ["baseline 报告存在且 exit 0", "mutation 报告存在且 exit 1", "能从报告定位至少一条具体失败而非只看总分"],
    sourceIds: ["S03", "S04", "S05"],
    evidenceBoundary: "本页已在离线录制 fixture 上运行；只证明评测 harness 和故障检测链路，不证明任何实时模型的当前质量。",
  },
  {
    id: "TD-T10",
    moduleId: "TD-M03",
    order: 10,
    title: "RAG 的检索质量",
    type: "跟做",
    status: "fixture-tested",
    duration: "32 分钟",
    summary: "区分检索遗漏、检索污染和生成错误，并用 recall/precision 证据定位问题。",
    why: "RAG 回答错误不一定是模型问题。没有单独检查检索层，就会不断改 Prompt，却修不到索引、过滤或排序。",
    prerequisites: ["TD-T09"],
    outcomes: ["按样例计算检索 recall 与 precision", "从报告区分 missing 与 extra context", "设计面向风险 slice 的检索门禁"],
    artifact: "检索质量报告和定位表",
    blocks: [
      {
        title: "两个最小指标",
        body: [
          "Retrieval recall：应该检索到的文档有多少被找到了。遗漏关键政策时，生成器再强也无从忠实回答。",
          "Retrieval precision：取回的文档中有多少真正相关。无关材料过多会污染上下文、挤掉关键证据并增加成本。",
        ],
        code: "recall = |retrieved ∩ required| / |required|\nprecision = |retrieved ∩ required| / |retrieved|",
      },
      {
        title: "手算一条样例",
        body: ["required = [policy-refund-001]，retrieved = [policy-refund-001, policy-shipping-001]。"],
        bullets: ["recall = 1/1 = 1.0", "precision = 1/2 = 0.5", "结论：没有漏取，但混入了促销材料"],
        expected: "这不是生成错误；应优先检查过滤、query rewrite、排序或索引元数据。",
      },
      {
        title: "在 mutation 报告中定位检索回归",
        body: ["先完成 TD-T09 的故障注入，再读取 mutation 报告中的 retrieval 指标和失败样例。"],
        code: "python3 -m json.tool reports/mutation.json",
        expected: "教学 mutation 中 retrieval_recall 与 retrieval_precision 都降到 0.5。",
      },
      {
        title: "不要只看全局平均值",
        body: ["高风险退款 slice 即使只有一条，也可能要求 recall=1.0；低风险 FAQ 可以接受不同阈值。应按业务代价切片。"],
        bullets: ["overall", "high-risk policy", "unknown/refusal", "tool-use", "language or region"],
        warning: "检索分数高不等于回答忠实。检索和生成必须分层测试。",
      },
    ],
    practice: ["构造一个 recall=0.5、precision=1.0 的例子", "为高风险和普通 FAQ 设计不同门禁", "为一次检索污染写出三个可能根因"],
    completion: ["能手算 recall/precision", "能区分漏取和污染", "检索门禁至少有一个业务风险 slice"],
    sourceIds: ["S09", "S13", "S23"],
    evidenceBoundary: "教学报告使用离线文档 ID 精确匹配；真实检索评测还需处理多文档等价、chunk 粒度、标注分歧和数据漂移。",
  },
  {
    id: "TD-T11",
    moduleId: "TD-M03",
    order: 11,
    title: "回答、引用、忠实性和拒答",
    type: "参考",
    status: "desk-researched",
    duration: "30 分钟",
    summary: "根据失败风险选择回答正确性、引用、忠实性或拒答检查，不再把所有问题压成一个“准确率”。",
    why: "回答正确但引用伪造、引用正确但回答捏造、证据不足却强答，都是不同问题，需要不同证据。",
    prerequisites: ["TD-T10"],
    outcomes: ["区分 correctness、citation、faithfulness 和 refusal", "为每个指标写出可失败反例", "确定哪些失败必须人工复核"],
    artifact: "指标到风险映射表",
    blocks: [
      {
        title: "四个概念不要混用",
        body: ["它们回答的是四个不同问题。"],
        bullets: [
          "Correctness：回答是否符合业务事实或参考答案",
          "Citation：声明是否给出存在且允许的来源",
          "Faithfulness：回答中的主张是否由已检索上下文支持",
          "Refusal：证据不足、越权或危险请求时是否正确拒绝或升级人工",
        ],
      },
      {
        title: "四种容易混淆的结果",
        body: ["用同一退款问题观察不同失败。"],
        bullets: [
          "回答政策正确，但引用了不存在的文档：citation fail",
          "引用文档真实，但回答添加“30 天无条件退款”：faithfulness/correctness fail",
          "没有检索到政策，却凭常识回答：refusal fail",
          "正确拒答，但用户其实是低风险公开 FAQ：可能是 over-refusal",
        ],
      },
      {
        title: "门禁顺序",
        body: ["推荐先做稳定、可解释的硬检查，再做语义评分和人工抽查。"],
        code: "schema -> citation existence -> forbidden claims -> tool safety\n       -> semantic correctness/faithfulness -> human review",
        warning: "一个 0.86 的综合分不能告诉发布负责人是否发生了危险退款承诺。保留每个 blocker 的独立结论。",
      },
      {
        title: "拒答也需要正反两组样例",
        body: [
          "只测试危险请求是否拒答，会把模型推向“什么都不回答”。同时加入正常可答问题，测量 over-refusal。",
          "拒答结果还要检查是否泄露敏感片段、是否调用了危险工具、是否给出安全的下一步。",
        ],
      },
    ],
    practice: ["为四个指标各写一条会失败的回答", "增加两条安全问题防止过度拒答", "为高风险分歧定义人工升级条件"],
    completion: ["能解释四个指标的差异", "每个指标都有反例", "拒答测试同时包含 should-refuse 和 should-answer"],
    sourceIds: ["S04", "S09", "S10", "S13"],
    evidenceBoundary: "不同工具对指标的命名和实现可能不同；页面采用概念层定义，具体 scorer 必须检查当前官方文档并做业务校准。",
  },
  {
    id: "TD-T12",
    moduleId: "TD-M03",
    order: 12,
    title: "让 RAG 的错误退款承诺在上线前变红",
    type: "跟做",
    status: "fixture-tested",
    duration: "60–90 分钟",
    summary: "把前面七页组合成一套可重复 RAG 发布门禁，亲眼完成 PASS → FAIL → PASS。",
    why: "这是第一条可独立交付的职业任务：不再随机问模型，而是用版本化数据、门禁和报告支持发布决策。",
    prerequisites: ["TD-T09", "TD-T10", "TD-T11"],
    outcomes: ["运行完整基线、故障注入和修复", "解释至少六类 AI 特有回归", "把退出码和报告接入发布门禁"],
    artifact: "评测集、阈值、三份报告、CI workflow 和复用清单",
    blocks: [
      {
        title: "业务事故：语言很顺，但承诺错了",
        body: [
          "知识库规定已激活数字商品不能自动退款，只能转人工复核。回归版本却回答“已为你自动退款”，没有引用政策，还调用了 refund_order。",
          "普通接口检查可能全部绿色：HTTP 200、JSON 合法、answer 非空。真正的业务风险只有 AI 质量门禁能看见。",
        ],
      },
      {
        title: "第一步：跑已知良好版本",
        body: ["进入 lab，重置录制输出并生成基线报告。"],
        code: "cd courses/td-ai-006-rag-eval-ci/lab\npython3 scripts/reset_candidate.py\npython3 scripts/evaluate.py --report reports/baseline.json",
        expected: "exit 0；coverage、task_pass_rate、citation、refusal 和 tool gate 通过；p95 延迟为 820ms。",
      },
      {
        title: "第二步：注入六类回归",
        body: ["脚本会注入退款幻觉、丢引用、拒答失守、Prompt injection、错误工具、延迟和成本恶化。"],
        code: "python3 scripts/inject_regression.py\npython3 scripts/evaluate.py --report reports/mutation.json\necho $?",
        expected: "exit 1；task_pass_rate=0，citation_pass_rate=0.2，forbidden_claim_rate=1.0，p95_latency_ms=4200。",
      },
      {
        title: "第三步：不要急着调阈值，先诊断",
        body: ["按失败类型回到对应层。"],
        bullets: [
          "retrieval recall/precision 下降：检索层",
          "禁止声明和忠实性失败：生成层",
          "拒答失守：安全策略与样例层",
          "refund_order 被调用：行动与权限层",
          "延迟/成本失败：运行层",
        ],
        warning: "把阈值放宽到 PASS 不是修复。修复必须改变系统行为或有负责人、原因和过期时间的 waiver。",
      },
      {
        title: "第四步：重置并证明恢复",
        body: ["恢复已知良好版本并生成 repair 报告。"],
        code: "python3 scripts/reset_candidate.py\npython3 scripts/evaluate.py --report reports/repair.json",
        expected: "exit 0，核心指标恢复；三份报告共同形成可审计的红绿证据。",
      },
      {
        title: "从教学夹具迁移到真实项目",
        body: ["按顺序替换，而不是一次性接入所有线上复杂度。"],
        bullets: [
          "把录制 candidate 换成你的 RAG 调用适配器",
          "把合成知识库换成脱敏测试知识库",
          "加入历史事故、高风险 slice 和人工标注",
          "校准语义 Judge 与人工一致率",
          "在 CI 中保存版本、报告和失败样例，不保存生产 PII",
        ],
      },
    ],
    practice: ["新增“诱导 Agent 自动退款”样例", "先制造错误工具调用并证明变红", "修复后保存报告", "说明该检查由机器阻断还是人工决定"],
    completion: ["baseline exit 0", "mutation exit 1", "repair exit 0", "能把每个失败映射到测试对象层", "保存三份报告和一次新增样例"],
    sourceIds: ["S03", "S04", "S09", "S13", "S23"],
    evidenceBoundary: "已验证离线 fixture 与 evaluator 机制；没有调用真实模型、真实检索器或企业数据，也没有经过目标学员和测试开发专家盲评。",
  },
  planned("TD-T13", "TD-M03", 13, "Prompt、模型和知识库版本 A/B", "跟做", "用同一评测集比较多个候选版本并给出门禁结论", "版本对比报告", ["TD-T12"]),
  planned("TD-T14", "TD-M03", 14, "LLM-as-judge 的校准和反例", "诊断", "识别 Judge 偏差、漂移和人工分歧", "Judge 校准集", ["TD-T13"]),
  planned("TD-T15", "TD-M04", 15, "最终结果、单步动作和完整轨迹", "概念", "区分 Agent 三个评测层级并选择证据", "Agent 评测层级图", ["TD-T03", "TD-T04"]),
  planned("TD-T16", "TD-M04", 16, "工具选择、参数和权限", "跟做", "注入错误工具和参数并由沙箱阻断", "工具策略与轨迹报告", ["TD-T15"]),
  planned("TD-T17", "TD-M04", 17, "Prompt injection、数据泄露和 excessive agency", "跟做", "构建攻击集并验证 Agent 不越权、不泄露", "攻击集与安全报告", ["TD-T16"]),
  planned("TD-T18", "TD-M04", 18, "Browser Agent 和 Playwright Test Agents", "跟做", "使用 planner、generator、healer 生成候选测试并保留证据", "Agent 生成测试包", ["TD-T06", "TD-T16"]),
  planned("TD-T19", "TD-M04", 19, "自愈测试为什么会误修绿", "诊断", "阻止 healer 通过删除断言或改变业务 oracle 修绿", "Healer 反作弊策略", ["TD-T18"]),
  planned("TD-T20", "TD-M05", 20, "把评测接入 CI", "跟做", "让 AI 质量回归返回非零退出码并阻断合并", "CI quality gate", ["TD-T12"]),
  planned("TD-T21", "TD-M05", 21, "评测集、Prompt、模型、知识库和工具版本", "参考", "为一次质量结论保存全部可重放依赖", "实验与版本账本", ["TD-T20"]),
  planned("TD-T22", "TD-M05", 22, "Trace、生产失败和回归集闭环", "跟做", "把脱敏线上失败转成有 lineage 的回归样例", "反馈流水线", ["TD-T21"]),
  planned("TD-T23", "TD-M05", 23, "质量、延迟和成本联合门禁", "参考", "比较质量、延迟和成本的多目标折中", "Pareto 对比报告", ["TD-T20"]),
  planned("TD-T24", "TD-M05", 24, "漂移、告警、waiver 和回滚", "诊断", "为 AI 质量异常设计告警、例外和回滚路径", "事故与回滚 runbook", ["TD-T21", "TD-T22", "TD-T23"]),
  planned("TD-T25", "TD-M05", 25, "Capstone：完成一个 AI Quality Engineering 仓库", "项目", "交付从 commit 到 CI、Trace、回归和人工门禁的端到端质量仓库", "AI QE Capstone 仓库", ["TD-T12", "TD-T17", "TD-T20", "TD-T24"]),
];

export const sourceNotes: Record<string, { title: string; url: string }> = {
  S03: { title: "Promptfoo Introduction", url: "https://www.promptfoo.dev/docs/intro/" },
  S04: { title: "DeepEval Introduction", url: "https://deepeval.com/docs/introduction" },
  S05: { title: "OpenAI Evals", url: "https://github.com/openai/evals" },
  S09: { title: "Ragas Metrics", url: "https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/" },
  S10: { title: "Application-specific Evaluation", url: "https://docs.langchain.com/langsmith/evaluation-approaches" },
  S13: { title: "A Practical Introduction to Testing LLMs", url: "https://www.ministryoftesting.com/insights/a-practical-introduction-to-testing-llms" },
  S23: { title: "ISTQB Certified Tester AI Testing Syllabus v2.0", url: "https://istqb.org/wp-content/uploads/2026/05/ISTQB-_CTAI_Syllabus_v2.0_Release.pdf" },
  S24: { title: "The ML Test Score", url: "https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/" },
  S32: { title: "Software Quality Assurance Analysts and Testers", url: "https://www.onetonline.org/link/summary/15-1253.00" },
};

export const firstUsablePath = ["TD-T01", "TD-T02", "TD-T03", "TD-T04", "TD-T09", "TD-T10", "TD-T11", "TD-T12"];
