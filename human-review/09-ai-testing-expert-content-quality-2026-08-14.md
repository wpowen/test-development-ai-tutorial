# AI 测试开发专家课程内容质量评估（2026-08-14）

## 0. 评估对象与结论边界

- 对象：`outputs/test-development-ai-v2` 的课程正文（103 个公共学习页、13 个模块）与配套可运行材料，重点评估「能否给学员足够帮助、是否足够详细、清晰、符合实际」。
- 方法：全量结构化字段扫描 + 第一学习路径（TD-F01 → TD-P01..P08，9 页）精读 + 学员端 `page-cycle` 实跑 + 门禁/测试实跑 + 与 `08-AI测试开发专家全文档审计-2026-08-14.md` 交叉引用。
- 结论边界：这是本地评估/修改任务。**未发布、未部署、未升级任何成熟度**。真实模型、企业集成、从业者、目标学员、生产效果仍为 `NOT_RUN` / `Unknown`。

## 1. 总体结论（先给结论）

正文层面的质量是「职业课程」级别：每页都有完整的学习闭环字段、判断表、架构图、常见错误和证据边界，**详细度和结构清晰度足够**。但本次实跑发现一个真实的「可运行闭环」缺陷：生命周期 8 页的「小白直接复制」Prompt Package 被 v2 任务提示词生成器覆盖，导致 `page-cycle` 门禁 BLOCKED、哈希漂移。该缺陷已定位根因并修复，相关门禁现已复绿。

因此：**正文内容本身够详细、清晰、诚实；但只有把配套材料的可运行闭环也闭合，才能说学员「照着文档能完整做下来」。**

## 2. 四维评估（Evidence / Inference / Unknown）

### 2.1 帮助度（能否给学员足够帮助）——强

Evidence：

- 103 页全部包含 `outcome`、`professional_relevance`、`plain_explanation`、`smallest_example`、`learner_action`、`expected_result`、`common_errors`、`completion_check`、`evidence_boundary`，缺页数为 0（直接解析 `tutorial/tutorial-site.json` 得到）。
- `learner_action` 是具体动作（如 TD-P08 的「保存 BLOCKED/FAIL/PASS 三种结果；新增一个未授权取消的 mutation；为一次接口契约变更生成 Impact Set」），不是「了解一下」这类空泛表述。
- 第一学习路径 8 页均有可运行材料：`pipeline.py`、各页 `page-prompts/TD-P0*/prompt-v1.md`、schema、eval、mutation，材料验证为 fixture-tested 或 static-reviewed。

### 2.2 详细度——足够，且不是大纲式

Evidence（中文字符口径，本次直接计算）：

| 指标 | median | min | max |
| --- | --- | --- | --- |
| `plain_explanation` 中文 | 70 | 42 | 255 |
| `teaching_blocks` 中文 | 3390 | 1947 | 4950 |
| `common_errors` 中文 | 73 | 30 | 162 |
| 每页判断表数量 | 10 | 8 | 17 |
| 每页 technical blocks | 3 | 2 | 6 |

Inference：L1 基础页（TD-P01/P03/P04、TD-FP01）内容最厚，L2–L3 进阶页相对薄但仍保持 1947+ 字教学块加表格，符合「基础手把手、进阶抓决策」的课程节奏。若学员目标只是快速过一遍，部分 L2–L3 页会显得密度偏高，但作为职业课程是合理深度。

### 2.3 清晰度——结构高度一致，但状态机术语仍有遗留混维

Evidence：

- 每页结构统一为 outcome → professional_relevance → plain_explanation → smallest_example → teaching_blocks（表格/图）→ learner_action → expected_result → common_errors → completion_check → evidence_boundary，几乎无例外。
- 表格普遍带「编号 / 测什么 / 关键指标 / 复测频率」或「失效形态 / 可核查数字 / 错误结论」等可执行口径，不是装饰性表格。

Inference：

- 08 审计报告遗留的 P0 状态机问题（`result_status/gate_status/maturity/record_lifecycle` 混维、`UNKNOWN` 传播语义不一致）会降低「门禁到底停不停」这一关键概念的清晰度。本次内容质量评估不重复修它，仍列为专业可信度的主要待办。

### 2.4 符合实际——诚实，但「直接复制」路径曾真实不可用

Evidence：

- `evidence_boundary` 逐页区分 fixture / live / practitioner / production，`receipt.json` 保持 `provider=none`、`model=offline-deterministic`、`model_status=NOT_RUN`、`raw_output_refs=[]`，没有把静态夹具吹成模型可用或生产证据。
- 负面：`DIRECT-USE-GUIDE.md` 承诺学员「打开 `page-prompts/<页面 ID>/prompt-v1.md`，复制『直接复制到 AI Agent』代码块」，但修复前 8 页的 `prompt-v1.md` 已被覆盖成七段式任务提示词，学员照做会拿不到承诺中的 one-shot 内容（见第 3 节，已修复）。

Unknown：课程正文是否真正帮助目标学员完成跨业务迁移，仍无 learner 观察证据；当前只有 deterministic fixture 与结构门禁证据，不能推断为从业者认可或生产效果。

## 3. 新发现：Prompt Package 双角色冲突（本次已修复）

### 3.1 事实链

Evidence：

1. 修复前运行学员端门禁：
   ```text
   python3 site/public/materials/requirements-to-evidence/pipeline.py page-cycle --page TD-P01
   → status=BLOCKED；缺失「## 能做什么」等 7 段；hash drift: prompt-v1.md / critic-v1.md
   ```
2. `node --test site/tests/lifecycle-direct-use-prompts.test.mjs` 修复前 6 项中 3 项失败（缺段 + 哈希漂移）。
3. 根因：`scripts/build-prompt-packages.py`（v2 七段式任务提示词生成器）按 `prompt-specs.json` 的 29 个主题全量生成，把 TD-P01..P08 也一并覆盖。这 8 页本来有另一套权威契约：
   - `prompt-v1.md` = 小白 one-shot（含 `## 能做什么`、`## 直接复制到 AI Agent` 等 7 段）；
   - `critic-v1.md` = v1.2.0 独立评审词；
   - 由 `build_direct_use_contracts.py`、`pipeline.py`、`DIRECT-USE-GUIDE.md`、`lifecycle-direct-use-prompts.test.mjs` 共同约束。
4. v2 脚本覆盖了 `prompt-v1.md`/`critic-v1.md`，却没有同步 `manifest.json` 的 `one_shot_copy_file` 与 `artifact_sha256`，于是同时产生「内容缺段」和「哈希漂移」两类失败。
5. 恢复源验证：`dist/publication-work/chatgpt-sites-source-materials-bottom/.../page-prompts/TD-P0*/` 中 8 页 `prompt-v1.md` + `critic-v1.md` 与 canonical lab `manifest.json` 钉住的哈希 **16/16 全部一致**，可作字节级恢复源。

### 3.2 修复决定

保留 8 页生命周期的「小白直接复制」契约，恢复 one-shot；把 v2 生成器从这 8 个主题中排除。理由：`DIRECT-USE-GUIDE.md`、命名测试与学员入口门禁是这 8 页的权威契约，v2 脚本未声明废弃该契约，属于覆盖事故，而不是有意的设计变更。

## 4. 本次已落地修改与复验

### 4.1 修改

- 恢复 8 页 `prompt-v1.md` + `critic-v1.md`（canonical lab 与 site/public 投影各 8 份）。
- 重建 `site/public/materials/requirements-to-evidence.zip`（173 个成员）。
- `scripts/build-prompt-packages.py`：新增 `DIRECT_USE_TOPICS = TD-P01..P08`，全量与单主题生成时跳过并提示改用 `build_direct_use_contracts.py`。
- `scripts/validate-prompt-packages.py`：同样识别这 8 个 direct-use 主题，不再把它们误报为「尚未改造」。

### 4.2 复验证据

```text
lifecycle-direct-use-prompts.test.mjs  → 6/6 PASS（修复前 3 fail）
page-cycle TD-P01 / TD-P08             → PASS：baseline PASS / fault FAIL / repair PASS / cycle PASS
validate-material-archives.py          → canonical/public + ZIP member/hash closure；16 bundles；6 red/green labs
test_pipeline.py                       → 4 tests OK
validate-prompt-packages.py            → 63 份七段契约 + 16 份 direct-use 单独校验
py_compile scripts/build-prompt-packages.py scripts/validate-prompt-packages.py → OK
```

## 5. 剩余风险与建议

- [低，E] `pipeline.py page-cycle --report /tmp/...` 这类「报告路径在包目录之外」的绝对路径会触发 `ValueError`；包内约定用法是相对 `reports/` 路径，本次按约定用法复验通过，未修改该 CLI 行为。
- [P0，承接 08 报告] 状态机统一、Oracle 分层与独立性、统计口径（pass@k/pass^k、20 样本 95% 下界、拒答阈值矛盾）仍未修；它们影响的是「专业可信度」，不阻塞本次内容可运行闭环修复，但在补齐前不得升级成熟度或发布。
- [Unknown] 本次修复证明的是「one-shot 路径恢复为可被门禁验证的静态/fixture 状态」，不是真实模型在学员业务上的执行效果；后者仍需真实运行与评测。
