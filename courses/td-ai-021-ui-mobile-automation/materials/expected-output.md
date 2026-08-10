# 预期输出

| 阶段 | 退出码 | 关键字段 |
|---|---:|---|
| baseline | 0 | `status=PASS`, `missing_contracts=[]` |
| 删除稳定 locator/业务断言 | 1 | `status=FAIL`, 两个字段都在 `missing_contracts` |
| repair | 0 | `status=PASS`, `oracle_pass=true` |

`evidence/execution-evidence.json` 保存本次真实执行的命令、时间、stdout 摘要、退出码与限制。
