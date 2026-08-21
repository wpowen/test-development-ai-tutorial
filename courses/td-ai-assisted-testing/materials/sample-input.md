# 样例输入说明

本课使用完全合成的数字商品退款场景。`lab/fixtures/basis.json` 冻结两条批准需求：已激活数字商品不能自动退款，退款审计事件只能产生一次；同一文件还列出允许引用的 Oracle ID。`lab/fixtures/oracles.json` 位于生成提示包之外，保存输入和批准期望，防止生成器从当前实现复制结果。

`lab/fixtures/failure-events.json` 保存用于聚类的合成事件，每条包含 event、trace、commit 与 environment。四页的 `input.json` 只提供完成候选任务所需的最小视图。它们不含客户、支付、凭据或生产日志，也不代表真实业务分布。迁移时必须由本地 owner 重新冻结需求、状态、约束、Oracle 与隐私策略。
