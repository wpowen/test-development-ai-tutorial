# TD-A05 research package

九件门禁文件、十二个打开来源、两次独立研究运行和逐页实验 Manifest 的索引。控制问题：怎样从 TTFT、TPOT、ITL 症状定位 Queue、prefill、decode、GPU、KV Cache 或工具瓶颈，并避免相关性误判？

## Editorial review

- 受保护专业细节：慢请求 Trace、queue/prefill/decode 分解、GPU/KV 信号、支持与反证、单变量结果。
- 方法选择理由：阶段 Trace 先定位 queue/prefill/decode，再把 GPU、KV 和工具 span 当支持或反证；相关性只有经过单变量翻转才可升级。
- 人工化检查：场景、Oracle、Prompt/Eval/Mutation、命令、0/1/0 预期与诊断均绑定 TD-A05，未用跨页通用结论替代。
- 边界检查：fixture 成功不代表 live serving、practitioner review、publication 或 production validation；真实 API、模型、硬件、流量与阈值保持 NOT_RUN/Unknown。
