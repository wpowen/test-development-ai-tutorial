# TD-AG-09｜四证据环与离线到在线的成熟度门

来源：S-USER-AGENT-V2；课程映射：agent-source-adjudication.md；本页方法包与教材保持同一 topic_id。

## Professional problem
离线分数通过不代表可以在线；如果没有 sandbox、shadow、online 的风险接受和硬红线，发布只是猜测。

## Method and rationale
成熟度阶梯法：按 offline、sandbox、shadow、online 四环登记证据，明确 statistical gate、hard redline、risk acceptance 与 receipt maturity。 把“已测”与“可发布”拆开，避免 fixture PASS 被误写成生产结论。

## Prompt-Eval-Mutation contract
Prompt manifest 为四环分别记录输入、门槛、证据 owner 和 receipt；shadow、online 明确写 NOT_RUN。 Eval 断言 OFFLINE、SANDBOX、UNRUN-BOUNDARY、HARD-REDLINE、STATISTICAL、RISK-ACCEPTANCE、RECEIPT。 Mutation 将 hard_redline 改为 false；模拟离线分数很好但关键风险未设硬门。

## Independent Oracle and executable evidence
UNRUN-BOUNDARY 必须保留 shadow/online=NOT_RUN；HARD-REDLINE、STATISTICAL、RISK-ACCEPTANCE、RECEIPT 共同决定能否升环。
实际命令：`python3 site/public/materials/agent-architecture-system/scripts/agent_architecture_lab.py --topic TD-AG-09 --phase cycle --report-dir reports/td-ag-09`。预期 baseline/fault/repair 退出码为 `[0,1,0]`；诊断字段为 `failed_oracle_ids`，fault 必须只命中本页命名变量。若 HARD-REDLINE 失败，停止晋级；若 UNRUN-BOUNDARY 失败，检查是否把规划写成已执行。

## Transfer and boundary
迁移到线上客服 Agent 时先补 sandbox 与 shadow 的真实 owner、分母、回滚和风险签收，再讨论 online。 本页只演示离线/沙箱记录结构，shadow 与 online 明确 NOT_RUN；没有 live、practitioner、production 或 learner gate 证据。

## Editorial review
- review_id: AG-EDITORIAL-2026-08-12-TD-AG-09
- reviewer: course-editorial-owner
- scope: 四证据环与离线到在线的成熟度门 的专业问题、方法与理由、独立 Oracle、Prompt/Eval/Mutation、实际 0-1-0 命令、故障诊断、迁移和边界。
- method: sentence-level duplicate scan against TD-AG-00..TD-AG-10；逐页检查主题专属术语、artifact chain 的 method/risk/oracle/prompt/eval/mutation 以及受保护的 fixture/NOT_RUN 语义。
- protected_items: fixture-tested、NOT_RUN、live、practitioner、production 边界不得被升级或删除。
- duplicate_scan: 本页已改为主题专属句子；四证据环、独立 Oracle 和边界词属于必要共享术语，不作为实质教学重复。
- decision: pending-independent-rerun；本记录不是 practitioner review、live evidence 或 production receipt。
- limitations: 需要 validation lane 重新运行独立 editorial audit 才能更新评分。

## Beginner check
初学者应能指出本页故障字段、独立 Oracle、实际命令、`[0,1,0]` 结果和迁移时新增的 owner/数据/权限；不能回答时保持 BLOCKED。
