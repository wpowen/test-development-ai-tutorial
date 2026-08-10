# 测试开发 × AI v2 验证报告

Verdict: `PASS-FIXTURE`，不等于 `PASS-LIVE` 或 `PASS-PRACTITIONER`。

## Evidence

- 研究账本包含 40 个来源，覆盖七类必需渠道和六个课程审计证据系统；能力声明优先使用官方文档、标准、原始论文和主仓库。
- 职业地图将测试开发拆为角色变体、5 个工作域、业务事件、业务产物、系统、决策责任和失败成本；每个场景只归属一个主工作域。
- 5 条原始招聘页来自 5 个雇主，只作为当前任务语言和需求信号，不作为市场规模证明。
- 两个 GitHub 候选已固定 commit、时间和许可证，但未作为本课实验运行，因此保持 `metadata-only`。
- 竞品矩阵包含 10 个直接供给，覆盖 DeepLearning.AI、Coursera、Ministry of Testing、Bilibili、知乎、慧测网和 Playwright Docs。
- 33 个课程单元按八个依赖阶段组织，并覆盖 `use-ai-for-work`、`test-ai-systems`、`agentize-work`、`build-ai-quality-system` 四条线。
- 新增专业能力迁移架构、32 单元覆盖矩阵和六个独立专家视角；传统测试基线、大模型基础、LLM/RAG/Agent/Workflow/Benchmark 专题与 Capstone 均有明确工件和退出考核。
- 首课 AI centrality 5/5；被测对象为 RAG/LLM/Tool Agent，移除 AI 后课程不成立。
- 离线 lab 实际运行三次：baseline PASS/exit 0；注入回归 FAIL/exit 1；reset 后 repair PASS/exit 0。
- Mutation 检测到退款幻觉、丢引用、拒答失守、Prompt injection、身份绕过、错误破坏性工具、延迟与成本回归。
- 新版 package validator 已用 `--run-labs` 实际执行 manifest 中 7 个步骤并通过；其中已知回归步骤按契约返回 exit 1。
- evaluator 的 10 个对抗回归测试全部通过，覆盖恶意引用、危险工具、中文提示词泄露、单次高成本、额外 candidate、负 telemetry、空答案、检索污染和过度拒答。
- Skill Creator `quick_validate.py` 通过；validator 自身 36 个 fail-closed 回归测试通过。
- 36 个测试包含来源集中度加 filler、渠道借用 blocked/其他 query、GitHub 借用任意报告、职业地图漏场景、长标题占位课程、空迁移标签、不存在 URL 的 live check、缺少教程查看器、计划页冒充已交付页、缺少学习层、缺少专家角色和未决高优先级课程缺口。
- 教程站已形成 8 个模块、38 个页面的专业知识树；其中 12 页组成从传统测试基线、大模型基础到 RAG 质量门禁的可读路径，其余 26 页明确标记 `planned`。
- 新版 Sites 首条路径为 TD-F01、F02、F03、F04、T01、T02、T03、T04、T09、T10、T11、T12；内容密度、前置依赖和交付状态由站点验证器检查。
- GitHub 私有分发仓库的远端 Actions 已在 commit `4704ebd` 上运行通过，包含 10 个 evaluator 对抗测试、良好候选通过和已知回归被拒绝；这证明公开分发包在 GitHub 托管运行器上可执行，不等于生产效果。
- OpenAI Sites 版本 1 已私有部署成功，用于内容评审；尚未开放公共访问。
- 先前选择 S01、S05、S32 三个高优先来源执行实时重开并通过；这不是 40 个来源的全量当前可达性证明。S33–S40 已在本轮检索中打开并登记，但未执行同一批次全量 URL 验证。
- 独立 reviewer 首轮发现 evaluator 假阳性、CI 只跑好快照和 RAG 检索未入执行路径三个阻断项；修复后复审 verdict 为 PASS，确认原 adversarial probes 全部被拒绝、根目录 CI 本地等价命令通过、7 个 manifest runtime steps 达到预期 exit code。

## Inference

- “离线可复现 + 可选 live adapter”能降低小白首次成功成本，同时维持证据边界。
- 以故障注入和工程门禁作为每课公共骨架，比按工具品牌组织课程更耐更新。
- 公开供给中可见“全套教程”和广泛模块，但完整红绿证据常未在课程页展示；这可以成为内容差异化假设。

## Unknown

- 未获得真实企业 RAG/Agent 项目数据、真实测试开发从业者评审和学员完成数据。
- 未验证课程的播放、转化、留资或付费表现。
- 未比较不同 live model/provider 的当前质量和成本。
- 竞品的真实内部作业、完成率和教学效果通常不可见。
- 未完成全部 40 个 URL 的同一次 `--verify-sources` 全量审计；部分招聘和社区页面可能受反爬或登录影响。

## Professional utility verdict

八门专业价值门禁自评：AI 中心性 2/2、职业真实性 2/2、可运行证明 2/2、测试敏感性 2/2、复用资产 2/2、证据质量 2/2、小白迁移 2/2、维护性 2/2，总分 16/16。该评分只针对交付结构和本地 fixture 证据；不能替代从业者评审。

## Not tested

- 真实 LLM/RAG provider 调用；
- 真实 retriever 的 context precision/recall 与 faithfulness judge；
- GitHub Actions 的持续稳定性和 pull request 场景；
- GitHub 与 Sites 的公开访问、分销转化和访问控制体验；
- 企业隐私、权限、SLO 和阈值校准；
- 测试开发从业者 blind review；
- 视频成片、平台分发和市场转化。

## Risks

- 当前确定性关键词 scorer 是教学工具，会误伤同义表达；真实项目需引入语义 scorer 和人工校准。
- 8 条样例只能展示机制，不能代表生产分布。
- 工具文档和 AI 框架更新快，使用前必须按 tool registry 重查版本并重跑最小验收。
