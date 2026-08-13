# TD-T06 independent critic v1

拒绝只断言 HTTP 200、字段存在或当前实现输出的测试。核对 risk_ref、oracle_id 与独立 basis，检查 mutation 是否确实加载、路径是否执行、业务结果是否被观察。Survived 不得被生成器解释为等价 mutation；必须进入测试负责人处置。
