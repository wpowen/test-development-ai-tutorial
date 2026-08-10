import type { TutorialPage } from "../course.ts";

export type TopicSpec = {
  id: string;
  moduleId: string;
  title: string;
  type: TutorialPage["type"];
  duration: string;
  summary: string;
  why: string;
  prerequisites: string[];
  outcomes: [string, string, string, ...string[]];
  artifact: string;
  problem: string;
  workflow: [string, string, string, ...string[]];
  scenario: string;
  code?: string;
  expected: string;
  failure: string;
  sourceIds: [string, string, string, ...string[]];
  evidenceBoundary: string;
};

export const buildTopicPage = (spec: TopicSpec): TutorialPage => ({
  id: spec.id,
  moduleId: spec.moduleId,
  order: 0,
  title: spec.title,
  type: spec.type,
  status: "outlined",
  duration: spec.duration,
  summary: spec.summary,
  why: spec.why,
  prerequisites: spec.prerequisites,
  outcomes: spec.outcomes,
  artifact: spec.artifact,
  blocks: [
    {
      title: "先把真实问题说清楚",
      body: [
        spec.problem,
        `这页不把 AI 当成一个“自动给答案”的黑盒。你需要先写清输入来自哪里、模型或 Agent 可以做什么、最终决定由谁负责，再把 ${spec.artifact} 作为可检查的职业工件。只有输出能回到需求、代码、数据、Trace 或版本记录，课程才算解决了测试开发的实际问题。`,
      ],
    },
    {
      title: "按证据顺序完成工作流",
      body: [
        "先固定业务目标和失败成本，再执行下面的步骤。每一步都保存输入、版本、输出和判定，不允许只留一段模型对话。完成后应能回答：哪个变化导致了哪个质量结论，已知坏版本能否稳定变红，谁有权接受例外。",
        "工具品牌可以替换，顺序不能颠倒。若前一步的输入或 Oracle 不可信，后面的自动化、评分和可视化只会更快地产生错误结论。",
      ],
      bullets: spec.workflow,
    },
    {
      title: "在最小业务场景里亲手做一次",
      body: [
        spec.scenario,
        "操作时先运行或推演已知良好版本，保存基线；再注入一个有业务意义的缺陷，确认检查变红；最后修复或重置并复跑。不能运行真实系统时，可以使用脱敏合成输入，但必须把它标成 fixture，不能把教学结果写成生产效果。",
      ],
      code: spec.code ?? `# ${spec.id} 最小执行记录\ninput_version: v1\nsystem_version: candidate-a\nrisk_slice: high\nexpected_gate: FAIL_ON_SEEDED_REGRESSION\nevidence: artifact/${spec.id.toLowerCase()}-report.json`,
      expected: spec.expected,
    },
    {
      title: "诊断失败，而不是把阈值调到通过",
      body: [
        spec.failure,
        "定位时按输入与数据、模型或 Prompt、检索与工具、执行环境、Scorer 与阈值五层检查。一次只改变一个变量，并把前后差异写进报告。若没有足够证据区分这些层，应输出“未知并升级人工”，而不是让大模型补一个听起来合理的根因。",
      ],
      warning: "降低阈值、删除断言、扩大权限或无限重试都可能制造假绿。任何 waiver 必须记录负责人、原因、补偿控制、过期时间和回滚条件。",
    },
    {
      title: "迁移到你的项目",
      body: [
        `先保留不变的部分：风险驱动、版本记录、故障注入、人工责任和 ${spec.artifact} 的验收字段。再替换业务输入、目标系统、风险切片和阈值。不要一次接入全部生产复杂度，先选一个可回放、低权限、可回滚的场景。`,
        "迁移成功的标准不是模型生成了更多内容，而是团队能更早发现一个真实风险、缩短定位时间，或把原本口头的发布判断变成可审计证据。若无法观察这些变化，应保留为学习实验，不进入生产门禁。",
      ],
      bullets: ["替换为脱敏的真实输入和当前版本", "补充历史事故与高风险切片", "由测试负责人确认 Oracle、阈值和人工升级边界"],
    },
  ],
  practice: [
    `用一个自己的业务变更完成最小流程，并保存 ${spec.artifact}`,
    "注入一个已知缺陷，确认检查能失败并从证据定位到具体层",
    "把同一方法迁移到不同业务对象，写出保持不变的原则和必须修改的两项配置",
  ],
  completion: [
    "工件记录输入、系统、数据、Prompt/模型/工具版本和负责人",
    "已知良好、故障注入、修复三个阶段都有可观察结果，不能只展示最终 PASS",
    "证据不足、越权或高风险分歧时会停止并进入明确的人工复核或回滚路径",
  ],
  sourceIds: spec.sourceIds,
  evidenceBoundary: spec.evidenceBoundary,
});
