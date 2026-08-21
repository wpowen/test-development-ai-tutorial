# TD-F05 研究包

## Research brief
控制问题：怎样先识别 AI 任务，再选择 F1、Recall@k、ROUGE、延迟或 QPS，并让指标支持明确决定？

## Source pack
10 个 opened 来源、五条 evidence lane、五个 source family、四类 source type 见 `source-pack.csv`。

## Evidence synthesis
任务、人口、分母、切片、独立 Oracle 和失败动作决定指标含义；任何单一平均值都不能推出业务正确性。

## Engineering blueprint
业务任务→错误成本→数据人口/切片→Oracle→指标公式→不确定性→owner/阈值→动作。

## Manuscript map
用分类、RAG、Agent 三个反例让学员先填 Metric Card，再注入 denominator/Oracle fault，最后迁移。

## Editorial review
吸收用户材料的功能、质量、性能、鲁棒、安全、可用和可解释维度；生产阈值仍由组织 owner 提供。

## Validation
两条 run、comparison 和合规 lab manifest 在本目录；仅 fixture-tested。

## Risk and evidence boundary
风险：用单一平均分或 AI 自评掩盖高风险切片、空分母和 Oracle 冲突。`fixture-tested` 仅证明离线 Metric Card 能拒绝坏输入；真实 `live` 流量、`practitioner` 复核和 `production` 质量均 `NOT_RUN`，业务阈值必须由 owner 配置。
