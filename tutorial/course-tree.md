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
- 深度正文：17/17 页。
- `desk-researched` 表示正文和来源已整理，但没有运行目标系统。
- `fixture-tested` 表示对应离线夹具已经运行，不代表生产效果。
- 内容完成度与证据等级分开记录，不因正文完整而升级证据状态。
