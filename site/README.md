# 测试开发 × AI 教程站

面向测试开发工程师的 AI 质量工程教程。课程不是工具清单，而是从职业问题出发，逐页完成可验证产物。

## 当前版本

- 52 页完整专业知识树，覆盖传统测试基线、大模型基础、AI 辅助测试、LLM/RAG、Agent/Workflow、质量工程、Benchmark 与 Capstone；
- 52/52 页达到正文交付门禁，0 个导航占位页；
- RAG 质量门禁实验已完成 `PASS → FAIL → PASS`；
- 当前证据等级为离线 fixture，不代表真实模型或生产效果。

## 本地预览

```bash
npm install
npm run dev
```

## 验证

```bash
npm test
```

验证包括：52 页完整性、内容密度、前置依赖、来源、证据边界、构建、服务端渲染、静态导出 JavaScript 语法和交付状态诚实性。

## 内容维护

课程内容位于 `content/course.ts`。页面 ID 必须稳定；计划页不得写成已完成页；证据状态不能超出真实验证范围。

GitHub 用于版本、实验和复用物料；OpenAI Sites 用于学习体验。两个渠道从同一份已验证内容构建。
