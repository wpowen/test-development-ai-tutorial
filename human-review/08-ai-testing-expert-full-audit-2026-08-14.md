# AI 测试开发专家全文档审计报告（2026-08-14）

## 0. 元信息与范围

- 审计对象：`outputs/test-development-ai-v2` 当前课程的全部文档/内容源/验证器，重点是 `methodology/`、`methodology/glossary-*.json`、`methodology/dimensions/_sources/*.json`、`site/content/modules/*.ts`、`courses/td-ai-agent-architecture-system/learner-materials/`。
- 审计角色：以 AI 测试开发专家视角，对内容正确性、统计口径、状态语义、门禁一致性、职业边界、可执行性、证据成熟度做多通道排查。
- 结论边界：这是本地审查/修改任务。**未发布、未部署、未升级任何成熟度**；所有高阶成熟度（真实模型、集成、从业者、学员、生产）维持原 `NOT_RUN`/`Unknown`。

## 1. 执行摘要

当前课程在“结构完整性 + 确定性 fixture 可复现性”上做得扎实：验证器基线一致通过（117 canonical topics、103 public pages、13 个公共模块、4 个内部未完成命题；deep-source 四段校验、catalog 校验、content 校验、material 闭包校验全部 PASS）。

但以“学员会照着文档做真实 AI 测试/发布决策”为验收标准，存在三类系统性问题：

1. **硬编码快照漂移**：`methodology/` 多处仍写“102 页”，而 canonical 现状是 103 公共页（`docs/PROJECT_STATUS.md` 已明确旧 102 快照被推翻）。这不是数字笔误，而是文档自身违背了项目“以 canonical manifest 为准、不得硬编码数量”的规则。
2. **统计与评测可信度表述有客观错误**：Cohen’s κ 取值范围写错、用“区间是否重叠”当回归判定、“judge 不可能比人更一致”被自有夹具输出直接反证、pass@k/pass^k 公式隐式同质独立假设未声明、样本量与 CI 口径混淆等。
3. **状态/门禁语义与实现混维**：`UNKNOWN` 阻断语义自相矛盾、Oracle 层 L1–L5 与根因层 L1–L5 复用命名、RACI 单一责任不表达“不可自动接管”、`result_status`/`gate_status`/`maturity`/`record_lifecycle` 混维、EVIDENCE-INSUFFICIENT 可被第三段签字绕过等。

本报告分领域给出高/中/低问题，明确标注 Evidence / Inference / Unknown；并记录本次已落地的一批最小、可复现修复及重新验证证据。

## 2. 审计方法与多渠道证据

- **通道 1｜基线验证器实跑**：`validate-deep-sources.py`、`validate-course-catalog.mjs`、`site/scripts/validate-content.ts`、`site/scripts/validate-material-archives.py`。
- **通道 2｜逐份精读**：`methodology/00–14 + README + prompt-design-contract` 全文，`glossary-core/deep.json`，D0–D7 相关 source TS 与 learner 文档。
- **通道 3｜五路独立 critic 子代理**：生命周期/门禁/状态语义、度量/统计/Benchmark、Agent 架构、RAG/LLM/安全、职业演进/专业化/术语。结论以“不可互相引用”的方式分别生成后汇总。
- **通道 4｜运行时反证**：实际运行 `agent_reliability_lab.py judge --fault none`，得到 `kappa_human_human=0.70`、`kappa_judge_human=0.9128`，用于推翻文档中的绝对化断言。
- **通道 5｜canonical 源交叉核对**：`research/catalog-manifest.json`、`tutorial/tutorial-site.json`、`site/content/modules/agent-architecture-deep.ts`、`docs/PROJECT_STATUS.md` 相互印证数量与命名。

## 3. 硬事实交叉核对（Evidence）

以下为本次直接读出的运行时/源文件事实，不是子代理转述：

| 项目 | 实测值 | 说明 |
| --- | --- | --- |
| 公共学习页 | **103** | `tutorial/tutorial-site.json` pages=103；`catalog-manifest.json` public=true 103 条 |
| 课程模块 | **13** | TD-M00..TD-M12 |
| catalog 全部命题 | 107 | 103 公共页 + 4 个内部未完成命题（TD-S01..S04，`outlined`） |
| “14 个模块” | **14 个 deep-source ENFORCED 名单** | 指 `validate-deep-sources.py` 的 `ENFORCED` 集合，不是课程模块数 |
| D0–D7 canonical 名 | D0 评估可信 / D1 单体能力 / D2 编排协作 / D3 交互协同 / D4 鲁棒可靠 / D5 安全对抗 / D6 效率经济 / D7 业务治理 | 来自 `agent-architecture-deep.ts` |
| judge 夹具 κ | `kappa_human_human=0.70`；`kappa_judge_human=0.9128`（judge 只在 26/30 共识样本上算） | 直接反证“judge 不可能比人更一致” |

结论：`methodology/` 中“102 页”必须改为“103 页”；“13 模块”本身正确；“14 个模块已强制”是另一命名空间，不能与课程模块混写。

## 4. 分领域发现

严重度定义：高=会误导学员或把 fixture 绿灯读成真实安全/质量证据；中=口径不一致或统计不严谨；低=表述/组织问题。每条尽量给出 Evidence（E）/ Inference（I）/ Unknown（U）。

### 4.1 生命周期 / 门禁 / 状态语义

- [高，E] `methodology/00-完整测试方案总览.md`、`README.md`、`09`、`13` 硬编码“102 页”，与 canonical 103 页冲突。本次已修。
- [高，E] 一周起步路线跳过 S3 直接进 S4，违反 S3→S4 依赖。需按阶段重排并补依赖说明。
- [高，E] `UNKNOWN` 同时被描述为“阻断下游”和“允许进入 S2”，传播语义矛盾。需统一为单一状态机：缺证据即停在该层并升级 owner。
- [高，E] 文档称唯一状态语义，但实际 JSON 出现未定义的 `ACCEPTED`、小写 `superseded`，且 `result_status`/`gate_status`/`maturity`/`record_lifecycle` 混维。需收敛为一份状态枚举 + 映射表。
- [高，I] Oracle 六层“独立性排序”与“blocker 放行权”混在一起；正文/模板/校验器三处不一致。
- [高，I] `0/1/0` 被当作所有有效执行的普遍定义，实际它只应是 harness validation 口径。
- [中，E] Oracle 层 `L1–L5` 与根因层 `L1–L5` 复用同一命名，且漏掉 L6/人工层。
- [中，I] “四个人工交互点，其余全自动”与 RACI 实际依赖不一致，会漏掉人类决策依赖。
- [中，I] Flaky 自动 quarantine 与 fail-closed 原则冲突；自动隔离会掩盖证据，应改为“自动标记 + 具名 owner 决定处置”。

### 4.2 度量 / 统计 / Benchmark

- [高，E] `pass@k = 1-(1-p)^k`、`pass^k = p^k` 隐含“同质独立任务”假设；任务异质/有限样本下应逐任务估计再聚合并给 CI。
- [高，E] `glossary-core.json` 把 Cohen’s κ 写成“取值 0 到 1”；κ 可为负。本次已修为 `[-1,1]`。
- [高，E] 多处用“两个 CI 是否重叠”判显著性；统计上不正确，尤其不适用于配对/聚类/非劣效。`glossary-core.json` 本次已对齐深度定义。
- [高，E] `quality-system.json` 要求 20 样本 95% CI 下界 ≥95%，数学上不可通过；应改为 MDE/power 设计。
- [高，I] “污染率=0”与“污染只能降低概率、不能证明不存在”自相矛盾；canary 泄露被过度解释为训练污染。
- [中，I] Judge 只要求 κ 和校准日期，缺校准、偏置、金标、元评估字段。
- [中，E] Goodput 在 ai-serving 与 agent 文件中分子/单位不一致。
- [中，I] 样本量阈值 30/50/100/500 无统计依据，需以任务级 power 分析推导。

### 4.3 Agent 架构 / D0–D7 / 评测可信

- [高，E] `docs/02-d0-evaluation-trust.md` 写“3 名标注员”，但夹具 `human_labels` 只有 2 名标注员；本次已修口径并标注夹具局限。
- [高，E] “judge 不可能比人与人之间更一致”被自有夹具 `0.9128 > 0.70` 反证；本次已在 learner 文档与 `agent-architecture-deep.ts` 两处修掉绝对化表述。
- [高，E] `methodology/07` 的 D1–D6 名称与 canonical `agent-architecture-deep.ts` 不一致；本次已归一。
- [高，I] D0 失败被说成“后面 32 维所有数字不可信”；D7 硬规则、D5 授权层、D6 延迟等确定性 Oracle 不依赖 Judge。应给每维标注 `judge-dependent` 或 `deterministic`，只冻结前者。
- [中，I] 36 维之间存在重复（如记忆、越权、不可逆动作、延迟各出现多次），但没有唯一测试边界；需为每维补“唯一问题/测试对象/Oracle/输入/工件/owner”。
- [中，I] “30–60 天内质量必然退化”是样本观察被过度推广；应改为“某观察样本出现退化”，生产退化概率/窗口/因果为 Unknown。

### 4.4 RAG / LLM / 安全

- [高，I] RAG 错答被简化成“两种可能”，实际链路含 query/filter/retrieve/rerank/context/generation/citation 多节点。
- [高，I] `nDCG` 被提到但没有 qrels/公式/分级相关性，学员无法复现。
- [高，E] 拒答阈值 `≥98%` 与 `<95% 阻断` 互相矛盾。
- [高，I] 间接注入“到达工具层即 blocker”错误；应区分模型提议、策略拒绝、真实副作用三层，只有真实副作用才按 blocker 处置。
- [高，I] 污染检查不覆盖预训练污染、公开 benchmark 暴露、合成数据回灌、prompt/rubric 泄漏。
- [中，E] Workflow 标成“确定性，不需要重复运行”，与幂等/恢复测试要求冲突。

### 4.5 职业演进 / 专业化 / 术语

- [高，I] RACI 只有唯一 A/R/C/I，不表达共同责任、不可自动接管和人工最终责任；需增加“责任状态 × 自动化权限 × 人工门禁 × 证据工件”矩阵。
- [高，I] 四态“跟做/设计/裁决/治理”是决策层级，不是 AI 场景下的主责/共同责任/接管状态。
- [高，I] 职业路径有 AI Evaluation/开发者生产力，但 RACI 无 AI 系统 owner、AI/ML owner、Evaluation owner。
- [高，I] `methodology/10-工具选型与成本.md` 明确“不推荐具体产品”，学员无法做可复现、可审计选型；建议补工具注册表（名称/版本/主源/许可/离线路径/验证日期）。
- [中，E] 专业化目录混用平台、测试方法、质量属性、数据生命周期、治理领域多分类轴；建议拆成四个正交维度再矩阵组合。
- [中，I] Web 只作为 UI 表一行，Android/iOS 却是独立专业化，平台覆盖口径不对称。
- [中，I] 混沌工程、CI/CD 缺独立专业化，只有一次故障注入/供应链门禁练习。
- [高，E] `glossary-core.json` Cohen’s κ 取值范围错（本次已修）。
- [中，E] `glossary-core.json` CI 用“区间是否重叠”判回归（本次已修）。
- [中，I] 证据成熟度等级在 core/deep 两个术语表数量与顺序不一致。
- [中，I] Oracle 核心定义允许“模型打分”但未要求独立于被测模型；应把“独立 Oracle、可返回 UNKNOWN/BLOCKED、保留失败理由”写入核心定义。

## 5. 本次已落地修改

### 5.1 修改文件与内容

- `methodology/00-完整测试方案总览.md`：3 处“102 页”→103 页。
- `methodology/README.md`：3 处“102 页”→103 页。
- `methodology/09-组织角色与能力.md`：培训路径标题“102 页”→103 页。
- `methodology/13-逐页扩写规范.md`：规范目标“102”→103；对 2026-08-12 历史快照补注“当前目录为 103 页”；门槛描述“102”→103。
- `methodology/07-AI系统专项方案.md`：D1–D6 名称对齐 canonical（单体能力/编排协作/交互协同/鲁棒可靠/安全对抗/效率经济）。
- `methodology/glossary-core.json`：Cohen’s κ 取值范围修正为 `[-1,1]`；CI 回归判定改为配对差值/聚类结构/效应量，不再用“区间是否重叠”作唯一判据。
- `courses/td-ai-agent-architecture-system/learner-materials/docs/02-d0-evaluation-trust.md`：标注员口径改为“≥2（夹具 2，生产建议 3+）”；删除“judge 不可能比人更一致”绝对上限，改为报告口径/样本量/CI 并与仲裁金标对照。
- `site/content/modules/agent-architecture-deep.ts`：同一处 caption 去掉绝对上限表述。
- 页数口径连带归一：`site/content/modules/career-evolution-deep.ts`、`methodology/dimensions/_sources/career-evolution.json`、`methodology/dimensions/career-evolution/TD-C01.md`、`research/topics/TD-C01/projection-ledger.json` 中的“读完 102 页”→103 页。

### 5.2 投影同步

- `python3 scripts/sync-agent-architecture-materials.py`：205 文件同步到 public + ZIP。
- `node site/scripts/export-static.ts`：103 页重新导出到 `site/dist-github-pages/index.html`。
- `node scripts/sync-tutorial-package.mjs`：`tutorial/tutorial-site.json` 等 5 个产物同步（103 页，源/材料哈希已记录）。

## 6. 重新验证证据

```text
validate-deep-sources.py       → 可落地性校验通过：14 个模块已强制（103 页）。
validate-course-catalog.mjs    → PASS：117 canonical topics; 103 public pages; 153 alias; 0 uncovered high-risk gaps; 117 content gates blocked。
site validate-content.ts       → Tutorial content valid: 103 delivered pages public; 4 incomplete topics kept internal。
site validate-material-archives.py → Learner materials valid: canonical/public + ZIP hash closure; 16 bundles; 6 red/green labs。
agent_reliability_lab.py judge → PASS（kappa_human_human=0.70; kappa_judge_human=0.9128; consensus=26/30）。
```

`glossary-core.json` 已通过 `json.load` 校验。

## 7. 未修复项与下一步优先级

以下问题需要设计决策或跨文件协调，本次未擅自改动，建议按序处理：

1. **状态机统一**（P0）：收敛 `result_status/gate_status/maturity/record_lifecycle`，补 `ACCEPTED` 定义与大小写归一，把 `UNKNOWN` 单一化为“缺证据即停 + 升级 owner”。
2. **Oracle 分层与独立性**（P0）：核心定义补“独立 Oracle / UNKNOWN / BLOCKED / 失败理由”，拆开独立性排序与 blocker 放行权，修 L1–L5 命名冲突。
3. **统计口径**（P0）：重写 `pass@k`/`pass^k` 为任务级估计 + CI；`quality-system.json` 的 20 样本 95% 下界 ≥95% 改为 MDE/power；修拒答阈值矛盾；Goodput 单位统一。
4. **四证据环/三段门禁**（P1）：EVIDENCE-INSUFFICIENT 不得被第三段签字升级为可发布；补每环准入/样本/CI/回滚/退出条件。
5. **D0–D7 维度去重**（P1）：为每维补唯一测试边界，标注 `judge-dependent` 与 `deterministic`。
6. **专业化目录重构**（P1）：按平台/质量属性/测试方法/治理四轴重组；补 Web、Chaos、CI/CD 覆盖口径。
7. **工具选型注册表**（P1）：给名称/版本/主源/许可/离线替代/验证日期。
8. **RACI→责任状态矩阵**（P1）：表达主责、共同责任、不可自动接管、人工门禁。

上述 P0/P1 修复前，不得把课程成熟度从 `PASS-FIXTURE` 升级，也不得发布。

## 8. 成熟度与门禁状态（未升级）

- 内容结构门禁：PASS（本地 fixture）。
- 高阶成熟度：`NOT_RUN` / `Unknown`（真实模型、企业集成、具名从业者、目标学员、生产效果）。
- 发布状态：**未发布、未部署**。本次仅修改 canonical source 并重建本地投影，未执行任何 publication lane。
