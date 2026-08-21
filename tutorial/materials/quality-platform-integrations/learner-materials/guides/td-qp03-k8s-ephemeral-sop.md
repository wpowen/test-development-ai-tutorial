# TD-QP03 K8s 临时环境 SOP

Provisioner 为每个 run 创建带 owner/run/MR/expiry 标签的非 default namespace，绑定只允许 namespace Job 操作的 Role；Runner 不读取 Secret、不创建 RoleBinding、不拥有 cluster-admin。Job 完成后保留证据引用，清理器按 owner 或 900 秒 TTL 回收；清理失败要告警和审计，不把环境残留解释成测试通过。
