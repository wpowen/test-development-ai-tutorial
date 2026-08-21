# TD-AG-07｜Economics 成本、长尾延迟与 goodput

来源：S-USER-AGENT-V2；课程映射：agent-source-adjudication.md；本页方法包与教材保持同一 topic_id。

## Professional problem
平均延迟和平均 token 费会掩盖 P99 超时、失败重试和低质量吞吐；没有 hard budget 就无法做工程取舍。

## Method and rationale
经济性尾部法：以 task trace 绑定结果、P95/P99、goodput、cost tail、hard budget 与 resource isolation，先排除失败任务再解释效率。 将质量、时延、成本放在同一任务分母中，避免用便宜但不可用的输出冒充提效。

## Prompt-Eval-Mutation contract
Prompt manifest 要求记录 task_trace、P95/P99、goodput、成本尾部、硬预算和资源隔离，不接受只报平均值。 Eval 断言 TASK-TRACE、TAILS、GOODPUT、COST-TAIL、HARD-BUDGET、RESOURCE-ISOLATION。 Mutation 将 hard_budget 改为 false，模拟预算保护被移除而不改变平均指标。

## Independent Oracle and executable evidence
TAILS 同时检查 p95/p99；GOODPUT 只计合格结果；COST-TAIL 与 HARD-BUDGET 防止长尾吞噬预算。
实际命令：`python3 site/public/materials/agent-architecture-system/scripts/agent_architecture_lab.py --topic TD-AG-07 --phase cycle --report-dir reports/td-ag-07`。预期 baseline/fault/repair 退出码为 `[0,1,0]`；诊断字段为 `failed_oracle_ids`，fault 必须只命中本页命名变量。若 HARD-BUDGET 失败，查看超预算任务与重试链；若 GOODPUT 失败，检查质量门是否被平均吞吐掩盖。

## Transfer and boundary
迁移到 CI Agent 时按任务记录 token、工具耗时、P95/P99、合格率和预算 owner，再决定并发或模型路由。 当前只用合成任务 trace 计算指标结构；真实账单、线上负载、practitioner productivity 与 production cost gate 均 NOT_RUN。

## Editorial review
- review_id: AG-EDITORIAL-2026-08-12-TD-AG-07
- reviewer: course-editorial-owner
- scope: Economics 成本、长尾延迟与 goodput 的专业问题、方法与理由、独立 Oracle、Prompt/Eval/Mutation、实际 0-1-0 命令、故障诊断、迁移和边界。
- method: sentence-level duplicate scan against TD-AG-00..TD-AG-10；逐页检查主题专属术语、artifact chain 的 method/risk/oracle/prompt/eval/mutation 以及受保护的 fixture/NOT_RUN 语义。
- protected_items: fixture-tested、NOT_RUN、live、practitioner、production 边界不得被升级或删除。
- duplicate_scan: 本页已改为主题专属句子；四证据环、独立 Oracle 和边界词属于必要共享术语，不作为实质教学重复。
- decision: pending-independent-rerun；本记录不是 practitioner review、live evidence 或 production receipt。
- limitations: 需要 validation lane 重新运行独立 editorial audit 才能更新评分。

## Beginner check
初学者应能指出本页故障字段、独立 Oracle、实际命令、`[0,1,0]` 结果和迁移时新增的 owner/数据/权限；不能回答时保持 BLOCKED。
