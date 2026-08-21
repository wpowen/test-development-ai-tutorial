# Quickstart：先做一次可审计的 Agent 质量实验

进入 `learner-materials`，固定 TD-T13 的数据、Prompt、retriever、tool scope、Judge 与重复次数。依次运行 baseline、fault、repair，预期退出码为 `0 / 1 / 0`。打开三份 JSON，确认 fault 的 `failed_oracle_ids` 包含 `SINGLE-VARIABLE`，并检查每份报告保留 `maturity=fixture-tested`、`not_run` 和状态 hash。无需模型 Key；这不是线上 Agent 证明。
