# 质量控制平面：从 Jira 变更到可审计的 CI 门禁

这是一课给测试开发/AI 质量平台工程师的离线实操课。你会把一次 Jira 需求变更关联到 GitLab MR 与 commit SHA，在受限 K8s namespace 中表示执行，聚合 JUnit，按指纹幂等回写 Jira/GitLab，发送脱敏通知，并保留可验证的审计链。所有外部系统都是标准库模拟器；真实集成边界明确标为 `static-reviewed/NOT_RUN`。

## Learner and prerequisites

适合能读 Python、理解 webhook/CI、知道 JUnit XML 与 Kubernetes namespace 的测试开发工程师。前置是 `td-ai-022-api-ai-automation` 或等价能力：能写独立 Oracle、区分 HTTP 成功与业务正确、阅读 JSON。无需账号、网络或第三方包。

## AI centrality

传统的“连几个系统”不是本课核心；核心是把 AI 生成的需求解析、风险与测试候选纳入版本化质量控制平面，同时让确定性 Oracle、SHA 绑定、权限和人工审批限制 AI 的权限。移除 AI 候选环节，就失去“候选可追溯但不可自批准”的主要质量问题；移除确定性门禁则无法证明 AI 没有误放行。AI 只负责候选与失败摘要，不能改变 expected、批准 waiver 或写入生产事实。

## System under test

离线系统包含 Event Gateway（HMAC 验签、时间/重放语义）、Inbox/Dedupe、Orchestrator 状态机、AI candidate store、Human Review、GitLab pipeline/JUnit adapter、K8s provisioner、Jira/GitLab writeback、redacted notification 和 append-only audit ledger。主键是 `project_id + mr_iid + commit_sha + run_id`；工件仅以 ref/hash 表示。

事件最小 schema 使用 `specversion,id,source,type,time,subject,datacontenttype,dataschema,data`，data 必须包含 `tenant_id,correlation_id,causation_id,trace_id,jira_issue_key,gitlab_project_id,mr_iid,commit_sha,run_id,artifact_refs`。状态机为 `Parsed -> Risked -> Proposed -> Human Approved -> Execution Requested -> Environment Ready -> Running -> Results Collected -> Gate Evaluated -> Passed|Failed|Superseded`。重复/乱序不会制造第二次副作用；过期 SHA 不能覆盖当前 HEAD。

架构边界：Jira 是需求/缺陷事实源，GitLab 是代码/Pipeline/报告事实源，K8s 只承载短生命周期执行环境，通知只消费脱敏结果，审计账本只追加。K8s 表示包括非 `default` namespace、`namespace-job-runner` Role、禁止 `cluster-admin`、900 秒 TTL 与 run owner 标签。

## Baseline and target

Baseline 是一个可重放的健康运行：签名 webhook 被接受一次，第二次 replay 被抑制；AI candidate 有模型/提示词哈希但必须人工 approve；run 绑定 `a*40` 当前 HEAD；JUnit 为 3/3；namespace 有限权和 TTL；Jira 与 GitLab 各一次幂等回写；通知不含 token/secret；审计 hash 链正确。目标是任何一个关键约束被破坏时，独立 Oracle 返回 `FAIL` 和非零退出码，而不是靠日志外观判绿。

## Inputs and contracts

输入是 `lab/fixtures/webhook.json`、`lab/configs/policy.json` 和 Python 内置的合成状态。输出报告是 `lab/reports/*.json`，每个检查有 `oracle_id,passed,reason`，保存 mutation、输入哈希和 Oracle 版本。阈值是教学契约，不是生产 SLA。候选记录必须有 `status=approved`、`auto_approved=false`、`model`、`prompt_hash`；门禁决策必须引用当前 SHA、pipeline、JUnit artifact hash、policy version 与人工动作。

## Commands

从本课程的 `lab/` 目录执行：

```bash
python3 platform_lab.py baseline --report baseline.json
python3 platform_lab.py stale_sha --report mutation.json; test $? -eq 1
python3 platform_lab.py repair --report repair.json
python3 -m unittest discover -s tests -v
```

也可测试 `replay`、`rbac`、`missing_report` 四类故障。报告会写入 `lab/reports/`；不要把 mutation 的预期非零改成成功。公开学习者材料在 `learner-materials/`，从它的根目录复制 README 命令即可独立运行。

## Metrics and thresholds

本课的确定性门禁为：`accepted=1, duplicates=1`；候选已人工批准且非自动批准；`run.commit_sha == gitlab.head_sha`；JUnit present 且 `failed=0`；namespace 非 default、无 cluster-admin、TTL>0；Jira/GitLab writeback 各 1；通知不含 `token`/`secret`；审计 hash 等于 `sha256(previous_hash + event)`。`0/1/0` 是故障检测力证据，不代表真实系统吞吐、延迟、覆盖率或模型质量。

## SOP and failure diagnosis tree

SOP 顺序固定为：验签并入 Inbox → 回读 Jira 当前 revision → AI 只生成候选 → 人工审核 → 以 MR/SHA/run 触发 Pipeline → 建立限权 namespace/Job/TTL → 回读 Pipeline 和 JUnit → 证据哈希与 SHA 校验 → 聚合 gate → 指纹幂等回写 → 脱敏通知 → 清理并写审计。权限模型分离 Jira writer、GitLab status writer、K8s provisioner、test runner、notifier、audit reader；任何服务都不得借 ChatOps 或备注绕过门禁。

诊断树：若验签失败，检查原始 body/密钥并拒绝；若重复副作用，查 inbox key 与 `accepted`；若候选自动通过，查 reviewer/approval；若报告红，先查 SHA/pipeline/artifact 一致性，再查 JUnit 缺失与失败计数；若 K8s 红，查 namespace、RoleBinding、TTL 和 cluster-admin；若回写重复，查 fingerprint/outbox；若通知泄密，查脱敏字段而不是重试发送。未知环境故障应为 `NOT_RUN`/`INCONCLUSIVE`，不可伪造 PASS。

## Failure injection

默认故障 `stale_sha` 把 run SHA 改成旧的 `b*40`，但 GitLab HEAD 仍为 `a*40`。运行 mutation 命令必须得到 exit code `1`、verdict `FAIL`、failed Oracle 包含 `SHA-BINDING`，证明旧成功状态不能覆盖新代码。额外 mutation：`replay` 使 inbox 产生第二次副作用；`rbac` 添加 `cluster-admin`；`missing_report` 移除 JUnit；四者都必须变红。故障诊断先读 `failed_oracle_ids`，再看 state 快照和 audit，不调整测试预期。

## Repair and rollback / cleanup

修复不是删除证据：恢复当前 SHA、去掉越权角色、补齐当前 pipeline 的 JUnit，或将缺失项标为阻断；随后重新运行 repair 并生成新报告。回滚流程是冻结新的成功状态、保留 outbox 与原始失败工件、在 Jira/GitLab 以指纹更新而不是重复创建、撤销临时 namespace 或等待 owner+TTL 回收，最后追加 `rollback_requested/cleanup_completed` 审计事件。真实系统中删除 namespace 需由清理器身份执行，不能由测试 runner 自删权限扩大。

## Human review gate

AI 可以提出技术方案、风险、用例、失败摘要和候选归因；人必须批准候选、确认风险和 Oracle、决定阻断/修复/有期限 waiver。质量负责人拥有门禁决策权，发布负责人承担残余风险。通知不是事实源，Jira transition 必须先读可用 transition 和权限；waiver 需要范围、原因、关联风险、审批人和到期时间。

## AI-specific failure boundary

AI 可能漏掉 replay、把旧 SHA 当最新、把报告缺失解释成通过、建议过宽 RBAC 或泄露敏感字段。防线是版本化 prompt/model hash、独立 Oracle、人工 approval、当前 HEAD 绑定、报告存在性检查、最小权限、脱敏和 append-only audit。真实 LLM、judge 稳定性、评测集泄漏、成本/延迟均未运行。

## Learner artifact

学员交付一份事件 schema/状态机图、权限矩阵、幂等键说明、Oracle catalog、三份 JSON 报告和 unittest 输出；练习是新增“重复 GitLab webhook + 旧 SHA”组合故障，并证明只创建一个 Jira defect、只写当前 SHA status。迁移到“企业审批系统到测试环境的受控回写”时必须更换业务状态、角色、事件和阈值，但保留 SHA、fingerprint、artifact hash、人工门和清理审计。

## Evidence status

当前 verdict 是 `PASS-FIXTURE`：Python 标准库离线模拟器和 learner-materials 的 0/1/0 将在交付前实际运行。真实 Jira/GitLab/Kubernetes/ChatOps、GitLab tier/版本差异、真实 webhook 网络、真实 Runner、真实模型、生产数据、吞吐/安全/学习效果均为 `static-reviewed/NOT_RUN`。这些未知项不因 JSON 或配置可解析而变成运行证据。
