# 分镜

| 段落 | 画面 | 学习者动作 | 证据 |
|---|---|---|---|
| 1. 冷开场 | 202 响应与 SHIPPED 状态并排 | 写下是否发布及原因 | mutation 报告红灯 |
| 2. 契约地图 | 两份 OpenAPI 与 operation graph | 标出契约、权限、状态和事件检查 | operationId 清单 |
| 3. 独立 Oracle | 被测实现与 Oracle 分栏 | 判断哪些规则不能从实现反推 | Oracle hash 与规则表 |
| 4. Baseline | 终端运行 baseline | 核对输入 hash 和全部 PASS case | exit 0、baseline.json |
| 5. Mutation | 运行 SHIPPED 缺陷 | 沿 case ID 定位 expected/actual | exit 1、BUS-SHIPPED-REJECT |
| 6. Repair | 只恢复实现状态检查 | 比较三份报告 | exit 0、repair.json |
| 7. Transfer | 企业审批 API 状态图 | 重建角色、状态与副作用 Oracle | 迁移版 Oracle catalog |
| 8. Handoff | learner-materials 文件树 | 区分 fixture-tested 与 NOT_RUN | 材料清单和证据边界 |
