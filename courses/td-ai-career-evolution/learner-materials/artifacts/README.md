# 可复用工件合同

| page | 工件 | 必填字段 | 复制前重填 |
|---|---|---|---|
| TD-C02 | responsibility-map.json | state, decision_rights, failure_cost, artifact, evidence_refs, reviewer | 业务风险、owner、证据路径 |
| TD-C03 | capability-self-assessment.json + 90-day-evidence-plan.md | claim, evidence_refs/UNKNOWN, gap_route, next_artifact, review_date | 当前基线、背景、导师 |
| TD-C04 | organization-level-adapter.yaml | organization, source_ref, owner, version, effective_from, mapping, threshold_owner | 内部 policy 和审批人 |
| TD-F05 | task-metric-card.yaml | task, population, denominator, slices, oracle, metric, uncertainty, owner, failure_action | 任务、数据、阈值 |
| TD-T26 | productivity-experiment-report.json | baseline, candidate, accepted, mutation_kill, time, cost, defect_yield, reviewer | 同任务 control、Mutation、成本 |
| TD-R01 | resource-index.json | resource, version, checked_at, purpose, limits, fallback, exit_artifact | 链接、维护状态、出口工件 |

## 已填写示例与空白模板

- 根目录的 `TD-C02-responsibility-map.json`、`TD-C03-capability-self-assessment.json`、`TD-R01-resource-index.json` 是带 `SOURCE-EXAMPLE-FILLED` 标记的完整示例，用于理解一份合格工件长什么样。
- `templates/` 下的同名 `.blank.json` 是可以直接复制的空白模板。不要把示例里的 fixture reviewer、日期或本地资源路径当成你项目的事实。
- 推荐顺序：先对照示例理解字段 → 复制空白模板 → 替换场景、owner、evidence_refs 和限制 → 注入一个故障 → 由独立 reviewer 复核。

`editable_fields` 只允许复制者填写具体业务数据和 owner；任何组织 band、生产阈值或就业结论必须有外部证据。未满足字段写 `UNKNOWN`，不能填合理猜测。`INTERNAL-UNKNOWN` 与 `BLOCK` 是安全结果，不是失败的课程体验。
