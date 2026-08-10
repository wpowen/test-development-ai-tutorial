# TD-PS04 · Web UI 关键旅程：隔离、定位器、网络控制与跨浏览器

## Research brief

业务场景是后台退款审批：审批人查看订单、金额、风险标签和审计记录，批准后页面先显示处理中，异步完成后才显示已完成。传统 UI 自动化常共享账号和数据、使用 CSS/坐标与固定 sleep，并把第三方网络成功当作产品结果。AI 可以从需求或 accessibility tree 生成旅程草稿、定位器候选和 Trace 分类；它不能以页面文字或到达成功页证明退款已发生。工具优先 Playwright，第三方支付/通知走受控 route，核心订单 API 保留契约验证。

## Source pack

- Playwright Locators：<https://playwright.dev/docs/locators>，支持 role、label、test id 等语义定位；定位器稳定性仍依赖产品可测试性。
- Playwright Actionability：<https://playwright.dev/docs/actionability>，说明动作前的可见、稳定、可交互检查和自动等待；不替代业务状态等待。
- Playwright Assertions：<https://playwright.dev/docs/test-assertions>，支持 web-first 重试断言；不能把重试当作修复错误 Oracle。
- Playwright Trace Viewer：<https://playwright.dev/docs/trace-viewer>，支持动作、网络、截图和错误上下文回放。

## Evidence synthesis

事实：BrowserContext 隔离、语义 Locator、业务信号等待和 Trace 采集分别解决状态污染、定位脆弱、异步时序和诊断问题。事实：跨浏览器矩阵应由用户风险裁剪，不是浏览器数量越多越好。工程综合：UI 断言必须与订单 API/状态或审计证据互证，清理失败必须使套件失败。

AI 变化是 codegen、planner、generator 和 healer 可以减少草稿成本；工程边界是自愈只能在 role/label/testid 白名单内提出候选，不能删业务断言、改成 skip 或无限重试。失败模式包括共享订单互相污染、第三方 flake、重复点击、异步状态误判、浏览器差异和清理残留。`static-reviewed` 只代表设计和页面材料经审阅。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| 测试数据工厂（输入） | 为审批人、订单、权限和金额创建独立 fixture；输出 seed、账户标识和清理计划。 |
| 浏览器上下文（处理） | 固定 browser/OS/locale/viewport，隔离 storage state；记录 build、浏览器版本和上下文 ID。 |
| Web UI（处理） | 使用 role/label/testid 与 web-first assertion；等待退款状态或 API response，不使用固定 sleep。 |
| 订单/退款 API（证据） | 校验订单状态、退款计数、金额和审计记录，作为 UI 成功的业务 Oracle。 |
| 第三方路由 Stub（处理/门禁） | 控制支付、通知延迟/500/断连；核心流程的外部依赖场景必须可重复。 |
| Trace/截图/控制台（证据） | 保存 trace、DOM、网络、console、截图、seed 和失败分类，支持最小重放。 |
| 回归门禁（人工决策） | 业务状态不符、权限越界、清理失败直接阻断；矩阵扩展和预期视觉差异由 owner 审批。 |

可执行物料是退款审批 fixture、Playwright journey spec、网络路由表、浏览器风险矩阵和 Trace manifest。运行顺序为环境探针、正常旅程、错误旅程、清理验证，再做跨浏览器切片。

## Manuscript map

先展示固定 sleep 在慢网络下的假绿，再比较 Locator、业务等待和 Trace。随后把数据工厂、上下文、UI、API、Stub、证据和 gate 串成一条旅程。页面应包含空列表、权限不足、重复点击、第三方失败和窄视口案例，并解释 retry 通过为何仍需记录 flaky。AI 章节只讨论草稿和候选修复。

## Editorial review

用“看到已完成”与“退款账本已增加一次”明确区分 UI 事实和业务事实；没有把 Playwright codegen 或 retry 说成质量保证。矩阵选择、依赖隔离、清理和证据字段均可审计。目标站点、真实浏览器兼容性和网络行为没有被伪造为已运行。

## Validation

当前状态：`desk-researched`，未启动目标站点或 Playwright 浏览器运行。

后续可离线升级为 fixture-tested：`validate_refund_journey.py` 检查步骤、Oracle 和权限边界；`fake_refund_server.py` 提供处理中/完成/500 状态；`replay_network_faults.py` 验证超时和第三方失败；`assert_trace_manifest.py` 检查每次失败含 DOM、网络和业务状态；`cleanup_probe.py` 检查订单与账户清理。离线 fixture 只能证明旅程控制逻辑，不能证明真实浏览器兼容。
