# TD-AG-01｜Judge 裁判模型校准与偏差检测

来源：S-USER-AGENT-V2；课程映射：agent-source-adjudication.md；本页方法包与教材保持同一 topic_id。

## Professional problem
Judge 可能因选项顺序或事实缺口改变结论；只报告一个总分会把裁判偏差误认为 Agent 能力。

## Method and rationale
双顺序裁判卡法：冻结 GOLD、独立 HUMAN-LABELS、A→B/B→A 两种顺序和 FACT-BLOCKER，再用 JUDGE-CARD 记录判定理由。 先验证裁判稳定性，才能把模型输出质量与评测器质量分开归因。

## Prompt-Eval-Mutation contract
Prompt manifest 固定 gold、human_labels、order_ab、order_ba、fact_blocker、card 六字段，明确不可根据结果改答案。 Eval 对 A/B 顺序交换、事实阻断和人工标签分别断言 GOLD、HUMAN-LABELS、ORDER-STABLE、FACT-BLOCKER、JUDGE-CARD。 Mutation 仅把 order_ba 改成 B，模拟位置偏差；不要同时改变 gold 或人工标签。

## Independent Oracle and executable evidence
ORDER-STABLE 比较 order_ab 与 order_ba；FACT-BLOCKER 检查事实不足时是否拒绝臆判，二者均独立于生成模型。
实际命令：`python3 site/public/materials/agent-architecture-system/scripts/agent_architecture_lab.py --topic TD-AG-01 --phase cycle --report-dir reports/td-ag-01`。预期 baseline/fault/repair 退出码为 `[0,1,0]`；诊断字段为 `failed_oracle_ids`，fault 必须只命中本页命名变量。若失败列表缺 ORDER-STABLE，先检查裁判输入是否真的交换；若缺 FACT-BLOCKER，检查证据不足时的拒答分支。

## Transfer and boundary
迁移到摘要或 RAG 评测时建立任务专属 gold 与双人标签，记录裁判版本和冲突升级人。 这是确定性 judge fixture 的偏差训练，不是模型排行榜或真实裁判一致性结论；live judge、practitioner calibration、production gate 与 learner transfer 均 NOT_RUN。

## Editorial review
- review_id: AG-EDITORIAL-2026-08-12-TD-AG-01
- reviewer: course-editorial-owner
- scope: Judge 裁判模型校准与偏差检测 的专业问题、方法与理由、独立 Oracle、Prompt/Eval/Mutation、实际 0-1-0 命令、故障诊断、迁移和边界。
- method: sentence-level duplicate scan against TD-AG-00..TD-AG-10；逐页检查主题专属术语、artifact chain 的 method/risk/oracle/prompt/eval/mutation 以及受保护的 fixture/NOT_RUN 语义。
- protected_items: fixture-tested、NOT_RUN、live、practitioner、production 边界不得被升级或删除。
- duplicate_scan: 本页已改为主题专属句子；四证据环、独立 Oracle 和边界词属于必要共享术语，不作为实质教学重复。
- decision: pending-independent-rerun；本记录不是 practitioner review、live evidence 或 production receipt。
- limitations: 需要 validation lane 重新运行独立 editorial audit 才能更新评分。

## Beginner check
初学者应能指出本页故障字段、独立 Oracle、实际命令、`[0,1,0]` 结果和迁移时新增的 owner/数据/权限；不能回答时保持 BLOCKED。
