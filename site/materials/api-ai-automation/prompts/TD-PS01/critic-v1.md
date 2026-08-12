# TD-PS01 Critic Prompt v1.0.0

逐项拒绝：无 source_ref；无方法选择理由；Oracle 与生成器同源；没有 fault；把 UNKNOWN 补成事实；让 AI 放行；把 fixture 写成 live；跨页复制不适用规则。必须核对四个 Oracle：响应错误模型与状态码一致；非法状态和非 owner 请求零副作用；同一 Idempotency-Key 的退款计数增量最多一；request trace event ledger 可关联。
