# TD-A01 research package

九件门禁文件、十二个打开来源、两次独立研究运行和逐页实验 Manifest 的索引。控制问题：怎样证明一次 AI API 结果来自哪组协议、模型、Prompt、上下文、采样、Schema、工具和区域变量，而不伪造供应商内部版本？

## Editorial review

- 受保护专业细节：request_id、公开模型别名、Prompt/Schema/Tool hash、错误分类和内部版本 UNKNOWN。
- 方法选择理由：普通 API Oracle 保留协议与副作用层；AI API 额外冻结 Prompt、Schema、Tool、采样和区域，因为这些变量会改变行为。
- 人工化检查：场景、Oracle、Prompt/Eval/Mutation、命令、0/1/0 预期与诊断均绑定 TD-A01，未用跨页通用结论替代。
- 边界检查：fixture 成功不代表 live serving、practitioner review、publication 或 production validation；真实 API、模型、硬件、流量与阈值保持 NOT_RUN/Unknown。
