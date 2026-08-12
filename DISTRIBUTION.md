# 测试开发 × AI 双发布说明

## 结论

课程只维护一套内容，GitHub 和 OpenAI Sites 是两个发布目标，不是两套课程。

- GitHub：版本、实验代码、可复制物料、Issue、Release 和更新历史。
- OpenAI Sites：面向学员的阅读、搜索、进度、复制和课程导航体验。
- GitHub Pages：<https://wpowen.github.io/test-development-ai-tutorial/>。
- ChatGPT Site：<https://test-development-ai-tutorial.wpowen.chatgpt.site/>。
- 当前 `site/content/course.ts` 是站点内容源；实验真实性仍由 `courses/`、`research/` 和验证报告提供。
- 旧 `tutorial/index.html` 是第一版原型，不再作为新增内容的权威来源。

## 当前公开预览范围

当前公开 85 个页面，其中 73 页达到 `fixture-tested`、12 页保持 `desk-researched`，另有 4 个未完成主题继续留在内部。预览覆盖职业现实、需求与技术文档解读、方法与 Oracle、传统测试专项、AI/LLM/RAG/Agent、质量平台、性能稳定性、Benchmark、Capstone 与高级安全质量专题。页面具备正文、练习、完成检查、来源、版本化 Prompt 或可运行 fixture 和证据边界；这仍不是 `PASS-LIVE`、`PASS-PRACTITIONER` 或生产适用性证明。

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

- GitHub 仓库与 GitHub Pages 由同一内容源生成，并由 Actions 验证后发布；
- ChatGPT Site 与 GitHub Pages 均由同一份已验证公开页面集合生成；
- 尚未做测试开发从业者与初学者可用性测试；
- 内部其余命题尚未完成逐题正文；真实企业系统、从业者盲评和学员学习效果仍未完成。
