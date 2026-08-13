# TD-A02 task prompt v1

读取批准的 `TD-A02` 输入，只生成能回链 source_ref 的候选。控制问题：怎样证明 streaming、structured output、tool call 和 async job 的过程与终态都合法，且取消或重试不会重复副作用？ 方法：为 SSE、结构化输出、工具调用、异步任务建立四个独立状态机，分别检查过程和终态。 Oracle：事件顺序合法且唯一终态；Schema 与业务语义均通过；工具副作用至多一次；异步部分失败不得汇总为完成。 输出严格满足 Schema。
