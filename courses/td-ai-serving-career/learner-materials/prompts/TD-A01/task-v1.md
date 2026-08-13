# TD-A01 task prompt v1

读取批准的 `TD-A01` 输入，只生成能回链 source_ref 的候选。控制问题：怎样证明一次 AI API 结果来自哪组协议、模型、Prompt、上下文、采样、Schema、工具和区域变量，而不伪造供应商内部版本？ 方法：保留 HTTP、鉴权、错误和幂等共同契约，再增加生成 Manifest、行为 Oracle、Token/成本和可靠性层。 Oracle：request_id 必须存在；公开版本变量齐全；不可见内部版本为 UNKNOWN；错误类别能驱动 retryable 决策。 输出严格满足 Schema。
