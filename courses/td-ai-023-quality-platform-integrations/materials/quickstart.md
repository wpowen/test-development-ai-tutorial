# 复现 0/1/0

进入 `lab/` 后执行 baseline、stale_sha mutation、repair 和 unittest。baseline/repair 为 0，mutation 为预期 1；打开报告查看 `failed_oracle_ids`、SHA、JUnit、namespace 和审计 hash。运行环境只需要 Python 3 标准库，不使用网络或密钥。
