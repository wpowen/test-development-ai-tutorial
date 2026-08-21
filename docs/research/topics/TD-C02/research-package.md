# TD-C02 研究包

## Research brief
控制问题：怎样用可观察责任、决策权、失败代价、工件和 reviewer 证明职业成长，而不是凭年限猜等级？范围覆盖责任梯、证据引用和人工复评；组织 band 与就业结论排除并标 UNKNOWN。

## Source pack
10 个来源见 `source-pack.csv`，覆盖 profession-authority、ai-capability、executable-artifact、practitioner-failure、market-signal 五条 lane。

## Evidence synthesis
标准和职业资料支持能力维度与风险责任；工程推断是将状态绑定 artifact/evidence/oracle/reviewer。固定 P5–P9 不可跨组织外推。

## Engineering blueprint
输入→责任状态→决策权→失败代价→工件→Mutation→独立 reviewer→升级/复评。缺证据写 UNKNOWN，禁止模型自批。

## Manuscript map
冷开场用“工作年限≠责任”；再运行责任地图的 baseline/fault/repair，最后迁移到新业务并重填 owner、风险和证据。

## Editorial review
保留用户文档关于职业演进、项目复杂度和影响力的核心；把未验证的固定年限、权重、晋升阈值改为 organization adapter。

## Validation
`lab-manifest.json` 声明合规离线 runner；两条研究路线在 `research-runs.json`，冲突裁决在 `comparison.md`。状态仅 `fixture-tested`，无 practitioner/live/production 证据。
