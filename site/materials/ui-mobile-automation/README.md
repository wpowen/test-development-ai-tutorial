# UI/移动端 Learner Materials

本目录可独立复制给学习者。只需要 Python 3 标准库，不需要 YAML/JSON 第三方解析包；YAML 文件由文本完整性检查验证，JSON 文件由 Python 标准库解析。

## 从本目录根目录运行

```bash
python3 scripts/ui_contract_lab.py validate

set +e
python3 scripts/ui_contract_lab.py baseline --report reports/baseline.json
b=$?
python3 scripts/ui_contract_lab.py mutation --report reports/mutation.json
m=$?
python3 scripts/ui_contract_lab.py repair --report reports/repair.json
r=$?
set -e
printf 'EXIT_SUMMARY baseline=%s mutation=%s repair=%s\n' "$b" "$m" "$r"
test "$b" -eq 0 && test "$m" -eq 1 && test "$r" -eq 0
```

预期：`baseline=0 mutation=1 repair=0`。mutation 会删除 `stable_locator` 与 `business_assertion`，所以退出码 1 是预期红灯；repair 从 canonical fixture 恢复后退出码 0。

## Learner materials

- 场景 fixtures：`fixtures/refund-approval.json`、`fixtures/android-receiving.yaml`、`fixtures/ios-reschedule.json`、`fixtures/return-trajectory.json`
- 配置：`configs/web-compatibility-matrix.yaml`、`configs/self-healing-policy.yaml`
- 指南：`guides/web-journey-sop.md`、`guides/a11y-visual-regression.md`、`guides/android-device-matrix.md`、`guides/ios-xcuitest-preflight.md`
- 独立脚本：`scripts/ui_contract_lab.py`

## 平台样例路径与证据状态

- Playwright：`../materials/examples/playwright/login.spec.ts`
- Maestro：`../materials/examples/maestro/login.yaml`
- Appium JavaScript：`../materials/examples/appium/login.js`
- Appium Python：`../materials/examples/appium/login.py`
- Appium 配置：`../materials/examples/appium/capabilities.json`
- Espresso Kotlin：`../materials/examples/espresso/LoginUiTest.kt`
- XCUITest Swift：`../materials/examples/xcuitest/LoginUITests.swift`

上述 Web/Android/iOS 工具链、浏览器、emulator、Simulator、真机和 AI/MCP 均为 `static-reviewed/NOT_RUN`；本目录的 `fixture-tested` 只证明标准库离线契约实验，不证明平台执行成功。
