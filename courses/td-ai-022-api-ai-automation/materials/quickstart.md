# 15分钟复现路径

进入 `learner-materials/` 根目录后依次运行：

```bash
python3 scripts/api_automation.py baseline --report reports/baseline.json
python3 scripts/api_automation.py mutation --report reports/mutation.json; test $? -eq 1
python3 scripts/api_automation.py repair --report reports/repair.json
python3 -m unittest discover -s tests -v
```

预期原始退出码依次为 `0 / 1 / 0`。打开三个报告，先看 `status`、`input_hashes`、`mutation_id`，再看失败 case 的 `actual` 和 `issues`。不要把 mutation 的非零退出码改成成功；它正是检测力证据。外部 Schemathesis、Pact、k6、GitLab CI 仍是 `static-reviewed/NOT_RUN`。
