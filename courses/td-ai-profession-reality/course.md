# 测试开发职业现实与 AI 能力迁移

这是一门给入门者的职业基线课：先把真实研发测试工作拆成可交付的责任链，再决定 AI 能帮哪一步。课程使用 TD-F01 的确定性自测夹具，练习从需求文档、技术文档、风险、方法、独立 Oracle 到执行归因和发布责任的完整传递；模型、Provider、真实组织流程和从业者判断均不被伪造。

## AI centrality

AI 不是本课末尾附加的工具清单，而是被测边界的一部分。学员必须把传统测试能力迁移到 Prompt、模型、数据集、Eval、Judge、Trace、工具权限、成本、漂移和版本回滚。AI 可以抽取候选、生成问题和聚合证据，但不能定义业务规则、替代独立 Oracle、确认根因、批准 waiver 或承担发布责任。移除 AI 质量流水线后，课程的迁移矩阵、评测门禁和新增失败边界都无法成立。

## System under test

被测系统是一个受控、脱敏的版本化 AI 质量发布流程：需求与技术依据进入责任地图，风险决定方法，版本化 Prompt/Input/Schema/Eval/Mutation 产生候选证据，确定性自测检查责任边界，最后由具名人类负责人决定阻断、修复、waiver 或回滚。离线夹具不代表任何企业内部流程，也不连接真实模型、网络、生产工具或招聘系统。

## Baseline and target

基线是把测试开发误解为写用例数量、只读技术实现、让模型裁决文档冲突、把实现输出当 Oracle，或把 AI 建议当发布结论。目标是交出一张可审计责任地图：每个阶段都有输入、artifact、oracle、decision、consumer；需求和技术文档冲突会 BLOCK；每个 AI 机会都写清权限和人类门禁；并用 0/1/0 的红绿修复周期证明故障真的能被检出。

## Commands

从公开学习包根目录运行；命令不需要密钥、网络、Provider、模型或 GPU。

```bash
cd learner-materials
python3 profession_self_check.py phase --phase baseline --report reports/TD-F01-baseline.json
python3 profession_self_check.py phase --phase fault --report reports/TD-F01-fault.json
python3 profession_self_check.py phase --phase repair --report reports/TD-F01-repair.json
python3 profession_self_check.py cycle --report reports/TD-F01-cycle.json
python3 test_profession_self_check.py
```

基线应退出 0，故障注入应退出 1，修复应退出 0；cycle 只在内部严格得到 `0/1/0` 时退出 0。报告必须保留 evidence boundary、provider=none 和 model_status=NOT_RUN。

## Metrics and thresholds

本课不以执行数量或证书数量作为职业能力指标。学员检查责任链覆盖率、每项工件的 owner/version/source/acceptance/consumer 完整率、需求与技术文档冲突阻断率、独立 Oracle 覆盖率、AI 权限边界完整率，以及 baseline-fault-repair 是否为 0/1/0。夹具阈值只用于证明门禁可检出故障，不是行业绩效、薪资、晋升或就业阈值。

## Failure injection

故障夹具会把“用例数量”冒充职业责任、跳过需求文档、让模型替代冲突裁决、复用实现输出当 Oracle，或让 AI 自动放行。预期 fault 进程非零、报告 verdict=FAIL，并指出具体责任字段；修复只能恢复正确的观察与边界，不能删除检查或改写 expected。若 fault 不变红，先判定教学资产没有检测力，不得把静态文档当完成。

## Human review gate

AI 质量负责人需要确认风险优先级、指标分母、Oracle 来源、阈值依据、owner、waiver 到期和回滚条件。产品/业务 owner 裁决业务规则，研发/架构 owner 对实现负责，测试开发提供独立证据，发布 owner 接受剩余风险，SRE 负责运行和回滚。AI 只能提出候选与汇总，不能匿名放行；招聘方和目标组织独立决定岗位、绩效、薪资和录用。

## AI-specific failure boundary

模型可能发明内部流程、把最终答案当事实、隐藏文档冲突、产生共同失败的 Oracle、泄漏敏感数据，或建议无限授权与自动发布。Prompt 包固定 provider=none、model_execution=NOT_RUN；JSON Schema 通过不等于模型效果通过，离线红绿不等于 live、practitioner 或 production 通过。所有内部流程、权限和绩效权重必须标为 INTERNAL-UNKNOWN 并指向待读文档或待访谈角色。

## Learner artifact

学员最终交付：职业责任地图；需求/技术文档双栏阅读表；冲突 BLOCK 记录；风险—方法—独立 Oracle 矩阵；工件 owner/version/source/acceptance/consumer 表；AI 能力迁移矩阵；版本化职业重建 Prompt 包；以及带 baseline/fault/repair 报告的个人学习路线。每个 artifact 都要有消费者和下一项决定，不能只提交一篇心得。

## Evidence status

当前状态为 `fixture-tested`。TD-F01 Python 标准库 runner 已在本地实际证明 baseline=0、fault=1、repair=0，并保存四份报告和 Prompt 输入/Schema/Eval；provider=none，model_execution=NOT_RUN。真实组织流程、从业者评审、模型效果、live provider、生产流量、就业结果和线上发布均是 Unknown/NOT_RUN，不得升级为 PASS-LIVE、PASS-PRACTITIONER 或完整生产课程。
