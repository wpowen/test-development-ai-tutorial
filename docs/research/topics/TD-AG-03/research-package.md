# TD-AG-03｜Orchestration 编排、交接与三重预算

来源：S-USER-AGENT-V2；课程映射：agent-source-adjudication.md；本页方法包与教材保持同一 topic_id。

## Professional problem
多 Agent 交接时事实可能丢失，且没有 step/time/cost 三重预算；系统会在错误上下文里继续执行。

## Method and rationale
交接契约法：先冻结 handoff schema 与事实字段，再验证隔离、事实存活数、step_limit、time_limit、cost_limit 和 stop_reason。 把“编排顺利”拆成可检查的上下文与预算合同，学习者才能判断应停在何处。

## Prompt-Eval-Mutation contract
Prompt manifest 输入 handoff_schema、facts_survive、isolation、step_limit、time_limit、cost_limit、stop_reason，并禁止隐式补全。 Eval 逐项断言 HANDOFF、FACT-SURVIVAL、ISOLATION、TRIPLE-BUDGET、STOP-REASON，失败后输出下游不可继续的理由。 Mutation 清空 stop_reason；其他字段保持原值，模拟无限重试而非普遍模型失败。

## Independent Oracle and executable evidence
FACT-SURVIVAL 要求至少 5 个事实跨交接保留；TRIPLE-BUDGET 检查三种预算同时存在；STOP-REASON 不能为空。
实际命令：`python3 site/public/materials/agent-architecture-system/scripts/agent_architecture_lab.py --topic TD-AG-03 --phase cycle --report-dir reports/td-ag-03`。预期 baseline/fault/repair 退出码为 `[0,1,0]`；诊断字段为 `failed_oracle_ids`，fault 必须只命中本页命名变量。若 STOP-REASON 失败，检查上游是否写入结构化停止原因；若 FACT-SURVIVAL 失败，比较交接前后事实键集合。

## Transfer and boundary
迁移到研发流水线时为每个子 Agent 规定输入/输出 schema、预算 owner、重试上限和升级路径。 本页只证明合成编排数据的交接与预算检查；真实多 Agent 运行、在线成本、practitioner handoff、production SLA 和 learner transfer 均 NOT_RUN。

## Editorial review
- review_id: AG-EDITORIAL-2026-08-12-TD-AG-03
- reviewer: course-editorial-owner
- scope: Orchestration 编排、交接与三重预算 的专业问题、方法与理由、独立 Oracle、Prompt/Eval/Mutation、实际 0-1-0 命令、故障诊断、迁移和边界。
- method: sentence-level duplicate scan against TD-AG-00..TD-AG-10；逐页检查主题专属术语、artifact chain 的 method/risk/oracle/prompt/eval/mutation 以及受保护的 fixture/NOT_RUN 语义。
- protected_items: fixture-tested、NOT_RUN、live、practitioner、production 边界不得被升级或删除。
- duplicate_scan: 本页已改为主题专属句子；四证据环、独立 Oracle 和边界词属于必要共享术语，不作为实质教学重复。
- decision: pending-independent-rerun；本记录不是 practitioner review、live evidence 或 production receipt。
- limitations: 需要 validation lane 重新运行独立 editorial audit 才能更新评分。

## Beginner check
初学者应能指出本页故障字段、独立 Oracle、实际命令、`[0,1,0]` 结果和迁移时新增的 owner/数据/权限；不能回答时保持 BLOCKED。
