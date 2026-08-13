# 最终课程验收

## 结论

当前产物已达到“85 页本地完整课程 + 确定性 fixture 实验”可用状态。旧审计指出的内容缩水、共享材料覆盖、模糊代码框、隐含工作目录、未发布路径、静态投影丢字段、移动端溢出和状态漂移均已修复。

它仍不是从业者已批准、真实模型已验证、企业系统已集成或生产有效的课程。对外成熟度保持 `NOT_RUN`。

## 小白能学到的完整链路

课程不再从“让 AI 生成测试用例”直接开始，而是要求学员依次完成：

1. 还原测试开发的责任、输入、工件、决定和反馈；
2. 分开阅读需求文档与技术文档，记录 locator、版本、权威 owner、冲突与 Unknown；
3. 把依据变成需求契约、风险与测试条件；
4. 根据失败模型选择边界值、决策表、状态、契约、属性、变形、组合、性能或故障注入方法；
5. 建立不依赖被测实现自证的 Oracle；
6. 将 Prompt、输入、Schema、Eval、Mutation 与模型边界版本化；
7. 运行 baseline→fault→repair，读取退出码、finding 和证据工件；
8. 汇总 PASS、FAIL、BLOCKED、UNKNOWN 与剩余风险，由具名人类 owner 决定发布、Waiver 或回滚；
9. 把生产反馈、事故和变更重新纳入回归与 Eval 资产。

## 当前课程面

- 85 个公共页面，12 个模块；
- 117 个 canonical topic，89 个站点命题；
- 传统测试专项、需求与技术文档、AI 辅助测试、LLM/RAG、Agent/Workflow、AI 性能可靠性、质量平台、Benchmark、Capstone、职业迁移与高级质量缺口；
- 每个公共页面都有独立研究包、Prompt/Eval/Mutation 或明确方法链、可检查命令/配置/图示、练习、完成检查、材料和证据边界。

## 新鲜证据

- executability：85/85 PASS，293 typed blocks，0 legacy、0 invalid path、0 implicit cwd；
- editorial：85/85 PASS，边界 85/85=100；
- materials：13 个 bundle，canonical/public/static/ZIP 闭包 PASS；
- factory：100 个回归 PASS；完整课程 validator 与 `--run-labs` PASS；
- site：validate、typecheck、lint、build、SSR、static export 和静态测试 PASS；
- mobile：390×844 遍历 85 页无横向溢出；
- fidelity：教程投影 85 页，source/material hash 漂移检查 PASS。

## Evidence / Inference / Unknown

- Evidence：以上数字来自 2026-08-11 本地 fresh run 与机器可读审计。
- Inference：该课程适合作为小白本地学习和专业工作流训练候选；是否真正提升岗位表现仍需人类验证。
- Unknown：真实模型、企业系统、从业者、初学者学习效果、外部发布与生产结果。

## 下一项验证

在独立 validation lane 中选择代表页面运行真实模型、从业者盲评和初学者任务测试。不得因本地 fixture 全绿就批量升级 maturity，也不得在验证前部署当前 85 页版本。
