# 预期输出

baseline 与 repaired 的 `gate_pass` 为 true；retry-storm 为 false。每个目录包含聚合 `summary.json` 和逐任务 `traces.jsonl`。坏版本应呈现显著排队、尾延迟与重试放大，修复后恢复到门禁范围。
