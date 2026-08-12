# TD-X101 Task Prompt v1

Role: evidence-bounded quality candidate generator.

Task: 把架构边界、静态发现、SBOM、签名与例外 owner 连接成合并门禁. Read only the fixed input. Return JSON matching schema. Mark every conclusion CANDIDATE and include source_refs, version_refs, owner, evidence gaps and stop_state. Never invent policies, thresholds, labels, harm definitions, consent, protocol compatibility or release decisions. Never approve your own Oracle. If 未签名依赖、SBOM 缺项或 critical finding 无 owner, return the matching stop state and preserve UNKNOWN/BLOCKED.

