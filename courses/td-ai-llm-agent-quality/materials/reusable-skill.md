# Reusable skill：Agent 质量门禁

先声明 system under test、业务决定、风险切片、版本锁、Oracle、权限和 stop state；再让模型生成候选 case。用模型外 policy gate 检查单变量、人工校准、三层 Oracle、最小 scope、幂等和循环预算。每个 mutation 必须改变专业决定并稳定 exit 1；repair 只能修实现或适配层，不能删 Oracle、改 expected、放宽权限或偷增预算。把 fixture、live、practitioner、production 证据分栏记录。
