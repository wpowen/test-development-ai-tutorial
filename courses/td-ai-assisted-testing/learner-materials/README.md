# AI-assisted testing learner lab

本目录只使用 Python 3 标准库和合成退款资料。四页分别有版本化 Prompt/Input/Schema/Eval/Mutation，统一 runner 只验证候选工件，不调用模型，也不让生成器修改独立 Oracle。

```bash
python3 ai_assisted_lab.py verify-packages
python3 ai_assisted_lab.py suite --phase baseline
python3 ai_assisted_lab.py suite --phase fault
python3 ai_assisted_lab.py suite --phase repair
```

预期 `0 / 0 / 1 / 0`。单页的精确命令、退出码和报告见 `page-manifests/`。故障阶段产生的 `FAIL`、`BLOCKED` 和 `UNKNOWN` 是应被保存的负控制，不是可以重试成空成功的格式问题。

证据边界：本实验仅证明确定性 fixture 的工件链和状态传播可复现。没有真实模型、真实仓库、真实支付系统、生产 Trace、从业者签字或学习效果证据。
