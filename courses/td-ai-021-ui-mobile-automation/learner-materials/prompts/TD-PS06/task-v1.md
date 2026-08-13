# TD-PS06 Task Prompt v1.0.0

控制问题：怎样证明移动生命周期恢复不丢扫描状态也不重复入账，并区分应用、设备和服务端失败？

业务场景：仓库收货扫码经过相机权限、旋转、后台、进程恢复、离线队列和库存 API

方法选择：ViewModel/组件测试覆盖状态，Espresso idling 覆盖同步，UI Automator 覆盖系统权限，设备矩阵覆盖风险切片，服务端幂等账本提供独立 Oracle

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。读取 Android 生命周期、权限、设备矩阵和库存契约，输出分层测试、同步信号、状态恢复与服务端 Oracle；未运行设备写 NOT_RUN。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
