# 测试开发 × AI：课程专业度缺口审计

更新时间：2026-08-11

## Research corpus

本次目录恢复沿用六类证据系统：职业知识体系、真实工作与从业信号、AI 一手技术、开源实现与 Benchmark、课程供给、失败与学习者反证。当前任务只修复课程目录真相，没有新增 live、practitioner 或 production 证据。

## Industry body of knowledge

Canonical 目录保留测试职业的风险、需求、Oracle、数据环境、自动化、执行诊断、发布和生产反馈链，并新增静态质量、数据管道、Web、Android、iOS 五个传统专项 gap。它们均未被标记完成。

## Real work and practitioner evidence

现有职业与工程证据支持这些能力进入目录，但尚无可追踪从业者签字、真实企业流程回读或目标学员工件证据。旧页面存在不等于职业可用性通过。

## Existing course supply

市场供给只能帮助识别结构和差异化，不能证明课程有效。旧版以 46、52、81 等不同数量表达课程范围，已造成完成度错觉。本次以 117 个 canonical topic 作为内部 backlog，不对外承诺完整课程。

## AI technology and benchmark frontier

目录补入多模态、多语言、Fine-tuning/模型更新、Memory/语义缓存、模型路由/Fallback/MCP 漂移、公平性与人工监督、在线实验七类 AI 高风险 gap。它们需要单独研究，不能由标题直接进入正文。

## Coverage matrix

- 原专业命题树：105。
- 旧 curriculum 合同：46。
- 站点内部页面：107，其中公开投影 103、内部页面 4。
- Canonical 目录：117，包含 105 个保留命题和 12 个新增 gap。
- Canonical complete：0；content gate blocked：117。

映射事实见 `research/course-catalog-migration.csv`；每个主题的状态、成熟度、前置和 alias 见 `research/course-catalog-manifest.json`。

Coverage 决策遵循“命题、课程合同、页面 ID 三层分离”：117 个 canonical topic 回答“知识与能力应该覆盖什么”，46 个 legacy curriculum contract 继续服务现有工厂验证和历史引用，107 个 site ID 只记录当前页面投影。三者通过迁移表连接，但互不冒充完成证据。一个旧课程或页面映射到多个 canonical topic，表示旧单元过宽，需要拆分生产；多个旧 ID 指向同一 canonical topic，表示重复入口，应保留 alias 而不重复计算主题数量。

当前 delivery 分布只表示材料存在形态：有旧页面映射的主题为 outlined，没有页面投影的主题为 planned，新增的高风险能力为 gap。Evidence maturity 只继承能够明确归属的旧证据，而且作用域固定为 alias；即使某个旧页面存在 fixture-tested 结果，也不能证明其映射到的整个 canonical topic、相邻主题或学习路径已经可用。所有 117 个主题继续保持 content gate blocked。

## Missing and overrepresented topics

缺失或过薄：静态与供应链质量、数据库/数据管道/迁移、Web/移动端独立工程链、多模态、多语言、AI 公平性、人类监督、训练更新、长期 Memory、模型路由/Fallback、在线质量实验。

过度代表：工具或平台名称、共享模拟器、同一通用正文模板，以及需求/性能/平台主题在多套 ID 中重复出现。

## Expert review

### Profession veteran

恢复测试生命周期和专项，但要求后续逐主题验证真实工件、决策权和失败成本。

### AI systems engineer

要求 AI 基础先于 LLM/RAG/Agent，安全和协议边界先于可写 Agent，Serving 指标必须绑定采集点和工作负载。

### Evaluation and quality expert

要求 Eval 数据、Oracle、Holdout、Scorer 和统计在应用专题之前；Fixture maturity 不得外推。

### Curriculum designer

新顺序固定为：职业责任 → AI 基础 → 测试生命周期 → Eval → AI 辅助 → LLM/RAG → Agent+安全 → Serving/性能 → 质量平台/生产 → Capstone。

### Market and learner researcher

主题数量不是差异化。学习者需要逐页工件、真实动作、失败诊断、修复和迁移，而不是更多导航标题。

### Adversarial critic

旧“52/52 正文完成”和“33/33 深度正文”与当前研究包事实冲突，已从 canonical 文档删除。任何页面或 alias 状态都不能升级 canonical topic。

## Curriculum decisions

1. 使用 117-topic canonical manifest 作为唯一内部课程目录。
2. 46 个旧合同和 107 个站点 ID 全部保留为 alias，不删除历史，也不重复计数。
3. 12 个主动缺口均已有直接 canonical 页面或既有专项 alias；coverage gap 为 0，但内容、从业者和发布门禁仍分别关闭。
4. Delivery 与 evidence maturity 分开；别名 Fixture 不升级内容完整度。
5. 每个 canonical topic 必须拥有自己的九文件研究包，才能离开 planned/outlined/gap。
6. 先修完整初学者路径，再扩展高级专题；不从 Agent 性能或平台页绕过基础。

### Delivery sequence and exit evidence

每个阶段必须先产出可复核工件再进入下一阶段。职业与 AI 基础阶段要求风险声明、系统边界和失败停止条件；测试生命周期阶段要求需求到 Oracle、数据、环境、执行、诊断和发布的可追踪链；Eval 阶段要求数据版本、Holdout、Scorer、统计与失败分析；LLM/RAG 和 Agent 阶段必须增加协议、权限、安全、可重放与回归证据；Serving、性能、平台和生产阶段必须绑定真实采集点、工作负载、容量、降级、发布与回滚。Capstone 必须组合前述证据，不能用演示截图替代。

目录顺序修复只解决生产路线和依赖真相，不自动补齐任何正文。后续每个 topic 仍要独立完成职业证据、AI 一手来源、反证、样本、工件、练习、自检、边界和来源九类材料，并通过对应页面类型的验证器。若一个主题无法给出真实动作、可运行样本、失败诊断和迁移说明，应继续 blocked，而不是用更长的概念说明填充。

## Remaining unknowns

- 12 个新增 gap 的页面落点已裁决；数据库、Web、Android、iOS 复用既有专项页，其余 8 个使用独立 canonical 页面。真实职业有效性仍待复核。
- 没有从业者盲评、目标学员试学和生产环境证据。
- 真实模型、真实 RAG、真实 Agent 权限、真实 Jira/GitLab/Kubernetes、浏览器与移动端集成仍未验证。
- 当前目录可用于恢复课程生产顺序，不能用于声称课程、职业能力或商业效果已完成。
