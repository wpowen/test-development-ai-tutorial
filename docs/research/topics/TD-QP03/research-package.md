# TD-QP03 · Kubernetes 临时测试环境、RBAC/NetworkPolicy/TTL、回收与审计

## Research brief

业务场景是每个 MR/质量 run 使用一个短生命周期 namespace 执行订单服务集成测试。环境必须有可追踪的 owner/run/SHA 标签，provisioner、test runner、cleanup worker 分离，RBAC 最小化，ResourceQuota/requests/limits 限制资源，NetworkPolicy 默认拒绝再显式放行，Job TTL 和显式 stop/cleanup 共同回收。真实生产集群不在范围内。

研究对象是 namespace、Role/RoleBinding、ServiceAccount、ResourceQuota、NetworkPolicy、Job `ttlSecondsAfterFinished`、ownerReferences、cleanup 和 Kubernetes audit。静态 manifest 不能证明网络插件 enforcement、实际 RBAC 响应、TTL 时延或无孤儿资源；目标集群验收为 `NOT_RUN`。

## Source pack

- [Kubernetes Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)：定义 namespace 隔离边界；不自动提供完整安全隔离。
- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)：说明 Role、RoleBinding、ClusterRole 和最小权限语义；具体集群权限必须用 `auth can-i` 验证。
- [Kubernetes NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)：说明 ingress/egress 规则与实现依赖网络插件；manifest 存在不等于 enforcement。
- [Automatic cleanup for finished Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/)：说明 Job TTL controller；TTL 不是精确回收 SLA。
- [Kubernetes auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)：说明 audit policy、backend 和事件内容；平台仍需关联自身 run/audit ID。

## Evidence synthesis

事实：RoleBinding 可以把权限限制到 namespace，显式 verbs/resources 比 wildcard 更可审计；ResourceQuota 会约束资源创建；NetworkPolicy 的实际效果依赖网络插件；Job TTL 由 controller 异步处理。事实：Secret 的 base64 不是加密，测试 runner 默认不应读取 Secret。

工程综合：将 namespace、RBAC、quota、NetworkPolicy、TTL、owner label 和审计作为一条环境契约。Provisioner 创建受控模板，runner 只在本 namespace 执行，cleaner 只按精确 owner/run 标签删除；环境 Ready、Job 完成、cleanup 成功和 audit 完整分别建模，不能用 namespace 删除请求已发出代替回收证据。

未知项：目标 cluster minor/API、CNI/NetworkPolicy enforcement、准入控制器、Pod Security、Runner、审计 backend、镜像策略和 cleanup 权限尚未验证。静态配置不能声明真实隔离已成立。

## Engineering blueprint

七节点架构与 TD-QP03 页面一致：

| 节点 | 实施与可审计输出 |
|---|---|
| MR/Run 请求（输入） | 绑定 project、MR、SHA、run、expires_at 和允许的环境模板；生产 namespace 明确拒绝。 |
| Namespace Provisioner（处理） | 只创建 allowlist namespace/template，记录 environment_id、policy_hash、actor 和结果。 |
| Namespace/RBAC/ServiceAccount（门禁） | 分离 provisioner、runner、cleaner；拒绝 cluster-admin、wildcard、跨 namespace 和 Secret 读取。 |
| Quota/NetworkPolicy（门禁） | 限制 CPU、内存、Pod/Job/Service；默认拒绝网络，逐项验证允许与拒绝连接。 |
| Test Job/Runner（处理/证据） | 运行合成/脱敏测试，保存 JUnit、日志、provenance 和资源状态；不改变权限策略。 |
| TTL/Stop/Cleanup Worker（处理） | Job TTL、MR close/merge stop 和过期扫描多重兜底；失败输出残留清单。 |
| K8s Audit/平台审计（证据/人工决策） | 关联 actor、action、resource、time、environment、run、trace、policy；安全 owner 复核越权和残留。 |

材料计划是 `ephemeral_namespace_cleanup.py`、`ephemeral-namespace-baseline.yaml`、`k8s-isolation-audit.json` 和 `td-qp03-k8s-ephemeral-sop.md`，均为页面指定的材料路径；当前交付只写页面和研究包。

## Manuscript map

用“MR 测试完成但 namespace 残留，并且 runner 能读 Secret”的反例开场。随后按身份、资源、网络、Job 生命周期、清理和审计拆解实现；通过 quota 拒绝、跨 namespace/Secret deny、未 allowlist 网络、cleanup 403 和 TTL 延迟说明故障注入与诊断。人类决策部分保留平台、安全、测试和集群 owner 的职责边界。

页面结尾必须写清：回滚先冻结创建、恢复上一版模板、按 owner 精确清理并重新验证；真实集群、CNI、准入和审计为 `NOT_RUN`，不能用 YAML 静态检查冒充运行证据。

## Editorial review

没有把 namespace 当成自动安全边界，也没有把 NetworkPolicy、TTL 或删除 API 调用写成已生效/已清理。保留 runner 与 provisioner 权限分离、Secret 禁止读取、quota、默认拒绝网络和 audit 关联。官方 URL 直接指向 Kubernetes 文档；版本和插件依赖均显式留给目标集群验收。

`static-reviewed` 只代表页面、研究包和材料计划经过静态审阅。任何“隔离成功”“清理完成”“审计完整”都需要目标集群的 allow/deny、资源列表、TTL 和 audit 证据。

## Validation

状态：`desk-researched`；真实 Kubernetes 集群、namespace、RBAC、CNI、NetworkPolicy、quota、Job TTL、Runner、cleanup worker 和 audit backend 均为 `NOT_RUN`。

静态验证范围：页面有 5 个实质 blocks、7 个 architecture nodes、至少 3 个 sourceIds、3 个 outcomes/practice/completion 项，并链接脚本、配置、夹具和指南计划文件。后续真实验收必须覆盖 `auth can-i`、Secret/跨 namespace deny、quota、网络 allow/deny、Job failure、TTL/stop、cleanup 权限、孤儿资源和 Kubernetes audit。
