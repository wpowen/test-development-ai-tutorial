# TD-T26 研究包

## Research brief
控制问题：AI 生成测试用例是否真正提效，还是只增加候选数量和幻觉？

## Source pack
10 个 opened 来源、五条 lane、五个 family、四类 type 见 `source-pack.csv`。

## Evidence synthesis
提效必须比较同任务 baseline/control、accepted-test、Mutation kill、人工时间、成本和 unique defect yield；AI 不能自判正确。

## Engineering blueprint
需求 Basis→风险→Oracle→Baseline/AI candidate→编译运行→Mutation→reviewer→决策。

## Manuscript map
先展示 500 条重复候选的假提效，再运行 TD-T26，注入 mutation，比较 accepted 和 kill。

## Editorial review
吸收用户材料的 AI 生成用例、Prompt 规则和提效指标；不把生成数量或响应速度升级为 ROI。

## Validation
合规 lab manifest、两条 run 和 comparison 已保存；仅 fixture-tested，真实团队 ROI、模型和生产缺陷 NOT_RUN。

## Risk and evidence boundary
风险：把生成数量、模型响应时间或单次样本提升误写为提效，忽略重复、漏测和人工返工。`fixture-tested` 只证明对照/Mutation 流程；真实 `live` 模型、`practitioner` 团队复核和 `production` 缺陷收益均 `NOT_RUN`，不能宣称 ROI。
