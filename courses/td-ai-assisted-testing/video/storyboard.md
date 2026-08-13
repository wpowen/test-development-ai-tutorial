# 教学视频 Storyboard

| 时间 | 画面 | 讲解重点 | 学习者动作 |
| --- | --- | --- | --- |
| 00:00 | 绿色测试报告切到守卫反转 | 绿色与覆盖不等于检测力 | 先判断能否发布并写未知项 |
| 01:30 | 四张卡片：PRD、Design、Oracle、Diff | 输入类型、版本和 owner 不可混合 | 标出一条冲突与一条缺引用 |
| 03:30 | 风险候选 JSON 与红色 BLOCKED | AI 只生成 candidate | 找出虚构 SLA |
| 05:30 | baseline/fault/repair 终端三联 | 0→1→0 是检测力证据 | 对照独立 Oracle 解释失败 |
| 09:00 | 四象限方法矩阵 | Boundary/Combination/Property/Fuzz | 按失败模型选方法 |
| 11:00 | seed 到最小反例的收缩动画 | 可重放需要输入与环境 | 把反例转回归 |
| 13:00 | raw events 到 cluster 的双层图 | 派生视图不覆盖原始证据 | 检查 trace/commit/environment |
| 14:30 | trace 被移除，UNKNOWN 亮起 | 聚类不是因果 | 设计下一控制实验 |
| 16:30 | 材料包目录与检查表 | 工件交付和迁移 | 复跑四页并列出 NOT_RUN |

视觉保持审计式：每个结论旁展示 source/oracle/version/status；红色代表预期 fault，不使用“AI 已自动解决”之类误导文案。
