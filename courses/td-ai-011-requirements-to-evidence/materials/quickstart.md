# 快速开始

进入 `lab/`，运行 `python3 pipeline.py reset`，再运行 `python3 pipeline.py all --report reports/baseline.json`。随后注入代码缺陷，预期退出 1；执行 `repair` 后再次运行，预期退出 0。最后注入文档冲突，确认 `all` 返回 2 且不生成下游测试。

环境只需要 Python 3 标准库，不需要账号或网络。报告位于 `lab/reports/`，测试包和证据包位于 `lab/artifacts/`。

如果目标是立即用于自己的需求评审或测试流程，先读 `lab/DIRECT-USE-GUIDE.md`，复制对应 `lab/page-prompts/<页面 ID>/prompt-v1.md`。替换方括号输入后人工检查 source_ref、Unknown、关键 Oracle 和 owner；Prompt 合同通过不代表真实模型输出已经验证。
