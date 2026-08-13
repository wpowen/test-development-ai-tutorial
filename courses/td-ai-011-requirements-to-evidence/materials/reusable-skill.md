# 可复用工作流

输入资料先建立版本、hash、owner、source_ref 和优先级。提取 Agent 只生成 Requirement Contract；Critic 单独检查冲突、未知和不可测项；测试设计 Agent 只读取 ACCEPTED 契约与风险计划；执行器保存版本和原始证据。

关键规则：无来源字段为 UNKNOWN；来源冲突为 BLOCKED；关键 Oracle 不得从被测实现推导；每条高风险至少有一个 mutation；发布结论由具名责任人决定。

实际使用从 `../lab/DIRECT-USE-GUIDE.md` 开始。八套 `../lab/page-prompts/TD-P01..TD-P08/prompt-v1.md` 已把测试依据、需求评审/解析、技术文档解析、风险方法、Oracle/用例、自动化、执行归因和回归发布拆成可复制任务。填写 `../lab/ADAPTATION-CARD.md` 后，只替换业务输入、来源权威、责任人、工具和验证方法；不要删除 source_ref、Evidence/Inference/Unknown、BLOCKED、独立 Oracle 和版本追踪。
