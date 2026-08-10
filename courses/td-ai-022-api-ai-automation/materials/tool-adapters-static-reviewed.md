# 官方工具适配记录（static-reviewed / NOT_RUN）

核对范围来自研究稿的官方文档链接；本包未安装、未调用、未生成其运行报告。

- Schemathesis：将 OAS 候选转 property/stateful case；接入时保存 seed、缩减序列和版本，并本地验证 OAS dialect。
- Pact：接入真实 consumer/provider 交互；不能由 provider OAS conformance 替代 consumer contract。
- k6：checks 只观察，thresholds 才让退出码失败；接入时补 p95/TTFT/完成时间的业务阈值。
- GitLab CI：按门禁顺序编排并上传 JSON/JUnit；protected branch 的必需检查必须 fail-closed。

状态：`static-reviewed/NOT_RUN`。这些说明不能升级本课程的 `fixture-tested` 状态。
