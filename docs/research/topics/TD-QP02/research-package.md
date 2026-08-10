# TD-QP02 · GitLab MR/Pipeline、当前 SHA、JUnit 聚合与 fail-closed 门禁

## Research brief

业务场景是订单服务 MR：Pipeline 在 commit A 上通过，随后 MR 推送 commit B；旧 Pipeline/JUnit/status 事件可能晚到。质量平台必须以 `project_id + mr_iid + pipeline_id + run_id + commit_sha` 绑定一次执行，回读当前 MR HEAD，验证 JUnit 和 artifact 属于同一 Pipeline/SHA，并在没有 Pipeline、报告缺失、必跑 suite 缺失或 SHA 不匹配时 fail-closed。

研究范围包括 GitLab MR/Pipeline/Job/Test Report API、JUnit 证据、重试/flaky/error 计数、外部 status check、审批和 protected branch 边界。Webhook 只触发回读；Pipeline success 不等于质量通过；真实 GitLab 实例、Runner、版本、tier、权限和 MR 合并结果为 `NOT_RUN`。

## Source pack

- [GitLab Pipelines API](https://docs.gitlab.com/api/pipelines/)：支持 Pipeline 查询、触发、变量/inputs 和 pipeline_id 绑定；版本/tier 能力需在目标实例复核。
- [GitLab merge requests API](https://docs.gitlab.com/api/merge_requests/)：提供 MR、head commit 和审批相关接口；不能替代质量证据聚合。
- [GitLab unit test reports](https://docs.gitlab.com/ci/testing/unit_test_reports/)：说明 JUnit 报告接入、结果展示和报告约束；报告存在不证明属于当前 SHA。
- [GitLab commit status API](https://docs.gitlab.com/api/commits/#post-the-build-status-to-a-commit) 和 [external status checks](https://docs.gitlab.com/api/status_checks/)：支持当前 commit 的状态回写；保护规则和注册权限仍需实测。
- [GitLab project webhook events](https://docs.gitlab.com/user/project/integrations/webhook_events/)：说明 MR、Pipeline 等事件；接收端仍要验签、去重和 API 回读。

## Evidence synthesis

事实：MR 当前 HEAD、Pipeline 的 commit SHA、Job/报告和外部 status 是不同层级的证据。事实：JUnit 需要确定性聚合，failed、error、skipped、flaky、retry attempt 和缺失 suite 不能被一个绿色总数掩盖。事实：没有 Pipeline 或无法证明报告归属时不能产生 success。

工程综合：在 pipeline_id 和 commit_sha 上做双重绑定；收集报告后再次回读当前 HEAD；旧 SHA 的 status 标记 superseded，不覆盖新 SHA。测试失败、证据不完整、GitLab API 不可用和权限失败必须区分为 failed/inconclusive/NOT_RUN，并分别进入缺陷、重试或人工处置。

未知项：目标 GitLab 部署形态、版本/tier、MR pipeline source、approval rules、status check 能力、Runner 镜像、JUnit 分页/保留和 merge policy 尚未验证。示例指标阈值不能外推到目标项目。

## Engineering blueprint

七节点架构与 TD-QP02 页面一致：

| 节点 | 实施与可审计输出 |
|---|---|
| GitLab MR/当前 HEAD（输入） | 保存 project、MR、source branch、head SHA、审批/线程状态和读取时间。 |
| Project Webhook/Inbox（处理） | 验签、去重、快速入队；事件只触发后续回读，不直接发布 gate。 |
| Pipeline 与 Jobs（处理） | 绑定 pipeline_id、ref、SHA、source、状态、job trace 和运行时间；没有 Pipeline 不得推断成功。 |
| JUnit/Artifact Store（证据） | 保存原始报告引用、hash、producer、suite、attempt、SHA 和 retention；报告缺失/篡改可诊断。 |
| 确定性聚合器（门禁） | 计算 total/passed/failed/error/skipped/flaky，检查必跑 suite、归属、时间和证据完整性。 |
| SHA-bound Status Check（处理） | 仅向当前 SHA 写 pending/running/success/failed，并携带 run、pipeline、URL、policy 和 reasons。 |
| MR Approval/Protected Branch Gate（人工决策） | 组合 Pipeline、外部质量状态、审批、线程和保护规则；waiver 有范围、原因和到期时间。 |

材料计划是 `gitlab_sha_junit_gate.py`、`gitlab-junit-gate.yaml`、`mr-pipeline-junit.json` 和 `td-qp02-sha-junit-sop.md`，均为页面规定的材料路径；当前交付不创建课程材料或修改 `course.ts`。

## Manuscript map

先展示“commit A 绿、commit B 已推送”的竞态，再拆开 MR HEAD、Pipeline、JUnit、artifact provenance 和 status。页面按探针→执行→收集→聚合→回读 HEAD→发布 gate 的顺序讲 SOP；用缺失 suite、损坏 XML、错误 SHA、重复 webhook 和 API 429 说明诊断路径。AI 只能辅助聚类和摘要，不能替代聚合器或批准人。

结尾必须明确回滚：冻结旧 status、恢复已批准的 gate/aggregator 版本、按当前 SHA 重跑，不覆盖失败证据。`NOT_RUN` 只表示未连接真实 GitLab/Runner，不是一次通过或失败运行。

## Editorial review

保留当前 SHA 主键、pipeline_id、JUnit 归属、必跑 suite 和 fail-closed 的具体约束。没有把 Pipeline green 写成产品质量通过，也没有把 flaky 自动忽略或用 ChatOps 评论代替 status。外部 URL 均为 GitLab 官方文档；版本/tier、API 响应、权限和报告格式留作真实验收项。

`static-reviewed` 仅描述静态设计和夹具计划，不描述真实 GitLab 执行。页面必须同时呈现产品失败、证据失败、平台不可用和人类 waiver 的不同结果，避免只显示一个总红绿灯。

## Validation

状态：`desk-researched`；真实 GitLab project、MR、Pipeline、Runner、JUnit/Test Report API、status check、审批规则、protected branch 和 merge 结果均为 `NOT_RUN`。

静态验证范围：页面有 5 个实质 blocks、7 个 architecture nodes、至少 3 个 sourceIds、3 个 outcomes/practice/completion 项，并链接脚本、配置、夹具和指南计划文件。后续真实验收必须覆盖旧 SHA 竞态、没有 Pipeline、报告缺失/损坏、JUnit 归属、必跑套件、429/403、重复事件和回滚。
