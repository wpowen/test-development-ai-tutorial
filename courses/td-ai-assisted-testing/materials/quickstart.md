# Quickstart

解压 `ai-assisted-testing.zip` 后进入 `ai-assisted-testing/`，先运行 `python3 ai_assisted_lab.py verify-packages`，再按 `page-manifests/<page-id>.json` 执行 baseline、fault、repair。不要把 fault 的非零退出码改写成成功；它是负控制证据。
