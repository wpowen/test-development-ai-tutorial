# Requirements-to-Evidence 离线实验

该实验不调用模型，也不连接生产服务。它覆盖八页完整链：Test Basis、Requirement Contract、可测试性评审、风险与方法选择、独立 Oracle、专业测试用例 Prompt、执行归因、变更回归与发布候选。每页都有独立 owner manifest、版本化 Prompt/input/schema/eval，以及 baseline → fault → repair 负控制。请先从课程页下载 zip，解压并进入本目录；不要从站点源码根目录运行。

目录同时提供 `inputs/`（PRD/技术方案/OpenAPI/authority policy）、`page-prompts/TD-P01..TD-P08/`（逐页 Prompt/input/schema/eval）、`page-manifests/`、`schemas/`、`reports/` 与 `receipts/`。所有 model manifest 明确 `provider=none`、`model=offline-deterministic`、`model_status=NOT_RUN`；这不是模型准确率证据。

逐页推荐入口（把页面 ID 换成 TD-P01 到 TD-P08）：

```bash
python3 pipeline.py page-cycle --page TD-P01 --report reports/TD-P01-cycle.json
```

每页 cycle 内部执行 baseline/fault/repair，三相退出码为 `0 / 1 / 0`，cycle 自身在预期三相都成立时退出 `0`。逐相命令和所需文件以 `page-manifests/<page_id>.json` 为唯一可执行契约。

下面的旧 TD-P02/Capstone 细粒度实验仍保留，用来观察真实需求门禁和订单状态 mutation：

```bash
python3 pipeline.py reset
python3 pipeline.py all --report reports/baseline.json
python3 pipeline.py inject-code-defect
python3 pipeline.py all --report reports/mutation.json
python3 pipeline.py repair
python3 pipeline.py all --report reports/repair.json
```

预期退出码为 `0 / 1 / 0`。文档冲突实验预期退出码为 `2`：

```bash
python3 pipeline.py reset
python3 pipeline.py inject-doc-conflict
python3 pipeline.py all
```

`2` 表示 `BLOCKED`，不是产品测试失败。

`receipts/fixture-baseline.json` 只为 deterministic fixture 的 `PASS_FIXTURE` 收据，显式保留 `provider=none` 与 `model_status=NOT_RUN`。真实模型、企业集成、从业者评审、线上与生产状态仍是 NOT_RUN/Unknown；离线结果最多支持带具名 owner 的 RELEASE_CANDIDATE，不会自动发布。
