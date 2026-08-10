# AI时代接口自动化：公开学习者材料

这是一个可复制、离线、无密钥的课程练习包。默认路径只使用 Python 3 标准库，读取两份 OpenAPI YAML 文本、事件 JSON、mutation catalog 和 AI 性能 workload，生成可审计 JSON 报告。

## 从本目录运行

先进入 `learner-materials/` 根目录，再复制执行：

```bash
python3 scripts/api_automation.py baseline --report reports/baseline.json
```

预期退出码 `0`，报告状态 `PASS`。

```bash
python3 scripts/api_automation.py mutation --report reports/mutation.json
```

预期退出码 `1`，报告状态 `FAIL`，唯一失败 case 为 `BUS-SHIPPED-REJECT`。这个红灯证明已知业务缺陷能被独立 Oracle 检出。

```bash
python3 scripts/api_automation.py repair --report reports/repair.json
```

预期退出码 `0`，报告状态恢复为 `PASS`。完整序列是 `0 / 1 / 0`。

如果 shell 启用了 `set -e`，mutation 的预期退出码会中止脚本。可用下面的验证命令明确接住预期红灯：

```bash
python3 scripts/api_automation.py mutation --report reports/mutation.json; test $? -eq 1
```

运行独立验证：

```bash
python3 -m unittest discover -s tests -v
```

## 你会得到什么

- `fixtures/order-cancel.openapi.yaml`：取消、任务轮询与 SSE 契约。
- `fixtures/payment-intent.openapi.yaml`：支付意图、权限、幂等和异步事件契约。
- `fixtures/checkout-events.json`：健康事件流与重复投递负控制。
- `configs/schema-mutations.yaml`：业务、Schema、幂等和 SSE mutation catalog。
- `configs/ai-performance-workload.yaml`：Agent/AI API workload 与指标维度模板。
- `guides/`：Run Manifest、consumer compatibility 与 AI 性能指标卡。
- `reports/`：每次运行生成的机器证据。

脚本从 Spec 的 `operationId` 生成契约候选，并用与服务模拟标志分离的 Oracle 检查业务状态、权限、幂等、异步状态和事件终态。报告保存输入 hash、Oracle hash、case 结果、mutation ID 与明确的 `NOT_RUN` 项。

## 外部工具状态

Schemathesis、Pact、k6 和 GitLab CI 都是 `static-reviewed/NOT_RUN`：本包提供了接入位置、配置思路和边界说明，但没有安装或运行它们，也没有 live endpoint、真实模型、支付服务或生产流量。不要把配置文件、官方文档能力或工具名写成运行证据。

真正接入时：Schemathesis 需 pin 版本并保存 seed/replay；Pact 需保存 consumer artifact 与 provider verification；k6 需用 thresholds 返回非零并重新校准 workload；GitLab CI 需配置 protected branch、artifact 和 fail-closed required job。

## AI 与人工边界

AI 可以从批准的 Spec、需求与失败 trace 生成候选 case、属性和归因草稿。业务状态、权限、金额、副作用和发布 Oracle 必须由对应 owner 批准；AI 不得自动降低阈值、根据实现改 expected、接受残余风险或调用真实破坏性 endpoint。

## 证据范围

当前状态仅为 `fixture-tested`。它证明公开材料在本地可读、脚本能从本目录运行、0/1/0 可复现；不证明真实 API 兼容性、模型质量、生产容量、费用、缺陷发现率或学习效果。
