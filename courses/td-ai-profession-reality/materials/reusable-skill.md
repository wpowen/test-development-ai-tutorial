# 可复用技能：需求—技术—测试提示词传递

先抽取需求规则、例外、验收和权威 owner；再抽取技术状态、接口、数据、失败恢复和可观测性；分别标注版本与 locator。冲突时输出 BLOCKED 和待裁决人。接着用风险决定方法，用独立于实现和模型输出的 Oracle 写测试条件，再把 owner、版本、来源、验收和消费者写进工件。提示词必须绑定输入、Schema、Eval 和 Mutation，并要求 FACT、PRACTITIONER-SIGNAL、INFERENCE、INTERNAL-UNKNOWN 分类。AI 只生成候选、执行受控比较和汇总证据；人类确认根因、阈值、waiver、发布与回滚。
