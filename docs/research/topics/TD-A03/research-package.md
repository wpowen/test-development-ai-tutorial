# TD-A03 research package

九件门禁文件、十二个打开来源、两次独立研究运行和逐页实验 Manifest 的索引。控制问题：怎样让 TTFT、TPOT、ITL、Goodput 和 cost_per_success 的时间点、分母、切片与质量条件都可重算？

## Editorial review

- 受保护专业细节：首/末 Token 时间戳、ITL 分布、全到达分母、质量条件和全部尝试成本。
- 方法选择理由：只有原始时间戳和完整到达分母能区分排队、生成和质量失败；GPU 利用率或平均总耗时不能替代用户与业务口径。
- 人工化检查：场景、Oracle、Prompt/Eval/Mutation、命令、0/1/0 预期与诊断均绑定 TD-A03，未用跨页通用结论替代。
- 边界检查：fixture 成功不代表 live serving、practitioner review、publication 或 production validation；真实 API、模型、硬件、流量与阈值保持 NOT_RUN/Unknown。
