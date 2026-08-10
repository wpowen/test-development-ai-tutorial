# Accessibility 与视觉回归

## 两个 oracle 的分工

Accessibility/语义 oracle 检查“用户能否找到并操作正确对象”；视觉 oracle 检查渲染结果是否发生受控变化。截图不能证明退款已批准、收货已入账或预约已改期。

## SOP

1. 先断言 role、label、identifier、resource-id 和业务状态。
2. 固定 OS、浏览器/SDK、字体、scale、locale、timezone、动画和网络。
3. 基线首次生成后进入人工审批，不自动覆盖。
4. 动态时间、广告、头像和网络结果使用明确 mask；每个 mask 记录理由。
5. diff 发生时先校准环境，再区分真实 UI 变化、数据变化与渲染漂移。
6. AI 可以聚类 diff 或写摘要，但不能批准 baseline 或放宽阈值。

## 证据字段

保存 baseline metadata、diff、截图、测试 commit、工具版本、设备/浏览器、mask、阈值、审批人和最终决定。没有实际截图运行时保持 `NOT_RUN/static-reviewed`。
