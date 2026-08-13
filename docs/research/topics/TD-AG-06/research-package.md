# TD-AG-06｜Security 注入、MCP 权限与租户隔离

来源：S-USER-AGENT-V2；课程映射：agent-source-adjudication.md；本页方法包与教材保持同一 topic_id。

## Professional problem
Agent 遇到 prompt injection 或恶意工具时，最危险的不是答错，而是跨租户读写和扩大工具权限。

## Method and rationale
最小权限攻击法：冻结攻击样本、manifest hash、tenant、scope、sandbox、side-effect 和 blast radius，再逐条证明拒绝路径。 安全评测必须观察权限与副作用，而不能只看回复是否礼貌。

## Prompt-Eval-Mutation contract
Prompt manifest 包含 8 个攻击案例、工具 manifest hash、租户标识、最小 scope 与 sandbox 开关，禁止真实副作用。 Eval 断言 ATTACK-CASES、MANIFEST、TENANT、SCOPE、SANDBOX、NO-SIDE-EFFECT、BLAST-RADIUS。 Mutation 将 tenant_isolation 改为 false；只制造跨租户边界缺口，保持攻击样本和 hash 不变。

## Independent Oracle and executable evidence
TENANT 检查租户隔离；SCOPE 与 SANDBOX 约束最小能力；BLAST-RADIUS 要求失败影响可界定且有 owner。
实际命令：`python3 site/public/materials/agent-architecture-system/scripts/agent_architecture_lab.py --topic TD-AG-06 --phase cycle --report-dir reports/td-ag-06`。预期 baseline/fault/repair 退出码为 `[0,1,0]`；诊断字段为 `failed_oracle_ids`，fault 必须只命中本页命名变量。若 TENANT 失败，立刻停止并检查请求租户、凭证和资源前缀；禁止以“模型拒答”代替权限证据。

## Transfer and boundary
迁移到飞书或 MCP 接入时，为每个工具登记 hash、租户、scope、sandbox、审计 owner 和撤销办法。 安全结论只来自无网络合成攻击 fixture；真实凭证、在线 MCP、practitioner red-team、production security approval 与 learner transfer 均 NOT_RUN。

## Editorial review
- review_id: AG-EDITORIAL-2026-08-12-TD-AG-06
- reviewer: course-editorial-owner
- scope: Security 注入、MCP 权限与租户隔离 的专业问题、方法与理由、独立 Oracle、Prompt/Eval/Mutation、实际 0-1-0 命令、故障诊断、迁移和边界。
- method: sentence-level duplicate scan against TD-AG-00..TD-AG-10；逐页检查主题专属术语、artifact chain 的 method/risk/oracle/prompt/eval/mutation 以及受保护的 fixture/NOT_RUN 语义。
- protected_items: fixture-tested、NOT_RUN、live、practitioner、production 边界不得被升级或删除。
- duplicate_scan: 本页已改为主题专属句子；四证据环、独立 Oracle 和边界词属于必要共享术语，不作为实质教学重复。
- decision: pending-independent-rerun；本记录不是 practitioner review、live evidence 或 production receipt。
- limitations: 需要 validation lane 重新运行独立 editorial audit 才能更新评分。

## Beginner check
初学者应能指出本页故障字段、独立 Oracle、实际命令、`[0,1,0]` 结果和迁移时新增的 owner/数据/权限；不能回答时保持 BLOCKED。
