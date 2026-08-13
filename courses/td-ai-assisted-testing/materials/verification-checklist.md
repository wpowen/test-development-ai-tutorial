# 验证清单

- [ ] Prompt、Input、Schema、Eval、Mutation、Critic 和 model-config 版本一致。
- [ ] 独立 Oracle 在生成器包之外，生成模型无修改和批准权限。
- [ ] 风险候选包含 requirement/diff/oracle/owner 引用；冲突与缺失保持 UNKNOWN/BLOCKED。
- [ ] baseline 在批准实现上退出 0，报告哈希与本轮输入一致。
- [ ] fault 只改变一个明确行为，实际非零退出与 manifest 完全一致。
- [ ] mutation 失败命中目标业务 Oracle，不是无关超时或旧构建。
- [ ] 数据方法有 failure model、合法域、约束、seed、预算、回放与最小反例。
- [ ] cluster 保留 raw event refs、commit、environment 和未归组事件；没有实验不写根因。
- [ ] repair 恢复权威输入或批准实现，绝不放宽 expected、删除断言或吞退出码。
- [ ] 真实模型、真实仓库、从业者、生产和发布未运行时明确标 `NOT_RUN`。
