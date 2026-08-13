# TD-C04 研究包

## Research brief
控制问题：如何把公共责任状态安全映射到组织 band，而不由 Skill 猜 P5–P9？

## Source pack
10 个 opened 来源、五条 lane、五个 family、四类 type 见 `source-pack.csv`。

## Evidence synthesis
用户文档提供 P5–P9 与年限矩阵作为输入，但作者/组织和政策未知；因此保留为 adapter 候选，缺 source_ref/owner/version/effective_from 时 INTERNAL-UNKNOWN/BLOCK。

## Engineering blueprint
公共状态→组织 policy→owner 审批→生效版本→岗位映射→Metric Card→复审周期。

## Manuscript map
先展示错误的“课程完成= P6”，再清空 policy 字段，观察 BLOCK，最后由学员填写自有组织适配器。

## Editorial review
完整吸收职业演进和 P5–P9 讨论，但不把固定年限、权重或阈值写成跨组织事实。

## Validation
lab manifest、两条 run 和 comparison 均保留；仅 fixture-tested，真实组织 policy 和晋升结果 NOT_RUN。

## Risk and evidence boundary
风险：把公共职级示例或 P5–P9 年限误写成组织政策，造成错误晋升判断。`fixture-tested` 只证明 adapter 的离线故障检测；真实 `live` policy、`practitioner` 复核和 `production` 结果均 `NOT_RUN`，不得由课程完成度推导。缺 source_ref/owner/version/effective_from 时必须 INTERNAL-UNKNOWN/BLOCK。
