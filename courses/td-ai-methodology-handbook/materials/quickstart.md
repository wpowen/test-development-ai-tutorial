# Quickstart：15 分钟跑通方法论门禁

## 0. 前提

只需要 Python 3（标准库）。无网络、无模型、无凭据。夹具不写入任何文件。

## 1. 看基线（应全绿）

```bash
cd learner-materials
python3 scripts/validate_handbook.py all
```

期望：七道门禁全部 `PASS`，退出码 `0`，末尾打印证据边界声明。

## 2. 注入一个已知缺陷（应变红）

```bash
python3 scripts/validate_handbook.py all --fault doc-conflict
```

期望：退出码 `1`，S1 门禁失败并输出「冲突 CONF-INJECTED 未指定升级责任人，下游生成必须停止」。

请注意它**没有**去判断哪份文档更合理——冲突的正确处置是阻断加升级，不是裁决。

## 3. 恢复（应重新变绿）

```bash
python3 scripts/validate_handbook.py all --fault none
```

期望：退出码 `0`。

`0 / 1 / 0` 这三段就是本方法论对「可运行」的定义。只有第 1 段的绿色不证明任何事。

## 4. 看看还能注入什么

```bash
python3 scripts/validate_handbook.py list-faults
python3 scripts/validate_handbook.py list-gates
```

逐个跑一遍五类故障，确认每一类都被**它应该被**拦下的那道门禁拦下，而不是被别的门禁顺带拦下。

## 5. 生成报告

```bash
python3 scripts/validate_handbook.py all --report reports/baseline.json
```

报告含 `fault`、`verdict`、逐门禁问题列表、`maturity` 与 `not_run` 四类未运行等级。

## 6. 换成你自己的工件

编辑 `examples/` 下的六份 JSON，把订单取消换成你的业务对象，再跑一次基线。第一次通常会红——那正是这套流程在告诉你哪一份工件还没填完。

## 下一步

按 `README.md` 的「模板使用顺序」表，从 `templates/01-test-strategy.md` 开始填你自己的项目。
