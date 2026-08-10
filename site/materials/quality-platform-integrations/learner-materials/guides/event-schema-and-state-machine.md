# 事件 schema 与状态机

CloudEvents 最小字段是 `specversion/id/source/type/time/subject/datacontenttype/dataschema/data`；data 再带 tenant、correlation、causation、trace、Jira key、MR、SHA、run、artifact refs。状态为 `Parsed → Risked → Proposed → Human Approved → Execution Requested → Environment Ready → Running → Results Collected → Gate Evaluated → Passed|Failed|Superseded`。过期 SHA、缺报告和重复事件必须停止或去重。
