# 逐命题深研与代码可执行性审计

> **Superseded historical audit（2026-08-11）**：本文记录 33 页修复前的 5/28 快照，用于解释缺陷来源，不再代表当前课程。当前结论请读取 `06-最终课程验收.md`、`research/executability-audit.json` 和 `research/editorial-review-2026-08-11-final.json`；新鲜结果为 85/85 executability PASS、85/85 editorial PASS。

## 当前结论

当前站点不应继续扩页，也不应把已有 33 页描述成可用课程。

问题不是“代码少”，而是页面把提示词、公式、伪代码、数据样例、架构字符图和真实命令都塞进同一种深色代码框，并统一提供“复制”按钮。用户无法判断它是解释、配置、提示词还是可以运行的命令。部分真实命令还引用了未发布目录，复制后必然失败。

本次静态审计只回答“页面交付路径是否自洽”，不代表专业内容已经通过。结果：

- 公开页面：33 页；
- 技术代码框：49 个；
- 基础执行路径通过：5 页；
- 基础执行路径失败：28 页；
- 代码框类型：14 个命令、6 个提示词、9 个伪代码、9 个公式、7 个 JSON、4 个字符图；
- 引用未发布 `courses/` 目录的命令：5 个；
- 缺少工作目录的相对命令：5 个；
- 没有作为版本化文件交付的提示词：6 个。

“通过”的 5 页只表示命令、压缩包和相对路径能组成一条候选执行路径，不表示内容深度、工具选型、真实集成或生产方案通过。

## 一个可复现的问题：TD-P02 需求契约

页面显示：

```bash
python3 pipeline.py reset
python3 pipeline.py validate-contract
python3 pipeline.py inject-unsupported-rule
python3 pipeline.py validate-contract
```

但页面没有先让用户下载实验包、解压，也没有声明工作目录。直接从站点工程或公开资料根目录运行时，Python 返回找不到 `pipeline.py`，退出码为 2。

实验包里的脚本实际位于：

```text
requirements-to-evidence/pipeline.py
```

正确的教学动作至少应从“下载 `requirements-to-evidence.zip` → 解压 → 进入 `requirements-to-evidence` → 运行基线 → 注入无来源规则 → 观察 BLOCKED → 重置/修复”开始，并展示每一步 stdout、退出码和生成文件。

更深一层的问题是：现有实验只验证离线规则门禁，没有真正演示“大模型怎样读取 PRD 与技术方案并生成契约”。因此它最多证明“校验器能拦截无来源字段”，不能证明 AI 需求解析流程可用。改造后必须把两部分拆开：

1. 模型提取层：版本化 Prompt、输入文档、JSON Schema、模型与参数 Manifest、原始输出、拒答/截断处理；
2. 证据门禁层：Schema、source_ref、冲突、权限、金额、状态、副作用和人工审批。

离线 fixture 可以证明第二层；有 API 凭证的集成实验才能证明第一层。两种证据状态不能混写。

## 按课程线划分的当前问题

### 职业与需求生命周期：TD-F01、TD-P01～TD-P08

- 提示词没有独立文件、输入夹具、输出 Schema 和评测样例；
- TD-P01、TD-P08 使用未发布的 `courses/...` 路径；
- TD-P02、TD-P05、TD-P07 命令依赖隐含工作目录；
- TD-P08 虽标记 `fixture-tested`，页面上的直接执行路径仍失败；
- 同一离线流水线被八页复用，但每一页没有独立证明自己的专业命题。

### 传统测试专项：TD-PS01～TD-PS12

- 大多数代码框是接口步骤、Playwright 片段、Android/iOS 伪 API、公式或 YAML 草图；
- 页面链接了一个共享 Python 模拟器，但没有证明展示片段就是该脚本的真实接口；
- 没有对应框架工程、依赖文件、设备/浏览器环境、真实命令、失败包和修复复跑；
- TD-PS12 是项目页，却没有任何可执行步骤。

### 质量平台：TD-QP01～TD-QP04

- 四页具备“下载压缩包 → 解压 → 进入目录 → 运行脚本”的基础路径；
- 但当前只是 Jira、GitLab、Kubernetes 和事件总线的离线 fixture，不是实际平台集成；
- 仍需分别补 OAuth/Webhook/API、权限、幂等、回读校验、清理、回滚和真实集成收据，才能升级证据状态。

### Agent 性能与稳定性：TD-AP01～TD-AP08

- 多数代码框是公式、Trace 字符图、YAML 草图或伪配置；
- TD-AP06 三条命令全部指向未发布 `courses/...` 目录；
- 当前 Python 实验可以证明一个合成重试风暴，但不能证明真实 Agent、模型端点、工具依赖和观测后端的容量结论；
- 工作负载、阶段延迟、质量门禁、成本、限流、重试、状态和副作用需要各自定义采集点、单位、分位数、阈值方法和负责人。

## 新的逐命题生产流程

每个公开命题必须拥有独立目录：

```text
research/topics/<topic-id>/
├── research-brief.md
├── source-pack.csv
├── research-runs.json
├── evidence-synthesis.md
├── engineering-blueprint.md
├── manuscript.md
├── comparison.md
├── lab-manifest.json
└── validation.md
```

每个工程命题至少需要：10 个已打开来源、5 条证据线、5 个独立来源家族、4 种来源类型；至少两次独立研究，再由不同角色比较分歧。来源必须同时覆盖专业基线、AI 一手资料、实现/仓库、实践失败或 issue、竞品课程。数量达标但与命题无关仍然失败。

`lab-manifest.json` 负责把页面与真实交付绑定：工作目录、必要文件、命令、预期退出码、预期产物、基线、故障注入、修复和证据边界。校验器逐个解析路径；只有作者目录里存在、公开包里不存在的文件，一律阻断发布。

## 代码框的新规则

后续页面不再使用一个模糊的 `code` 字段，必须明确类型：

- `command`：从声明工作目录可直接运行；
- `source-file`：来自已链接仓库文件的真实片段；
- `config`：有效格式，并说明谁读取它；
- `prompt`：有版本化文件、固定输入、输出 Schema、评测集和模型 Manifest；
- `formula`：解释变量、单位、维度、聚合和算例；
- `diagram`：只用于解释架构或时序；
- `pseudocode`：明确标记“不可运行”，并链接真实实现，否则删除。

只有经过校验的 `command`、`source-file`、`config` 和完整打包的 `prompt` 可以显示“复制使用”。公式、图和伪代码不再伪装成可执行代码。

## 第一批深度研究

第一批只处理四个代表命题：

- TD-F01：职业现实与 AI 重构；
- TD-P02：PRD/技术方案到可追溯需求契约；
- TD-PS01：AI 时代的 API 自动化；
- TD-AP01：Agent 任务级压测与稳定性。

四个命题分别独立检索。第一批通过后，先重写 TD-P02 的研究包、页面和实验，再用同一门禁决定是否进入下一批。未通过的页面保留在内部课程目录，不继续发布。
