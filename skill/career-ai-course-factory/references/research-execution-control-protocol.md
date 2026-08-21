# Research execution control protocol

## Purpose

本协议把“完成 103 页正式研究、审计、裁决、饱和并发布”拆成可停止、可复核的批次。它解决两类失控：把规划/整合 token 当成研究进度，以及在没有新证据、没有新收据或没有晋级可能时继续运行。

## 1. Global goal contract

在任何研究请求前，必须建立一个 hash-bound control artifact，至少声明：

- `goal_id`、固定 scope（页面数、命题数、发布目标）；
- 成功条件：每个 promised page 的 claim inventory、route、provider/local/target/teaching evidence、独立审计、terminal disposition、saturation、promotion 和 publication closure；
- 当前批次的 `claim_ids`、`canonical_unit_ids`、phase、execution surface；
- 硬上限：批次命题数、provider runs、elapsed minutes、可报告 token 上限；
- checkpoint 间隔和停止动作；
- current counters、last progress evidence、next action、limitations。

没有 control artifact、artifact hash 不匹配、预算/计数为 `UNKNOWN`，或 provider capability 未通过 preflight 时，不能发送研究请求。

## 2. 最小批次规则

1. 首批只能是 1 个命题；通过后最多扩展到同一 canonical unit 的小批次。不得直接启动 103 页全量请求。
2. Luna/planner 只能提出分类、去重和缺口排序；不能增加 provider run 上限，也不能把自身输出当正式证据。
3. 每个批次必须有可观察的 terminal result：`COMPLETED-RECEIPT`、`BLOCKED-CAPABILITY`、`BLOCKED-EVIDENCE`、`TIMEOUT` 或 `CANCELLED`。
4. 运行中若没有新报告、source-opening ledger、raw response 或 disposition 变化，就不算 progress。

## 3. 强制停止条件

立即停止当前批次并写入 control artifact：

- 达到任一硬上限（命题数、provider runs、时间或 token）；
- 相同失败连续两次，或 provider capability/preflight 失败；
- 研究请求完成但缺 raw response、response/export ID、opened-source ledger、citations、hash 或 limitations；
- 连续两个 checkpoint 没有新增可验证证据、没有 disposition 变化，也没有明确 gap-fill；
- route、identity、locator、source freshness 或 execution contract 变为 `BLOCKED`；
- 需要人工/目标组织/凭证才能继续；
- 研究结果只是在重复已有 canonical packet，且 transfer check 没有 decision-changing delta。

停止不是失败：停止记录必须区分 `BLOCKED`、`TIMEOUT`、`CANCELLED` 和“已完成但不能晋级”。任何停止状态都不得被编译为 `PASS` 或 saturation。

## 4. Global completion condition

只有同时满足以下条件才可把 global goal 标为 complete：

1. 103/103 页面覆盖；
2. 每条命题都有批准 identity、route 和 locator；
3. 每个外部 canonical unit 有真实 provider receipt、counterevidence 和饱和依据；local/target/teaching 命题有对应运行或人工证据；
4. 每个页面有独立 adjudication、contradiction disposition、promotion receipt 和当前 hash closure；
5. `validate_career_package.py`、release gates、站点构建、部署和线上回读全部通过；
6. 没有 `BLOCKED`、`UNKNOWN` 或未解释的旧证据漂移。

“测试通过”“页面生成”“研究任务已提交”“ChatGPT 正在思考”都不是 global completion。

## 5. 每批次输出

每个批次必须写：control artifact、cost telemetry event、provider/raw evidence（若有）、audit note、next action 和 stop reason。下一批次只能在上一批次的 terminal result 已被本地 schema/validator 验证后创建。

