# TD-T07 method selection adviser v1

读取 Schema、业务约束、状态与风险，先判定输入形状，再推荐 equivalence/BVA、decision table/combination、state、property、metamorphic 或 fuzz。记录选择理由、拒绝方法和 residual combinations。AI 可以提出维度，不能补写合法域、不变量或隐私数据。所有生成器必须固定 seed，失败必须保存最小反例、系统版本与重放命令。
