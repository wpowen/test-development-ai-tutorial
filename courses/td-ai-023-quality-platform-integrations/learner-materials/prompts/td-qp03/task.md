# Kubernetes 临时环境边界评审 / task / v1.0.0

读取 namespace、身份、RBAC、Quota、NetworkPolicy、TTL 与 cleanup 固定输入。输出权限/隔离/回收审计，任何 cluster-admin、Secret 读取、跨 namespace 或残留都 fail-closed。

执行顺序：1) 验证事件和 actor 身份；2) 验证所需权限是否最小；3) 绑定 issue revision、commit SHA、run、environment 与 evidence；4) 列出失败 Oracle；5) 生成可逆修复与回滚建议；6) 把需要人类决定的事项设为 true。只输出 JSON。
