# 预期输出与读法

`verify-packages` 返回 PASS 且 `model_evidence=NOT_RUN`。suite baseline 退出 0，四页报告均为 PASS。suite fault 统一退出 1：TD-T05 单页为 BLOCKED/2，表明缺 diff 引用和虚构 SLA 被拒；TD-T06 为 FAIL/1，独立 Oracle 杀死守卫反转；TD-T07 为 FAIL/1，幂等属性产生最小反例；TD-T08 为 UNKNOWN/2，缺 trace 与混合版本阻止根因批准。suite repair 恢复退出 0。

这些状态不能相互归一：BLOCKED 表示输入/权限不足，FAIL 表示受控错误被检测，UNKNOWN 表示证据不足，PASS 只说明当前 fixture 合同成立。报告同时保存 basis、Oracle 与 Prompt manifest 哈希，任何哈希变化都需要新一轮基线。
