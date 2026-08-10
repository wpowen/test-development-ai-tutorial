# 可复用 Skill：UI 契约与 AI 修复候选卡

```text
输入：已批准的 Given-When-Then、DOM/ARIA snapshot 或 UI hierarchy、原始 trace/log、版本与设备信息。
输出：平台 locator、动作、业务 oracle、证据引用、失败分类、候选 patch、匹配数、反例结果。
允许：生成草稿、摘要、候选 locator。
禁止：删除/弱化 oracle，改视觉阈值，增加无限 retry/force/skip，直接写回仓库，访问生产副作用账号。
门禁：先静态检查，再 replay；候选 patch 必须显示 diff、原失败、业务 oracle 结果和人工批准。
```

AI 输出是候选，不是事实。原始 trace、层级树、日志和业务状态优先于模型解释。
