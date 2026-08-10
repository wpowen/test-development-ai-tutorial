# TD-PS08 · AI UI 生成与自愈：先证明检测力，再谈省维护

## Research brief

业务场景是电商退货：页面同时有“申请退货”“取消订单”“联系客服”，AI 可能点到语义相近的错误控件。传统做法把 codegen、视觉定位或自愈后的“到达成功页”当作通过，维护成本下降却可能把错误路径修绿。AI 的合理变化是从需求、页面语义和失败 Trace 生成候选步骤/Locator、聚类失败并提交 patch；工程边界是 business Oracle、权限和副作用不可由 AI 改写。工具优先 Playwright Planner/Generator/Healer 或 MCP 做提议，确定性 UI/API/账本断言做门禁。

## Source pack

- Playwright Test Agents：<https://playwright.dev/docs/test-agents>，提供 planner、generator、healer 的官方入口；官方能力不等于无人审批正确性。
- Playwright Locators：<https://playwright.dev/docs/locators>，定义语义定位器和稳定性边界；候选 Locator 仍需业务回放。
- Playwright MCP 官方仓库：<https://github.com/microsoft/playwright-mcp>，以 accessibility snapshot 支持代理交互；不证明生产测试覆盖。
- Playwright retries：<https://playwright.dev/docs/test-retries>，说明 retry 只能管理偶发失败，不能修复错误断言或误修绿。

## Evidence synthesis

事实：生成测试、Locator 自愈、视觉理解和业务验证是四种不同能力。事实：自愈接受率上升不能说明检测力上升，必须同时看误修绿率、原失败重现率、业务 Oracle 覆盖和人工审查率。工程综合：把 agent 输出限制为带 `source_ref`、候选范围、Oracle、权限边界、置信度和 diff 的结构化 patch。

AI 变化是搜索空间扩大、失败 triage 加速和需求到草稿变快；工程边界是 healer 只能改 Locator/wait/fixture 白名单，不得删步骤、改断言、放宽阈值、增加无限重试或自动更新 baseline。失败模式包括相似按钮误点、旧权限页面、自愈绕过授权、成功页与账本不一致、只在已见 fixture 上过拟合。当前研究包只 static-reviewed。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| 需求/业务 Oracle（输入） | 输入退货规则、订单状态、金额、权限、审计事件和反例；每个 expected state 有 source_ref。 |
| 页面与可访问性树（输入/处理） | 固定页面 fixture、role/label/testid、相似控件和错误权限视图；保存 snapshot hash。 |
| Planner（处理） | 把需求转为 Given/When/Then 候选旅程；输出来源、前置条件和未决问题，不直接写回仓库。 |
| Generator/Locator 候选（处理） | 仅从允许的 role/label/testid 候选集中生成步骤；保留原 Locator、替换理由和 diff。 |
| Critic/轨迹评测（门禁/证据） | 回放候选并核对订单状态、金额、权限、审计；相似按钮或旧状态必须红。 |
| 人工审查（人工决策） | 责任人审查 patch、证据、未覆盖场景和是否修改产品语义；未批准不得合并。 |
| CI 门禁（证据/门禁） | 同故障 replay、未修改回归集和 mutation 通过后才接受；误修绿或证据缺失阻断。 |

可执行物料是退货轨迹 fixture、相似按钮页面、self-healing policy YAML、候选 patch schema 和误修绿报告。先预埋坏 Locator 证明红，再比较 healer 前后检测力。

## Manuscript map

以错误点击“取消订单”但页面仍显示成功为反例。接着说明 planner/generator/critic 的三段隔离、业务 Oracle 与 Locator 白名单。页面必须呈现一次候选 patch 的前后 diff、轨迹、账本和人工批准记录，并用 mutation 交换按钮/隐藏权限来计算误修绿。结尾明确“省维护”只能在质量不下降后讨论。

## Editorial review

没有使用 agent benchmark、生成数量或 retry 通过率推断检测力。每个 AI 动作都有来源、证据和人工写回边界；把 Playwright 官方 Agents/MCP 标为生产入口或试点能力时，仍保留真实项目验证要求。页面不伪造浏览器 Agent 已运行。

## Validation

当前状态：`desk-researched`，未运行浏览器 Agent、MCP、healer 或目标退货站点。

后续可离线升级为 fixture-tested：`validate_agent_patch_schema.py` 检查 source_ref、Oracle、权限边界和白名单；`seed_wrong_locator_fixture.py` 预埋错误控件；`replay_heal_candidate.py` 对比原失败/候选轨迹；`inject_similar_button.py` 计算误修绿；`require_human_approval.py` 阻止未审 patch。离线结果只证明审查协议和 fixture 检测力，不证明生产维护率。
