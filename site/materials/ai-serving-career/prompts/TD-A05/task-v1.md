# TD-A05 task prompt v1

读取批准的 `TD-A05` 输入，只生成能回链 source_ref 的候选。控制问题：怎样从 TTFT、TPOT、ITL 症状定位 Queue、prefill、decode、GPU、KV Cache 或工具瓶颈，并避免相关性误判？ 方法：先按阶段症状分流，再关联 request trace 与资源信号，最后用单变量实验确认或推翻候选根因。 Oracle：高 TTFT 且 queue 占主要比例指向排队；KV 高必须伴随 eviction/preemption 或对照实验；不可见指标为 UNKNOWN。 输出严格满足 Schema。
