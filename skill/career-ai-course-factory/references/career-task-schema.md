# AI-Native Career and Course Schema

## Task record

```json
{
  "task_id": "career-ai-001",
  "career_id": "stable-slug",
  "scenario_id": "stable-scenario-id",
  "title": "AI 与职业交叉的可观察任务",
  "ai_lane": "use-ai-for-work|test-ai-systems|agentize-work|build-ai-quality-system",
  "ai_role": "assistant|system-under-test|agent|judge|infrastructure",
  "system_under_test": "具体 AI/职业系统；无则写 none 并说明",
  "professional_problem": "真实工作问题及失败代价",
  "inputs": ["可获得且可脱敏的输入"],
  "non_ai_baseline": "没有 AI 时的工作流与成本",
  "ai_workflow": "模型、Agent 或评测系统如何改变工作",
  "ai_specific_failures": ["幻觉、漂移、越权、脆弱自动化等"],
  "learner_proof": "学习者如何直接看到有效或失败",
  "deliverables": ["可运行或可审计物料"],
  "work_domain_id": "profession-map 中的稳定工作域",
  "business_event": "触发该任务的业务事件，必须与 scenario 一致",
  "primary_artifact_id": "本任务负责产出的主物料",
  "decision_owner": "最终专业判断责任人",
  "allowed_ai_authority": "AI 可执行和不可执行的边界",
  "handoff_target": "产物交给谁以及触发何种决策",
  "scores": {
    "ai_centrality": 1,
    "professional_leverage": 1,
    "pain_frequency": 1,
    "repeat_reuse": 1,
    "runnable_proof": 1,
    "differentiation": 1,
    "source_strength": 1,
    "learner_accessibility": 1,
    "risk": 1,
    "verification_difficulty": 1
  },
  "acceptance_criteria": ["机器或人工可检查标准"],
  "human_gate": "专业人员必须做的判断",
  "privacy_notes": "数据边界",
  "status": "hypothesis|desk-researched|fixture-tested|live-tested|practitioner-reviewed|blocked",
  "evidence_ids": ["S01"]
}
```

## AI centrality rubric

- 5: AI/AI system is the object or engine of the work; removing it destroys the course.
- 4: AI changes the professional workflow and introduces AI-specific verification or governance.
- 3: AI accelerates a task, but the lesson remains mostly ordinary professional training.
- 2: a generic prompt creates a draft with limited profession-specific control.
- 1: AI is decorative or only mentioned.

Only scores 4-5 may become courses.

## Ranking and gates

Rank positive dimensions separately from risk. Recommended priority score:

`2*AI centrality + 2*professional leverage + 2*runnable proof + repeat reuse + differentiation + source strength + accessibility`

Hard gates:

- AI centrality >= 4;
- runnable proof >= 3;
- source strength >= 3;
- at least one acceptance criterion can fail;
- deliverable is more than a prompt or prose answer;
- risk <= 3 for unsupervised beginner practice;
- hidden credentials are not required for the default path.

For a 10-20 course series, include all relevant AI lanes and avoid repeating the same “upload → ask → copy” interaction under different titles.

Each curriculum entry also records `delivery_status`: `planned|researched|fixture-tested|live-tested|practitioner-reviewed|blocked`. A planned title is not a built course. Any tested status requires a matching course directory and execution evidence.
