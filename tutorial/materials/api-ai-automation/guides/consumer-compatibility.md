# Consumer Compatibility：OpenAPI 与 Pact 各负责什么

OpenAPI 描述 provider 允许的路径、参数、状态码与数据形状；consumer contract 记录某个消费者真正依赖的交互样例。两者不是替代关系。

## 兼容性审查表

| 变更 | Provider/OpenAPI gate | Consumer/Pact gate | 默认发布动作 |
|---|---|---|---|
| 新增可选响应字段 | Schema 通常兼容 | 严格反序列化消费者可能失败 | 检查真实消费者后放行 |
| 删除响应字段 | breaking diff | 依赖该字段的 interaction 失败 | 阻断并版本化 |
| optional 请求字段改 required | breaking diff | 旧 consumer 请求失败 | 阻断 |
| 200 改 202 + 异步 task | 状态码和响应 schema 变化 | 消费者流程语义变化 | 新版本 + 迁移期 |
| 新增鉴权 scope | security contract 变化 | consumer 凭证可能不足 | 阻断，确认权限 owner |
| 事件字段删除/改名 | 事件 schema breaking | 消费者反序列化/业务处理失败 | 阻断并回放事件 fixture |

## 推荐工作流

1. Provider 先做 OpenAPI parse/lint、breaking diff 和 response conformance。
2. 每个关键 consumer 维护其使用到的 request/response interaction，并由 provider verify。
3. 用 `checkout-events.json` 回放 at-least-once、重复投递和终态语义；消费者必须按 `event_id` 去重。
4. 对未覆盖的 consumer、未上报的动态客户端与内部脚本保持 `UNKNOWN`，不能用一个 Pact 全绿推断“所有消费者兼容”。

## 人工责任

API owner 决定版本与迁移窗口；consumer owner 确认实际依赖；安全 owner 确认 scope；测试负责人确认负控制。AI 可从调用日志生成候选 interaction，但不得替 consumer owner 宣称依赖完整，也不得自动接受 breaking change。

## 工具状态

本材料没有安装或运行 Pact broker、consumer test 或 provider verification。这里是按官方能力边界整理的 `static-reviewed/NOT_RUN` 适配说明；真正接入时必须 pin 版本、保存 pact artifact、provider 版本和 verification 输出。
