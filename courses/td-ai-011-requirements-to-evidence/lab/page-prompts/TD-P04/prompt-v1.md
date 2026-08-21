# TD-P04 风险分析与测试方法选择 Prompt v1.1.0

## 能做什么

把已确认的需求和技术契约转成风险驱动的测试策略，回答“什么最值得测、用什么方法、在哪一层测、如何判断、漏测由谁承担”。它避免 AI 直接堆出大量相似用例，并把等价类、边界值、决策表、状态转换、契约、属性、变形和场景测试与具体风险绑定。

## 使用前准备

准备 ACCEPTED Requirement Contract、技术解析结果、历史缺陷、变更范围、系统约束和可用测试环境。高风险等级、发布门槛与损失定义必须由团队提供；没有统一标准时保留 Unknown，不要让 AI 生成“高/中/低”的万能阈值。

## 直接复制到 AI Agent

```text
你是一名风险驱动的测试架构师。请基于给定证据选择测试方法和层级，不按用例数量优化，也不把所有检查都推给 E2E。

【业务范围与变更】
[粘贴本次功能、变更点、未变范围]

【Requirement Contract】
[粘贴 ACCEPTED requirement_id、规则、状态、不变量、异常、NFR、source_ref]

【技术解析】
[粘贴组件、接口、数据、状态、异步、重试、幂等、可观测性和安全结论]

【风险与损失口径】
[粘贴组织已批准的严重度定义、失败成本、法规/隐私/资金边界、owner；没有则写“未定义”]

【历史与约束】
[粘贴相关缺陷、事故、流量/数据形态、环境、预算、时间、不可测依赖]

【方法选择规则】
1. 先识别 failure、trigger、impact、exposure、detectability、reversibility、owner 和 source_refs，再决定测试。
2. 数值/长度/时间边界：等价类 + 边界值；写出有效类、无效类和边界点。
3. 多条件交互：决策表/组合；写出因素、约束、不可行组合和剩余组合风险。
4. 生命周期与非法转换：状态转换/N-switch；写出状态、事件、guard、允许和禁止路径。
5. 跨系统业务旅程：场景测试；写出角色、触发、副作用、交接、补偿和回滚。
6. API/事件/数据 Schema：契约测试；写出版本、兼容性、错误和消费者 Oracle。
7. 稳定不变量：属性测试；写出生成器、不变量、独立检查和缩减策略。
8. 无单一标准答案：变形测试；写出输入变换和应保持的输出关系。
9. 规格不完整：探索性测试；写出 charter、timebox、观察和后续问题，不能伪装成完备覆盖。
10. 选择层级 unit/component/contract/integration/e2e/production-observation，并解释为何选择、为何拒绝其他层级。
11. 每个关键风险必须绑定独立 Oracle、测试数据、环境、监控、失败动作和 residual-risk owner。
12. 不要编造严重性、概率、覆盖率、SLA 或阈值。无 Oracle、无 owner、无可观察点的关键风险 status=BLOCKED。

【输出格式】
A. 风险摘要：最关键风险及业务影响
B. Risk Test Plan 表：risk_id、requirement_ids、failure、impact、evidence、method、rationale、rejected_methods、test_levels、oracle_id、data、environment、monitoring、owner、residual_risk、status
C. 方法选择决策表
D. 测试层级分配图（unit→contract→integration→E2E→observation）
E. Evidence / Inference / Unknown 清单
F. BLOCKED 风险与 owner_questions
G. 可交给用例设计的 risk_id 清单

【输入粘贴区结束后的强制自检】
- 每个关键 requirement_id 是否至少关联一个风险？
- 每个关键风险是否有方法理由、独立 Oracle、监控与 owner？
- 是否用“更多 E2E”代替了方法选择？
- 是否出现来源中没有的严重度或阈值？
- rejected_methods 和 residual_risk 是否真实保留？
```

## 修改这些字段就能复用

替换业务范围、需求、技术解析、风险口径、历史与约束。方法选择规则可按系统删减，但必须保留“输入形态 + 风险 + Oracle + 层级 + 成本”的选择逻辑。将组织自己的严重度矩阵放进风险口径，不要修改 Prompt 里的 Evidence/Inference/Unknown 和 BLOCKED 规则。

## 预期输出

输出是一份能指导用例编写和自动化投资的 Risk Test Plan：每个风险说明为什么选某种方法、在哪层执行、用什么独立 Oracle、失败后做什么。它不是一串“功能/性能/安全都要测”的泛化清单。

## 结果自检

- 高风险是否优先覆盖不可逆、资金、权限、数据污染和不可恢复失败？
- 方法是否与数据/状态/条件结构匹配？
- E2E 是否只保留关键旅程而非全部组合？
- 生产监控是否被误写成上线前测试的替代品？
- 风险接受是否有具名 owner，而不是 AI 判断？

## 停止条件与边界

关键需求仍 BLOCKED、损失口径缺 owner、关键风险没有独立 Oracle/环境/可观察证据、涉及权限或不可逆副作用但无控制时必须停止。该 Prompt 生成候选策略，不证明风险等级、覆盖充分性或生产适用性。
