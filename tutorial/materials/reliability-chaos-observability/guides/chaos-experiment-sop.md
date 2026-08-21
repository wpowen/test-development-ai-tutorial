# Chaos 实验 SOP

## 默认边界

本 learner-materials 默认实验只运行 Python 标准库夹具。`fixtures/` 中的 YAML 是合成输入与报告模板；真实 Kubernetes/Chaos Mesh 操作保持 `static-reviewed / NOT_RUN`，没有在课程验证中 `kubectl apply`。

## 授权前检查

在任何真实实验前填写 owner、环境、namespace、精确 selector、开始/结束时间、最大持续时间、停止条件、凭证边界、观测 run_id 和回滚命令。先确认观测链可写，再用当前 Chaos Mesh CRD 做 server-side dry-run。只对单个非关键 workload 或已批准 canary 注入一个变量。

## 执行与停止

先跑健康 baseline，再注入一个 Pod 或单向网络变量。若 good-task rate、queue、尾延迟、成本、副作用、观测完整性或 selector 范围异常，立即停止并回滚。PDB 不等于所有节点故障保护；不要把静态 YAML 或官方能力描述成目标服务恢复证据。

## 收尾

保存 manifest、注入开始/结束事件、summary、Trace、阈值版本、诊断四元组和修复复测。将 `PASS-FIXTURE`、`PASS-LIVE`、`BLOCKED`、`NOT_RUN` 分开；没有真实集群执行证据就保持 `NOT_RUN`。
