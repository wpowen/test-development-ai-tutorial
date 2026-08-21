# TD-AG-00｜Agent 测试架构总览与边界登记

来源：S-USER-AGENT-V2；课程映射：agent-source-adjudication.md；本页方法包与教材保持同一 topic_id。

## Professional problem
架构图如果只有节点名称，测试开发工程师仍无法证明 D0-D7 的输入、权限、状态、四证据环和责任人已经闭合。

## Method and rationale
边界闭合表法：先把输入、D0-D7 域、四证据环、guard、owner、Oracle 写成不可省略的字段，再以一条故障只破坏 OWNER-ORACLE 做反例。 这样学习者能把“画架构”转换成可审计的风险清单，而不是凭图形判断覆盖率。

## Prompt-Eval-Mutation contract
Prompt manifest 以 boundary.inputs/domains/rings/guards/owners/oracles 为输入，固定 TD-AG-00 fixture。 Eval 读取 baseline、fault、repair 的 failed_oracle_ids，并核对 INPUTS、D0-D7、FOUR-RINGS、GUARDS、OWNER-ORACLE。 Mutation 只将 boundary.oracles 从 true 改为 false，禁止调阈值或删除检查。

## Independent Oracle and executable evidence
OWNER-ORACLE 同时检查 owners 与 oracles；故障态必须列出 OWNER-ORACLE，不能用模型质量解释。
实际命令：`python3 site/public/materials/agent-architecture-system/scripts/agent_architecture_lab.py --topic TD-AG-00 --phase cycle --report-dir reports/td-ag-00`。预期 baseline/fault/repair 退出码为 `[0,1,0]`；诊断字段为 `failed_oracle_ids`，fault 必须只命中本页命名变量。若 fault 返回 []，说明 Oracle 没有独立读取边界字段；若出现 OWNER-ORACLE，回看 owner/oracle 责任矩阵。

## Transfer and boundary
迁移到客服 Agent 时重填会话输入、工具权限、状态字段、四环证据和批准人；架构图必须伴随边界表。 本页仅以离线合成边界 fixture 证明闭环；真实模型、在线工具、企业数据、practitioner review、learner transfer 与 production deployment 均 NOT_RUN。

## Editorial review
- review_id: AG-EDITORIAL-2026-08-12-TD-AG-00
- reviewer: course-editorial-owner
- scope: Agent 测试架构总览与边界登记 的专业问题、方法与理由、独立 Oracle、Prompt/Eval/Mutation、实际 0-1-0 命令、故障诊断、迁移和边界。
- method: sentence-level duplicate scan against TD-AG-00..TD-AG-10；逐页检查主题专属术语、artifact chain 的 method/risk/oracle/prompt/eval/mutation 以及受保护的 fixture/NOT_RUN 语义。
- protected_items: fixture-tested、NOT_RUN、live、practitioner、production 边界不得被升级或删除。
- duplicate_scan: 本页已改为主题专属句子；四证据环、独立 Oracle 和边界词属于必要共享术语，不作为实质教学重复。
- decision: pending-independent-rerun；本记录不是 practitioner review、live evidence 或 production receipt。
- limitations: 需要 validation lane 重新运行独立 editorial audit 才能更新评分。

## Beginner check
初学者应能指出本页故障字段、独立 Oracle、实际命令、`[0,1,0]` 结果和迁移时新增的 owner/数据/权限；不能回答时保持 BLOCKED。
