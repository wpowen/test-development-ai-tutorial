# TD-P08 变更影响、回归选择与发布证据｜Task Prompt v1.2.0

使用紧随其后的 input.json 完成一次 TD-P08 分析。不要读取未列入 source_refs 的隐含信息。

处理方法：
1. 识别 before/after change set
2. 沿追踪图传播 impact
3. 按风险选择回归并解释未选项
4. 封装证据、残余风险和发布决策

你必须回答的专业决策：是否形成 release candidate；哪些旧 PASS 已失效，哪些残余风险必须由人类 release owner 决定。

输出要求：
1. 只输出一个符合 schema.json 的 JSON 对象，不加 Markdown 围栏。
2. 每个事实写 source_refs 或显式标为 Inference / Unknown。
3. 若命中 BLOCKED、SOURCE_CONFLICT、UNSUPPORTED_RULE、SEMANTIC_UNKNOWN、SCHEMA_INVALID、REFUSED 或 INCOMPLETE，不得继续生成下游成功结论。
4. 不得声称已调用模型、已执行企业集成、已获 practitioner 批准或已具备 production 证据。
