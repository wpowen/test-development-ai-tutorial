# 快速开始

默认离线路径不安装任何第三方依赖：

以下命令从课程包根目录执行，不依赖先切换到 `lab/`：

```bash
python3 lab/scripts/validate_package.py
python3 -m unittest discover -s lab/tests -v
python3 lab/scripts/reset_candidate.py
python3 lab/scripts/evaluate.py --report lab/reports/baseline.json       # 退出 0
python3 lab/scripts/inject_regression.py
python3 lab/scripts/evaluate.py --report lab/reports/mutation.json; test $? -eq 1  # 预期退出 1
python3 lab/scripts/reset_candidate.py
python3 lab/scripts/evaluate.py --report lab/reports/repair.json         # 退出 0
```

真实工具链是可选路径：Playwright 需要项目 lockfile 与浏览器；Maestro 需要 Java 17+ 和设备/浏览器；Appium 3 需要 Node 20.19.0+、独立 driver 与 Android/iOS 工具链；Espresso/XCUITest 需要各自原生工程。版本、设备、commit 和日志必须写进项目报告；本包未执行这些链路。
