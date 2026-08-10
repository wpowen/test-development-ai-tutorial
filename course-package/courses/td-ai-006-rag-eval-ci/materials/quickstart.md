# 15 分钟 Quickstart

1. 进入 `lab/`。
2. 运行 `python3 scripts/reset_candidate.py`。
3. 运行 `python3 scripts/evaluate.py --report reports/baseline.json`，确认 PASS。
4. 打开 `data/eval_cases.jsonl`，理解每条样例的 oracle。
5. 运行 `python3 scripts/inject_regression.py`。
6. 再运行 evaluator；确认命令以非零退出并在报告中指出幻觉、引用、拒答、工具和性能问题。
7. reset 并重跑，确认回绿。

如果 mutation 没有变红，先修评测，不要继续拍视频或接 CI。
