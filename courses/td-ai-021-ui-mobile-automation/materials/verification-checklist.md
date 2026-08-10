# 验证清单

- [ ] 场景有前置状态、动作、业务 oracle、清理动作。
- [ ] Web 使用 role/label/test-id；移动端使用 accessibility/resource-id/identifier。
- [ ] 每个关键动作后有明确 assertion；没有坐标、全局 sleep、无限 retry。
- [ ] 真实运行前锁定 Node/Java/Xcode/SDK/driver/browser/device image 与 commit。
- [ ] 首次失败与最终重试分开统计；trace、hierarchy、截图、console/device log 可追溯。
- [ ] AI 仅生成/诊断/候选修复；不批准基线、不改 oracle、不执行生产副作用。
- [ ] 本地离线证据为 `fixture-tested`；设备/浏览器证据诚实标记 `NOT_RUN/static-reviewed`。
