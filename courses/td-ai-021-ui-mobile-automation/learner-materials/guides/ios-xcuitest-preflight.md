# iOS XCUITest Preflight

执行 XCUITest 前逐项记录：

1. `xcodebuild -version`、Xcode scheme、SDK 与 destination。
2. Simulator/device 型号、OS、分辨率、locale、timezone、键盘与权限状态。
3. app build、bundle identifier、签名、安装状态和 `accessibilityIdentifier`。
4. 网络 stub、测试账号、seed、`-ui-testing` 启动参数和清理路径。
5. `.xcresult`、截图、console/device log、UI hierarchy 和测试 commit 输出位置。

失败先分为 Xcode/signing/device/app 启动、Accessibility 查询、同步/expectation、业务 assertion 四类。不要先改 locator，更不要用坐标或删除断言。没有 macOS/Xcode/Simulator 执行证据时保持 `NOT_RUN/static-reviewed`。
