# 视频脚本

## 冷开场

“这个接口返回了 202，自动化也全绿，但订单已经 SHIPPED。你会放行吗？”先展示 mutation 报告：`BUS-SHIPPED-REJECT` 期望 409、实际 202，进程 exit 1。请学习者先写发布判断和仍缺少的证据。

## 建立模型

OpenAPI 像道路图，说明有哪些入口和数据形状；独立 Oracle 像交通规则，决定某个状态和角色能不能执行。AI 可以从 Spec、需求和 trace 提出候选路线，但不能自己制定业务规则，更不能根据被测实现修改 expected。

## Guided demo

进入 learner-materials 根目录，运行 baseline。打开报告核对订单和支付 operationId、权限、幂等、异步状态、唯一 SSE 终态、输入 hash 与 Oracle hash。baseline 必须 PASS/exit 0。

## 红灯与修复

运行 mutation，确认 `MUT-ORDER-SHIPPED-ACCEPTED` 让同一 case 稳定 FAIL/exit 1。沿 actual 和 issues 解释缺陷。随后运行 repair，确认同一 Oracle 恢复 PASS/exit 0。强调“修实现，不修测试”。

## 迁移与交付

学习者把方法迁移到企业审批 API，重建审批状态、角色矩阵、通知/webhook 副作用和门禁阈值。最后交付 OpenAPI、事件 fixture、mutation catalog、三份机器报告、Run Manifest 和仍为 NOT_RUN 的外部工具清单。
