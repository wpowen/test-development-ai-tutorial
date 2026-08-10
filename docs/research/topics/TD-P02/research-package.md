# TD-P02 · 需求契约与结构化抽取

## Research brief

控制问题：怎样把自然语言需求变成下游测试设计可以直接消费、且每条规则能回到原文的 Requirement Contract？学习者要区分 Schema 合规和业务正确。产物是经过引用校验的 `requirement-contract.json`。

## Source pack

- OpenAI Structured Outputs：供应商说明 JSON Schema 约束、refusal 和 incomplete 处理；Schema 合规不保证字段值语义正确。
- ISO/IEC/IEEE 29148：需求信息项的结构化依据；页面公开信息不足以支持逐条引用标准原文。
- ISTQB CTFL 4.0.1：test basis 与测试工件追溯。
- OpenAPI 3.2：JSON Pointer 可作为接口字段和响应的稳定引用。
- JSONSchemaBench：结构合规、约束覆盖与输出质量是不同问题；研究结果不直接等同于任一业务模型准确率。

## Evidence synthesis

事实：Structured Outputs 可提高输出结构稳定性，并要求调用方处理拒绝或不完整结果。工程综合：关键字段分成事实、未知和冲突，所有 ACCEPTED 规则必须带 source_refs；金额、权限、状态和副作用仍由领域 owner 复核。未知：模型在目标企业文档上的提取准确率。

## Engineering blueprint

契约字段覆盖 actor、trigger、preconditions、state transitions、invariants、exceptions、side effects、NFR、unknowns、conflicts 和 source_refs。先做 Schema 校验，再做引用存在性校验，最后做人工语义审查。实验注入一个没有来源的 `refund_timeout_hours=24`，预期返回 BLOCKED。

## Manuscript map

页面先展示一个真实可消费的数据形状，再解释结构正确的边界，然后提供提取任务和无来源字段负控制。避免把提示词包装成最终能力。

## Editorial review

PASS 95/100。保留字段名、枚举、命令与“不保证语义正确”的边界。删除“智能解析”“高质量输出”等没有度量的词。每段都指向契约字段、校验动作或责任人。

## Validation

PASS：干净契约返回 0；无来源规则返回 2 并指出 requirement_id 和字段。尚未用真实模型生成契约，因此状态为 desk-researched。
