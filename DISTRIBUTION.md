# 测试开发 × AI 双发布说明

## 结论

课程只维护一套内容，GitHub 和 OpenAI Sites 是两个发布目标，不是两套课程。

- GitHub：版本、实验代码、可复制物料、Issue、Release 和更新历史。
- OpenAI Sites：面向学员的阅读、搜索、进度、复制和课程导航体验。
- GitHub Pages 历史地址：<https://wpowen.github.io/test-development-ai-tutorial/>。
- ChatGPT Site 历史地址：<https://test-development-ai-tutorial.wpowen.chatgpt.site/>。
- 本轮未部署 85 页版本；上述地址只代表历史发布目标，不能作为当前版本在线证据。
- 当前 `site/content/course.ts` 是站点内容源；实验真实性仍由 `courses/`、`research/` 和验证报告提供。
- `tutorial/` 是由同步器生成的课程投影，不是新增内容的权威来源；禁止手工修补其中的 JSON、Markdown 或 HTML。

## 当前公共投影范围

截至 2026-08-11，当前内容源投影为 85 页、12 个公共模块，另有 4 个内部未完成命题。公共集合覆盖职业与需求生命周期、传统测试专项、AI 基础、AI 辅助测试、AI 服务性能可靠性、LLM/RAG、Agent/Workflow、质量系统、Benchmark、质量平台、Capstone、职业迁移和高级质量缺口。

这 85 页已通过本地研究、内容、执行性、材料和独立编辑门禁，但只达到 `fixture-tested` / local course candidate。历史文档中的 17、33、44、52 或 65 页均为旧快照，不得继续写成当前范围；当前事实以 `site/content/course.ts`、`research/catalog-manifest.json`、`tutorial/tutorial-site.json` 和 `tutorial/fidelity-manifest.json` 的一致结果为准。

每条路线都要求从输入依据、风险与方法、独立 Oracle、Prompt/Eval/Mutation、运行收据到发布判断形成闭环。内部知识树继续维护其他命题，但未通过逐题研究与教材门禁的内容不会进入公共投影。

## 保真同步与漂移门禁

同步器必须完整保留每个教学 block 的全部字段，包括正文、列表、表格、typed technical metadata、代码、工作目录、预期结果和 warning；同时保留页面材料、来源和证据状态。`fidelity-manifest.json` 为每页记录：

- `source_hash`：规范化后的完整页面源内容哈希；
- `material_hash`：材料描述和实际引用文件字节的组合哈希；
- `material_entries`：材料 href、描述哈希、文件路径、文件哈希和大小。

先检查漂移，不写文件：

```bash
node scripts/sync-tutorial-package.mjs --check
```

确认上游内容与静态站构建均已通过相应门禁后，执行同步：

```bash
(cd site && npm run export:static)
node scripts/sync-tutorial-package.mjs
node scripts/sync-tutorial-package.mjs --check
```

如果新投影的页面数少于现有 `tutorial/tutorial-site.json`，同步器默认拒绝。只有显式提供与旧、新页面 ID 完全匹配的决策文件才可缩减：

```bash
node scripts/sync-tutorial-package.mjs \
  --scope-change-decision docs/decisions/<approved-scope-change>.json
```

决策文件必须包含 `schema_version: "1.0"`、`decision: "approved-page-scope-reduction"`、`approved: true`、审批人、审批时间、原因，以及精确的 `previous_page_ids`、`next_page_ids` 和 `removed_page_ids`。该门禁只授权范围变化，不会把未通过页面升级为可发布。

## GitHub 发布包

公开仓库只包含：

- 教程站源码与构建说明；
- 脱敏、合成的课程 fixture；
- 可运行实验与自动化测试；
- 公开来源说明和证据边界；
- Release manifest、变更记录和问题反馈模板。

不得进入公开仓库：凭证、真实生产数据、内部日志、未经批准的企业材料、私人研究笔记和无法确认授权的课程内容。

## OpenAI Sites 发布包

Sites 使用同一份教程内容构建。评审阶段优先私有部署；公开分销前必须确认：

1. 首条学习路径全部通过内容门禁；
2. 实验命令通过 `PASS → FAIL → PASS`；
3. 所有外链、来源和证据状态可追踪；
4. 页面不包含私密研究资料或凭证；
5. 公开访问范围得到明确确认。

## 版本策略

- `page_id` 永久稳定；标题可以优化，旧链接不能静默失效。
- 内容新增使用 minor 版本，措辞和错误修复使用 patch 版本。
- 工具更新只修改 adapter，并重跑相关课程，不重写稳定知识树。
- 每次发布记录 source commit、内容哈希、验证结论和目标渠道。

## 尚未完成

- 当前 85 页版本尚未部署到 GitHub Pages 或 ChatGPT Site；
- 尚未做真实模型/provider 与企业系统集成；
- 尚未做测试开发从业者盲评与初学者可用性/学习效果测试；
- 4 个内部命题仍未晋级，117 个 canonical topic 的内容门禁仍保持 fail-closed；
- 生产安全、可靠性、成本和商业转化均未验证。

## 当前本地交付物

已生成但未部署：

- 静态站目录：`site/dist-github-pages/`；
- 静态站 ZIP：`dist/test-development-ai-site-85p.zip`；
- GitHub 仓库候选目录：`dist/github-candidate/`；
- GitHub 仓库候选 ZIP：`dist/test-development-ai-github-candidate-85p.zip`；
- 机器清单：`dist/PUBLICATION-CANDIDATES.json`。

GitHub 候选包包含当前 85 页、13 个材料包、GitHub Actions、Skill、课程实验以及 `SOLUTION-MANIFEST.json`、`CATALOG-MANIFEST.json`、`PAGE-PROMOTION-MANIFEST.json`、`EXECUTABILITY-MANIFEST.json`、`ARTIFACT-CLOSURE.json`。其 `RELEASE-MANIFEST.json` 必须保持 `BLOCKED-HIGHER-MATURITY`，直至真实集成、具名从业者审批和公开发布回读门禁通过。
