# Web 关键旅程 SOP

## 目标

把已批准的业务场景转成 Playwright 可重放旅程。先定义业务 oracle，再选择 role、label、test-id 等语义 locator；截图和 AI 摘要只能作为附加证据。

## 操作顺序

1. 固定 URL、账号、seed、locale、timezone、字体、动画、网络 stub、浏览器版本。
2. 写 Given/When/Then：每个关键动作都要有可观察结果与清理动作。
3. 用 `getByRole`、`getByLabel`、`getByTestId`，避免坐标、宽 CSS selector、全局 sleep。
4. 使用 web-first assertion；失败开启 trace、截图、console 和 network 摘要。
5. 先记录首次失败，再记录重试结果；不得用 retry 覆盖 flake。
6. AI 只能从 DOM/ARIA/trace 提出候选 patch；人工检查 diff、反例和业务 oracle 后再写回。

## 发布门禁

浏览器矩阵每一项都要记录实际版本、commit、输入 seed 和结果。没有真实浏览器执行时状态保持 `NOT_RUN/static-reviewed`，不能把静态样例升级为 PASS。
