# TD-AG-04｜Human takeover 人工接管、脏状态与回滚

来源：S-USER-AGENT-V2；课程映射：agent-source-adjudication.md；本页方法包与教材保持同一 topic_id。

## Professional problem
高影响动作需要人在环；如果中断后留下 dirty state，人工接管可能重复提交或无法回滚。

## Method and rationale
接管回滚法：在指定 interrupt_step 注入暂停，分别记录 dirty_state、rollback、takeover、approval、owner，再验证状态恢复。 先证明可暂停和可回滚，才有资格讨论自动化比例或无人值守。

## Prompt-Eval-Mutation contract
Prompt manifest 固定 interrupt_step=2，并要求输出状态快照、回滚动作、审批人和接管人，不允许把暂停写成成功。 Eval 检查 INTERRUPT、NO-DIRTY-STATE、ROLLBACK、TAKEOVER、APPROVAL-OWNER 五个独立 Oracle。 Mutation 将 rollback 改为 false；故障模拟中断后无法恢复，而不改变审批字段。

## Independent Oracle and executable evidence
NO-DIRTY-STATE 要求 dirty_state=false；ROLLBACK、TAKEOVER、APPROVAL-OWNER 共同证明人工接管可执行且有责任人。
实际命令：`python3 site/public/materials/agent-architecture-system/scripts/agent_architecture_lab.py --topic TD-AG-04 --phase cycle --report-dir reports/td-ag-04`。预期 baseline/fault/repair 退出码为 `[0,1,0]`；诊断字段为 `failed_oracle_ids`，fault 必须只命中本页命名变量。若 ROLLBACK 失败，先对照状态快照确认哪一步产生脏写；若 APPROVAL-OWNER 失败，停止任何自动执行。

## Transfer and boundary
迁移到发布或数据修复流程时，设计 dry-run、人工批准、幂等键、补偿动作和回滚 owner。 这是离线接管状态机 fixture；真实人工值班、企业权限、生产回滚演练、practitioner sign-off 与 learner transfer 均 NOT_RUN。

## Editorial review
- review_id: AG-EDITORIAL-2026-08-12-TD-AG-04
- reviewer: course-editorial-owner
- scope: Human takeover 人工接管、脏状态与回滚 的专业问题、方法与理由、独立 Oracle、Prompt/Eval/Mutation、实际 0-1-0 命令、故障诊断、迁移和边界。
- method: sentence-level duplicate scan against TD-AG-00..TD-AG-10；逐页检查主题专属术语、artifact chain 的 method/risk/oracle/prompt/eval/mutation 以及受保护的 fixture/NOT_RUN 语义。
- protected_items: fixture-tested、NOT_RUN、live、practitioner、production 边界不得被升级或删除。
- duplicate_scan: 本页已改为主题专属句子；四证据环、独立 Oracle 和边界词属于必要共享术语，不作为实质教学重复。
- decision: pending-independent-rerun；本记录不是 practitioner review、live evidence 或 production receipt。
- limitations: 需要 validation lane 重新运行独立 editorial audit 才能更新评分。

## Beginner check
初学者应能指出本页故障字段、独立 Oracle、实际命令、`[0,1,0]` 结果和迁移时新增的 owner/数据/权限；不能回答时保持 BLOCKED。
