# Jira 需求事件证据评审 / task / v1.0.0

读取固定 Jira 事件与当前 issue 快照。只基于 source_refs 生成 Basis Gate 决策、冲突、unknowns 与候选测试；禁止自动批准。

执行顺序：1) 验证事件和 actor 身份；2) 验证所需权限是否最小；3) 绑定 issue revision、commit SHA、run、environment 与 evidence；4) 列出失败 Oracle；5) 生成可逆修复与回滚建议；6) 把需要人类决定的事项设为 true。只输出 JSON。
