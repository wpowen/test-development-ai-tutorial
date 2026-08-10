# 测试开发 × AI

一套面向测试开发工程师的可操作 AI 质量工程教程。

这里不是 Prompt 合集，也不是 AI 工具清单。第一条学习路径从 AI 测试对象、系统结构、Oracle 和评测数据开始，最终完成一个可运行的 RAG 发布质量门禁。

## 当前完成度

- 完整知识树：25 页；
- 已交付首条学习路径：8 页；
- 已运行实验：离线 RAG evaluator；
- 已保存证据：`PASS → FAIL → PASS`；
- 尚未完成：真实模型、真实检索器、远端 Actions、从业者和学员验证。

其余 17 页仍明确标记为 `planned`，本仓库不把课程目录宣传成完整课程。

## 阅读教程

教程站源码在 `site/`：

```bash
cd site
npm install
npm run dev
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
