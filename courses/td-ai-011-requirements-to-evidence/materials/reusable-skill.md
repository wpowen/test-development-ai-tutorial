# 可复用工作流

输入资料先建立版本、hash、owner、source_ref 和优先级。提取 Agent 只生成 Requirement Contract；Critic 单独检查冲突、未知和不可测项；测试设计 Agent 只读取 ACCEPTED 契约与风险计划；执行器保存版本和原始证据。

关键规则：无来源字段为 UNKNOWN；来源冲突为 BLOCKED；关键 Oracle 不得从被测实现推导；每条高风险至少有一个 mutation；发布结论由具名责任人决定。
