# TD-PS07 · iOS 自动化：可访问性标识、权限、签名与状态残留

## Research brief

业务场景是医疗预约改期：患者选择新时段并确认，通知权限、网络切换、后台恢复和旧预约残留都不能造成重复占号。传统做法依赖坐标或可变文本，在一个模拟器和共享账户上运行，忽略 Bundle/signing、Keychain、系统授权、动画等待与服务端 `slot_version`。AI 可以解释 xcresult、建议缺失的 accessibility identifier 和聚类失败，但不能替代签名、真机或预约业务 owner。工具选型为 XCTest/XCUITest 做原生门禁，Appium XCUITest/Maestro 仅在有跨平台或设备编排理由时加入。

## Source pack

- Apple UI testing archive：<https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/testing_with_xcode/chapters/09-ui_testing.html>，说明 XCTest、XCUIApplication、XCUIElement 和 Accessibility 查询；页面较旧，运行版本需以 Xcode/SDK 锁定。
- XCTest 官方文档：<https://developer.apple.com/documentation/xctest>，提供测试、expectation 和结果能力；不替代业务状态断言。
- XCUIAutomation 官方文档：<https://developer.apple.com/documentation/xcuiautomation>，支持 UI element/query 自动化；定位稳定性依赖应用标识。
- Appium architecture：<https://appium.io/docs/en/latest/intro/appium/>，说明 server、client、driver 和设备链路；iOS 的 macOS、Xcode、签名和 WDA 前置条件仍需按目标环境验证。

## Evidence synthesis

事实：稳定 `accessibilityIdentifier`、服务端预约版本、系统权限状态和干净 Keychain/应用数据分别是可定位、业务正确、平台可用和状态隔离的前提。事实：XCUITest 通过不等于所有 iPhone/OS/辅助技术组合通过。工程综合：每次运行记录 Bundle、签名、Xcode/SDK、模拟器或真机、区域、权限、数据清理和 xcresult。

AI 变化是从结果包和 UI hierarchy 生成候选定位修复；工程边界是不得以文字相似度替代 accessibility contract，不得在失败时放宽等待或删除服务端断言。失败模式包括无 identifier、权限弹窗遮挡、动画 race、后台恢复旧状态、slot 版本冲突、Keychain 残留和模拟器/真机差异。材料状态为 static-reviewed。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| 患者与 iOS 设备（输入） | 输入患者账户、预约、目标时段、设备/OS、区域、通知权限和 `slot_version` fixture。 |
| XCUITest/Accessibility（处理） | 通过稳定 identifier/query 定位和点击；记录 UI hierarchy、动作序列与可访问性信息。 |
| 系统权限与生命周期（门禁） | 探针覆盖签名、安装、通知允许/拒绝、后台挂起、恢复和清理；前置失败不得伪装为产品失败。 |
| 预约 API（处理） | 注入离线、超时和冲突响应；为每次提交传播 appointment/trace ID。 |
| Slot 版本/账本（证据） | 以 `appointment_id`、`slot_version` 和变更计数判断唯一改期，独立于 UI 文案。 |
| xcresult/系统日志（证据） | 保存 xcresult、截图、系统日志、设备元数据和服务 Trace，支持按层分类。 |
| 回归门禁（人工决策） | 重复占号、越权、清理失败和未解释的签名/设备差异阻断；预期 OS 变化由 owner 审批。 |

可执行物料是预约 JSON、identifier 清单、权限/生命周期矩阵、并发版本冲突 fixture 和 xcresult 字段规范。顺序为签名/安装探针、权限路径、正常改期、冲突/恢复、清理。

## Manuscript map

先展示两个点击都成功但 `slot_version` 只应接受一次的并发反例。再解释 accessibility identifier、XCUITest expectation、权限/后台状态和服务端账本的分工。页面需要对比模拟器与真机能分别证明什么，加入通知拒绝、离线、后台挂起、旧 Keychain 四个失败包，并保留人工批准点。

## Editorial review

避免把 Apple archive 的历史页面当成当前 SDK 兼容矩阵；版本结论必须回到项目 Xcode/SDK 运行证据。没有把模拟器通过外推为所有 iPhone，也没有把 AI 结果解释当作签名或业务验证。工具边界、残留清理和服务端 Oracle 写得具体。

## Validation

当前状态：`desk-researched`，未运行 XCUITest、模拟器、真机、签名构建或预约服务。

后续可离线升级为 fixture-tested：`validate_ios_reschedule_fixture.py` 检查 identifier、权限和 slot 版本；`simulate_xcui_state.py` 回放等待/后台/冲突状态；`assert_appointment_idempotency.py` 验证并发提交；`parse_xcresult_fixture.py` 检查结果包字段；`detect_state_residue.py` 模拟 Keychain/应用数据残留。离线夹具不能证明 Xcode signing、动画和真实设备差异。
