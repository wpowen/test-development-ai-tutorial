# RACI 与组织适配器

R=执行 A=最终负责（唯一） C=被咨询 I=被告知

## 1. RACI（填入你组织的实际角色名）

| 活动 | 测试开发 | 产品 owner | 研发 owner | 发布 owner | 安全 owner | 数据 owner | SRE |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 依据冻结与版本登记 | A/R | C | C | I | I | C | I |
| 裁决业务规则冲突 | R | **A** | C | I | I | I | I |
| S2 需求契约化 | A/R | C | C | I | I | I | I |
| 需求语义确认 | R | **A** | C | I | I | I | I |
| S3 技术契约化 | R | I | **A** | I | C | I | C |
| 可测试性与可观测性缺口 | A/R | I | C | I | I | I | C |
| S4 风险登记与打分 | A/R | C | C | C | C | I | C |
| 测试深度与方法选择 | A/R | I | C | I | C | I | I |
| S5 Oracle 设计 | A/R | C | C | I | I | I | I |
| S6 用例与数据设计 | A/R | I | C | I | I | C | I |
| 生产数据脱敏授权 | R | I | I | I | C | **A** | I |
| S7 环境与自动化 | A/R | I | C | I | I | I | C |
| 生产写权限授予 | C | I | C | I | **A** | C | R |
| S8 执行与归因 | A/R | I | C | I | I | I | C |
| 缺陷分级 Severity | R | C | C | I | C | I | C |
| 缺陷优先级 Priority | C | **A** | C | I | I | I | I |
| S9 准出判定 | R | C | C | **A** | C | I | C |
| Waiver 批准 | C | C | C | **A** | C | I | I |
| 安全例外批准 | C | I | I | C | **A** | I | I |
| 发布决定 | C | C | C | **A** | C | I | C |
| 回滚决定与执行 | C | I | C | C | I | I | **A/R** |
| 生产事件回灌 | A/R | I | C | I | I | I | C |

**唯一性自查**：每行有且仅有一个 A。出现两个 A 的行，说明该决定实际无人负责。

| 检查 | 结果 |
| --- | --- |
| 是否每行恰好一个 A | |
| 六个关键 A 是否已有具名人 | |

## 2. 具名登记

| 角色 | 姓名 | 生效日期 | 备份人 |
| --- | --- | --- | --- |
| 产品 owner | | | |
| 研发 owner | | | |
| 发布 owner | | | |
| 安全 owner | | | |
| 数据 owner | | | |
| SRE / 运行负责人 | | | |

## 3. 组织职级适配器

> ⚠ 本手册**不规定**职级、年限、晋升周期或薪酬。以下由你的组织填写；缺 owner 时保持 `INTERNAL-UNKNOWN`，不得引用为通用规则。

| 本手册能力级别 | 你组织的职级 | 判定依据（可展示工件） | 批准人 | 状态 |
| --- | --- | --- | --- | --- |
| L1 跟做 | | | | INTERNAL-UNKNOWN |
| L2 独立执行 | | | | INTERNAL-UNKNOWN |
| L3 设计 | | | | INTERNAL-UNKNOWN |
| L4 系统 | | | | INTERNAL-UNKNOWN |
| L5 治理 | | | | INTERNAL-UNKNOWN |
