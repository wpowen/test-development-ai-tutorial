# TD-P05 Oracle、测试点与测试用例生成｜Task Prompt v1.2.0

使用紧随其后的 input.json 完成一次 TD-P05 分析。不要读取未列入 source_refs 的隐含信息。

处理方法：
1. 先定义独立 Oracle
2. 用等价类/边界/状态/决策表拆条件
3. 写前置/步骤/数据/预期/清理
4. 闭合 source_ref 与风险追踪

你必须回答的专业决策：每个用例是否能独立判断结果，是否覆盖关键风险，缺少哪项输入时必须 BLOCKED。

输出要求：
1. 只输出一个符合 schema.json 的 JSON 对象，不加 Markdown 围栏。
2. 每个事实写 source_refs 或显式标为 Inference / Unknown。
3. 若命中 BLOCKED、SOURCE_CONFLICT、UNSUPPORTED_RULE、SEMANTIC_UNKNOWN、SCHEMA_INVALID、REFUSED 或 INCOMPLETE，不得继续生成下游成功结论。
4. 不得声称已调用模型、已执行企业集成、已获 practitioner 批准或已具备 production 证据。
