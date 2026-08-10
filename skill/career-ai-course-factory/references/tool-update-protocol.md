# Tool Update Protocol

## Tool adapter record

Keep tools separate from career tasks. A course points to a tool adapter, not to a permanent brand assumption.

```json
{
  "tool_id": "stable-slug",
  "name": "工具名称",
  "category": "coding|browser-testing|document|data|voice|video",
  "capability": "它能做的具体动作",
  "official_source": "https://...",
  "version_or_date": "版本或访问日期",
  "setup": "安装和权限要求",
  "input_contract": "输入要求",
  "output_contract": "输出形式",
  "limits": ["不能做什么"],
  "fallbacks": ["替代路径"],
  "last_tested": "YYYY-MM-DD",
  "status": "current|stale|blocked|deprecated"
}
```

## Refresh rules

Refresh when a course is used again after a meaningful tool release, when the tool's official docs change, when a learner reports a failure, or when a new tool claims to replace a step. Verify the new capability from a primary source and re-run the smallest course acceptance test.

Record:

- old and new capability;
- source and access date;
- affected courses and materials;
- migration or wording change;
- fallback still available;
- test result and remaining uncertainty.

Never replace a tool in a material pack merely because it is newer. Replace it only when it improves the learner's observable outcome and the result can be re-verified.

