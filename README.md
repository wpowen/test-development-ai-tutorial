# 测试开发 × AI

一套从职业知识体系出发、逐题调研和验证的 AI 质量工程教程。

## 当前真实状态

- canonical 命题目录：117 个职业命题；站点目录 89 个命题；
- 本地站点候选：85 个已通过逐题研究、编辑、执行性与材料闭包门禁的页面，分为 12 个公共模块；
- 4 个未完成命题只保留在内部目录，不进入导航、HTML、JSON、搜索或候选包；
- 13 个材料包均有 canonical → public → static → ZIP 闭包；声明的 baseline → fault → repair 实验按契约得到 `0 → 非零 → 0`；
- 85/85 页面执行性 PASS，独立编辑审计 85/85 PASS；
- 尚未完成：真实模型/provider、企业系统集成、具名测试开发从业者盲评、初学者学习效果和外部发布回读。

## 深度样章讲什么

课程从“Task 不是 Request”开始，依次讲指标树、真实工作负载、Trace/Data Schema、压测架构与工具、完整 SOP、故障诊断，以及生产 SLO、告警、降级和 Runbook。它同时覆盖传统 Golden Signals、TTFT/TTFO/ITL/E2E、Agent 轨迹、重试放大、单位成功成本和 Goodput。

## 两种阅读方式

- 本地静态站：`site/index.html`；
- 本地完整教程投影：`tutorial/index.html`。

历史 ChatGPT Site 与 GitHub Pages 地址没有部署当前 85 页版本，不得作为当前版本证据。

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

本目录是 GitHub 仓库候选包，不是已批准的公开 Release。`RELEASE-MANIFEST.json` 保持 `BLOCKED-HIGHER-MATURITY`；只有真实集成、具名从业者审批和公开发布验证全部通过后，GitHub Pages workflow 才允许部署。
