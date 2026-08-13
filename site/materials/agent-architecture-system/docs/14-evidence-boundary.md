# 14 本维度的证据边界

## 14.1 成熟度声明

| 内容 | 等级 | 依据 |
| --- | --- | --- |
| 8 域 36 维划分、域间依赖、四环模型、三段门禁 | **Inference** | 由来源观测与工程原则综合推导 |
| pass@k / pass^k 的数学定义与差距 | **Evidence** | 公开基准与可验证的概率计算 |
| τ-bench / Claw-Eval / MCPTox 等具体数值 | **Evidence（来源观测）** | 公开基准结果，非本项目实测 |
| OWASP ASI01–ASI10 类别 | **Evidence** | 公开清单 |
| 法规时间线与罚则量级 | **Evidence（来源观测）** | 适用性判定属法务与合规 owner |
| 所有 κ、pass^k、ASR、延迟、成本阈值 | **占位** | 无出处，必须实测后重设 |
| 配套 lab 与 fixture | **L1 `fixture-tested`** | 0/1/0 红绿已验证 |
| 迁移路线图 | **Inference** | 未在任何真实组织落地验证 |

**整体等级：L1 `fixture-tested`。L2–L5 全部 `NOT_RUN`。**

## 14.2 未运行清单

```text
NOT_RUN  任何真实模型（provider=none, model=offline-deterministic）
NOT_RUN  任何真实 Agent 框架、MCP server、工具或浏览器
NOT_RUN  任何真实队列、交易后端或支付通道
NOT_RUN  环 3 影子模式（无真实流量）
NOT_RUN  环 4 在线持续评估（无生产接入）
NOT_RUN  真实 judge 的 κ 测量
NOT_RUN  真实攻击面的渗透测试
NOT_RUN  从业者盲评
NOT_RUN  目标学习者的掌握度与迁移成功率
NOT_RUN  任何生产环境的事故率或成本变化
```

## 14.3 数值使用纪律（再次强调）

本维度所有数字分两类，**不得混用**：

| 类别 | 标志 | 允许的用法 | 禁止的用法 |
| --- | --- | --- | --- |
| **来源观测** | 有出处（τ-bench、MCPTox、法规等） | 论证"这个问题真实存在"及其量级 | 当作你系统的预期值或验收阈值 |
| **结构占位** | 形如 `<阈值>`、κ ≥ 0.7、k=10 | 说明判据的形状 | 直接抄进门禁 |

阈值设定方法见 [方法论 08 章 8.6 节](https://local/methodology/08-度量体系.md)：先采集 3–5 个稳定周期的实测分布，取 p50/p95 作锚点，由风险 owner 决定方向与超阈动作，每季度复评。

## 14.4 引用本维度时的正确表述

✅ 可以说：

- "按 D0–D7 八域组织 Agent 测试"
- "承诺基于 `pass^k` 而非 `pass@k`，区间以任务为聚类单位"
- "本地夹具验证了三段式门禁的判定逻辑，真实系统未接入"
- "公开基准上 `pass@1` 与 `pass^8` 可相差 36 个百分点，因此两个口径必须分开报告"

❌ 不能说：

- "本架构可将生产事故降低 67%"（那是持续评估的来源观测，不是本架构的效果）
- "judge κ 应达到 0.7"（占位值，非行业标准）
- "Agent 攻击成功率通常超过 60%"（那是 MCPTox 在特定 server 集上的观测）
- "本方案已在交易系统验证"（`NOT_RUN`）
- "通过本课程即可交付生产级 Agent 测试"（fixture 不能升级为 production）

## 14.5 与主手册的一致性

本维度与 [方法论主手册](https://local/methodology/README.md) 共用同一套：

- 状态词语义（[14 章](https://local/methodology/14-证据边界与状态语义.md)）
- 成熟度阶梯（[01 章 1.4](https://local/methodology/01-公理与责任模型.md)）
- 决策权归属与 AI 授权边界（[01 章 1.2 / 1.3](https://local/methodology/01-公理与责任模型.md)）
- 阈值设定方法（[08 章 8.6](https://local/methodology/08-度量体系.md)）

冲突时以主手册为准；本维度只在 Agent 特有之处做加严，不做放宽。
