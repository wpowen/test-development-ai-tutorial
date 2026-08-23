# 别再装错 Pi Agent：验证它能否发现你已有的 Codex Skill

状态：`PASS-STRUCTURE / NOT-LEARNER-TESTED / NOT-PRODUCTION-VALIDATED`

## 1. 命题雷达与选择

入选命题：别再装错 Pi Agent：它为什么看起来很小，却能读取你的 Codex Skills？

- 搜索窗口：2026-05-07 至 2026-08-23；易变信息按 2026-08-23 复核
- 已搜索渠道：community-friction；current-package-metadata；official-change；platform-supply；technical-evidence
- 身份/版本结论：当前官方项目是 Earendil Works 下的 Pi Agent Harness；官方仓库为 earendil-works/pi，npm 安装包为 @earendil-works/pi-coding-agent。2026-05-07 的 0.74.0 起从旧 badlogic/@mariozechner 命名迁移。
- 研究处置：APPROVE-AS-CREATOR-TRACK-EXPERIMENT；进入结构化脚本与录制准备，但保持 NOT-LIVE-TESTED

被拒绝或暂缓的候选：

- Pi Agent 五分钟完整安装教程：已有中文入门供给，差异化弱；对普通用户仍有终端和模型认证门槛
- Pi Agent 能做所有事情：需求过宽、不可验收且会掩盖第三方扩展的系统权限风险

## 2. 市场痛点

官方包名近期迁移，社区内容同时混用新旧名称；功能介绍又常把核心、Skill、Extension 和第三方 Package 混在一起，用户难以做低风险的第一步验证。

- 触发时刻：看到 Pi Agent 热点、功能清单或旧教程，准备安装或迁移工作流
- 可能损失：安装弃用包或照着旧文档操作；重复制作已有 Skill；给未知扩展过高权限；把发现能力误写成已验证执行能力
- 现有非 AI 做法：逐页查官方迁移公告、文档、仓库、npm 元数据，再人工对比本机 Skill 目录和配置。
- 现有摩擦：来源分散、命名变化快、能力分层术语多；但最终判断仍可以通过官方文档和实际只读输出核验。

## 3. 对应人群

- 主要受众：有终端基础、已积累 Codex/Claude Skills 的 AI 内容生产者和独立开发者
- 次要受众：想理解 Pi 能力分层、但暂不准备安装的 AI 工具观察者
- 观看者：在短视频、B站或知识库看到 Pi 热点的人
- 操作者：能在隔离测试目录运行命令的人
- 风险承担者：本机账号、文件与凭证所有者
- 最终决策者：决定是否安装、授权和迁移工作流的用户本人

## 4. 可复用 AI 能力

固定六步：`对象 → 主张 → 证据 → 来源 → 边界 → 行动`。

- 识别当前项目、包名、版本和能力声明
- 把能力拆为核心、Skill、Extension、Package、SDK/RPC
- 打开官方来源并生成迁移检查表
- 在无敏感数据的测试目录执行只读发现验证
- 记录成功、失败和未验证边界

AI 禁止做：

- 未经审查安装第三方扩展或 Package
- 在包含密钥或私有代码的目录直接试跑
- 把文档声明写成本机实测结果
- 把高 GitHub star 写成效果证明

## 5. 场景适配器

### 核验当前官方安装入口

- 触发：中文教程给出 @mariozechner/pi-coding-agent 或旧 badlogic 仓库
- 输入：一条安装命令、一个仓库链接或教程截图
- AI 任务：抽取包名、仓库、版本和日期，打开官方迁移公告与 latest 文档形成差异表
- 可检查产物：current-install-check.md：输入命令、当前官方命令、迁移日期、证据 URL、不能推断项
- 独立核验：逐字符对照 pi.dev latest quickstart 与官方迁移公告
- 失败：AI 只依据旧搜索摘要，继续推荐 @mariozechner scope
- Human Gate：用户确认来源域名、发布日期与命令，再决定是否安装

### 验证现有 Codex Skill 是否被发现

- 触发：用户已有 ~/.codex/skills/ai-small-experiment-producer，想知道能否复用
- 输入：一个公开可审查的 SKILL.md 和 Pi 官方 Skill 发现规则
- AI 任务：读取 Skill 的名称与描述，生成只读发现测试和预期输出；不执行 Skill 内脚本
- 可检查产物：skill-discovery-evidence.md：Skill 路径、Pi 输出、预期/实际对照、执行兼容性未验证声明
- 独立核验：用本机文件路径和 Pi 实际列出的 Skill 名称对照；保存终端原始输出
- 失败：Pi 能看到 Skill 名称，但脚本依赖 Codex 专有工具；内容却误写成‘完全兼容’
- Human Gate：只通过发现门禁；执行门禁需另建测试目录逐项验证依赖、工具与副作用

## 6. 教授内容

学习结果：学习者能用官方来源核验 Pi 当前身份，并在不执行未知代码的前提下完成一次 Codex Skill 发现验证。

1. **pain**：展示新旧包名同时存在，提出‘到底装哪个、现有 Skill 要不要重做’（证据：官方迁移公告与用户 discoverability issue）
2. **baseline**：演示人工逐页查迁移公告、latest 文档与本机 Skill 路径（证据：打开的 URL 和本机只读路径）
3. **demo**：让 AI 把旧教程命令拆成对象、主张、证据、来源、边界和行动，并生成发现测试（证据：结构化检查表）
4. **pause**：观众暂停，复制官方 current 包名和自己的 Skill 名称到实验卡（证据：已填写实验卡）
5. **verify**：对照 pi.dev latest、迁移公告、pi --version 和实际 Skill 列表（证据：官方页面与终端原始输出）
6. **failure**：展示 AI 沿用旧包名，或把 Skill 被发现误写成完全兼容（证据：红色失败卡和不成立的结论）
7. **repair**：增加来源日期、四级兼容性和禁止执行未知代码的约束（证据：修订后的提示卡）
8. **rerun**：用同一个 Skill 重新生成判定，只允许得到‘发现通过/执行未测’（证据：同输入红绿对照）
9. **transfer**：换一个 Claude Skill 或项目级 .pi/skills 路径，重复发现门禁（证据：第二个路径的独立对照表）
10. **human-gate**：由用户决定是否进入安装、执行和第三方 Package 审查；敏感目录与未知代码直接停止（证据：签字/勾选的权限检查表）

## 7. 视频命题

- 别再装错 Pi Agent：它为什么能看到你的 Codex Skills？
- Pi Agent 功能很多？先分清哪些是内置、哪些是外接
- 我把现有 Codex Skill 交给 Pi：第一步只验证这件事

Hook：网上两条 Pi 安装命令，只有一条是 2026 年 5 月迁移后的当前入口。更关键的是：Pi 说能读 Codex Skills，但‘能看到’绝不等于‘能完整运行’。

## 8. 口播稿

### 开场

如果你最近搜 Pi Agent，可能会看到两套安装名字。别急着复制命令。2026 年 5 月，Pi 的官方仓库和 npm 包已经迁到 Earendil Works。旧包还在，但当前入口已经变了。

### 能力分层

Pi 看起来功能很多，真正关键的不是背功能表，而是分清能力从哪来。它把核心保持得比较小，再通过 Extension、Skill、提示模板、主题和 Package 长出工作流。第三方扩展不是网页插件，它可能就是能操作你电脑的代码。

### 小实验

我们第一期只验证一件事：Pi 能不能发现我已经做好的 Codex Skill。官方文档确实写了 Codex 的 Skills 目录，但验证必须看本机原始输出，不能让 Pi 自己说‘我可以’就算通过。这里如果能列出 Skill 名称，只能写 PASS-DISCOVER。加载、执行、最终完成，都是后面的独立门禁。

### 失败与修复

最容易犯的两个错：照旧教程装旧 scope；或者看到 Skill 名字就说完全兼容。修复方法很简单：每条易变信息都带日期，兼容性拆成发现、加载、执行、完成四级，第三方代码先审查再运行。

### 收口

所以 Pi 适合讲成一个可验证的能力底座，不适合讲成万能 Agent。你下一步只要做三件事：核验当前包名，准备一个无敏感信息的测试目录，保存 Skill 发现的原始输出。执行兼容性，我们下一期再测。

## 9. 你需要操作什么

- `user-01-review-install` 录制当天重新打开 pi.dev latest 与迁移公告，确认当前安装命令和包名 → 带日期的官方页面录屏与 current-install-check.md（验收：域名、发布日期、包名逐字符一致；状态：READY）
- `user-02-sanitize` 建立空白测试目录，清理终端历史，隐藏用户名、API key、私有仓库和全局配置 → 可安全录屏的测试环境检查表（验收：隐私检查表所有项 PASS 后才录制；状态：READY）
- `user-03-install-run` 在确认授权后安装当前官方 Pi，记录 pi --version，并进行只读 Skill 发现测试 → 未经剪辑的终端原始录屏和 skill-discovery-evidence.md（验收：版本、Skill 名称、路径与原始输出可逐项对照；不执行 Skill 脚本；状态：READY）
- `user-04-host-record` 录制开场和边界收口；中段可只用屏幕录制与旁白 → 两段真人或稳定 IP 口播素材（验收：口播不出现‘完全兼容、万能、安全无风险’等越界表述；状态：READY）

## 10. 系统需要构建什么

- `build-01-experiment-card` 生成《Pi 当前入口 + Skill 四级兼容性实验卡》 → 可下载 PDF/Markdown 卡片（验收：包含来源日期、四级判定、隐私项、停止条件和证据粘贴位；状态：DONE）
- `build-02-visuals` 生成能力分层图、四级兼容性阶梯和新旧包名红绿卡 → 三张 9:16 原创图解和横屏变体（验收：技术文字与 fact sheet 一致；不生成伪 UI、不使用竞品品牌视觉；状态：READY）
- `build-03-edit-pack` 把真人口播、exact screen recording、图解和字幕装配成 90–150 秒样片 → 竖屏样片、字幕、封面与 QC 回执（验收：exact UI 来自实录；PASS-DISCOVER 与 NOT-EXECUTED 同屏；无密钥和私有路径；状态：BLOCKED）
- `build-04-course-module` 把样片扩展为 15–25 分钟实验课，加入失败、修复、重跑和第二 Skill 迁移 → 模块讲义、实验步骤、学员提交模板与评分表（验收：至少 5 名目标学员完成后才可升级为 LEARNER-TESTED；状态：BLOCKED）

下一步交接：

当前交给 validation lane：先完成安装授权后的本机只读发现实验。只有获得原始终端证据，才交给视频流水线生成 exact screen recording 和最终样片。

## 11. 物料

- `mat-host-hook` human-host-video：开场提出新旧包名冲突（真人拍摄或本人授权稳定 IP）
- `mat-old-new-package` generated-diagram：展示旧 @mariozechner 与新 @earendil-works scope（本地图片/排版流水线原创生成）
- `mat-official-screen` screen-recording：核验迁移公告与 latest 文档（录制当天打开官方页面）
- `mat-capability-layers` generated-diagram：区分核心、Skill、Extension、Package、SDK/RPC（原创四/五层架构图）
- `mat-terminal-discovery` screen-recording：展示本机 Skill 发现结果（隔离目录 exact terminal recording）
- `mat-compatibility-ladder` generated-diagram：展示 discover/load/execute/complete 四级（原创信息图）
- `mat-red-green` generated-comparison：展示旧结论与修复结论（依据同输入失败/修复结果排版）
- `mat-permission-check` download-card：安装和第三方代码前停止检查（依据官方安全边界原创制作）
- `mat-host-close` human-host-video：说清本轮未执行与下一期门禁（真人拍摄或本人授权稳定 IP）

## 12. 独立验收与停止动作

- 对照 pi.dev 当前安装文档和 2026-05-07 迁移公告核验包名
- 安装后用 pi --version、Skill 列表/路径输出和文件系统实际路径逐项对照，不用模型自述作证

停止条件：

- 安装命令仍指向旧 scope
- 要求粘贴密钥到公开录屏
- 第三方包来源或权限不明
- Skill 需要执行破坏性命令才能证明发现

升级动作：

- 停止安装或执行
- 回到官方 latest 文档
- 改用空白测试目录和无密钥模型
- 把结果标记为 BLOCKED-EVIDENCE 或 NOT-LIVE-TESTED

## 13. 复用规则

换热点时保留六步能力、Oracle 独立性、失败—修复—迁移和安全门禁；重新研究痛点、人群、规则、来源、fixture、脚本与物料。旧题材的结论不得继承。

## 14. 证据边界

本包只通过结构门禁。尚未运行真实模型 fixture、目标学习者测试或生产效果验证。
