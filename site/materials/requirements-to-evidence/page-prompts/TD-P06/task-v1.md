# TD-P06 用例审查与自动化适配｜Task Prompt v1.2.0

使用紧随其后的 input.json 完成一次 TD-P06 分析。不要读取未列入 source_refs 的隐含信息。

处理方法：
1. 审查 Oracle 与追踪
2. 区分业务步骤和工具适配
3. 定义 Adapter Contract 与禁止副作用
4. 给出可重放红绿命令与证据路径

你必须回答的专业决策：哪些用例可自动化、哪些仍需修复/人工判断，以及执行所需 cwd、依赖、清理和证据。

输出要求：
1. 只输出一个符合 schema.json 的 JSON 对象，不加 Markdown 围栏。
2. 每个事实写 source_refs 或显式标为 Inference / Unknown。
3. 若命中 BLOCKED、SOURCE_CONFLICT、UNSUPPORTED_RULE、SEMANTIC_UNKNOWN、SCHEMA_INVALID、REFUSED 或 INCOMPLETE，不得继续生成下游成功结论。
4. 不得声称已调用模型、已执行企业集成、已获 practitioner 批准或已具备 production 证据。
