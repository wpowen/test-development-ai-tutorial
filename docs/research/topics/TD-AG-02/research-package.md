# TD-AG-02｜Trace 级轨迹、工具调用与首错定位

来源：S-USER-AGENT-V2；课程映射：agent-source-adjudication.md；本页方法包与教材保持同一 topic_id。

## Professional problem
最终答案正确并不代表过程安全；一次被禁止的工具调用或缺失的首错 span 可能被最后的文本掩盖。

## Method and rationale
轨迹首错法：把 outcome、每步 action、工具参数、授权结果、trace 完整性和 first_error 置于同一事件序列，优先定位最早违反合同的 span。 首错定位能阻止团队在下游输出上反复调 Prompt，却漏掉真正的权限或状态根因。

## Prompt-Eval-Mutation contract
Prompt manifest 要求输出 trace.outcome、prohibited_calls、authorized、complete、first_error，并保留原始事件顺序。 Eval 分别验证 OUTCOME、STEP-SAFETY、TRACE-COMPLETE、FIRST-ERROR，不接受只给最终文本的替代证据。 Mutation 把 prohibited_calls 从 0 改为 1；故障只增加一次越权调用，不重写 outcome。

## Independent Oracle and executable evidence
STEP-SAFETY 检查 prohibited_calls=0 且 authorized；FIRST-ERROR 要求首个异常 span 可回指，TRACE-COMPLETE 检查链条无洞。
实际命令：`python3 site/public/materials/agent-architecture-system/scripts/agent_architecture_lab.py --topic TD-AG-02 --phase cycle --report-dir reports/td-ag-02`。预期 baseline/fault/repair 退出码为 `[0,1,0]`；诊断字段为 `failed_oracle_ids`，fault 必须只命中本页命名变量。failed_oracle_ids 出现 STEP-SAFETY 时查看调用参数和权限快照；出现 FIRST-ERROR 时定位 trace 中最早异常 span。

## Transfer and boundary
迁移到 Playwright 或 MCP 工具链时，为每步保留 action、参数、授权、结果、时间戳和首错指针。 当前只执行离线 trace fixture；真实 Agent trace、在线工具副作用、practitioner incident review、production observability 与 learner transfer 均 NOT_RUN。

## Editorial review
- review_id: AG-EDITORIAL-2026-08-12-TD-AG-02
- reviewer: course-editorial-owner
- scope: Trace 级轨迹、工具调用与首错定位 的专业问题、方法与理由、独立 Oracle、Prompt/Eval/Mutation、实际 0-1-0 命令、故障诊断、迁移和边界。
- method: sentence-level duplicate scan against TD-AG-00..TD-AG-10；逐页检查主题专属术语、artifact chain 的 method/risk/oracle/prompt/eval/mutation 以及受保护的 fixture/NOT_RUN 语义。
- protected_items: fixture-tested、NOT_RUN、live、practitioner、production 边界不得被升级或删除。
- duplicate_scan: 本页已改为主题专属句子；四证据环、独立 Oracle 和边界词属于必要共享术语，不作为实质教学重复。
- decision: pending-independent-rerun；本记录不是 practitioner review、live evidence 或 production receipt。
- limitations: 需要 validation lane 重新运行独立 editorial audit 才能更新评分。

## Beginner check
初学者应能指出本页故障字段、独立 Oracle、实际命令、`[0,1,0]` 结果和迁移时新增的 owner/数据/权限；不能回答时保持 BLOCKED。
