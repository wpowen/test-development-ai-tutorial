# TD-P07 测试执行、结果归因与缺陷报告｜适配卡

## 能做什么

冻结运行版本和原始证据，区分产品、环境、数据、脚本和 Oracle 故障，再形成可复现缺陷。 它输出草案和证据边界，不能替责任人批准。

## 组合顺序

多轮专业用法：

1. 把 `system-v1.md` 放入 Agent 的 system/instructions 区；
2. 发送 `task-v1.md`；
3. 紧接着粘贴已替换的 `input.json`；
4. 得到首轮 JSON 后，再发送 `critic-v1.md` 做独立批判；
5. 用 `schema.json`、`eval.json` 和 `mutation.json` 验证，而不是相信模型自评。

若工具只有一个输入框，可直接复制保留的 `prompt-v1.md`，然后补上业务材料；它便于入门，但不能替代分角色复核。

## 修改这些字段

- `run_goal`
- `version_manifest`
- `command_cwd`
- `selected_tests`
- `raw_evidence`

同时替换 `baseline_id`、`source_refs`、`authority_policy` 和 `fixture_boundary`。不得把示例 source_ref 带入真实项目。

## 不可修改的安全边界

- Evidence / Inference / Unknown 必须分开；
- 命中停止状态必须 fail-closed；
- 业务、技术、测试和发布 owner 的决策不得交给模型；
- 真实材料先脱敏，生产凭据、个人信息和商业秘密不得粘贴到未批准的 provider。

## 验证与状态

先跑 Schema，再跑 eval 和 mutation，最后由独立责任人审查。当前包只完成静态构建和 deterministic fixture；provider=`none`、model=`offline-deterministic`、模型证据为 `NOT_RUN`，没有 raw model output，也不构成 live、practitioner 或 production 证据。
