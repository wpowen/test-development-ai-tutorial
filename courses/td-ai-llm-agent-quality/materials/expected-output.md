# Expected output

baseline 与 repair 报告应为 `verdict=PASS`、`expected_exit_code=0`，并记录五项锁、三次重复和 `not_run`。fault 报告应为 `verdict=FAIL`、`expected_exit_code=1`、`failed_oracle_ids=["SINGLE-VARIABLE"]`，因为候选同时修改了 model 与 retriever。结果只证明离线合同检测力，不证明模型、Browser Agent、工具后端或生产流量。
