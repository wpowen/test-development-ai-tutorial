# TD-P03 · 需求可测试性评审

## Research brief

控制问题：AI 怎样帮助资深测试人员发现歧义、冲突、缺失分支和不可观察条件，而不替产品决定规则？学习者要把一个模糊意见改成可回答、可关闭、会阻断下游工作的评审问题。

## Source pack

- ISTQB CTAL Test Analyst v4.0：test analysis 检查完整性和可测试性，test conditions 保持追溯；不提供订单业务决策。
- ISTQB CTFL 4.0.1：早期测试和静态测试可以在执行前发现缺陷。
- ISO/IEC 20246 工作产品评审页面：评审过程框架；未获取标准全文。
- NIST AI RMF Measure：记录测试、指标、限制和独立评审；它针对 AI 风险治理，不是普通订单需求流程模板。
- 失败样例：只有“请补充异常场景”的问题，没有证据、影响、owner 或关闭条件。

## Evidence synthesis

事实：需求分析需要评估测试性，测试条件应能追溯到 basis。工程综合：Review Question 强制包含 type、source_refs、impact、owner、block_level 和 close_with。高风险语义冲突不能由提取 Agent 自审后关闭。未知：企业 P0/P1 定义和评审权限。

## Engineering blueprint

评审器读取原始引用和 Requirement Contract，输出歧义、冲突、未知、不可观察副作用与 NFR 缺口。`RELEASE_BLOCKER` 传播到下游，关闭问题必须生成新契约版本并把旧版标记 SUPERSEDED。

## Manuscript map

页面用五类问题表格、RQ-007 JSON、独立评审角色提示和版本关闭规则构成完整评审动作。没有用“发现更多问题”作为完成标准。

## Editorial review

PASS 93/100。保留 BLOCKED、owner、来源和版本语义。删去鼓励性导语，问题示例直接显示谁回答、影响什么、用什么证据关闭。

## Validation

PASS（静态）：问题 Schema、阻断规则和版本迁移已审查。课程夹具把文档冲突作为负控制，但没有模拟多人评审会议效果，仍需企业专家验证。
