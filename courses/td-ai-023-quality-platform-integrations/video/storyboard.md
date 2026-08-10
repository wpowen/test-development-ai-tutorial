# 分镜

|镜头|画面|证据|
|---|---|---|
|1|Jira→Gateway→Orchestrator→GitLab→K8s→Artifact→回写/通知|架构边界|
|2|baseline JSON|PASS/0 与 hash|
|3|stale SHA mutation|FAIL/1、SHA-BINDING|
|4|policy 与 Role 表示|无 cluster-admin、TTL|
|5|repair JSON|PASS/0|
|6|README 与 NOT_RUN 清单|学习者可复跑边界|
