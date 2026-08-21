# TD-AG-10｜高风险 Agent：建议与执行分离、硬限额与双批准

来源：S-USER-AGENT-V2；课程映射：agent-source-adjudication.md；本页方法包与教材保持同一 topic_id。

## Professional problem
涉及资金、删除或高影响决定时，建议文本一旦越过执行边界就会产生不可逆后果。

## Method and rationale
高风险隔离法：先写 timestamp，再分开 advice/execution，施加 capability sandbox、hard limit、dual approval、kill switch，并声明 no_real_funds。 安全关键不是让 Agent 更聪明，而是让危险动作在权限和审批上不可隐式发生。

## Prompt-Eval-Mutation contract
Prompt manifest 固定时间戳、能力沙箱、硬限额、双批准、kill switch 与无真实资金标志，输出建议不得触发副作用。 Eval 断言 TIMESTAMP、ADVICE-EXECUTION、SANDBOX、HARD-LIMIT、DUAL-APPROVAL、KILL-SWITCH、NO-REAL-FUNDS。 Mutation 将 hard_limit 改为 false，模拟危险动作失去上限；其余批准和 kill switch 保持不变。

## Independent Oracle and executable evidence
ADVICE-EXECUTION 检查建议与执行分离；HARD-LIMIT、DUAL-APPROVAL、KILL-SWITCH 和 NO-REAL-FUNDS 构成最后防线。
实际命令：`python3 site/public/materials/agent-architecture-system/scripts/agent_architecture_lab.py --topic TD-AG-10 --phase cycle --report-dir reports/td-ag-10`。预期 baseline/fault/repair 退出码为 `[0,1,0]`；诊断字段为 `failed_oracle_ids`，fault 必须只命中本页命名变量。若 HARD-LIMIT 失败，立即阻断执行并记录时间戳、请求人和批准链；不能用文本解释覆盖硬门。

## Transfer and boundary
迁移到支付、删除或生产变更流程时，用 dry-run、双人批准、最小能力、可撤销令牌和独立 kill switch。 当前仅为无真实资金的高风险状态 fixture；真实建议、执行权限、practitioner approval、production action 与 learner transfer 均 NOT_RUN.

## Editorial review
- review_id: AG-EDITORIAL-2026-08-12-TD-AG-10
- reviewer: course-editorial-owner
- scope: 高风险 Agent：建议与执行分离、硬限额与双批准 的专业问题、方法与理由、独立 Oracle、Prompt/Eval/Mutation、实际 0-1-0 命令、故障诊断、迁移和边界。
- method: sentence-level duplicate scan against TD-AG-00..TD-AG-10；逐页检查主题专属术语、artifact chain 的 method/risk/oracle/prompt/eval/mutation 以及受保护的 fixture/NOT_RUN 语义。
- protected_items: fixture-tested、NOT_RUN、live、practitioner、production 边界不得被升级或删除。
- duplicate_scan: 本页已改为主题专属句子；四证据环、独立 Oracle 和边界词属于必要共享术语，不作为实质教学重复。
- decision: pending-independent-rerun；本记录不是 practitioner review、live evidence 或 production receipt。
- limitations: 需要 validation lane 重新运行独立 editorial audit 才能更新评分。

## Beginner check
初学者应能指出本页故障字段、独立 Oracle、实际命令、`[0,1,0]` 结果和迁移时新增的 owner/数据/权限；不能回答时保持 BLOCKED。
