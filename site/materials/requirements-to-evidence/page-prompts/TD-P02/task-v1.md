# TD-P02 需求评审与需求解析｜Task Prompt v1.2.0

使用紧随其后的 input.json 完成一次 TD-P02 分析。不要读取未列入 source_refs 的隐含信息。

处理方法：
1. 识别角色与业务结果
2. 拆正常/边界/异常/权限/状态规则
3. 将规则改写为可观察验收标准
4. 登记评审问题与 readiness gate

你必须回答的专业决策：需求是否达到 test-ready；哪些问题必须由产品、业务或合规责任人关闭。

输出要求：
1. 只输出一个符合 schema.json 的 JSON 对象，不加 Markdown 围栏。
2. 每个事实写 source_refs 或显式标为 Inference / Unknown。
3. 若命中 BLOCKED、SOURCE_CONFLICT、UNSUPPORTED_RULE、SEMANTIC_UNKNOWN、SCHEMA_INVALID、REFUSED 或 INCOMPLETE，不得继续生成下游成功结论。
4. 不得声称已调用模型、已执行企业集成、已获 practitioner 批准或已具备 production 证据。
