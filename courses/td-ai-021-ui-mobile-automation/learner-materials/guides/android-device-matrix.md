# Android 设备矩阵

| 维度 | 必填记录 | 失败时先查 |
|---|---|---|
| OS/API | Android version、API level、emulator image | image 与 app min/target SDK |
| 设备 | model、resolution、density、orientation | keyboard、insets、布局差异 |
| 工具链 | Java、ADB、Appium、UiAutomator2、Maestro、Gradle | server/driver/ADB 兼容性 |
| 应用 | build、签名、package/activity、commit | 安装、启动、权限 |
| 数据 | account、seed、clearState/reset、network | 共享状态、后端 500 |
| 证据 | logcat、hierarchy、截图、report | locator、同步、业务 assertion |

默认组合：源码内快速反馈用 Espresso；跨 app/黑盒用 Maestro 或 Appium UiAutomator2。真实设备和 emulator 未在本课程执行，状态是 `NOT_RUN/static-reviewed`。
