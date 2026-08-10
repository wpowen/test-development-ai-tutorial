# 快速开始

在发布包根目录依次运行 `TD-AP06` 的 baseline、retry-storm、repaired 三条命令。每次输出目录包含 `summary.json` 与 `traces.jsonl`。

先比较 workload 与 seed，再按任务成功率、Goodput、E2E p95、queue p95、重试放大、单位成功成本的顺序阅读。不要把离线夹具数字当成生产阈值。
