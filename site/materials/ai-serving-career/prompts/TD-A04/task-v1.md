# TD-A04 task prompt v1

读取批准的 `TD-A04` 输入，只生成能回链 source_ref 的候选。控制问题：怎样固定到达率、Token 长度、缓存、场景和质量条件，找到 fixture 的 Goodput 拐点且不发生 coordinated omission？ 方法：open-loop 保持外部到达并记录 dropped arrivals；closed-loop 仅诊断单用户上限；阶梯实验每级只改到达率。 Oracle：计划到达数等于完成、失败、dropped 和仍排队之和；SLO 破坏后停止；容量以 Goodput 判定。 输出严格满足 Schema。
