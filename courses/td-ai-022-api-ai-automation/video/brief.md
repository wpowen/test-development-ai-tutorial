# 视频简报

## 核心任务

用一个“SHIPPED 订单被接口错误接受取消”的红灯开场。学习者不是观看讲师写请求，而是从 OpenAPI 生成候选检查，再用独立 Oracle 证明协议成功不等于业务正确。

## 可见证据

画面必须展示 learner-materials 根目录、两份 OpenAPI、checkout 事件 fixture、baseline/mutation/repair 三条命令、JSON 报告中的输入 hash、mutation ID 和 `BUS-SHIPPED-REJECT`。修复时只恢复实现状态检查，不修改 expected 或跳过 case。

## 边界

Schemathesis、Pact、k6、GitLab CI 只展示 `static-reviewed/NOT_RUN` 适配位置；不展示模拟的外部工具终端，也不称为 live evidence。最终发布决定属于 AI 质量负责人和 API owner。
