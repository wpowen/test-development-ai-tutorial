# Verification checklist

- [ ] manifest 的 working directory、命令、报告路径与实际 runner 一致。
- [ ] baseline/fault/repair 退出码严格为 0/1/0，fault 不是伪造的成功。
- [ ] fault 改变了专业决定，且报告列出命名的 failed Oracle。
- [ ] repair 没有删除 Oracle、修改 expected、扩大 tool scope 或增加预算。
- [ ] A/B 锁、Judge 校准、outcome/step/trajectory、权限和 stop reason 均可追溯。
- [ ] 报告保留 provider/model NOT_RUN、Unknown 与人工 owner；迁移到真实系统前不能升级成熟度。
