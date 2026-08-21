# TD-C03 研究包

## Research brief
控制问题：如何把能力自评改成有证据的 30/60/90 天计划，而不是“会/不会”问卷？

## Source pack
10 个来源、五条 evidence lane、五个 source family 和四类 source type 见 `source-pack.csv`。

## Evidence synthesis
能力主张必须有 evidence_ref 或 UNKNOWN；里程碑必须产生工件和 reviewer 收据，不能承诺就业或晋升。

## Engineering blueprint
基线→主张→证据检查→缺口路由→30 天工件→60 天 fault→90 天复评。空引用自动 BLOCK。

## Manuscript map
从空泛“想学 AI 测试”开始，填写自评 JSON，运行缺 evidence fault，再修复并生成路线。

## Editorial review
吸收用户文档的学习阶段、能力维度和项目证据；把结果承诺改为可复验工件。

## Validation
两条研究路线、合规 lab manifest 和边界见本目录；仅 fixture-tested，真实学习效果 NOT_RUN。

## Risk and evidence boundary
风险：空证据被误判为能力通过，或把计划工件误写成就业/晋升结果。`fixture-tested` 只表示离线夹具与 0/1/0 runner；真实模型/在线环境为 `NOT_RUN`，`live`、`practitioner`、`production` 均未证明。任何组织政策和雇佣结果保持 UNKNOWN/BLOCK。
