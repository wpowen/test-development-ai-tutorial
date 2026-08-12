# 跨系统重放与回滚评审 / task / v1.0.0

读取 CloudEvents 风格信封、Inbox/Outbox、Jira/GitLab/K8s 副作用与审计固定输入。核对 source+id 幂等、trace、重试、脱敏、对账和回滚；重复副作用必须失败。

执行顺序：1) 验证事件和 actor 身份；2) 验证所需权限是否最小；3) 绑定 issue revision、commit SHA、run、environment 与 evidence；4) 列出失败 Oracle；5) 生成可逆修复与回滚建议；6) 把需要人类决定的事项设为 true。只输出 JSON。
