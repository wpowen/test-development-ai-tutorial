# 故障诊断 Runbook

## 1. 先分层

`preflight → session → locator/hierarchy → actionability/sync → business assertion → screenshot/agent`。preflight 或 session 失败时先修环境，不改 locator；assertion 失败时保留原始证据，不让 AI 直接“修绿”。

## 2. 症状到证据

| 症状 | 先取什么 | 常见方向 | 禁止的伪修复 |
|---|---|---|---|
| locator 找不到 | DOM/ARIA、UI hierarchy、route、截图 | 页面状态、语言/权限弹窗、测试标识缺失 | 坐标点击、盲选 `first` |
| Playwright timeout | trace actionability、console/network | 遮罩、动画、异步、错误等待点 | `force: true`、全局 sleep |
| Espresso flaky | logcat、fake network、IdlingResource | 未同步后台任务、共享状态污染 | `Thread.sleep` |
| XCUITest timeout | `.xcresult`、UI snapshot、simctl、console | app/identifier/权限/Simulator 状态 | 放宽 assertion |
| Appium session/WDA | server/driver/WDA/ADB log、capabilities、版本 | Node/Appium/driver/Xcode/签名/端口 | 只升级 server |
| Maestro flaky | flow report、截图、hierarchy、设备日志 | 未清 state、动态文本、网络差异 | 无限 retry |
| 视觉 diff | baseline metadata、diff、字体/OS/scale | 环境漂移、动态区、真实 UI 变更 | 直接放宽阈值 |
| agent 绿但业务错 | patch diff、重放、业务状态、反例 | 点中相似控件、删步骤/断言 | 把模型高置信度当证据 |

## 3. 报告字段

记录首次失败率、最终失败率、工具/driver/model 版本、设备/浏览器、app build、测试 commit、seed、输入脱敏状态、trace/log/screenshot 路径、分类与人工决定。`NOT_RUN`、`BLOCKED`、`UNKNOWN` 不得改写成 PASS。
