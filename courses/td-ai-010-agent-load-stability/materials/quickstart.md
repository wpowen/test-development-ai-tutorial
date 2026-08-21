# 快速开始：8 个 Agent 性能与稳定性实验

## 1. 环境

只需 Python 3 标准库，无凭证、无网络、无外部副作用。进入课程目录后：

```bash
cd lab
python3 scripts/agent_performance_lab.py --manifest manifests/TD-AP01-lab.json --mode cycle
```

TD-AP01 可替换为 TD-AP02～TD-AP08。

## 2. 预期

每个页面先跑 baseline，再跑 fault，最后跑 repair。阶段退出码为 0/1/0，cycle 为 0；报告写入 `../evidence/<PAGE_ID>/`。fault 返回 1 是检测力证据。

## 3. 阅读

先看 `cycle-summary.json` 的 observed_exit_codes 和 fault_detected_by；再比较三份 summary；最后打开 fault/traces.jsonl 找具体任务。任何缺 manifest、缺输入、fault 未红、repair 未绿或边界缺失都标记 BLOCKED。

