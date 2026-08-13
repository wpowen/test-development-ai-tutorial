# TD-A04 research package

九件门禁文件、十二个打开来源、两次独立研究运行和逐页实验 Manifest 的索引。控制问题：怎样固定到达率、Token 长度、缓存、场景和质量条件，找到 fixture 的 Goodput 拐点且不发生 coordinated omission？

## Editorial review

- 受保护专业细节：workload hash、planned arrivals、dropped/queued、风险切片、Goodput 和停止恢复窗口。
- 方法选择理由：open-loop 才能保持外部到达并暴露 coordinated omission；closed-loop 只适合观察单用户上限，不能单独给出容量。
- 人工化检查：场景、Oracle、Prompt/Eval/Mutation、命令、0/1/0 预期与诊断均绑定 TD-A04，未用跨页通用结论替代。
- 边界检查：fixture 成功不代表 live serving、practitioner review、publication 或 production validation；真实 API、模型、硬件、流量与阈值保持 NOT_RUN/Unknown。
