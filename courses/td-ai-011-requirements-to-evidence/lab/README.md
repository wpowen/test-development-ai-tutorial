# Requirements-to-Evidence 离线实验

该实验不调用模型，也不连接生产服务。它验证三件事：文档冲突会阻断下游生成；无来源规则会阻断契约；已知产品缺陷会让测试变红。

```bash
python3 pipeline.py reset
python3 pipeline.py all --report reports/baseline.json
python3 pipeline.py inject-code-defect
python3 pipeline.py all --report reports/mutation.json
python3 pipeline.py repair
python3 pipeline.py all --report reports/repair.json
```

预期退出码为 `0 / 1 / 0`。文档冲突实验预期退出码为 `2`：

```bash
python3 pipeline.py reset
python3 pipeline.py inject-doc-conflict
python3 pipeline.py all
```

`2` 表示 `BLOCKED`，不是产品测试失败。
