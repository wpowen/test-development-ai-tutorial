# 可复用 Skill 合同

输入按 `需求/背景 → 风险 → Oracle → Metric Card → 工件 → Reviewer` 传递。Prompt 只生成候选，不能批准阈值、职级、waiver 或就业结论。复制到新业务时必须重填版本、owner、分母、切片、失败动作和限制；缺证据写 `UNKNOWN`，组织来源缺失时固定 `INTERNAL-UNKNOWN/BLOCK`。

推荐提示词骨架：

1. 角色：AI 测试证据教练；
2. 输入：版本化 fixture 与 source refs；
3. 任务：输出指定 Schema 的结构化工件；
4. Oracle：独立字段、Mutation 和 reviewer；
5. 边界：`provider=none`、`model_execution=NOT_RUN`、不得猜测；
6. 失败：不满足字段即 BLOCK；
7. 迁移：只修改 `editable_fields` 并重新评审。
