# TD-P01 测试生命周期总控与 Test Basis｜Task Prompt v1.2.0

使用紧随其后的 input.json 完成一次 TD-P01 分析。不要读取未列入 source_refs 的隐含信息。

处理方法：
1. 建立来源清单与版本
2. 按权威策略提取 claim
3. 显式登记冲突和 Unknown
4. 形成下游入口门禁

你必须回答的专业决策：Test Basis 是否足以启动需求解析；若不足，谁必须补齐什么证据。

输出要求：
1. 只输出一个符合 schema.json 的 JSON 对象，不加 Markdown 围栏。
2. 每个事实写 source_refs 或显式标为 Inference / Unknown。
3. 若命中 BLOCKED、SOURCE_CONFLICT、UNSUPPORTED_RULE、SEMANTIC_UNKNOWN、SCHEMA_INVALID、REFUSED 或 INCOMPLETE，不得继续生成下游成功结论。
4. 不得声称已调用模型、已执行企业集成、已获 practitioner 批准或已具备 production 证据。
