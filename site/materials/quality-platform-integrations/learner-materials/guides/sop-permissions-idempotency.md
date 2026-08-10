# SOP、权限与幂等

先验签入 Inbox，再回读 Jira/GitLab，AI 只生成候选，人工批准后触发 Pipeline；K8s provisioner 建立非 default namespace、最小 Role、owner 标签和 TTL；读取 JUnit 并校验当前 SHA、artifact hash 后聚合；以 defect fingerprint 和 source event id 去重回写；通知仅发脱敏摘要；最后清理并追加审计。Jira writer、GitLab status writer、K8s provisioner、test runner、notifier、audit reader 分离，禁止 cluster-admin 和 Secret 读取。
