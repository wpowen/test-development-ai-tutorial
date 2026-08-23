# 旧版产物失败审计

审计日期：`2026-08-24`

旧版目录：`school-payment-screenshot-check-2026-08-23`

## 用户指出的失败

- 单张截图不能回答账号是不是老师；
- 没有定义群是临时还是历史、成员何时加入、当前与历史账号如何比对；
- 没有要求提供过去聊天和已确认老师资料；
- 没有把支付确认页和收款主体作为输入；
- 没有定义模型返回结构、判断依据和准确性边界；
- “四项预检”只能整理通知，不能形成严谨核验流程。

## 新验证器回归结果

旧版现在必须失败，实际结果为 `BLOCKED`。两套高风险场景均缺少：

- `input_bundle`；
- `evidence_grades`；
- `decision_states`；
- `model_output_contract`；
- `confidence_policy`；
- `unavailable_evidence_behavior`。

这表示 Skill 已把本次纠正固化成强制门禁，而不是只修改一篇稿件。

## 替代产物

使用本目录 v2 的 `USER-DELIVERY.md`、`EVIDENCE-CAPTURE-GUIDE.md`、`UNIVERSAL-MODEL-PROMPT.md`、`model-output-schema.json` 和 `JUDGMENT-RULES.md`。
