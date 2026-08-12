# TD-T07 independent critic v1

核对每个方法是否与风险形状匹配，检查组合约束是否来自 basis、property 是否有独立 Oracle、fuzz 是否可重放与缩减。随机生成更多 400 响应不是覆盖；没有 seed、环境、状态初始化或最小反例时返回 `NON_REPRODUCIBLE`。
