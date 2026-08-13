# 测试开发 × AI v2 验证报告

Verdict: `PASS-FIXTURE / PASS-LOCAL-COURSE`。不等于 `PASS-LIVE`、`PASS-PRACTITIONER`、`PASS-PUBLICATION` 或 `PASS-PRODUCTION`。

## Evidence

- 公共课程为 85 页、12 个模块；另有 4 个未完成命题保留在内部目录，不进入导航、搜索、静态站或发布承诺。
- canonical 目录包含 117 个职业命题，89 个站点命题映射，85 个公共页面；12 个高风险补充缺口全部有映射，117 个 content gate 仍保持 blocked，防止目录存在被解释为成熟度通过。
- 每个公共页面都有九件独立研究包：brief、source pack、research runs、synthesis、blueprint、manuscript、comparison、lab manifest、validation。每页至少两次研究运行并有独立比较。
- 独立编辑审计 `research/editorial-review-2026-08-11-final.json`：85/85 页面 editorial score ≥90，85/85 boundary preservation=100；旧失败审计通过 SHA-256 superseded chain 保留。
- 执行性审计：85/85 页面 PASS；293 个 typed technical blocks，包括 109 command、83 versioned prompt、30 config、37 diagram、26 pseudocode、8 formula；0 个 untyped block、0 个未发布 `courses/` 路径、0 个隐含工作目录。
- 13 个动态发现的学习材料包通过 canonical→public→static→ZIP 双向成员与 SHA-256 闭包。
- 工厂 validator 与 `--run-labs` 均通过。实验真实执行 baseline、fault、repair；fault 按合同返回非零，修复后恢复为 0。T05/T08 的故障结果保留 `BLOCKED`/`UNKNOWN`，没有被改写成伪 PASS。
- 解决方案架构以六个 solution unit 覆盖并追踪全部 85 页；设计、真实集成、从业者与外部 publication maturity 继续保持 partial/internal/NOT_RUN。
- 站点 `validate:release`、材料验证、TypeScript、ESLint、vinext build、SSR、静态导出、静态脚本、材料闭包测试全部通过。
- Playwright 在 390×844 视口遍历 85 页，全部无 document-level 横向溢出。
- 教程投影完整保留 85 页内容、typed technical metadata、材料和 source/material hash；`sync-tutorial-package.mjs --check` 通过。
- 通用 factory Skill 的 validator/public-release 回归 100/100 PASS，源码与 `/Users/owen/.codex/skills/career-ai-course-factory` 安装目录一致，Skill 自检通过。

## Inference

- 当前产物已经达到“可供小白本地学习、跟做离线实验、观察故障与修复、理解证据边界”的完整课程候选状态。
- 将问题、方法、独立 Oracle、Prompt、Eval、Mutation 和 0→1→0 收据绑定到每页，比共享模板和工具清单更能迁移到其他职业课程。
- 真实模型和企业系统可能暴露新的工具权限、数据隐私、Judge 偏差、成本与非确定性问题；这些不能从 fixture 结果推断。

## Unknown

- 未运行真实 LLM/provider 的 85 页全套 Prompt；provider/model/参数表现未知。
- 未连接真实 Jira、GitLab、Kubernetes、浏览器/移动设备、模型服务、队列、观测后端和生产数据。
- 未完成测试开发从业者盲评、初学者可用性测试、学习完成率、迁移效果或商业转化验证。
- 未部署当前 85 页版本，也没有线上 hash 与匿名访问回读；旧部署记录不能替代当前版本发布证据。

## Professional utility verdict

本地课程与 fixture 证据通过。外部职业有效性仍须由具名测试开发从业者、初学者任务表现和真实系统收据共同裁决；AI 和课程作者自评不能替代这些门禁。

## Not tested

- live model/provider；
- enterprise integration；
- practitioner blind review；
- beginner usability and learning outcome；
- external publication readback；
- production safety, reliability, cost and effectiveness。

## Superseded evidence

历史 17 页报告、33 页分发说明、6 PASS / 27 FAIL 执行性审计和 293 条工厂错误均描述修复前状态。它们保留用于解释缺陷演进，但不再代表当前产物。
