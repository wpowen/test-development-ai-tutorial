# 输入样例

`lab/fixtures/webhook.json` 是合成 Jira 事件，`lab/configs/policy.json` 是版本化教学策略。不要把 webhook body、token、Secret 或个人数据塞入事件 envelope；大报告使用 artifact ref 和 hash。当前 run 使用 `a*40`，旧版本 mutation 使用 `b*40`。
