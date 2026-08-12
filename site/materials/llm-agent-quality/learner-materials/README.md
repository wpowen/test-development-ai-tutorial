# LLM Judge 与 Agent/Workflow 质量离线实验

本包只使用 Python 标准库和合成状态，不调用模型、浏览器、工具后端或队列。每页命令都执行 baseline→fault→repair，并要求观察到 `0/1/0`。安全页 TD-T16、TD-T17 在任何可写副作用前执行身份、权限、tenant 和 human gate；模型/Judge/healer 不可批准自己的输出。

## 页面命令

- TD-T13 版本 A/B 可比性: `python3 scripts/agent_quality_lab.py --topic TD-T13 --phase cycle --report-dir reports/td-t13`
- TD-T14 Judge 校准与反例: `python3 scripts/agent_quality_lab.py --topic TD-T14 --phase cycle --report-dir reports/td-t14`
- TD-T15 Outcome/Step/Trajectory 三层 Oracle: `python3 scripts/agent_quality_lab.py --topic TD-T15 --phase cycle --report-dir reports/td-t15`
- TD-T16 工具选择、参数、身份与权限: `python3 scripts/agent_quality_lab.py --topic TD-T16 --phase cycle --report-dir reports/td-t16`
- TD-T17 Prompt Injection、泄露与 Excessive Agency: `python3 scripts/agent_quality_lab.py --topic TD-T17 --phase cycle --report-dir reports/td-t17`
- TD-T18 Browser Agent 证据链: `python3 scripts/agent_quality_lab.py --topic TD-T18 --phase cycle --report-dir reports/td-t18`
- TD-T19 自愈反作弊: `python3 scripts/agent_quality_lab.py --topic TD-T19 --phase cycle --report-dir reports/td-t19`
- TD-W01 Agent/Worker/Workflow 边界: `python3 scripts/agent_quality_lab.py --topic TD-W01 --phase cycle --report-dir reports/td-w01`
- TD-W02 状态、循环、重试、Handoff 与终止: `python3 scripts/agent_quality_lab.py --topic TD-W02 --phase cycle --report-dir reports/td-w02`
- TD-W03 单/多 Agent 公平实验: `python3 scripts/agent_quality_lab.py --topic TD-W03 --phase cycle --report-dir reports/td-w03`

## 证据边界

Prompt 包可复用但 provider/model 均为 NOT_RUN。报告证明离线门禁能红绿切换，不证明真实模型、浏览器、工具、队列、组织审批或生产效果。
