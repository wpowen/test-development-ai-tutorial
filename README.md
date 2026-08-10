# 测试开发 × AI

一套面向测试开发工程师的可操作 AI 质量工程教程。

这里不是 Prompt 合集，也不是 AI 工具清单。专业主路径从完整测试生命周期、传统专项、大模型运行和 AI 接口开始，进入生成式性能可靠性、Oracle、评测数据与 RAG 发布门禁，并给出职业迁移路线。

## 当前完成度

- 完整知识树：52 页；
- 已交付完整课程：52/52 页，0 个导航占位页；
- 已运行实验：离线 RAG evaluator；
- 已保存证据：`PASS → FAIL → PASS`；
- 尚未完成：真实模型、真实检索器、从业者和学员验证。

课程正文已达到完整目录交付门禁，但证据等级没有被正文完成度抬高：多数页面仍是 `desk-researched`，只有离线 RAG 路径达到 `fixture-tested`。

## 先看专业架构与缺口审计

- `docs/learning-architecture.md`：传统测试主线与 AI 主线怎样由浅入深融合；
- `docs/industry-framework.md`：生命周期、专项、系统对象、质量属性和职业演进的完整行业框架；
- `docs/course-map.md`：八阶段课程地图、学员工件和退出标准；
- `docs/curriculum-gap-analysis.md`：Skill 如何从六类来源主动发现缺课，而不是等待用户提醒；
- `docs/research/profession-knowledge-system.json`：可机器校验的职业知识系统和覆盖立方体；
- `skill/career-ai-course-factory/`：可复用课程研究与生成 Skill。

## 阅读教程

- ChatGPT Site：<https://test-development-ai-tutorial.wpowen.chatgpt.site/>
- GitHub Pages：<https://wpowen.github.io/test-development-ai-tutorial/>

教程站源码在 `site/`：

```bash
cd site
npm install
npm run dev
```

同一内容可导出到 GitHub Pages：

```bash
cd site
npm test
npm run export:static
```

## 运行实验

```bash
cd courses/td-ai-006-rag-eval-ci/lab

python3 scripts/reset_candidate.py
python3 scripts/evaluate.py --report reports/baseline.json

python3 scripts/inject_regression.py
python3 scripts/evaluate.py --report reports/mutation.json

python3 scripts/reset_candidate.py
python3 scripts/evaluate.py --report reports/repair.json
```

期望退出码：`0 → 1 → 0`。如果故障注入后仍然返回 0，这套评测没有检测力，应判定失败。

## 验证

```bash
cd site && npm test
cd ../courses/td-ai-006-rag-eval-ci/lab && python3 -m unittest discover -s tests -v
```

## 证据边界

当前结论是 `fixture-tested`：证明离线评测机制和故障敏感性，不证明实时模型、生产业务质量或学习效果。阈值和教学数据不得直接复制到真实项目。

## 发布方式

- GitHub：实验、教程源码、物料、Issue 和版本记录；
- OpenAI Sites：面向学习者的教程界面。

两者从同一份课程内容生成，不能分别手改。
