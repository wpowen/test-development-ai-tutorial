# TD-PS04 Task Prompt v1.0.0

控制问题：怎样让 UI 测试等待业务终态、隔离数据并保存可诊断 Trace，而不是靠 sleep 和文本出现判绿？

业务场景：后台退款审批需跨 UI、订单 API、异步状态和审计记录完成

方法选择：用户感知 locator 与显式 test id 负责定位，auto-wait 负责 actionability，API/账本负责业务 Oracle，独立上下文负责隔离，Trace 负责诊断

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。读取旅程、角色、网络契约和风险矩阵，输出 locator 选择、等待信号、隔离数据、业务 Oracle 与失败证据；不得生成 fixed sleep。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
