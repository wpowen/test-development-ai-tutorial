# Verification checklist

- [ ] AI 是被测对象/评测器/Agent，而不是装饰性文案工具。
- [ ] 每条 case 有明确 slice、oracle 和可失败条件。
- [ ] 需要引用的回答只能使用允许引用。
- [ ] 高风险与 injection 样例检查拒答和敏感信息。
- [ ] 工具调用同时检查名称与参数。
- [ ] baseline exit 0，mutation exit 非 0，repair exit 0。
- [ ] 报告保存 per-case failures，不只有总分。
- [ ] 阈值被标注为项目策略，不冒充行业标准。
- [ ] snapshot 证据没有被表述成 live model 证据。
- [ ] 真实数据接入前完成脱敏、权限与留存审查。
