# 可复用工作法：AI 辅助传统测试证据链

## 适用条件

当团队需要从需求与代码变化生成测试候选，或需要对大量失败进行初步分诊时使用。AI 只能提议风险、测试、数据方法和失败簇；需求权威、业务 Oracle、生产权限和根因批准仍归具名 owner。

## 输入合同

冻结 requirement/design/diff/Oracle/commit/environment，保存版本、哈希、来源类型与 owner。先定义 stop states：缺引用、冲突、越权、不可重放、混合版本都不得自动补齐。为每个任务版本化 Prompt、Input、Schema、Eval、Mutation、Critic 与模型配置。

## 执行循环

1. 运行 baseline，证明批准行为和证据可观察。
2. 注入单一、可解释的 fault；非零退出是门禁检测力证据。
3. 修复输入或实现，不修改 Oracle 迎合错误。
4. 用相同版本合同重放 repair。
5. 保存原始报告、未知项和人工决定；迁移时替换业务规则与阈值。

## 禁止动作

不得让生成模型批准自己的 Oracle，不得把 diff 当完整影响面，不得用覆盖率替代 mutation，不得对未授权生产接口 fuzz，不得把 cluster 直接写成 root cause，也不得把本地 fixture 写成 live 或 practitioner。
