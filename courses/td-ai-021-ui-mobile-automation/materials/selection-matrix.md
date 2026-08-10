# 选型矩阵

| 方案 | 最适合 | 同步/稳定性 | AI 演进定位 | 主要边界 |
|---|---|---|---|---|
| Playwright | Web 关键旅程、trace、语义 locator | 强：auto-wait/web-first assertion | 草稿、Agents/MCP、候选诊断；写回需审查 | 不测原生 App |
| Espresso | Android 源码内组件测试 | 强：主线程/IdlingResource | 无官方 NL agent；确定性优先 | 需要源码，非跨 app |
| XCUITest | iOS 原生与 Accessibility 门禁 | 原生整合；用 expectation/wait | 无官方 NL agent；确定性优先 | macOS/Xcode/签名 |
| Maestro | Android+iOS 共用黑盒 smoke | smart waiting，仍需项目实测 | MCP/flow 草拟为试点 | 深度白盒断言有限 |
| Appium | 跨 app、真机、多语言、统一协议 | 链路长，需锁 server/driver/WDA/ADB | 外部 agent 只能受限调用 WebDriver | 兼容矩阵与诊断成本高 |
| 视觉层 | 渲染差异补充 oracle | 环境敏感 | 可聚类/解释，不能自动批准 | 不是语义或业务断言 |

决策顺序：业务 oracle → 平台边界 → 最短稳定链 → 证据采集 → AI 旁路辅助。来源为 `materials/source-ledger.md`。
