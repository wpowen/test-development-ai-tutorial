# TD-PS06 · Android 自动化：生命周期、同步、权限与设备矩阵

## Research brief

业务场景是仓库扫码收货：收货员扫描条码并上传库存；相机首次拒绝、切后台、网络断开、旋转、进程被杀和低电量都不应导致重复入库。传统做法在单一模拟器上点击流程并 `sleep` 等待，无法解释 Activity/process 状态、系统权限或服务端幂等。AI 可以聚类 logcat、提出设备切片和候选断言，但没有真实设备运行时不能宣称兼容性通过。工具选型：源码内组件用 Espresso，黑盒/跨应用或设备矩阵可用 Appium UiAutomator2/Maestro；库存 API 和 `receipt_id` 账本是独立 Oracle。

## Source pack

- Android Espresso：<https://developer.android.com/training/testing/espresso>，支持 View matcher、actions、assertions 和同步/IdlingResource；需要测试构建和应用可观测性。
- Android permissions：<https://developer.android.com/training/permissions/requesting>，说明运行时权限请求和用户拒绝路径；系统对话框行为仍需设备验证。
- Android testing samples：<https://github.com/android/testing-samples>，提供官方测试样例和工程结构参考；样例不代表目标应用兼容性。
- Appium UiAutomator2 quickstart：<https://appium.io/docs/en/latest/quickstart/uiauto2-driver/>，支持 Android 黑盒/设备链路；server、driver、ADB 和设备版本需要锁定。

## Evidence synthesis

事实：Espresso 的同步依赖主线程与 IdlingResource，不能用固定 sleep 取代可观察状态。事实：移动 UI 状态和服务端库存账本必须双断言；截图显示上传成功不证明入库一次。工程综合：设备矩阵按 API level、厂商、分辨率、网络和业务风险裁剪，运行包必须包含 APK、设备、权限、网络和 logcat 元数据。

AI 变化是从历史崩溃和 logcat 发现设备切片候选；工程边界是未连接模拟器/真机时所有设备结论为未知。失败模式包括权限拒绝后状态丢失、进程重启重复上传、旋转清空扫描队列、网络恢复重复提交、ANR 和厂商差异。`static-reviewed` 材料只证明策略已审阅。

## Engineering blueprint

七节点架构与页面定义一致：

| 节点 | 实施与可审计输出 |
|---|---|
| 收货员与设备（输入） | 输入角色、APK build、设备型号/API、网络、权限初始状态、`receipt_id` 和条码 fixture。 |
| Android Activity/Process（处理） | 覆盖启动、后台、旋转、进程杀死和恢复；记录 lifecycle 事件与 app state hash。 |
| 扫描与权限层（门禁） | 明确首次允许、首次拒绝、再次请求和永久拒绝；权限失败不能伪装成上传失败。 |
| 本地状态/队列（处理/证据） | 保存扫描状态、待上传队列、重试预算和恢复记录；重复发送必须带同一 `receipt_id`。 |
| 库存 API（处理） | 在合成环境注入断网/500/延迟，返回可分类错误并传播 trace。 |
| 库存账本（证据） | 查询 `receipt_id` 最终计数、SKU 数量和时间线，作为唯一入库 Oracle。 |
| logcat/Trace/报告（人工决策） | 失败包关联设备日志、截图、网络和服务证据；设备覆盖扩展、阻断或降级由 owner 决定。 |

可执行物料是收货 YAML、权限状态表、生命周期序列、设备矩阵和失败包规范。先跑启动/登录探针，再跑权限、恢复、断网和重复上传。

## Manuscript map

从“旋转后 UI 显示一件、账本入库两次”的反例说明双 Oracle。接着比较组件、应用、API 和设备层，展示 Espresso IdlingResource 与 Appium 设备链路的职责。页面必须包含首次权限拒绝、后台恢复、进程杀死、网络切换和三种设备切片，并把 logcat/Trace/账本串进报告。

## Editorial review

没有把单模拟器绿推断成 Android 兼容性，也没有把 Appium、Espresso 和 Maestro 混成同一种能力。明确源码/黑盒选型、权限系统边界、服务端幂等和设备版本锁定。所有设备结论保留 `desk-researched`，没有伪造 emulator 或真机结果。

## Validation

当前状态：`desk-researched`，未启动 Android emulator、真机、APK 或库存服务。

后续可离线升级为 fixture-tested：`validate_android_receiving_fixture.py` 检查生命周期和 Oracle；`simulate_permission_matrix.py` 模拟允许/拒绝/永久拒绝；`replay_receipt_queue.py` 验证同一 `receipt_id` 不重复；`classify_logcat_fixture.py` 分类 ANR/崩溃/权限；`build_device_manifest.py` 检查 API、厂商、分辨率和网络字段。离线模拟不能证明 ROM、相机和真实系统弹窗行为。
