# Prompt Kit 迁移卡

## 业务场景

- 目标角色：
- 触发事件：
- 业务对象：
- 成功结果：
- 失败成本：

## 来源权威

- 当前有效 PRD/需求：
- 当前技术设计/ADR：
- 接口/事件/数据契约：
- 冲突裁决责任人：
- 关闭冲突所需证据：

## 责任人

- 需求 owner：
- 技术 owner：
- Oracle owner：
- 风险接受 owner：
- 发布 owner：

## 可修改

- 业务名词、角色、状态、接口、数据、测试层级和工具适配器。
- 组织批准的 Metric Card、严重度、SLA、权限和发布门禁。

## 不可修改

- Evidence / Inference / Unknown 分层。
- 事实必须有 source_ref；关键冲突必须 BLOCKED。
- Oracle 不能来自被测实现或同一生成输出。
- requirement→risk→method→oracle→case→result 的追踪链。
- fixture、model、integration、practitioner、live、production 证据必须分开。

## 验证方法

1. 用一个已批准的小范围输入生成 baseline，人工回读来源与 Oracle。
2. 删除关键 source_ref 或植入错误规则，确认结果 BLOCKED/FAIL。
3. 修复输入，确认结果恢复且旧收据被 supersede。
4. 保存 AI provider/model/version、Prompt hash、input/output hash、评测和人工 owner。
