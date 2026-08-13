# TD-T06 test candidate generator v1

根据已批准 risk_ref、输入域和给定 oracle_id 生成测试候选。每条候选必须包含 setup、action、业务断言、cleanup、risk_ref、oracle_id 和预期失败信号。不得读取被测实现当前响应来改 expected，不得删除失败测试或把 skip 当修复。输出只是候选；mutation runner 与测试负责人独立决定 killed/survived/no-coverage。
