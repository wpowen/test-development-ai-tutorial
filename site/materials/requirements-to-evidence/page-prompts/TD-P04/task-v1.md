# TD-P04 风险分析与测试方法选择｜Task Prompt v1.2.0

使用紧随其后的 input.json 完成一次 TD-P04 分析。不要读取未列入 source_refs 的隐含信息。

处理方法：
1. 按失败成本和可探测性建风险项
2. 为每项选择技术与测试层
3. 绑定独立 Oracle 和数据/环境
4. 登记阻断与残余风险

你必须回答的专业决策：测什么、为什么测、在哪一层测、何时停止，以及哪些残余风险需要责任人接受。

输出要求：
1. 只输出一个符合 schema.json 的 JSON 对象，不加 Markdown 围栏。
2. 每个事实写 source_refs 或显式标为 Inference / Unknown。
3. 若命中 BLOCKED、SOURCE_CONFLICT、UNSUPPORTED_RULE、SEMANTIC_UNKNOWN、SCHEMA_INVALID、REFUSED 或 INCOMPLETE，不得继续生成下游成功结论。
4. 不得声称已调用模型、已执行企业集成、已获 practitioner 批准或已具备 production 证据。
