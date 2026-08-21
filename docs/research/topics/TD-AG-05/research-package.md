# TD-AG-05｜Reliability 重复运行、pass@k 与 pass^k

来源：S-USER-AGENT-V2；课程映射：agent-source-adjudication.md；本页方法包与教材保持同一 topic_id。

## Professional problem
单次成功会掩盖长轨迹失败；把 pass@k 和 pass^k 混称会错误估计 Agent 在连续任务中的可靠性。

## Method and rationale
分布可靠性法：按任务与运行重复采样，分别计算 pass@k、pass^k，使用 clustered CI、horizon buckets 和 sample_reason 描述分母。 把“能否找到一次成功”与“连续多步都成功”分离，才能制定可信的上线门槛。

## Prompt-Eval-Mutation contract
Prompt manifest 冻结 tasks=12、runs=5、两种通过率、置信区间聚类方式、轨迹长度桶和抽样理由。 Eval 断言 TASKS、REPEATS、PASS-K-SEPARATE、CLUSTERED-CI、HORIZON、SAMPLE-REASON，并保存分母。 Mutation 将 clustered_ci 改为 false，模拟把相关重复当成独立样本。

## Independent Oracle and executable evidence
PASS-K-SEPARATE 要求 pass_at_k 不被当作 pass_all_k；CLUSTERED-CI、HORIZON、SAMPLE-REASON 约束统计解释。
实际命令：`python3 site/public/materials/agent-architecture-system/scripts/agent_architecture_lab.py --topic TD-AG-05 --phase cycle --report-dir reports/td-ag-05`。预期 baseline/fault/repair 退出码为 `[0,1,0]`；诊断字段为 `failed_oracle_ids`，fault 必须只命中本页命名变量。若 CLUSTERED-CI 失败，回查任务簇与重复运行键；若 PASS-K-SEPARATE 失败，重算两种定义而非调阈值。

## Transfer and boundary
迁移到回归集时按任务 ID 分层报告成功率、轨迹长度、成本和 CI，并为短轨/长轨设置不同观察窗。 本页仅在 12 个合成任务上演示统计结构；真实模型稳定性、线上样本、practitioner reliability 与 production SLO 均 NOT_RUN。

## Editorial review
- review_id: AG-EDITORIAL-2026-08-12-TD-AG-05
- reviewer: course-editorial-owner
- scope: Reliability 重复运行、pass@k 与 pass^k 的专业问题、方法与理由、独立 Oracle、Prompt/Eval/Mutation、实际 0-1-0 命令、故障诊断、迁移和边界。
- method: sentence-level duplicate scan against TD-AG-00..TD-AG-10；逐页检查主题专属术语、artifact chain 的 method/risk/oracle/prompt/eval/mutation 以及受保护的 fixture/NOT_RUN 语义。
- protected_items: fixture-tested、NOT_RUN、live、practitioner、production 边界不得被升级或删除。
- duplicate_scan: 本页已改为主题专属句子；四证据环、独立 Oracle 和边界词属于必要共享术语，不作为实质教学重复。
- decision: pending-independent-rerun；本记录不是 practitioner review、live evidence 或 production receipt。
- limitations: 需要 validation lane 重新运行独立 editorial audit 才能更新评分。

## Beginner check
初学者应能指出本页故障字段、独立 Oracle、实际命令、`[0,1,0]` 结果和迁移时新增的 owner/数据/权限；不能回答时保持 BLOCKED。
