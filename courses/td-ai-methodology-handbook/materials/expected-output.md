# 期望输出

## 基线（`all`，退出码 0）

```text
[PASS] S1 依据冻结
[PASS] S2 需求契约
[PASS] S4 风险与策略
[PASS] S5 Oracle 设计
[PASS] S8 执行与证据
[PASS] S9 发布判断
[PASS] 工件闭包

== PASS == fault=none 门禁 7 项，问题 0 条
证据边界：确定性离线 fixture（L1 fixture-tested）；真实模型、企业集成、从业者评审与生产验证均 NOT_RUN。
```

## 五类故障（退出码 1）

每一类必须被**指定的那一道**门禁拦下，并给出具体状态词：

```text
--fault doc-conflict
[FAIL] S1 依据冻结
        - $.conflicts[0].escalated_to: 长度 0 < 最小 1
        - S1 BLOCKED：冲突 CONF-INJECTED 未指定升级责任人，下游生成必须停止

--fault unsupported-rule
[FAIL] S2 需求契约
        - S2 UNSUPPORTED_RULE：REQ-CANCEL-001 的 refund_timeout_hours 没有来源支持

--fault missing-oracle
[FAIL] S5 Oracle 设计
        - S5 BLOCKED：关键风险 R-001 没有 Oracle 设计记录

--fault expired-waiver
[FAIL] S9 发布判断
        - S9 BLOCKED：Waiver W-2026-0812-01 已于 2020-01-01 过期，发布必须阻断

--fault judge-self-approval
[FAIL] S5 Oracle 设计
        - S5：R-001 是 blocker，但只用了 ['L5']；语义层不得单独放行，必须含 L4 规则或 L6 人工
```

## 修复（`--fault none`，退出码 0）

输出与基线一致。

## 报告结构

```json
{
  "fault": "none",
  "verdict": "PASS",
  "gate_count": 7,
  "problem_count": 0,
  "gates": [{"gate": "S1 依据冻结", "verdict": "PASS", "problems": []}],
  "maturity": "fixture-tested",
  "not_run": ["model-integrated", "integration-tested", "practitioner-reviewed", "production-validated"]
}
```

## 怎么读这些输出

退出码本身就是结论：`0` 通过，`1` 门禁阻断，`2` 用法错误。门禁失败时永远指名**哪一条工件的哪一个字段**，而不是笼统的「校验不通过」——这一点是可归因的前提。

若某类故障返回了 `0`，说明门禁在这条规则上没有牙齿。这是课程本身的缺陷，请对照 `scripts/validate_handbook.py` 中对应的 `gate_*` 函数检查。
