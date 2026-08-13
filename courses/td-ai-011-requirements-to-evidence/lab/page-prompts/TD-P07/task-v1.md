# TD-P07 测试执行、结果归因与缺陷报告｜Task Prompt v1.2.0

使用紧随其后的 input.json 完成一次 TD-P07 分析。不要读取未列入 source_refs 的隐含信息。

处理方法：
1. 冻结版本/命令/cwd/环境
2. 保留每次尝试和原始证据
3. 按证据归因而非猜测
4. 形成复现步骤、影响、owner 和决策

你必须回答的专业决策：当前结果属于 PASS、FAIL、BLOCKED 还是 INCOMPLETE；是否足以提交缺陷或进入下一阶段。

输出要求：
1. 只输出一个符合 schema.json 的 JSON 对象，不加 Markdown 围栏。
2. 每个事实写 source_refs 或显式标为 Inference / Unknown。
3. 若命中 BLOCKED、SOURCE_CONFLICT、UNSUPPORTED_RULE、SEMANTIC_UNKNOWN、SCHEMA_INVALID、REFUSED 或 INCOMPLETE，不得继续生成下游成功结论。
4. 不得声称已调用模型、已执行企业集成、已获 practitioner 批准或已具备 production 证据。
