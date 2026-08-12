# TD-A06 task prompt v1

读取批准的 `TD-A06` 输入，只生成能回链 source_ref 的候选。控制问题：怎样保证 429、5xx、超时和断流下重试有界、工具副作用不重复，fallback 不会无声突破质量与安全底线？ 方法：先分类错误并传播 deadline；次数、总时间、Token/费用和副作用共同限制重试；fallback 必须独立评测。 Oracle：429 尊重 Retry-After；attempt/time/cost 均不超预算；同一幂等键副作用至多一；fallback quality gate 通过才可使用。 输出严格满足 Schema。
