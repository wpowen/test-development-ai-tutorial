# Web/Android/iOS UI 自动化与 AI 演进

## 课程结果

你将为同一个“登录后进入 Dashboard”业务结果，分别写出 Web、Android、iOS 的可读 UI 自动化样例，并建立一条不依赖设备或浏览器的离线质量门禁。门禁会真实检测稳定 locator 与业务 oracle 是否仍在；删除它们后必须变红，恢复后重新变绿。

## 学习者与前置条件

适合已经会读一种测试语言、能理解 Given/When/Then 和 CI 退出码的 QA、开发或测试开发工程师。需要 Python 3.9+ 标准库；Web/Android/iOS 工具链不是默认路径的前置条件。样例中的版本占位符必须由项目 lockfile、`--version`、设备 image 和 commit SHA 替换。

## AI centrality

跨平台 UI 测试的成本不只是“写点击步骤”：同一业务 oracle 会经过 DOM、Accessibility、Android resource-id、iOS accessibilityIdentifier 和不同同步模型。本课程对应共享包已知场景 `TD-S05`，AI 负责把批准过的规格转成测试草稿、从 trace/hierarchy/log 摘要故障并提出 locator 候选；如果移除 AI，课程就失去“受控生成与防误修绿”这一核心工作流。但 AI 不能决定结算是否正确，也不能为了绿色删除断言，最终质量责任仍由结算测试负责人和确定性 oracle 持有。

## System under test

- 系统/场景：合成 Web 结算登录与跨平台 UI 契约；输入为 `qa@example.test` 与非生产密码。
- 业务 oracle：点击 Sign in 后，Dashboard 可见且账户状态为 Active。
- 平台契约：Web 使用 role/label/test-id；Android 使用 resource-id/Accessibility；iOS 使用 accessibilityIdentifier/label。
- 输出：可复制的测试文件、选型矩阵、故障 Runbook，以及 `lab/reports/*.json`。
- 隐私边界：示例账号为 synthetic；不得把真实 token、客户截图、支付数据或生产账号交给模型。Playwright、Maestro、Appium、Espresso、XCUITest 示例只做静态审阅，实际浏览器、模拟器、真机和外部模型均未运行。

## Baseline and target

baseline 是 `stable_locator` 与 `business_assertion` 同时存在，标准库验证器返回 `PASS`、退出码 0；target 是允许 AI 对 locator 提出候选修复，同时冻结业务 oracle。行为 mutation 或删除 oracle 时门禁必须返回 `FAIL`，不能由 healer 改写为绿色。repair 只恢复 canonical contract，不放宽阈值。该门禁只证明本地合成 fixture 具备回归敏感性，不代表真实 Web、Android 或 iOS 应用已经运行。

## Commands

从课程包根目录执行以下命令，不依赖调用者先进入 `lab`：

```bash
python3 -m unittest discover -s lab/tests -v
python3 lab/scripts/reset_candidate.py
python3 lab/scripts/evaluate.py --report lab/reports/baseline.json   # 退出 0
python3 lab/scripts/inject_regression.py
python3 lab/scripts/evaluate.py --report lab/reports/mutation.json   # 退出 1，这是预期红灯
python3 lab/scripts/reset_candidate.py
python3 lab/scripts/evaluate.py --report lab/reports/repair.json     # 退出 0
```

`mutation.json` 必须记录两个缺失字段，而不是只记录“测试失败”。这模拟了真实的可测试性回归：元素可能仍能被坐标点到，但测试已经无法证明正确业务结果。

## Metrics and thresholds

离线门禁只有两个必要合同字段：`stable_locator` 和 `business_assertion`。baseline 与 repair 的阈值是 `missing_contracts=[]`、`oracle_pass=true`、`status=PASS`、退出码 0；mutation 的阈值是两个字段同时出现在 `missing_contracts`、`oracle_pass=false`、`status=FAIL`、退出码非零。任何自动修复若删除断言、改成 skip、增加无限 retry 或把 FAIL 改写为 PASS，均视为 false repair，不得合并。

## 一条 plain mental model：locator 是地址，oracle 是验收单

locator 解决“去哪里交互”；oracle 解决“交互后什么才算完成”。AI 可以从当前 DOM 或 UI hierarchy 建议地址，但不能凭相似文本改写验收单。先用语义 locator，再用平台原生同步，最后用业务断言收口；视觉截图是附加证据，不是业务 oracle 的替代品。

## Web：Playwright 可复制样例

文件：`materials/examples/playwright/login.spec.ts`。它展示 label、role、test-id 与 web-first assertion；不使用坐标或全局 sleep。运行前应在真实项目中替换 URL、锁定 Playwright 版本并执行 `npx playwright install`。

## Android：Maestro、Appium 与 Espresso

`materials/examples/maestro/login.yaml` 适合跨平台黑盒 smoke；`materials/examples/appium/login.js` 与 `login.py` 分别展示 JavaScript/Python WebDriver 客户端和显式等待；`materials/examples/espresso/LoginUiTest.kt` 适合拥有源码的 Android instrumentation 测试，异步工作应使用 IdlingResource 或测试替身，而不是 `Thread.sleep`。

## iOS：XCTest/XCUITest

`materials/examples/xcuitest/LoginUITests.swift` 使用 `XCUIApplication`、accessibility identifier 和 `waitForExistence`。真实执行依赖 macOS、Xcode、签名、Simulator/device 与 app build；本课程未执行这些外部链路。

## 选型决策

详见 `materials/selection-matrix.md`。默认决策是：Web 关键路径选 Playwright；Android 白盒快速反馈选 Espresso；iOS 原生门禁选 XCUITest；Android+iOS 共用黑盒 flow 选 Maestro；跨 app/真实设备/多语言统一协议才引入 Appium。视觉层旁路加入，AI 先做草拟、摘要和候选修复，任何写回都要人工审查。

## AI-specific failure boundary

可生产试点的动作：需求到测试草稿、trace/hierarchy 到失败摘要、从当前树提出 locator 候选、隔离 staging 探索。AI 特有失败包括删断言修绿、用相似控件误修、无限等待、将环境故障误判为产品故障、无证据编造根因。自动 healer、Maestro MCP 和视觉主 locator 仍属实验路径。禁止自动批准视觉基线、弱化业务断言、无限 retry/force/skip、生产副作用动作，模型自报“已修复”不能成为证据。

## 故障诊断 Runbook

按 `materials/diagnostic-runbook.md` 的顺序排障：先 preflight，再 session，再 DOM/UI hierarchy，再 actionability/同步，再业务 assertion，最后视觉 diff 或 agent。保留首次失败和最终重试结果；不要把设备离线、WDA 崩溃、网络 500、产品 assertion 混成一个“测试失败”。AI 没有 trace、hierarchy、console 和业务状态时，不得给出高置信度根因。

## Failure injection

`inject_regression.py` 删除 `lab/fixture/ui_contract.json` 中的 `stable_locator` 和 `business_assertion`。可观察失败结果是验证器退出码 1、`status=FAIL`、`oracle_pass=false`，且 `missing_contracts` 同时列出这两个字段。`reset_candidate.py` 从 `canonical_contract.json` 恢复契约，repair 再次退出 0。该实验只证明离线门禁能抓住“删 locator 与删 oracle”的有意义回归，不证明任何浏览器、模拟器、真机、Appium server、Xcode、Maestro 或模型已经运行。

## Human review gate

结算测试负责人必须审核 AI 生成的 spec、业务断言与 healing diff。允许 AI 生成计划和测试并提出修复，不得删除业务 oracle；视觉 baseline、阈值放宽、测试 skip 和生产副作用动作必须由责任人拒绝或单独审批。故障报告要保留原失败、DOM/UI hierarchy、patch diff、重放结果和业务状态；缺少这些证据时结论保持 `UNKNOWN` 或 `NOT_RUN`，不能升级为 PASS。

## Learner artifact

学习者交付 Playwright spec、Maestro flow、Appium JavaScript/Python 示例、Espresso Kotlin、XCUITest Swift、选型矩阵、故障 Runbook 和三份 JSON 报告。迁移任务把 Web 结算登录变为 Android 收货与 iOS 改期，至少改变输入 fixture、平台 locator 和业务 assertion。成功标准是新 canonical contract baseline 通过，删除 locator/oracle 后稳定失败，恢复后重新通过，同时明确平台代码仍是 `static-reviewed/NOT_RUN`。

## 交付物、评估与下一课

交付 `materials/examples/` 中至少两个平台样例、选型矩阵、Runbook 和一次包含 `0/1/0` 的 JSON 报告。评分重点是：语义 locator 选择、业务 oracle 完整性、失败分类、AI 权限边界和证据诚实度。下一课应把本课程的确定性门禁接入 CI，并增加 trace/screenshot/device log 采集；不要直接接入自动自愈。

## Evidence status

`fixture-tested` 仅适用于本目录 Python 标准库离线验证。Web 浏览器、Android emulator/device、iOS Simulator/device、Maestro CLI、Appium server/driver、Espresso instrumentation、Xcode build 和任何 AI/MCP 运行均为 `NOT_RUN/static-reviewed`。官方资料支持 API/架构/边界，不支持本项目的 flake rate、ROI 或 AI 生产级结论。研究输入为 `research-redesign/20-ui-mobile-automation.md`，来源清单与 URL 见 `materials/source-ledger.md`。

<!-- WAVE1-SPECIALTIES-START -->
## Wave 1 独立专业专项

### TD-PS04 · Web UI 关键旅程：隔离、定位器、网络控制与跨浏览器

- 控制问题：怎样让 UI 测试等待业务终态、隔离数据并保存可诊断 Trace，而不是靠 sleep 和文本出现判绿？
- 方法选择：用户感知 locator 与显式 test id 负责定位，auto-wait 负责 actionability，API/账本负责业务 Oracle，独立上下文负责隔离，Trace 负责诊断
- 独立 Oracle：批准控件角色名称与权限一致；重复点击只产生一次退款意图；UI 终态与订单 API 和审计记录一致；失败包含 DOM 网络控制台和 trace
- Prompt：读取旅程、角色、网络契约和风险矩阵，输出 locator 选择、等待信号、隔离数据、业务 Oracle 与失败证据；不得生成 fixed sleep
- Failure cycle：baseline → 退款 API 延迟后返回 500 → repair
- Unknown：目标浏览器流量占比、第三方沙箱稳定性和真实页面可访问名称

### TD-PS05 · Web UI 无障碍、兼容性与视觉回归

- 控制问题：怎样区分 DOM 规则、键盘旅程、可访问语义和视觉差异，并防止自动更新基线掩盖回归？
- 方法选择：WCAG/ARIA 定义控制问题，自动规则找常见缺陷，键盘与读屏旅程验证过程，风险矩阵裁剪环境，人工审批视觉基线
- 独立 Oracle：关键控件 name role value 可编程确定；完整退款过程键盘可达且焦点可见；390px 与长文本不遮挡风险和批准控件；视觉基线变更有设计 owner 审批
- Prompt：从 WCAG 条款、旅程和视口矩阵生成分层检查与人工复核清单；明确自动扫描未覆盖项，禁止自动批准截图基线
- Failure cycle：baseline → 移除对话框 accessible name → repair
- Unknown：真实辅助技术组合、用户研究结果和品牌容差

### TD-PS06 · Android 自动化：生命周期、同步、权限与设备矩阵

- 控制问题：怎样证明移动生命周期恢复不丢扫描状态也不重复入账，并区分应用、设备和服务端失败？
- 方法选择：ViewModel/组件测试覆盖状态，Espresso idling 覆盖同步，UI Automator 覆盖系统权限，设备矩阵覆盖风险切片，服务端幂等账本提供独立 Oracle
- 独立 Oracle：权限拒绝不创建收货记录；旋转后台与恢复保留可解释扫描状态；同一 receipt_id 只入账一次；失败包关联 logcat 设备状态和服务 trace
- Prompt：读取 Android 生命周期、权限、设备矩阵和库存契约，输出分层测试、同步信号、状态恢复与服务端 Oracle；未运行设备写 NOT_RUN
- Failure cycle：baseline → 扫描后进程被杀 → repair
- Unknown：OEM 定制行为、目标 API level 分布和真机资源限制

### TD-PS07 · iOS 自动化：标识、权限、签名与状态残留

- 控制问题：怎样区分 XCUITest 可见状态、系统权限、签名环境与服务端预约结果，并确保测试后无状态残留？
- 方法选择：accessibility identifier 保持定位契约，launch arguments 注入可控状态，XCTest expectation 等待业务信号，环境 manifest 固定签名和设备，后端预约版本作 Oracle
- 独立 Oracle：稳定 identifier 不依赖本地化文字；权限拒绝仍可完成安全替代路径；同一预约版本只应用一次改期；清理后通知日历 keychain 与后端状态回到基线
- Prompt：读取预约状态机、XCUITest preflight、权限与环境清单，生成 launch state、等待条件、清理和后端 Oracle；不得把模拟器通过写成真机通过
- Failure cycle：baseline → 动画和异步回调延迟 → repair
- Unknown：目标签名配置、真实通知服务和 iOS 版本分布

共享 bundle 只复用 runner；页级 manifest、owner、Oracle、Prompt、fault 和证据互不继承。
<!-- WAVE1-SPECIALTIES-END -->
