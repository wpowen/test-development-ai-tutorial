# TD-PS12 Task Prompt v1.0.0

控制问题：怎样从 threat model 和权限矩阵构建确定性安全 Oracle，并证明拒绝发生在工具边界且没有跨租户读取或写副作用？

业务场景：退款助手能读取订单并调用工具，攻击者可能利用对象 ID、Prompt 注入、越权 token 或日志泄密

方法选择：ASVS/WSTG 提供控制目录，威胁建模映射资产与信任边界，身份/对象/功能级权限矩阵构造负例，输入验证和工具 allowlist 强制策略，审计 Trace 提供拒绝证据

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。读取 threat model、角色权限、API/工具 schema 与数据分类，生成 abuse case、独立 Oracle 和证据要求；不得生成真实攻击生产命令或自动批准风险。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
