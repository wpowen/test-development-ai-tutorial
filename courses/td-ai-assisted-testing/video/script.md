# 教学视频脚本

## 00:00—01:30 冷开场

“这里有十二条 AI 生成测试，全部绿色。你会放行吗？”画面反转退款守卫，测试如果仍绿，就说明数量和覆盖没有证明检测力。今天不追求更多测试，而是建立一条能被反证的证据链。

## 01:30—05:00 冻结依据与风险候选

需求、设计、Oracle 与 diff 是四种不同输入。diff 只显示直接变化，不显示完整影响。每条风险候选都要带 requirement、diff、oracle、owner；缺一项就 BLOCKED。AI 可以连接证据，不能发明 SLA，也不能决定谁有权批准。

## 05:00—09:00 用 Mutation 证明测试会失败

先跑 baseline，确认批准实现和独立 Oracle 一致。再反转 activated digital refund 守卫。fault 退出 1 是正确结果，因为目标用例被打红；最后恢复实现，repair 回到 0。强调不能修改 expected 迎合错误，不能让生成器批准自己的 Oracle。

## 09:00—13:00 选择数据方法

阈值用 boundary，离散交互用 combination，全称不变量用 property，未知语法面且有授权沙箱才用 fuzz。固定 seed 之外还要保存版本、依赖和环境。幂等故障产生最小反例后，把它转为固定回归。

## 13:00—16:30 聚类不等于根因

先保存 event、trace、commit、environment 与 raw artifact，再允许 AI 形成候选 cluster。删除 trace 并混合 commit 后，正确状态是 UNKNOWN/2，不是“连接池耗尽已确认”。根因升级需要控制实验和 incident owner。

## 16:30—18:00 交付与边界

观众复跑四页命令，检查版本化 Prompt/Eval/Mutation 和三阶段报告，再迁移到订阅续费。最后重申：当前是 synthetic fixture-tested；模型、真实集成、从业者评审和生产发布仍为 NOT_RUN。
