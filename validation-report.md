# 测试开发 × AI v2 验证报告

Verdict: `PASS-FIXTURE`，不等于 `PASS-LIVE` 或 `PASS-PRACTITIONER`。

## Evidence

- 研究账本包含 66 个来源，新增完整测试流程、接口契约、性能容量、可靠性安全、AI serving 指标、AI API 和职业演进的一手资料；能力声明优先使用官方文档、标准、原始论文和主仓库。
- 职业地图将测试开发拆为角色变体、5 个工作域、业务事件、业务产物、系统、决策责任和失败成本；每个场景只归属一个主工作域。
- 5 条原始招聘页来自 5 个雇主，只作为当前任务语言和需求信号，不作为市场规模证明。
- 两个 GitHub 候选已固定 commit、时间和许可证，但未作为本课实验运行，因此保持 `metadata-only`。
- 竞品矩阵包含 10 个直接供给，覆盖 DeepLearning.AI、Coursera、Ministry of Testing、Bilibili、知乎、慧测网和 Playwright Docs。
- 课程单元扩展了需求追踪、风险策略、数据环境、接口集成、UI/兼容、性能容量、稳定性安全、AI API、TTFT/TPOT/Goodput、AI 容量诊断和职业迁移，并覆盖 `use-ai-for-work`、`test-ai-systems`、`agentize-work`、`build-ai-quality-system` 四条线。
- 新增专业能力迁移架构、32 单元覆盖矩阵和六个独立专家视角；传统测试基线、大模型基础、LLM/RAG/Agent/Workflow/Benchmark 专题与 Capstone 均有明确工件和退出考核。
- 首课 AI centrality 5/5；被测对象为 RAG/LLM/Tool Agent，移除 AI 后课程不成立。
- 离线 lab 实际运行三次：baseline PASS/exit 0；注入回归 FAIL/exit 1；reset 后 repair PASS/exit 0。
- Mutation 检测到退款幻觉、丢引用、拒答失守、Prompt injection、身份绕过、错误破坏性工具、延迟与成本回归。
- 新版 package validator 已用 `--run-labs` 实际执行 manifest 中 7 个步骤并通过；其中已知回归步骤按契约返回 exit 1。
- evaluator 的 10 个对抗回归测试全部通过，覆盖恶意引用、危险工具、中文提示词泄露、单次高成本、额外 candidate、负 telemetry、空答案、检索污染和过度拒答。
- Skill validator 自身 47 个 fail-closed 回归测试通过；任何公开发布模式都禁止混入 planned、outlined、blocked、未承诺页面或空模块，公开页面 ID 必须与 `promised_page_ids` 完全一致。
- 回归测试还包含来源集中度加 filler、渠道借用、GitHub 报告冒用、职业地图漏场景、占位课程、空迁移标签、不存在 URL、缺少教程查看器、计划页冒充已交付页、缺少学习层和缺少专家角色。
- 内部课程目录保留 65 个站点命题位置；公开教程只投影 17 个通过逐题研究、正文、编辑与验证门禁的页面，分属 2 个非空模块。其余 48 个未完成命题不会进入公开 HTML、JSON、导航、搜索或发布承诺。
- 站点内容门禁、TypeScript 类型检查、vinext 生产构建、服务端 HTML 测试、同源 GitHub Pages 静态导出与静态安全测试全部通过；静态测试新增浏览器脚本语法解析，防止 GitHub Pages 因非法内联 JavaScript 卡在 loading。
- GitHub 公开仓库提交 `4bf127a` 的 `rag-eval-gate` 运行 `31366782842` 成功，覆盖 40 个 Skill 回归、职业课程包验证、站点构建、10 个 evaluator 对抗测试、良好候选通过和已知回归被拒绝。
- GitHub Pages 运行 `31367062592` 成功完成 build 与 deploy；公开 URL 匿名请求返回 200，并包含需求流程、AI 性能与职业演进章节。
- ChatGPT Site 版本 3 已从提交 `68004b0` 部署成功并开放公共访问；匿名 HTTP 请求返回 200，页面包含新增 AI 性能与职业演进章节。
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
- 分销转化、长期访问稳定性和真实学员体验；
- 企业隐私、权限、SLO 和阈值校准；
- 测试开发从业者 blind review；
- 视频成片、平台分发和市场转化。

## Risks

- 当前确定性关键词 scorer 是教学工具，会误伤同义表达；真实项目需引入语义 scorer 和人工校准。
- 8 条样例只能展示机制，不能代表生产分布。
- 工具文档和 AI 框架更新快，使用前必须按 tool registry 重查版本并重跑最小验收。
