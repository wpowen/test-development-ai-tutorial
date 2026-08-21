# 验收清单

## 每页研究

- [ ] 精确九件研究包；至少 10 个已打开来源、两个独立 run 和独立 comparison
- [ ] Evidence / Inference / Unknown / Counterevidence 分开
- [ ] source family、publisher、evidence lane 和限制可审计

## 每页实验

- [ ] Prompt/Input/Schema/Eval/Mutation 均锁定 v1.0.0 与 SHA-256
- [ ] manifest 的 cwd、required files、命令、退出码、工件完全一致
- [ ] baseline=0、fault=1、repair=0、cycle=0
- [ ] fault 至少击中一个有效 gate，repair 未删除阈值
- [ ] 能从 traces.jsonl 找到一项具体任务证据

## 全课闭包

- [ ] TD-AP01～TD-AP08 全部通过 typed technical block 审计
- [ ] canonical lab → public、canonical evidence → public reports、public → static dist → ZIP 文件和 SHA-256 一致
- [ ] 移动端 390×844 遍历当前 releaseScope 全部页面且无横向 overflow
- [ ] 明确 PASS-FIXTURE，不写成 live、practitioner 或 production capacity

