#!/usr/bin/env node

import { copyFile, mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const { modules, pages, releaseScope } = await import(resolve(root, "site/content/course.ts"));

const pageType = {
  概念: "concept",
  跟做: "guided-lab",
  诊断: "diagnostic",
  参考: "reference",
  项目: "project",
};

const tutorialPages = pages.map((page, index) => {
  const examples = page.blocks.flatMap((block) => [block.code, block.expected]).filter(Boolean);
  const warnings = page.blocks.flatMap((block) => block.warning ? [block.warning] : []);
  return {
    page_id: page.id,
    slug: page.id.toLowerCase(),
    module_id: page.moduleId,
    title: page.title,
    page_type: pageType[page.type],
    level: page.id.startsWith("TD-F") || page.id.startsWith("TD-P") ? "L1" : page.id.startsWith("TD-B") || page.id === "TD-T25" ? "L4" : "L2-L3",
    order: page.order,
    prerequisite_ids: page.prerequisites,
    scenario_ids: ["TD-SYNTHETIC-COURSE"],
    learner_result: page.outcomes.join("；"),
    artifact: page.artifact,
    keywords: [page.id, page.moduleId, page.title],
    evidence_status: page.status,
    delivery_status: page.status,
    updated_at: releaseScope.validatedAt,
    source_ids: page.sourceIds,
    previous_page_id: index === 0 ? "" : pages[index - 1].id,
    next_page_id: index === pages.length - 1 ? "" : pages[index + 1].id,
    content_sections: {
      outcome: page.outcomes.join("；"),
      professional_relevance: page.why,
      plain_explanation: page.blocks[0]?.body.join("\n") ?? page.summary,
      smallest_example: examples[0] ?? page.blocks[1]?.body.join("\n") ?? page.summary,
      learner_action: page.practice.join("；"),
      expected_result: examples[1] ?? page.completion.join("；"),
      common_errors: warnings.join("；") || "按页面完成检查逐项复核；没有证据时不得把推断当成通过。",
      completion_check: page.completion.join("；"),
      evidence_boundary: page.evidenceBoundary,
    },
  };
});

const tutorial = {
  tutorial_id: "test-development-ai-tutorial-v2",
  title: "测试开发 × AI 完整教程",
  audience: "希望从传统测试开发系统进阶到 AI 质量工程的学习者",
  updated_at: releaseScope.validatedAt,
  default_page_id: releaseScope.promisedPageIds[0],
  release_scope: {
    mode: releaseScope.mode,
    promised_page_ids: releaseScope.promisedPageIds,
    catalog_complete: releaseScope.catalogComplete,
    validated_at: releaseScope.validatedAt,
  },
  modules: modules.map((module, index) => ({
    module_id: module.id,
    title: module.title,
    learner_result: module.subtitle,
    order: index + 1,
  })),
  pages: tutorialPages,
};

const tree = [
  "# 测试开发 × AI 课程树",
  "",
  "## 学习路线",
  "",
  "从传统测试生命周期开始，依次进入大模型基础、AI 辅助测试、AI 系统评测、Agent/Workflow、质量工程、Benchmark 和 Capstone。页面顺序由前置依赖决定。",
  "",
  "## 模块",
  "",
  ...modules.flatMap((module) => [
    `### ${module.title}`,
    "",
    module.subtitle,
    "",
    ...pages.filter((page) => page.moduleId === module.id).map((page) => `- ${page.id} · ${page.title} · ${page.status}`),
    "",
  ]),
  "## 页面状态",
  "",
  `- 发布范围：\`${releaseScope.mode}\`。`,
  `- 深度正文：${pages.filter((page) => ["desk-researched", "fixture-tested"].includes(page.status)).length}/${pages.length} 页。`,
  "- `outlined` 表示知识位置已确定，但逐题研究和教材正文尚未通过门禁。",
  "- `desk-researched` 表示正文和来源已整理，但没有运行目标系统。",
  "- `fixture-tested` 表示对应离线夹具已经运行，不代表生产效果。",
  "- 内容完成度与证据等级分开记录，不因正文完整而升级证据状态。",
  "",
].join("\n");

const readme = `# 测试开发 × AI 知识体系与深度样章

当前版本公开完整知识命题树，并深度交付“Agent 性能与稳定性工程”八页样章。旧批量模板页已经降级为提纲，不再冒充完整课程。

## 如何学习

打开 \`index.html\`，从左侧课程树进入。每页包含学习结果、职业场景、通俗解释、可复制示例、练习、完成检查、来源和证据边界。浏览器会在本地保存完成进度。

不要只连续阅读。每完成一页，至少要留下页面要求的工件，并按完成检查逐项验收。跟做页中的命令是最小执行形状：如果页面明确标为离线夹具，可以直接复现；如果页面标为资料已审，则应先换成脱敏业务输入，在隔离环境中验证后再接入真实系统。遇到证据不足、越权动作或高风险分歧时，正确结果是停止并进入人工复核，而不是让模型继续猜测。

## 教程结构

知识体系覆盖传统测试生命周期与专项、大模型基础、AI 辅助传统测试、AI API 与性能可靠性、LLM/RAG/Agent/Workflow 评测、AI 质量系统、Benchmark、Capstone 和职业演进。当前深度路径依次讲清 Agent 被测对象、指标、工作负载、Trace、压测架构、SOP、诊断与生产稳定性。

学习顺序保留了传统测试的专业骨架：需求与风险、测试设计与 Oracle、数据与环境、执行证据、失败诊断、CI 发布和生产反馈。AI 相关能力不是独立工具清单，而是逐层加入模型、Prompt、知识库、检索器、工具、状态、轨迹、Judge、成本与漂移。最终目标是让学习者能够解释一个 AI 版本为何通过或失败，并能保存可回放的证据。

## 当前完成度

当前发布范围为 \`${releaseScope.mode}\`：${releaseScope.promisedPageIds.length} 页 Agent 性能与稳定性样章达到正文门禁；其余页面只表示知识位置或早期正文，必须按新的逐题研究协议重写。课程尚未完成真实企业系统、从业者盲评和学员效果验证。

正文交付门禁要求每页至少包含可观察学习结果、真实职业问题、分步工作流、最小场景、练习、完成检查、来源和证据边界。这个门禁证明内容不是空目录，却不证明课程已经在生产环境有效。工具版本、业务阈值、权限和数据政策都需要在使用前重新确认。

## 证据边界

“课程正文完整”不等于“生产有效性已验证”。页面会分别标注资料整理、离线夹具运行和仍需人工或生产验证的边界。
`;

const tutorialDir = resolve(root, "tutorial");
await mkdir(tutorialDir, { recursive: true });
await writeFile(resolve(tutorialDir, "tutorial-site.json"), `${JSON.stringify(tutorial, null, 2)}\n`, "utf8");
await writeFile(resolve(tutorialDir, "course-tree.md"), tree, "utf8");
await writeFile(resolve(tutorialDir, "README.md"), readme, "utf8");
await copyFile(resolve(root, "site/dist-github-pages/index.html"), resolve(tutorialDir, "index.html"));

console.log(`Tutorial package synchronized: ${releaseScope.promisedPageIds.length} deep pages, ${pages.length} catalog topics.`);
