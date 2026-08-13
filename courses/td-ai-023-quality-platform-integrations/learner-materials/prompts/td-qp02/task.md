# GitLab 当前 SHA 测试证据评审 / task / v1.0.0

读取 MR、Pipeline 与 JUnit 固定输入。先核对 current SHA、pipeline_id、suite 完整性和 artifact hash，再输出 fail-closed gate；不得把旧 SHA 或缺报告写成通过。

执行顺序：1) 验证事件和 actor 身份；2) 验证所需权限是否最小；3) 绑定 issue revision、commit SHA、run、environment 与 evidence；4) 列出失败 Oracle；5) 生成可逆修复与回滚建议；6) 把需要人类决定的事项设为 true。只输出 JSON。
