# Pi × Codex Skill 四级兼容性实验卡

状态：`READY-FOR-LIVE-EXPERIMENT`

目标：验证 Pi 能否发现 `ai-small-experiment-producer`。本实验不执行 Skill 脚本，不安装第三方 Package。

## 0. 隐私与权限

- [ ] 使用空白测试目录
- [ ] 终端画面没有 API key、用户名、私有仓库或历史命令
- [ ] Skill 内容可公开审查
- [ ] 不运行 Skill 内脚本
- [ ] 保存未经剪辑的原始输出

任一项未勾选：`STOP`。

## 1. Discover

问题：Pi 是否列出 Skill 名称、描述或来源路径？

- 预期 Skill：`ai-small-experiment-producer`
- 预期来源：`~/.codex/skills/**/SKILL.md`
- 实际输出：`________________________________`
- 原始证据文件：`________________________________`
- 结果：`PASS-DISCOVER / FAIL-DISCOVER / BLOCKED`

## 2. Load

问题：Pi 是否在明确请求时读取了完整 `SKILL.md`？

- 本期状态：`NOT-RUN`
- 后续证据：Skill 读取日志或可核验上下文

## 3. Execute

问题：Skill 引用的脚本、工具、路径和依赖是否可在 Pi 中执行？

- 本期状态：`NOT-RUN`
- 后续要求：隔离目录、依赖清单、逐项副作用审查、失败证据

## 4. Complete

问题：Pi 是否生成完整产物，并通过与 Codex 版本相同的门禁？

- 本期状态：`NOT-RUN`
- 后续要求：同输入、同 Oracle、同验证器、输出差异报告

## 允许发布的结论

即使第一级通过，也只能写：

> 本机已验证 Pi 能发现这个 Codex Skill；加载、执行和完整产物尚未验证。

禁止写：`完全兼容`、`无缝迁移`、`所有 Codex Skills 都能运行`。
