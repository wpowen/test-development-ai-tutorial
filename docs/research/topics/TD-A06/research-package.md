# TD-A06 research package

九件门禁文件、十二个打开来源、两次独立研究运行和逐页实验 Manifest 的索引。控制问题：怎样保证 429、5xx、超时和断流下重试有界、工具副作用不重复，fallback 不会无声突破质量与安全底线？

## Editorial review

- 受保护专业细节：错误类别、Retry-After、四类 retry budget、幂等账本、fallback 质量和用户提示。
- 方法选择理由：错误先分类，随后传播 deadline；次数、总时间、Token/费用和副作用共同限制恢复，fallback 还要经过独立质量门禁。
- 人工化检查：场景、Oracle、Prompt/Eval/Mutation、命令、0/1/0 预期与诊断均绑定 TD-A06，未用跨页通用结论替代。
- 边界检查：fixture 成功不代表 live serving、practitioner review、publication 或 production validation；真实 API、模型、硬件、流量与阈值保持 NOT_RUN/Unknown。
