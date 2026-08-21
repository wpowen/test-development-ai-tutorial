# 测试方法论与实施方案｜可直接使用的工件包

配套文档：`methodology/`（14 篇）。本包是其中所有模板、检查单、Schema、样例与自检器的实体。

## 目录

```
learner-materials/
├── templates/     19 份文档与配置模板（复制→替换 <> 占位→使用）
├── checklists/     8 份可逐条打勾的检查单
├── schemas/        5 份 JSON Schema（机器可校验）
├── examples/       6 份"订单取消与退款"贯穿案例的填写样例
└── scripts/        1 个标准库自检器（无网络、无模型、不写文件）
```

## 5 分钟上手

```bash
# 1. 看基线：全部门禁应通过
python3 scripts/validate_handbook.py all

# 2. 注入一个已知缺陷：门禁应阻断
python3 scripts/validate_handbook.py all --fault doc-conflict

# 3. 恢复：门禁应重新通过
python3 scripts/validate_handbook.py all --fault none
```

期望退出码依次为 **0 / 1 / 0**。这三段就是本方法论对"可运行"的定义——
只有第 1 段的绿色不证明任何事，它可能只是因为检查根本没做。

## 可注入的故障

```bash
python3 scripts/validate_handbook.py list-faults
```

| 故障 | 被哪道门禁拦下 |
| --- | --- |
| `doc-conflict` | S1 依据冻结：冲突未指定升级责任人 |
| `unsupported-rule` | S2 需求契约：规则没有来源支持 |
| `missing-oracle` | S5 Oracle 设计：关键风险无 Oracle 记录 |
| `expired-waiver` | S9 发布判断：Waiver 已过期 |
| `judge-self-approval` | S5 Oracle 设计：语义层单独放行 blocker |

## 生成报告

```bash
python3 scripts/validate_handbook.py all --report reports/baseline.json
```

## 模板使用顺序

| 阶段 | 用哪份模板 |
| --- | --- |
| 接手项目 | `templates/01-test-strategy.md` |
| 每个迭代 | `templates/02-test-plan.md` |
| S1 冻结依据 | `templates/03-test-basis-pack.md` + `schemas/source-manifest.schema.json` |
| S2 需求契约 | `templates/04-requirement-contract-guide.md` + `schemas/requirement-contract.schema.json` |
| S4 风险与策略 | `templates/05-risk-register.csv` + `templates/06-technique-selection-matrix.md` |
| S5 Oracle | `templates/07-oracle-design-record.md` |
| S6 数据 | `templates/08-test-data-management.md` |
| S7 环境 | `templates/09-environment-register.md` |
| S8 缺陷 | `templates/10-defect-severity-taxonomy.md` + `schemas/run-receipt.schema.json` |
| S9 发布 | `templates/11-entry-exit-criteria.md` + `templates/14-release-decision-record.md` + `schemas/waiver.schema.json` |
| 组织与人 | `templates/12-raci-and-level-adapter.md`、`16-能力矩阵与自评.md`、`17-估算与排期.md` |
| 度量与报表 | `templates/13-metrics-catalog.json`、`19-质量周报.md` |
| 工具选型 | `templates/15-tool-selection-scorecard.md` |
| 任何结论 | `templates/18-evidence-boundary-statement.md` |

评审会上按 `checklists/01`–`08` 逐条打勾。

## 证据边界

本包为**确定性离线 fixture**（`fixture-tested` / L1）。它证明：工件结构自洽、
追溯闭包成立、五类预埋缺陷能被门禁发现。

它**不**证明：真实模型的抽取准确率、企业系统集成效果、从业者认可、
目标学习者的掌握程度、生产环境收益。上述全部为 `NOT_RUN`。

包内所有数值阈值（覆盖率、次数、天数、百分比）均为**结构占位**，不是建议值。
直接照抄会得到一个既不阻断真问题、又天天误报的门禁。定阈值的方法见
`methodology/08-度量体系.md` 第 8.6 节。
