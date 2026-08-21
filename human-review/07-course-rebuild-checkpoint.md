---
status: superseded
superseded_at: 2026-08-16
replacement: human-review/11-测试开发专家全量质量审计与修订计划-2026-08-16.md
reason: 102-page reconstruction checkpoint predates the current 103-page canonical catalog and evidence-governance contract.
---

> **历史快照（已废弃）**：本文只记录 2026-08-12 的重建阶段，不得作为当前课程、晋级或发布依据。请读取 [`11-测试开发专家全量质量审计与修订计划-2026-08-16.md`](11-测试开发专家全量质量审计与修订计划-2026-08-16.md)。

# 102 页课程重建检查点（历史）

## 当前结论

本文件取代 04、05、06 的旧范围结论，记录 2026-08-12 的 course lane 实现事实。课程已从 85 页扩展为 102 个公开学习页，并完成用户两份材料的来源吸收、职业演进六页、Agent 测试架构十一页、连续编号、小白复用合同和逐页主题视觉。

这不是独立 validation 结论，也不是线上发布批准。真实模型、企业系统、从业者盲评、目标初学者任务测试和生产效果仍为 `NOT_RUN`；旧的“85 页最终课程验收”不得继续作为当前状态。

## 当前课程面

- 117 个 canonical 能力主题；106 个内部页面；102 个公开页面；13 个公开模块。
- 新增职业演进：责任证据梯、自评与 30/60/90 证据计划、组织职级适配器、AI 任务/指标卡、AI 辅助提效实验、资源雷达。
- 新增 Agent 测试架构：总览、D0–D7、四证据环、`pass@k`/`pass^k`、人机接管、安全、成本、治理和高风险适配器。
- 课程导航使用唯一 `display_number=1..102`，前置页面必须位于使用者之前。
- 每页具备小白术语、心智模型、正反例、失败诊断、复用工件和仓库内主题 SVG；页面图不是生产拓扑证明。

## 来源吸收

- 冻结来源：2 份。
- 章节：198；原子：413；总计 611。
- disposition：312 `incorporated`、175 `adapted`、120 `blocked`、4 `rejected`、0 `UNMAPPED`。
- 职级、年限、晋升周期和固定百分比不得作为通用规则；它们进入组织适配器或 Metric Card，缺 owner/依据时保持 `INTERNAL-UNKNOWN` 或 `BLOCKED`。
- Agent 文档中的固定阈值不得写成行业标准；D0–D7、四环和统计语义保留，阈值由任务、总体、切片、基线、置信区间、owner 和失败动作决定。

## Fresh course evidence

- 课程重建合同：8/8 PASS。
- 内容结构：102 delivered public，4 incomplete internal。
- executability：102/102 PASS；344 个 typed technical blocks；0 unpublished path；0 implicit cwd；0 legacy block。
- 材料：15 个动态发现 bundle 的 canonical/public/ZIP 与六组 red/green labs 门禁通过。
- 目录：117 canonical topics、106 internal pages、102 public pages、269 migration rows，0 uncovered high-risk gaps。
- 本地静态站点与教程 JSON 已同步为 102 页；这只属于 course artifact，不表示 GitHub 或 ChatGPT Site 已发布。

## Evidence / Inference / Unknown

- Evidence：上述数量来自本地课程源、机器清单、确定性 fixture 和 fresh 命令输出。
- Inference：当前结构比旧 85 页更接近“小白可读、可跟做、可迁移”的课程候选。
- Unknown：独立 editorial 评分、初学者完成率与迁移成功率、真实模型波动、企业适配器、从业者认可、线上发布和生产收益。

## 下一项门禁

course lane 只在课程包、逐页研究包、编号、视觉、复用与本地构建全部通过后，移交独立 validation lane。validation 必须重新审计 102 页，不得沿用 85 页 editorial/PASS；若任一逐页研究、promotion、solution trace、移动端或 clean-room 门禁失败，发布继续阻断。
