# 质量控制平面：公开离线材料

本目录可独立运行，不需要进入课程目录、不需要网络、不需要账号。它模拟签名 webhook、inbox/dedupe、AI candidate/人工批准、当前 SHA、JUnit、K8s namespace/RBAC/TTL、Jira/GitLab 回写、脱敏通知和审计 hash 链。

## 从本目录根目录运行

```bash
python3 scripts/quality_platform.py baseline --report reports/baseline.json
```

预期退出码 `0`，报告 `PASS`。

```bash
python3 scripts/quality_platform.py mutation --report reports/mutation.json; test $? -eq 1
```

预期退出码 `1`，报告 `FAIL`，失败 Oracle 为 `SHA-BINDING`。

```bash
python3 scripts/quality_platform.py repair --report reports/repair.json
python3 -m unittest discover -s tests -v
```

完整路径是 `0/1/0`。也可用 `python3 scripts/quality_platform.py replay|rbac|missing-report --report reports/<name>.json` 检查其他故障。

## 四页独立 baseline → fault → repair

每页都有自己的 lab manifest、Prompt/Schema/eval/version manifest、状态对象和命名 Oracle。以下命令各自生成 baseline、fault、repair 与 cycle-summary，只有观察到 `0/1/0` 才退出 `0`：

```bash
python3 scripts/basis_gate_and_candidate_review.py cycle --report-dir reports/td-qp01
python3 scripts/gitlab_sha_junit_gate.py cycle --report-dir reports/td-qp02
python3 scripts/ephemeral_namespace_cleanup.py cycle --report-dir reports/td-qp03
python3 scripts/event_replay_and_reconcile.py cycle --report-dir reports/td-qp04
```

对应的配置、fixtures 和 SOP 分别位于 `configs/jira-basis-gate.yaml`、`configs/gitlab-junit-gate.yaml`、`configs/ephemeral-namespace-baseline.yaml`、`configs/event-gateway-policy.yaml`，`fixtures/` 和 `guides/td-qp*.md`。页面级运行契约在 `manifests/td-qp*-lab.json`，Prompt 契约在 `prompts/td-qp*/`；`manifests/shared-bundle-owners.json` 精确列出四个 owner，不允许前缀继承。

## 文件与边界

`fixtures/webhook.json` 和 `configs/policy.json` 是可解析的合成夹具；`guides/` 说明事件 schema、SOP、权限和诊断。Prompt 的 provider/model 也是 `NOT_RUN`。真实 Jira/GitLab/K8s/ChatOps 与 tier/版本能力没有被本材料伪造成 live evidence。
