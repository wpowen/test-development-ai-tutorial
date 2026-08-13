# TD-A02 research package

九件门禁文件、十二个打开来源、两次独立研究运行和逐页实验 Manifest 的索引。控制问题：怎样证明 streaming、structured output、tool call 和 async job 的过程与终态都合法，且取消或重试不会重复副作用？

## Editorial review

- 受保护专业细节：事件序列、Schema+业务语义、工具 allowlist/幂等键、task_id 与唯一终态。
- 方法选择理由：SSE 顺序、结构化语义、工具幂等和异步唯一终态是四个不同协议问题；最终文本无法覆盖中间态。
- 人工化检查：场景、Oracle、Prompt/Eval/Mutation、命令、0/1/0 预期与诊断均绑定 TD-A02，未用跨页通用结论替代。
- 边界检查：fixture 成功不代表 live serving、practitioner review、publication 或 production validation；真实 API、模型、硬件、流量与阈值保持 NOT_RUN/Unknown。
