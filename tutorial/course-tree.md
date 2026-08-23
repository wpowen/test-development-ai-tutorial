# 测试开发 × AI 课程树

## 文档导航

可按任务、主题或文档类型进入：Learn、Do、Look up、Understand、Report / Decide。页面的前置关系只表达局部依赖，不构成规定的使用顺序。

## 模块

### 完整测试生命周期

从需求、策略、设计、执行到发布与生产反馈，先建立专业测试骨架

- TD-F01 · 测试开发如何与 AI 协作，以及哪些发布责任必须由人承担 · fixture-tested
- TD-P01 · PRD、技术方案和接口文档说法不一致时，测试应该信谁 · fixture-tested
- TD-P02 · 拿到一份需求后，怎么拆出角色、状态和业务规则 · fixture-tested
- TD-P03 · 技术方案评审时，接口、事件和状态要问清哪些问题 · fixture-tested
- TD-P04 · 项目时间有限时，单元、接口和 E2E 测试应该怎么分配 · fixture-tested
- TD-P05 · 测试用例的预期结果从哪里来，怎么避免 AI 自己判自己对 · fixture-tested
- TD-P06 · AI 生成测试代码：需求、用例和代码要保持对应 · fixture-tested
- TD-P07 · 测试失败后，怎么判断是产品、脚本还是环境的问题 · fixture-tested
- TD-P08 · 需求变更后的回归选择：该重跑什么，什么时候能发布 · fixture-tested

### 传统测试专项

接口、集成、UI、数据、性能、稳定性、安全、可观测性和混沌工程

- TD-PS01 · 接口返回 200 但业务仍然出错：怎么验证状态和真实副作用 · desk-researched
- TD-PS02 · 字段格式都正确，为什么 API 仍可能出错 · desk-researched
- TD-PS03 · 跨服务事件丢失、重复或乱序时，应该怎么测试 · desk-researched
- TD-PS04 · Web UI 自动化为什么总不稳定，应该从哪里排查 · desk-researched
- TD-PS05 · 网页换浏览器或屏幕后出问题，兼容性应该怎么测 · desk-researched
- TD-PS06 · Android 自动化在不同设备上结果不一样，怎么排查 · desk-researched
- TD-PS07 · iOS 自动化在真机上失败时，先检查哪些问题 · desk-researched
- TD-PS08 · 数据库升级后数据有没有丢、能不能回滚，应该怎么测 · desk-researched
- TD-PS09 · AI 客服性能测试：速度、质量和成本必须一起看 · desk-researched
- TD-PS10 · 服务超时或流量过载时，怎样降级才不会扩大故障 · desk-researched
- TD-PS11 · 线上 AI 回答变差：按模型、检索和工具逐层排查 · desk-researched
- TD-PS12 · AI 助手上线前，哪些安全问题必须拦住 · desk-researched
- TD-X101 · 代码合并前的两类检查：架构变更和依赖供应链风险 · fixture-tested

### 大模型与 AI 系统基础

理解模型如何运行，以及 Token、Context、RAG、Tool 和 Agent 为什么会失败

- TD-FP01 · 一段 Prompt 怎样变成能复现、能测试、能回滚的工程资产 · fixture-tested
- TD-F02 · 大模型回答是怎么产生的，出错时应该查哪一层 · fixture-tested
- TD-F03 · 为什么同一个问题问几次，AI 的答案会不一样 · fixture-tested
- TD-F04 · AI 应用只是回答问题，还是会查资料、调工具和改状态 · fixture-tested
- TD-T01 · 评测开始前要约定什么，结果才不会各说各话 · fixture-tested
- TD-T02 · 评测样例怎么分组，才能避免调参时偷看最终答案 · fixture-tested
- TD-T03 · AI 答案没有标准答案时，怎样判断它到底对不对 · fixture-tested
- TD-T04 · 一次评测结果不稳定，重复几次后应该怎样下结论 · fixture-tested

### AI 帮你做传统测试

用 AI 提效，但必须证明生成结果有检测力

- TD-T05 · 需求和代码同时变更：这次最该测的风险在哪里 · fixture-tested
- TD-T06 · AI 生成测试的验收：先证明它真的能抓到缺陷 · fixture-tested
- TD-T07 · 边界值、组合测试和随机测试，什么时候该用哪一种 · fixture-tested
- TD-T08 · 一批测试同时失败：先保留证据，再做失败聚类 · fixture-tested

### AI 接口、性能与可靠性

测试流式协议、结构化输出、TTFT、TPOT、Goodput、容量、限流、重试和降级

- TD-A01 · 测试普通接口和 AI 接口，断言方式有什么不同 · fixture-tested
- TD-A02 · AI 接口边生成边返回，还会调用工具，自动化测试怎么写 · fixture-tested
- TD-A03 · AI 服务快不快、能处理多少请求、花多少钱，应该看哪些指标 · fixture-tested
- TD-A04 · AI 服务能扛多少用户，怎样找到开始排队和掉速的临界点 · fixture-tested
- TD-A05 · AI 服务变慢：按排队、模型、缓存和外部接口逐层排查 · fixture-tested
- TD-A06 · AI 服务出错后，什么时候该重试、限流或直接降级 · fixture-tested

### 测试 LLM 和 RAG

把概率性回答变成可重复、可审计的质量证据

- TD-T09 · 知识库内容过期、重复或越权时，RAG 上线前怎么治理 · fixture-tested
- TD-T10 · 知识库里明明有答案，RAG 为什么还是搜不到 · fixture-tested
- TD-T11 · AI 回答带了引用，怎样判断引用真的支持答案 · fixture-tested
- TD-T12 · RAG 上线前，哪些检索、拒答和权限问题必须拦住 · fixture-tested
- TD-X501 · AI 同时看图和文字：重点检查图文矛盾和理解错误 · fixture-tested
- TD-X502 · 多语言 AI 换一种语言或地区后，还能不能完成同一个任务 · fixture-tested
- TD-T13 · Prompt、模型或知识库变更：只改一个变量再比较 · fixture-tested
- TD-T14 · 用另一个模型给答案打分靠谱吗，什么时候必须人工复核 · fixture-tested

### 测试 Agent、Worker 与 Workflow

检查轨迹、状态、工具、权限、Handoff、副作用和自愈风险

- TD-T15 · Agent 最终答对了，为什么执行过程仍可能不安全 · fixture-tested
- TD-T16 · Agent 选错工具、参数或权限时，测试怎么发现 · fixture-tested
- TD-T17 · Agent 读取网页、邮件和工具返回时的注入与泄露风险 · fixture-tested
- TD-T18 · AI 自动生成 Web 测试后，怎样确认它没有改错断言 · fixture-tested
- TD-T19 · 自愈测试把失败改绿：先确认修的是脚本，不是掩盖产品缺陷 · fixture-tested
- TD-W01 · 一个流程到底需不需要 Agent，还是普通脚本就够了 · fixture-tested
- TD-W02 · AI 长流程为什么会丢状态、重复执行或一直不结束 · fixture-tested
- TD-W03 · 多 Agent 一定比单 Agent 好吗，怎样做对照实验 · fixture-tested
- TD-X603 · AI 长期记忆的三类风险：记错、串号和删不干净 · fixture-tested
- TD-X604 · 切换模型或工具后，哪些功能和安全行为必须重新测试 · fixture-tested

### 建设 AI 质量系统

把评测接入 CI、生产反馈、版本与回滚体系

- TD-X602 · 模型更新后，怎样判断可以升级还是应该回滚 · fixture-tested
- TD-X601 · AI 对不同人群结果不一致时，怎样评估公平性并保留人工复核 · fixture-tested
- TD-T20 · AI 质量检查接入 CI：危险失败必须真正阻止合并 · fixture-tested
- TD-T21 · 一次 AI 评测要记录哪些版本，才能复现历史结果 · fixture-tested
- TD-T22 · 把线上出现过的 AI 故障变成自动回归用例 · fixture-tested
- TD-T23 · 质量更好但更慢更贵时，这个 AI 版本到底能不能发 · fixture-tested
- TD-T24 · 线上 AI 持续变化：临时放行必须带到期时间和回滚方案 · fixture-tested
- TD-X805 · AI 新版本从离线测试到小流量上线 · fixture-tested

### Benchmark 与分数工程

弄清数据、协议、Scorer、聚合、污染和榜单分数如何产生

- TD-B01 · 同一个模型在不同榜单分数不同，问题出在哪里 · fixture-tested
- TD-B02 · 企业 AI 评测集：从真实任务抽样，不照搬公开题库 · fixture-tested
- TD-B03 · AI 评测分数怎么计算，样本少时结果能信吗 · fixture-tested
- TD-B04 · 评测分数变了，是模型变了还是测试工具变了 · fixture-tested
- TD-B05 · 公开榜单分数为什么会被数据污染、样本量和版本变化误导 · fixture-tested
- TD-B06 · 把公开榜单的方法改造成企业自己的业务评测 · fixture-tested

### 专业专题与 Capstone

按岗位路线组合工件，交付端到端 AI Quality Engineering 系统

- TD-QP01 · 需求系统更新后，怎样自动生成可审核的测试依据 · fixture-tested
- TD-QP02 · 代码已经更新，为什么测试报告可能还是旧版本的 · fixture-tested
- TD-QP03 · 每个合并请求一套独立测试环境：创建、隔离和自动回收 · fixture-tested
- TD-QP04 · 把需求、代码流水线和测试环境串成一条证据记录 · fixture-tested
- TD-T25 · AI 版本发布前的质量报告应该写什么 · fixture-tested

### 职业演进

从测试执行转向质量信号、评测工程、平台工程与生产可靠性

- TD-C01 · 传统测试开发转向 AI 质量岗位，需要补哪些能力和作品 · fixture-tested
- TD-C02 · 测试开发能力到了什么水平，不能只看工作年限 · fixture-tested
- TD-C03 · 未来 90 天的 AI 测试能力提升计划 · fixture-tested
- TD-C04 · 把通用能力模型换算成公司自己的职级标准 · fixture-tested
- TD-F05 · 面对问答、检索、代码和 Agent 任务，评测指标怎么选 · fixture-tested
- TD-T26 · AI 生成测试到底省没省时间，怎样用对照实验算清楚 · fixture-tested
- TD-R01 · 学习 AI 测试时，文档、工具和案例应该怎么选 · fixture-tested

### Agent 性能与稳定性工程

从工作负载、指标、Trace、容量压测到生产 SLO、告警与故障处置

- TD-AP01 · Agent 性能测试的第一步：设计一组真实任务 · fixture-tested
- TD-AP02 · 用户等 Agent 太久：把排队、模型、工具和重试耗时拆开 · fixture-tested
- TD-AP03 · 记录 Agent 每一步，定位慢点和最早失败 · fixture-tested
- TD-AP04 · 压测工具为什么会在系统变慢时少发请求，造成结果看起来更好 · fixture-tested
- TD-AP05 · Agent 用户越来越多：容量上限和第一个瓶颈在哪里 · fixture-tested
- TD-AP06 · Agent 超时后的重试风暴：控制请求和副作用放大 · fixture-tested
- TD-AP07 · Agent 连续运行几天后变慢：区分缓存、漂移和资源泄漏 · fixture-tested
- TD-AP08 · Agent 上线后的告警、降级和事故复盘 · fixture-tested

### Agent 测试架构

从 D0 评估可信到 D7 业务治理，用四证据环验证轨迹、协作、安全、可靠性与成本

- TD-AG-00 · 一套 Agent 测试体系应该覆盖模型、工具、状态、权限和评估器哪些层 · fixture-tested
- TD-AG-01 · 给 AI 答案打分的模型也会出错：先校准，再自动评分 · fixture-tested
- TD-AG-02 · Agent 最终失败：找到最早出错的那一步 · fixture-tested
- TD-AG-03 · 多个 Agent 交接任务：防止信息越传越错 · fixture-tested
- TD-AG-04 · Agent 执行到一半时，人能不能暂停、确认和接管 · fixture-tested
- TD-AG-05 · Agent 偶尔成功不算稳定：用重复运行看可靠性 · fixture-tested
- TD-AG-06 · Agent 被网页和工具返回内容诱导：持续安全测试怎么做 · fixture-tested
- TD-AG-07 · Agent 完成一个任务值不值：一起计算成功率、时间和成本 · fixture-tested
- TD-AG-08 · Agent 违反业务规则：从版本和操作记录追到责任人 · fixture-tested
- TD-AG-09 · Agent 上线前后的四类检查：模型、工具、业务和运行证据 · fixture-tested
- TD-AG-10 · 交易 Agent 上线前：隔离执行风险，准备分钟级回滚 · fixture-tested

## 页面状态

- 发布范围：`validated-subset`。
- 同步页面：103 页。
- 深度正文状态：103/103 页。
- `desk-researched` 表示正文和来源已整理，但没有运行目标系统。
- `fixture-tested` 表示对应离线夹具已经运行，不代表生产效果。
- 内容完成度与证据等级分开记录，不因正文完整而升级证据状态。
