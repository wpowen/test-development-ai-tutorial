# 三条端到端学习路径

机器可读的逐步合同在 [learning-paths.json](learning-paths.json)。每个步骤都有前置、输入、可复制命令、预期输出、常见失败、人工检查和交付物；这些字段是为了让学习者能从失败中恢复，而不是只跟着目录阅读。

| 路径 | 面向对象 | 结束工件 | 不会证明什么 |
| --- | --- | --- | --- |
| 7 天 AI 质量入门 | 能读普通测试报告、第一次进入 AI Quality | Eval Contract、风险切片和一次去标识迁移任务 | 真实 Provider、从业者认可或生产能力 |
| 30 天测试开发迁移 | 从确定性服务测试迁移到 AI 工作流的测试开发 | 策略、数据/Oracle、Agent 安全和质量平台 Capstone | 企业集成或上线效果 |
| 60 天 AI Quality 系统建设 | 有系统测试经验的 QA/SDET | 目标系统 TEVV 矩阵、Judge/Gold/阈值治理包和真实验证协议 | 未授权的真实验证或任何预期 PASS |

每条路径都以 fixture 的 `0 → 1 → 0` 作为可复现练习：基线通过、注入故障必须失败、保留 Oracle 的修复再次通过。只要没有真实执行收据，Provider、集成、从业者、学习者和生产结论必须保持 `NOT_RUN`。最后的 60 天 Capstone 要求准备而不是伪造这些收据。

开始前先运行结构检查：

```bash
node outputs/test-development-ai-v2/scripts/validate-tevv-governance.mjs
```
