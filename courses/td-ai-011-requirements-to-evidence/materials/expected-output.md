# 预期输出

三态实验依次返回：baseline `PASS/0`；mutation `FAIL/1`，失败测试为 `T-CANCEL-SHIPPED-01`；repair `PASS/0`。文档冲突实验返回 `BLOCKED/2`，并列出两个冲突 source_ref 和产品 owner。

报告必须包含 input hashes、selected tests、skip、retry、requirement/risk 映射、期望与实际值，以及 synthetic fixture 边界。
