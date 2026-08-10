# Reusable Skill：把一次 AI 失败变成稳定回归用例

## Input

- 已脱敏的用户输入；
- 系统输出、引用、工具调用和 Trace；
- 已确认的知识或策略；
- 失败影响与人工判断。

## Process

1. 将事实与推断分开；缺少 reference 时停止补写。
2. 判断失败发生在 input、retrieval、generation、tool step、trajectory、policy 或 infrastructure。
3. 生成最小可重现 case：输入、允许变化、必须满足、禁止出现、允许引用、预期工具/参数、风险 slice。
4. 选择 scorer：优先确定性；语义等价才用固定版本 judge；高风险保留人工 gate。
5. 先对失败版本运行，证明 case 是红色。
6. 对修复版本运行，证明绿色。
7. 再加入一个相邻反例，避免规则只记住一句话。
8. 记录数据来源、版本、阈值、owner、隐私和过期/刷新条件。

## Output

输出一个 JSONL case、推荐 scorer、失败原因、预期红绿结果、CI 阈值建议和人工复核项。不得只输出“优化后的 Prompt”。

## Stop

当 reference 未确认、包含未脱敏数据、无法构造可失败 oracle、或需要高风险专业授权时，标记 blocked。
