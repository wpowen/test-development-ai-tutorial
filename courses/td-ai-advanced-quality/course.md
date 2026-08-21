# 高级 AI 质量缺口：从模型更新到在线发布

本课补齐测试开发 × AI 课程中最容易被一个总分或一张架构图掩盖的八个高风险面：模型训练与更新、代码和依赖供应链、多模态关系、多语言与可访问、群体伤害与 HITL、长期 Memory 与语义缓存、模型/Provider/工具路由，以及在线实验与 Canary。学习者交付的不是概念清单，而是一条能重放红灯的证据链。

## AI centrality

AI 在这些工作流中生成候选比较、聚合复杂证据、发现异常切片并帮助组织评测，但它同时带来训练污染、自评偏差、跨模态幻觉、少数群体掩盖、陈旧记忆、fallback 权限降级和线上抽样偏差。移除 AI 后，Prompt、Schema、Eval、Mutation、模型版本和独立 Judge 问题会消失，因此 AI 是系统核心而非附加功能。课程明确禁止同一模型生成候选后批准自己的 Oracle；Critic 只寻找证据缺口。

## System under test

系统由八条相互连接但责任不同的证据链组成：模型候选从数据 lineage 和 sealed holdout 进入注册表；代码变更从 commit、SBOM、签名和架构规则进入合并门禁；多模态与多语言任务从配对 fixture 和用户任务进入独立复核；公平与伤害从合法切片进入 HITL；Memory、缓存、Provider、MCP 工具和在线 Canary 都必须绑定版本、权限、owner 与回滚。任何一条断链都保持 FAIL、BLOCKED 或 UNKNOWN。

## Baseline and target

常见基线是分别运行训练评测、扫描器、可访问检查和线上指标，再把绿色状态拼成“质量通过”。目标状态是让每个结论都能反查原始输入、版本、独立 Oracle、分切片指标、具名 owner、停止条件和回滚，并用一个受控 fault 证明门禁真的会红。当前目标严格限定为八页合成 fixture 的 baseline/fault/repair；真实模型、真实用户与生产结果不在完成声明中。

## Commands

从 courses/td-ai-advanced-quality/lab 运行：

```bash
python3 advanced_quality_lab.py verify-packages
python3 advanced_quality_lab.py suite --phase baseline
python3 advanced_quality_lab.py suite --phase fault
python3 advanced_quality_lab.py suite --phase repair
```

预期退出依次为 0、0、1、0。Fault 的 1 是成功观察到负控制，不得吞掉。也可按 topic 单独运行并写入 reports。公开材料使用相同工作目录和相对路径，不需要 API key、网络或第三方包。

## Metrics and thresholds

指标必须声明分子、分母、切片、聚合、时间窗和 owner。训练页看关键切片、holdout 污染与回滚；供应链页看 SBOM、签名和 critical owner；多模态页看关系一致与应拒答；包容性页看 locale 任务、键盘和名称 blocker；公平页看最坏切片、伤害 blocker 和 HITL 效果；Memory 页看跨用户、陈旧命中与删除传播；路由页看能力错配、Schema、重复副作用；Canary 页看 assignment、guardrail、代表性样本和回滚。教学阈值只适用于合成数据，不外推业务。

## Failure injection

八个 fault 分别破坏训练版本和 holdout、加入未签名依赖并删除 owner、制造跨模态矛盾、删除必要 locale/键盘语义、只保留总体平均并自评、制造跨用户陈旧缓存、降级到不满足能力的 fallback 并注入 Schema 漂移，以及污染实验分流并只抽成功样本。每个 fault 必须产生明确 failed_checks 和退出 1；若退出 0，说明课程门禁失效。

## Human review gate

AI 质量负责人批准评测和有期限例外；安全 owner 处理供应链 critical；领域与本地化人员批准语义、文化和可访问任务；隐私 owner 决定 Memory 写入与删除；工具 owner 决定 fallback 与副作用；发布 owner 决定 Canary 扩量或回滚。人工步骤必须有独立性、样本覆盖、实际 override 权力、理由与回执；流程图中写了 human 并不构成 HITL 有效性。

## AI-specific failure boundary

模型会以流畅文本掩盖缺来源，Judge 可能与生成器共享偏差，训练集可能污染 holdout，多数切片会掩盖严重伤害，缓存会返回旧策略，fallback 会改变权限和结构化输出，线上样本会只看到幸存请求。课程用外置 owner、版本闭包、单点 mutation、最坏切片、拒答状态和预置回滚控制这些风险。离线 fixture 不构成公平、安全、隐私、无障碍、合规或生产批准。

## Learner artifact

学习者提交八个逐页研究包、八个 Prompt/Input/Schema/Eval/Mutation 合同、公开执行 manifest、baseline/fault/repair 报告、owner 注册表、材料归档哈希和一份迁移清单。迁移清单要明确真实系统的输入、权限、阈值、观测点、回滚、隐私/安全审查和未完成证据；不能复制 fixture 的取值或通过状态。

## Evidence status

确定性 Python 标准库 runner 已执行：八个 baseline 均 PASS/0，八个 fault 均 FAIL 并使 suite 退出 1，八个 repair 均 PASS/0。Prompt 包结构、八类 eval 和 model_evidence=NOT_RUN 已由 verify-packages 检查。没有调用真实模型、Provider、MCP server、训练系统、用户或生产流量；没有从业者、公平性、安全、无障碍、隐私或法务评审。因此唯一允许的成熟度是 fixture-tested。

## Transfer and stop conditions

迁移时先捕获真实 baseline，再替换合成 manifest、owner、阈值和 mutation。输入版本无法冻结、数据授权缺失、Oracle 不独立、严重切片失败、协议版本不明、删除无回执、分流污染或回滚不可用时立即停止。只有真实集成可重放、独立专业评审完成、发布门禁通过并取得运行后读回，才可在新的证据记录中讨论更高成熟度。
