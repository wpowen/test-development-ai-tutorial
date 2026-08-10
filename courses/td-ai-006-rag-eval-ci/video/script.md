# 4–6 分钟视频脚本

## 0:00–0:20 Hook

“客服 AI 昨天还说 7 天退款，今天换了 Prompt，突然说 30 天无条件退款。你不能靠和它聊三句判断能不能上线。今天我们做一套会在回归时直接变红的 AI 测试门禁。”

画面：并排显示知识库 `7 个自然日` 与错误回答 `30 天无条件退款`。

## 0:20–0:55 先看交付物

打开 `eval_cases.jsonl`、`thresholds.json`、`evaluate.py`、CI workflow。说明它们不是提示词合集，而是数据集、oracle、指标和执行证据。

## 0:55–1:35 建立 baseline

运行 reset + evaluate。终端显示 PASS、8/8、citation 100%、refusal 100%、tool 100%、p95 820ms。强调：snapshot 只让教学可复现，不代表某个线上模型已经通过。

## 1:35–2:30 故意破坏 AI

运行 mutation。展示它注入：退款幻觉、丢引用、Prompt injection 泄露、身份绕过、错误退款工具和 4.2s 延迟。

再次运行 evaluator。命令 exit 1。打开报告中的 case failures：这一步是课程价值核心——评测必须证明自己能发现错误。

## 2:30–3:30 为什么不是一个总分

解释确定性 gate：引用 ID、禁止词、拒答、工具参数、延迟、成本。再说明真实项目应加入 faithfulness/relevance 等语义 judge 和人工抽审；LLM-as-judge 也要版本化、校准，不能当真理。

## 3:30–4:15 修复回绿

reset 并重跑，恢复 PASS。展示 CI 文件如何使用非零退出码阻断 PR。

## 4:15–5:00 观众立刻上手

挑战：新增“诱导 Agent 直接退款”的 case，先用错误输出跑红，再修正。下载包里已有 reusable Skill，能把一条脱敏线上失败变成回归用例。

## 5:00–5:20 Human gate

“测试脚本可以阻断版本，但决定什么风险必须阻断、什么 waiver 可以接受，仍然是测试开发和业务负责人共同的责任。”
