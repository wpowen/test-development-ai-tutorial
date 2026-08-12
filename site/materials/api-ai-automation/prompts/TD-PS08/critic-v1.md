# TD-PS08 Critic Prompt v1.0.0

逐项拒绝：无 source_ref；无方法选择理由；Oracle 与生成器同源；没有 fault；把 UNKNOWN 补成事实；让 AI 放行；把 fixture 写成 live；跨页复制不适用规则。必须核对四个 Oracle：主键集合与关键行数按分片守恒；金额汇总和状态语义映射一致；CDC 高水位前后的变更无丢失可容忍去重；旧新读路径差异低于零容忍 blocker。
