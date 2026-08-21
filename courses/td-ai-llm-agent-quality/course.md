# LLM Judge 与 Agent/Workflow 质量工程

## 课程目标

这是一条十页离线 fixture 课程链。学习目标不是背 Agent 术语，而是把需求风险、技术边界、权限、可观察证据和人工决定传递成可执行测试。课程从可比 A/B 和 Judge 校准开始，进入 outcome、step、trajectory 三层 Oracle，再处理工具权限、Prompt Injection、Browser Agent、自愈反作弊、Agent/Worker/Workflow 边界、状态恢复和单/多 Agent 公平实验。

完成课程后，学员应能交付五类可复用工件：版本冻结 manifest；独立于模型的 Oracle；能稳定变红的 Mutation；身份、权限和副作用 receipt；包含 owner、rollback 与 Unknown 的评测报告。任何总分都不能覆盖事实、安全、权限、重复写或终止失控 blocker。

## 十页专业链

1. **TD-T13 — Prompt、模型和知识库版本 A/B**：冻结数据、Prompt、检索、工具、Judge 和预算，只改变一个变量；交付可比较实验 manifest 与风险切片决定。
2. **TD-T14 — LLM-as-judge 校准与反例**：用人工双标、顺序翻转、风格扰动和事实反例测量 Judge 偏差；交付分歧矩阵与人工升级规则。
3. **TD-T15 — outcome、step 与 trajectory Oracle**：分别验证业务最终状态、关键动作和完整轨迹；正确最终文本不能掩盖越权调用。
4. **TD-T16 — 工具选择、参数和权限**：把参数 Schema、身份、tenant、scope、人工批准和幂等键放到写操作之前；交付写前授权证据链。
5. **TD-T17 — Prompt Injection、泄露与 excessive agency**：把网页、邮件和检索文本视作不可信数据，以模型外授权、最小权限和 DLP 阻断跨租户、泄露与写入。
6. **TD-T18 — Browser Agent 生成测试**：从风险 ID 生成候选测试，用隔离浏览器、后端业务状态与 mutation 证明测试不只是断言页面文字。
7. **TD-T19 — 自愈测试反作弊**：允许 locator 和非语义适配，禁止删除 Oracle、修改 expected、跳步和无限重试；候选 patch 必须重新杀死原 mutation。
8. **TD-W01 — Agent、Worker 与 Workflow 边界**：根据下一步控制权、状态所有权和副作用提交点分类组件，并选择不同测试方法。
9. **TD-W02 — 状态、循环、重试、handoff 与终止**：用 checkpoint、幂等 receipt、预算守卫和 stop reason 验证可恢复工作流。
10. **TD-W03 — 单 Agent 与多 Agent 公平实验**：锁定模型、任务、总 Token、工具、重试和人工干预预算，重复运行后再作架构决定。

## 每页如何学习

每页先阅读自己的研究九件包，而不是套用共用摘要：`research-brief.md` 定义控制问题，`source-pack.csv` 记录至少十个实际打开来源及其限制，两次独立研究运行分别从职业风险和系统对抗角度分析，`comparison.md` 负责裁决分歧，工程蓝图与 manuscript 再把结论变成教学与实验。

随后检查 `learner-materials/prompts/<PAGE-ID>/`。`system.md` 限制模型权力，`task.md` 说明工作对象，`critic.md` 查自批准和权限越界，`input.json` 固定输入，`output.schema.json` 固定输出契约，`eval.json` 固定正常与反例，`mutation.json` 固定必须杀死的故障，`manifest.json` 关闭浮动版本和隐式权限。

最后运行该页 lab manifest 中的三条命令：

1. baseline 必须退出 0，并保存完整 passed Oracle；
2. fault 必须退出 1，并输出命名 `failed_oracle_ids`；
3. repair 必须再次退出 0，但不能删除 Oracle、修改 expected、扩大权限或偷增预算。

`cycle` 会复跑三阶段并检查内部退出序列精确为 `0 / 1 / 0`。绿色 baseline 只说明 fixture 能执行；真正的检测力来自 fault 稳定变红，真正的修复来自保留原问题后重新变绿。

## 权力与安全边界

所有可写副作用都由确定性 policy gate 先行拒绝。模型输出、模型 Judge、Browser Agent 和 healer 建议都只是候选，不具有批准 expected、reference、权限扩张、合并或发布的权力。身份、tenant、scope、参数 Schema、预算和 human approval 必须在工具执行前留下 receipt。

不可信内容只能进入数据通道，不能覆盖 system policy。高风险事实、安全、权限、重复副作用和无限循环属于独立 blocker；另一个同源模型的同意不能解除 blocker。人工 owner 必须能读取原始输入、版本、失败 Oracle、动作日志、成本和 residual risk，并拥有拒绝与回滚权。

## 产物闭包

canonical `learner-materials` 是唯一课程源。站点静态材料和 ZIP 必须拥有完全相同的相对成员集合与 SHA-256；共享 runner 和归档只归属 `owners.json` 精确列出的十个页面，不按 `TD-T` 或 `TD-W` 前缀继承。每页仍保留独立 manifest、Prompt/Input/Schema/Eval/Mutation 和报告目录，防止跨 ID 污染。

## AI centrality

AI 不是装饰性的写作助手，而是被测系统的一部分：模型、Judge、检索上下文、工具调用、Browser Agent、healer 与多 Agent 编排都会改变可观察行为。课程只允许把它们当作候选生成器或受限执行器，最终 Oracle、权限、预算和发布决定必须由模型外的确定性门禁与人工 owner 持有。

## System under test

系统边界从版本 manifest 开始，包含 Prompt、模型或 provider 标识、数据/知识库切片、Judge、工具 schema、身份租户、浏览器沙箱、队列状态、checkpoint、重试和最终副作用 receipt。测试不能只读取最终文本；要分别读取 outcome、关键 step、完整 trajectory、授权前置条件和停止原因。

## Baseline and target

Baseline 是固定输入、预算、工具 scope、重复次数和人工干预预算下的安全轨迹；target 是在只改变一个明确变量后仍能解释差异，并保留独立 Oracle。先保存 baseline 的 0 退出、报告 hash 与 Unknown，再比较目标版本；总分不能覆盖权限、事实、重复写、越权或无限循环 blocker。

## Commands

在本课程目录执行以下离线命令，不需要 API Key：

```bash
cd learner-materials
python3 scripts/agent_quality_lab.py --topic TD-T13 --phase baseline --report reports/TD-T13/baseline.json
python3 scripts/agent_quality_lab.py --topic TD-T13 --phase fault --report reports/TD-T13/fault.json
python3 scripts/agent_quality_lab.py --topic TD-T13 --phase repair --report reports/TD-T13/repair.json
```

三次调用的预期退出码是 `0 / 1 / 0`。报告里的 `failed_oracle_ids`、状态 hash 和 `not_run` 必须与命令输出一并保存；其他页面沿用各自的 prompt manifest 和同样的三阶段协议。

## Metrics and thresholds

关键指标不是单一平均分：A/B 必须 `SINGLE-VARIABLE`、`LOCKS-COMPLETE`、`REPEATED-RUNS`；Judge 必须位置稳定、人工校准和事实 blocker；Agent 必须通过 `STEP-SAFETY`、`AUTH-BEFORE-ACTION`、`NO-DIRECT-WRITE`、`TRAJECTORY`；Workflow 必须通过幂等写、循环预算、handoff owner 和公平 token/tool/task 预算。任一高风险 Oracle 失败即 BLOCKED，不用均值抵消。

## Failure injection

TD-T13 的 fault 同时改变 model 与 retriever，违反单变量实验，因此 `SINGLE-VARIABLE` 变红并以 exit 1 结束。修复只恢复 manifest 中的实验隔离，不删除 Oracle、不修改 expected、不增加重试或权限；repair 回到 exit 0。迁移到权限或轨迹页面时，故障必须真实改变业务决定，例如越权工具调用、跨租户泄露、删除 Oracle 或无界循环。

## Human review gate

AI 生成的 case、Judge、healer patch 和 waiver 都只能是候选。人工 owner 必须读取原始输入、版本、失败 Oracle、动作与成本 receipt，确认业务 Oracle、权限和回滚策略后才能批准。模型不能批准自己的期望、修复、豁免或发布；真实组织审批、红队和从业者盲评目前 NOT_RUN。

## AI-specific failure boundary

本课程的确定性 runner 没有调用真实模型、Browser Agent、工具后端、队列或企业身份系统。它证明的是声明的 mutation 可以被独立 Oracle 稳定杀死，不证明模型质量、线上延迟、真实安全性、生产容量或从业者可用性。任何 provider、数据分布和组织策略变化都必须重新冻结 manifest 并重跑完整链路。

## Learner artifact

学员最终提交一个可审计包：版本 manifest、风险切片、三层 Oracle、Prompt/Input/Schema/Eval/Mutation、权限与幂等 receipt、baseline/fault/repair 报告、残余风险与 Unknown、owner/rollback 以及迁移挑战说明。工件必须能让另一位工程师在无模型凭证的 fixture 中复现 0/1/0，并明确哪些结论需要下一阶段 live 或 practitioner 证据。

## Evidence status

十个页面的研究与离线实验包为 `fixture-tested`，当前课程也只声明 `fixture-tested`。报告保留 `model=NOT_RUN`、provider=none 及无真实系统边界；不存在 live-tested、practitioner-reviewed 或 production-validated 证据。发布前仍需真实集成回读、独立安全审查、从业者核对和页面级 promotion receipt，缺一项即保持 fail-closed。

## 证据状态与晋级

当前成熟度仅为 **fixture-tested**。真实模型、真实 Browser Agent、真实工具后端、真实队列、企业身份系统、线上流量、组织审批、安全红队和从业者评审均为 **NOT_RUN**。这些 Unknown 不能由静态文件、退出码或论文结论填充。

晋级至少需要：在隔离集成环境回读真实动作与权限 receipt；重复运行并报告分布而非单次最好结果；独立安全审查；职业从业者核对业务 Oracle、工件可读性和回滚；发布 owner 签署页面级 promotion receipt。任一项缺失时保持 fail-closed，不写成 live-tested、practitioner-reviewed 或 production-validated。
