# TD-F01 快速开始

从本目录的 `learner-materials/` 进入，先读 `README.md` 和 `manifest.json`，再运行 `python3 profession_self_check.py cycle --report reports/TD-F01-cycle.json`。这个 cycle 会依次执行 baseline、故障注入和 repair，预期退出码严格为 `0/1/0`。打开四份报告核对每个责任字段、故障原因、provider=none 和 model_status=NOT_RUN。最后运行 `python3 test_profession_self_check.py`，把自己的责任地图与 `examples/career-responsibility-map.json` 比较。任何缺少需求依据、独立 Oracle 或具名发布 owner 的输入都应保持 BLOCKED，而不是由模型补齐。
