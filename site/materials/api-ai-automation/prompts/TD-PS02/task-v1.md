# TD-PS02 Task Prompt v1.0.0

控制问题：怎样证明 Schema 生成的用例具备业务检测力，而不是生成大量合法 JSON？

业务场景：支付意图 amount currency merchant customer 与过期状态形成跨字段约束

方法选择：Schema 正反例负责结构，属性测试负责不变量，固定 seed 与 shrink 负责复现，mutation 负责检测力；四者职责不能合并

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。读取 OpenAPI 和历史缺陷，只输出风险约束、最小正反例、固定 seed 与 mutation 映射；不得把 Schema 通过写成业务通过。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
