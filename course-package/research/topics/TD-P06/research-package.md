# TD-P06 · 自动化适配器与追溯

## Research brief

控制问题：已批准 TestPackage 怎样转换成 API、契约、集成或 UI 自动化，同时不让生成 Agent 修改 Oracle 或执行生产副作用？产物是测试骨架、适配器契约和 traceability index。

## Source pack

- Playwright Test Agents：planner、generator、healer 的职责和运行方式；官方提示生成测试可能有错误或被跳过。
- OpenAPI 3.2：接口形状与 JSON Pointer。
- Pact：消费者契约、provider verification 与功能测试边界。
- Cucumber Gherkin：业务可观察示例与步骤实现分离。
- GitHub custom agents 配置：prompt、工具限制和提交版本；编排配置不是测试正确性证明。
- 失败样例：只断言状态码、吞异常、自动 skip、healer 放宽业务断言。

## Evidence synthesis

事实：当前工具能规划、生成、执行并尝试修复测试；生成成功不等于测试通过。工程综合：生成器只读 ACCEPTED TestPackage；适配器明确定义 sandbox 权限和证据输出；healer 不得改业务 Oracle。未知：目标仓库的 selector、fixture 和环境能力。

## Engineering blueprint

Adapter Contract 列出允许动作、数据范围、环境和禁止副作用。生成代码包含 test_id、requirement_ids、risk_ids 和 oracle_ids。静态门禁查找空断言、宽泛 catch、固定 sleep、skip 和 mock 自证；运行门禁依赖 mutation。

## Manuscript map

页面先做适配器边界表，再给代码生成任务、假绿审查清单和追溯索引用途。没有假设某一个框架可以覆盖全部层级。

## Editorial review

PASS 94/100。保留工具能力与限制，未使用“自动修复即可”。所有命令、字段和禁止动作未因口语化编辑而删除。

## Validation

PASS（静态）：工具边界与追溯字段已经审查；当前离线夹具模拟执行语义，没有实际生成 Playwright/Pact 文件，因此页面状态为 desk-researched。
