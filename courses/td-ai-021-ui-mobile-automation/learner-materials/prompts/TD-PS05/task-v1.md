# TD-PS05 Task Prompt v1.0.0

控制问题：怎样区分 DOM 规则、键盘旅程、可访问语义和视觉差异，并防止自动更新基线掩盖回归？

业务场景：客服工作台在键盘、辅助技术、窄视口和中英文长文本下仍需安全完成退款

方法选择：WCAG/ARIA 定义控制问题，自动规则找常见缺陷，键盘与读屏旅程验证过程，风险矩阵裁剪环境，人工审批视觉基线

请读取固定 input fixture，只输出符合 schema 的 test_package。每条 test 必须含 risk_id、source_refs、method_reason、oracle_id、fixture、expected、fault、evidence 和 human_gate。从 WCAG 条款、旅程和视口矩阵生成分层检查与人工复核清单；明确自动扫描未覆盖项，禁止自动批准截图基线。资料没有说明的字段写 UNKNOWN；冲突写 BLOCKED；不得新增业务规则、权限、阈值或生产命令。
