# 视频脚本

入口返回成功，不等于 AI 任务完成。先打开 `summary.json`：task 是业务分母，HTTP/request 只是观察层。运行 baseline，查看 p95、queue、retry、call、cost 和 Trace；再运行故障配置，预测哪一个门禁先红，沿 JSONL 找到工具 error 与重试；最后运行 repair，确认同一 workload 恢复为绿。结尾交代真实模型、集群、成本和恢复时间仍是 UNKNOWN，Chaos Mesh 文件只供授权人员静态复核。
