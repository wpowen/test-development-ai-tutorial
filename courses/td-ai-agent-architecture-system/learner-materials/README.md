# Agent Architecture System

11-page D0-D7 learning chain. Run each manifest from `materials/agent-architecture-system` with the exact command. Reports are deterministic fixture evidence only; live model, integration, practitioner and learner validation remain NOT_RUN.

## 来源专属视觉入口

`source-visual-manifest.json` 将用户提供的 Agent 架构材料分别投影成四种不可互换的学习图：

- `visuals/AG-DIM-ARCHITECTURE.svg`：系统边界、D0-D7、护栏、决定与失败回灌；
- `visuals/AG-DIM-FOUR-RINGS.svg`：四个证据环各自的 entry、exit、block、owner 与 rollback；
- `visuals/AG-DIM-GATE.svg`：硬政策、统计证据与具名风险接受三段门禁；
- `visuals/AG-DIM-36.svg`：D0-D7 共 36 维覆盖地图。

`visuals/agent-visual-source.json` 是可编辑语义源。来源中的分钟、天数、采样比例和固定阈值均已改为 Metric Card 参数；没有场景 population、uncertainty 与 owner 时保持 Unknown。当前课程只运行离线 fixture，受控沙箱、影子/灰度和在线持续评估均 `NOT_RUN`。
