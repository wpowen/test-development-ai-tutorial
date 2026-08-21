# 完整测试生命周期 Prompt Kit：小白直接使用指南

这套材料不是让你一次性把所有文档丢给 AI。正确顺序是：先看能做什么，再准备当前步骤需要的输入，直接复制对应 Prompt，替换输入粘贴区，检查输出，通过门禁后才进入下一步。

## 八步流程

1. TD-P01：冻结测试依据，确认版本、来源权威、冲突和下游入口。
2. TD-P02：做需求评审和需求解析，形成 Requirement Contract 与验收标准。
3. TD-P03：解析技术文档，形成组件、接口、状态、失败恢复和需求一致性矩阵。
4. TD-P04：从风险选择测试方法、层级、Oracle、监控和责任人。
5. TD-P05：先固定独立 Oracle，再生成测试点和可执行测试用例。
6. TD-P06：审查用例，再适配 API、契约、组件、UI 或数据自动化。
7. TD-P07：固定运行版本与证据，分类失败，生成可复现缺陷和决策摘要。
8. TD-P08：分析变更影响，选择回归集，使过期 PASS 失效，生成发布候选证据。

## 第一次怎么用

打开当前步骤的 `page-prompts/<页面 ID>/prompt-v1.md`，复制“直接复制到 AI Agent”代码块，粘贴到你使用的 AI Agent。只替换方括号里的业务范围、文档和责任规则。输入过长时按一个业务能力分批处理，保留相同 baseline_id 和 source_ref。

这是“一次复制”的入门路径。需要更稳定、可审查的专业路径时，进入同一页面目录，按以下组合顺序使用完整 Prompt Package：

1. 把 `system-v1.md` 放在 AI Agent 的 system/instructions 区；
2. 发送 `task-v1.md`；
3. 紧接着附上已替换的 `input.json`；
4. 得到首轮 JSON 后，另起一轮发送 `critic-v1.md`；
5. 用 `schema.json` 检查结构，用 `eval.json` 检查正向、边界、冲突、缺失、越权、拒答、截断和中英混合，用 `mutation.json` 验证关键错误能被发现；
6. 用 `expected-output.json` 理解字段，不要把示例业务值当成你项目的正确答案。

每个目录的 `adaptation-card.md` 解释该阶段具体该改什么，`manifest.json` 固定组合顺序和每个文件的 SHA-256，`receipt.json` 明确当前没有模型原始输出。

## 你必须检查什么

- AI 引用的事实能否回到你粘贴的原文？
- Evidence、Inference、Unknown 是否分开？
- AI 是否偷偷补了金额、状态、错误码、时间、权限或阈值？
- BLOCKED 项是否真的停止下游？
- 结果是否有 owner、close_with 和可执行下一步？

## 不能替你决定什么

AI 不能替产品批准需求，不能替架构师选择冲突设计，不能替测试负责人接受残余风险，也不能批准发布。Prompt 文件经过结构与离线负控制检查，但真实模型执行为 NOT_RUN；在你的业务中必须人工抽样回读并保存模型/版本/输入/输出收据。

当前每套 `receipt.json` 都是 `static-package-build-receipt`：`provider=none`、`model=offline-deterministic`、`model_status=NOT_RUN`，`raw_output_refs=[]`。这表示包已经构建并可做静态/fixture 验证，不表示某个模型已经运行，更不表示准确率、企业集成、从业者认可或生产可用。

## 改完如何复用

先填写 `ADAPTATION-CARD.md`：换业务场景、来源权威、责任人、数据/权限边界和验证方法；保持 source_ref、独立 Oracle、状态门禁、追踪 ID 和证据分层不变。完成后先用小范围 fixture 跑一次，再植入一个已知错误验证能变红，修复后重跑变绿。
