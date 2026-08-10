# 测试开发 × AI 课程树

## 学习路线

从传统测试生命周期开始，依次进入大模型基础、AI 辅助测试、AI 系统评测、Agent/Workflow、质量工程、Benchmark 和 Capstone。页面顺序由前置依赖决定。

## 模块

### 完整测试生命周期

从需求、策略、设计、执行到发布与生产反馈，先建立专业测试骨架

- TD-F01 · 先重建测试开发这份工作，再判断 AI 应该改哪里 · desk-researched
- TD-P01 · 先冻结测试依据：别让 AI 读一堆互相打架的文档 · desk-researched
- TD-P02 · 把自然语言变成需求契约：让下游程序能直接消费 · desk-researched
- TD-P03 · 需求评审不是让 AI 总结：要把歧义、冲突和不可测项逼出来 · desk-researched
- TD-P04 · 从需求契约到风险策略：决定测什么、在哪一层测 · desk-researched
- TD-P05 · 生成测试之前先固定 Oracle：否则 AI 只会生成自洽答案 · desk-researched
- TD-P06 · 把测试包接到自动化：接口、契约、集成和 UI 各自负责什么 · desk-researched
- TD-P07 · 执行、收集、归因：一次绿色结果需要哪些证据 · desk-researched
- TD-P08 · 变更回归与发布判断：把整条证据链串起来 · fixture-tested

### 传统测试专项

接口、集成、UI、数据、性能、稳定性、安全、可观测性和混沌工程

- TD-PS01 · API 业务契约：从 HTTP 结果到可验证副作用 · desk-researched
- TD-PS02 · OpenAPI Schema 与属性测试：让坏请求和破坏性变更变红 · desk-researched
- TD-PS03 · 契约、事件与鉴权：测试跨服务边界的真实兼容性 · desk-researched
- TD-PS04 · Web UI 关键旅程：隔离、定位器、网络控制与跨浏览器 · desk-researched
- TD-PS05 · Web UI 兼容性、无障碍与视觉回归 · desk-researched
- TD-PS06 · Android 自动化：生命周期、同步、权限与设备矩阵 · desk-researched
- TD-PS07 · iOS 自动化：可访问性标识、权限、签名与状态残留 · desk-researched
- TD-PS10 · 故障注入：从单点失败到重试风暴与级联故障 · desk-researched

### AI 帮你做传统测试

用 AI 提效，但必须证明生成结果有检测力

- TD-PS08 · AI UI 生成与自愈：先证明检测力，再谈省维护 · desk-researched

### AI 接口、性能与可靠性

测试流式协议、结构化输出、TTFT、TPOT、Goodput、容量、限流、重试和降级

- TD-PS09 · AI 性能指标：TTFT、TPOT、Goodput 与单位成功成本 · desk-researched
- TD-PS11 · 线上可观测性：把 AI 质量、Trace、成本和 SLO 接成一条链 · desk-researched
- TD-PS12 · 稳定性 Runbook：SLO 触发后的冻结、回滚与复盘 · desk-researched

### 专业专题与 Capstone

按岗位路线组合工件，交付端到端 AI Quality Engineering 系统

- TD-QP01 · Jira 需求事件：从 Basis Gate 到人工批准 · desk-researched
- TD-QP02 · GitLab MR 与 Pipeline：把 JUnit 证据绑定到当前 SHA · desk-researched
- TD-QP03 · Kubernetes 临时测试环境：隔离、回收与审计 · desk-researched
- TD-QP04 · 跨系统事件总线：幂等、重放、脱敏通知与审计闭环 · desk-researched

### Agent 性能与稳定性工程

从工作负载、指标、Trace、容量压测到生产 SLO、告警与故障处置

- TD-AP01 · 为什么 Agent 压测不是把并发数调高 · desk-researched
- TD-AP02 · 建立 Agent 性能指标树：系统、模型、轨迹、成本 · desk-researched
- TD-AP03 · 设计工作负载：任务、上下文、工具与故障分布 · desk-researched
- TD-AP04 · 设计 Trace 与数据模型：让一次慢任务可下钻 · desk-researched
- TD-AP05 · 搭建压测架构：发压、夹具、观测、判定四层分离 · desk-researched
- TD-AP06 · 执行完整压测 SOP：基线、变坏、修复、容量 · fixture-tested
- TD-AP07 · 诊断压测失败：从症状反推瓶颈与反馈环 · desk-researched
- TD-AP08 · 把压测接入生产：SLO、告警、降级与 Runbook · desk-researched

## 页面状态

- 发布范围：`pilot-path`。
- 深度正文：33/33 页。
- `desk-researched` 表示正文和来源已整理，但没有运行目标系统。
- `fixture-tested` 表示对应离线夹具已经运行，不代表生产效果。
- 内容完成度与证据等级分开记录，不因正文完整而升级证据状态。
