# TD-F01 职业入口材料包

本包把“测试开发是什么”变成可运行的入场能力检查。它不调用模型，不连接公司系统，也不作发布决定。

运行完整红绿修复循环：

```bash
python3 profession_self_check.py cycle --report reports/TD-F01-cycle.json
```

预期：baseline=0、fault=1、repair=0，cycle 总体退出码为 0。报告只能证明确定性 fixture 的边界检查已生效；不能证明从业者评审、真实集成、线上运行或发布成熟度。
