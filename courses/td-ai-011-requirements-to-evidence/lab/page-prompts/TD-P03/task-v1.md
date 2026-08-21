# TD-P03 技术文档解析与一致性审查｜Task Prompt v1.2.0

使用紧随其后的 input.json 完成一次 TD-P03 分析。不要读取未列入 source_refs 的隐含信息。

处理方法：
1. 画出组件和调用边界
2. 提取接口/状态/时序合同
3. 分析失败恢复与幂等
4. 构建需求到设计映射和审查问题

你必须回答的专业决策：技术方案能否实现并验证需求；哪些差异属于 SOURCE_CONFLICT 或 SEMANTIC_UNKNOWN。

输出要求：
1. 只输出一个符合 schema.json 的 JSON 对象，不加 Markdown 围栏。
2. 每个事实写 source_refs 或显式标为 Inference / Unknown。
3. 若命中 BLOCKED、SOURCE_CONFLICT、UNSUPPORTED_RULE、SEMANTIC_UNKNOWN、SCHEMA_INVALID、REFUSED 或 INCOMPLETE，不得继续生成下游成功结论。
4. 不得声称已调用模型、已执行企业集成、已获 practitioner 批准或已具备 production 证据。
