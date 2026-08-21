# TD-AG-08｜Governance 业务规则、四版本链与审计

来源：S-USER-AGENT-V2；课程映射：agent-source-adjudication.md；本页方法包与教材保持同一 topic_id。

## Professional problem
模型、Prompt、工具、记忆任何一项漂移，都可能让同一业务规则得到不可复现的结果；缺少 owner 就无法追责。

## Method and rationale
四版本审计法：把 business_rules、audit_chain、model/prompt/tool/memory 四版本、human_owner 与 rollback 绑定为一条可回放记录。 版本链让问题从“模型变了”具体落到可比较的变更和回滚动作。

## Prompt-Eval-Mutation contract
Prompt manifest 记录四版本哈希、规则引用、事件序列、owner 和 rollback 指针，禁止用当前版本覆盖历史。 Eval 断言 BUSINESS-RULES、AUDIT、FOUR-VERSION、OWNER、ROLLBACK 五项，并核对 tool_version 变异。 Mutation 将 tool_version 改为 false，模拟工具契约漂移；其他版本保持稳定。

## Independent Oracle and executable evidence
FOUR-VERSION 要求四类版本齐全；AUDIT 连接业务规则与事件；OWNER、ROLLBACK 保证有人能批准和恢复。
实际命令：`python3 site/public/materials/agent-architecture-system/scripts/agent_architecture_lab.py --topic TD-AG-08 --phase cycle --report-dir reports/td-ag-08`。预期 baseline/fault/repair 退出码为 `[0,1,0]`；诊断字段为 `failed_oracle_ids`，fault 必须只命中本页命名变量。若 FOUR-VERSION 失败，比较四个版本字段与审计链；若 OWNER 失败，结论只能是 BLOCKED。

## Transfer and boundary
迁移到企业 RAG 时，将知识库快照、检索器、Prompt、模型、工具和记忆版本写入同一发布 receipt。 四版本结论来自离线治理 fixture；真实企业审计、在线模型漂移、practitioner accountability 与 production rollback 均 NOT_RUN。

## Editorial review
- review_id: AG-EDITORIAL-2026-08-12-TD-AG-08
- reviewer: course-editorial-owner
- scope: Governance 业务规则、四版本链与审计 的专业问题、方法与理由、独立 Oracle、Prompt/Eval/Mutation、实际 0-1-0 命令、故障诊断、迁移和边界。
- method: sentence-level duplicate scan against TD-AG-00..TD-AG-10；逐页检查主题专属术语、artifact chain 的 method/risk/oracle/prompt/eval/mutation 以及受保护的 fixture/NOT_RUN 语义。
- protected_items: fixture-tested、NOT_RUN、live、practitioner、production 边界不得被升级或删除。
- duplicate_scan: 本页已改为主题专属句子；四证据环、独立 Oracle 和边界词属于必要共享术语，不作为实质教学重复。
- decision: pending-independent-rerun；本记录不是 practitioner review、live evidence 或 production receipt。
- limitations: 需要 validation lane 重新运行独立 editorial audit 才能更新评分。

## Beginner check
初学者应能指出本页故障字段、独立 Oracle、实际命令、`[0,1,0]` 结果和迁移时新增的 owner/数据/权限；不能回答时保持 BLOCKED。
