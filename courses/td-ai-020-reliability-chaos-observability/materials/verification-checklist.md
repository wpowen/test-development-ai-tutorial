# 验收清单

- [ ] baseline exit 0 且 `gate_pass=true`
- [ ] latency/retry fault exit 1 且至少一个 check 为 false
- [ ] repaired exit 0 且队列、p95、重试/调用放大在阈值内
- [ ] 每个 admitted task 有 task_id、trace_id 和终态
- [ ] 可以从 JSONL 找到工具失败和后续 attempt
- [ ] unittest 实际通过，不依赖第三方包
- [ ] K8s/Chaos Mesh 文件只做静态审查，没有伪造 apply 或生产验证
- [ ] 报告明确标注 synthetic fixture、virtual time 和未知项
