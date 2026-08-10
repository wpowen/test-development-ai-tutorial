# TD-P08 · 变更回归与发布证据 Capstone

## Research brief

控制问题：怎样把上游资料、需求、风险、测试、执行和变更连接为一个可审计闭环，并证明旧证据在版本变化后不会自动继承？产物是 Evidence Pack 和 Impact Set；课程只生成发布候选，不替 owner 做 Go/No-Go。

## Source pack

- ISTQB CTFL 4.0.1：basis、testware、结果和缺陷之间的追溯。
- ISTQB CTAL Test Analyst v4.0：测试分析、设计与风险驱动活动。
- ISO/IEC/IEEE 29148：需求信息项与版本化需求工程框架。
- OpenAI Structured Outputs：结构化中间工件能力与语义错误边界。
- NIST AI RMF Measure：版本、测试、指标、独立评审和上线监测。
- 公开工具证据：Playwright、Pact、OpenAPI 能生成或执行部分资产，但没有任何一个工具独立证明完整业务正确。

## Evidence synthesis

事实：追溯、执行和持续监测是不同但相连的质量活动。工程综合：九个工件共享父子关系、hash、状态和 owner；文档冲突返回 BLOCKED，产品 mutation 返回 FAIL，修复返回 PASS。发布仍需要残余风险与责任人。未知：真实组织的发布权限、Waiver 和回滚规则。

## Engineering blueprint

Capstone 执行 `reset -> all -> inject-code-defect -> all -> repair -> all`，预期 0/1/0。独立文档冲突控制预期退出 2，且不生成下游测试。Evidence Pack 记录三份报告 hash、synthetic fixture、not production validated 和 human release decision required。Impact Set 根据需求、契约、代码、模型/Prompt/工具变化选择回归资产。

## Manuscript map

页面按九工件链、文档阻断、产品负控制、修复发布证据和变更影响五段展开。每段都有输入、命令、结果和权限边界，不再放通用“学习收获”广告块。

## Editorial review

PASS 96/100。所有命令、退出码、状态、工件名和证据边界已锁定。删除“从入门到精通”“完整掌握”等无法验证承诺。结论只说明夹具证明了什么、没有证明什么。

## Validation

PASS：2026-08-10 本地运行得到 baseline PASS、mutation FAIL、repair PASS；文档冲突返回 BLOCKED。证据属于确定性离线夹具，不代表真实模型提取准确率、企业缺陷发现率或生产发布效果。
