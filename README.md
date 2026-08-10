# 测试开发 × AI

一套从职业知识体系出发、逐题调研和验证的 AI 质量工程教程。

## 当前真实状态

- 知识命题树 v3：13 个模块、约 95 个原子课题；
- 站点当前公开：17 个已通过门禁的页面，分属职业现实/需求到证据与 Agent 性能稳定性两条路线；
- 未完成命题只保留在内部研究与课程路线图中，不进入公开导航、HTML、JSON、搜索或发布包；
- 可运行实验：Agent baseline → retry storm → repair，退出码 `0 → 1 → 0`；
- 尚未完成：内部其余课题逐题重写、真实企业系统、从业者盲评和学员效果验证。

## 深度样章讲什么

课程从“Task 不是 Request”开始，依次讲指标树、真实工作负载、Trace/Data Schema、压测架构与工具、完整 SOP、故障诊断，以及生产 SLO、告警、降级和 Runbook。它同时覆盖传统 Golden Signals、TTFT/TTFO/ITL/E2E、Agent 轨迹、重试放大、单位成功成本和 Goodput。

## 两种阅读方式

- ChatGPT Site：<https://test-development-ai-tutorial.wpowen.chatgpt.site/#TD-AP01>
- GitHub Pages：<https://wpowen.github.io/test-development-ai-tutorial/#TD-AP01>

## 运行 Agent 压测实验

```bash
python3 courses/td-ai-010-agent-load-stability/lab/agent_load_lab.py --config courses/td-ai-010-agent-load-stability/lab/configs/baseline.json --output courses/td-ai-010-agent-load-stability/evidence/baseline
python3 courses/td-ai-010-agent-load-stability/lab/agent_load_lab.py --config courses/td-ai-010-agent-load-stability/lab/configs/retry-storm.json --output courses/td-ai-010-agent-load-stability/evidence/retry-storm
python3 courses/td-ai-010-agent-load-stability/lab/agent_load_lab.py --config courses/td-ai-010-agent-load-stability/lab/configs/repaired.json --output courses/td-ai-010-agent-load-stability/evidence/repaired
```

第二条命令返回 1 是预期结果：它证明已知坏场景能让门禁变红。

## Skill 如何防止再次生成空内容

`skill/career-ai-course-factory/` 现在要求：

1. 先构建完整职业 × AI 命题树；
2. 每个承诺页面必须有独立研究包；
3. 研究包包含问题、来源、证据综合、工程蓝图、正文映射和验证；
4. 跟做课必须有 baseline、故障注入、修复与可观察红绿结果；
5. 缺少研究包、编辑审查、实操验证或证据边界时，页面留在内部生产状态，不进入公开产品；
6. 公开页面 ID 必须与 `promised_page_ids` 完全一致，空模块或任何 `planned/outlined/blocked` 页面都会让构建失败。

## 证据边界

Agent 实验达到 `fixture-tested`：证明离线采集、聚合、故障注入和门禁逻辑可运行；不证明真实模型、真实工具、生产容量或学习效果。所有生产阈值必须按目标业务重新推导。
