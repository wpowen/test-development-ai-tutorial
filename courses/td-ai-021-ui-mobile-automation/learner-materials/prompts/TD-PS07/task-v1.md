# TD-PS07 Task Prompt v1.0.0

控制问题：怎样区分 XCUITest 可见状态、系统权限、签名环境与服务端预约结果，并确保测试后无状态残留？

业务场景：医疗预约改期跨日期控件、通知权限、后台恢复、模拟器/真机和后端预约版本

方法选择：accessibility identifier 保持定位契约，launch arguments 注入可控状态，XCTest expectation 等待业务信号，环境 manifest 固定签名和设备，后端预约版本作 Oracle

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。读取预约状态机、XCUITest preflight、权限与环境清单，生成 launch state、等待条件、清理和后端 Oracle；不得把模拟器通过写成真机通过。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
