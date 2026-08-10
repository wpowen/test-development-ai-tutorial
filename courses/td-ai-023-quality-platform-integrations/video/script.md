# 视频脚本

1. 冷开场：旧 commit 的绿色状态为什么不能放行新 MR？
2. 运行 baseline，展示 event id、candidate approval、current SHA、JUnit、namespace 和 audit hash。
3. 注入 stale SHA，观察 `SHA-BINDING` 红灯与 exit 1。
4. 解释重放、报告缺失、cluster-admin 和脱敏通知的独立 Oracle。
5. 运行 repair 回绿；强调 AI 只能候选，质量负责人保留审批。
6. 打开 learner-materials README，说明可复制命令与 NOT_RUN 边界。
