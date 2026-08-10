# Business Scenario Evidence Protocol

## Controlling rule

A course begins with a business event and an observable decision, not a tool feature. “Use AI to generate X” is a technique; it becomes a scenario only when the professional context, failure cost, constraints, handoff, and verification are concrete.

## Required scenario artifact

Create `research/scenarios.json`:

```json
{
  "profession": "stable profession id",
  "scenarios": [{
    "scenario_id": "stable-id",
    "title": "business outcome",
    "ai_lane": "use-ai-for-work|test-ai-systems|agentize-work|build-ai-quality-system",
    "actor": "specific role and level",
    "work_setting": "team/product/domain context",
    "trigger": "event that starts the work",
    "business_system": "real system or system class",
    "business_object": "order, claim, release, ticket, contract, patient record, etc.",
    "inputs": ["realistic and available inputs"],
    "current_workflow": "non-AI workflow",
    "pain_and_failure_cost": "observable cost or risk",
    "constraints": ["privacy, latency, policy, access, budget"],
    "ai_intervention": "bounded AI workflow",
    "ai_role": "assistant|system-under-test|agent|judge|infrastructure",
    "outputs": ["inspectable artifacts"],
    "decision_or_handoff": "who decides what next",
    "ai_specific_failures": ["failure modes introduced by AI"],
    "privacy_security": "data and authority boundary",
    "evidence_ids": ["profession evidence", "AI evidence", "practice evidence"],
    "evidence_classes": ["profession-workflow", "ai-capability", "practice-artifact"],
    "evidence_map": {
      "profession-workflow": ["S01"],
      "ai-capability": ["S02"],
      "practice-artifact": ["S03"]
    },
    "semantic_contract": {
      "actor_role": "specific role",
      "actor_seniority": "level or responsibility scope",
      "business_domain": "domain/team",
      "system_name_or_class": "specific system or system class",
      "failure_impact": "business consequence",
      "observable_indicator": "what can be measured or inspected",
      "measurement_status": "unmeasured|estimated|measured",
      "decision_owner": "human owner",
      "decision": "release, payment, escalation, etc.",
      "allowed_ai_authority": "bounded authority",
      "human_approval_required": true
    },
    "artifact": "downloadable or runnable learner artifact",
    "demo_fixture": "public, sanitized, synthetic, or blocked",
    "validation_plan": ["baseline", "failure", "repair"],
    "scores": {"ai_centrality": 5, "business_specificity": 5, "artifact_accessibility": 4, "testability": 5},
    "evidence_status": "hypothesis|desk-researched|fixture-tested|live-tested|practitioner-reviewed|production-validated|blocked"
  }]
}
```

## Triangulation gate

A selected scenario needs at least one opened source from each class:

1. `profession-workflow`: role, workflow, job, standard, or authoritative professional artifact;
2. `ai-capability`: official documentation, release note, standard, or primary repository;
3. `practice-artifact`: practitioner implementation, issue, case, job requirement, dataset, repository, trace, postmortem, or counterevidence.

A vendor case study may contribute only as `vendor-claim`. It cannot by itself establish prevalence or efficacy. If no third-class source exists, retain the scenario as a hypothesis and do not promise professional validation.

Bind every evidence class to concrete source IDs through `evidence_map`. Each mapped source must exist in the source ledger, appear in a selected search-log row with an opened URL, and match the class: AI capability uses official/primary/standard/repository evidence; practice artifact uses practitioner, job, issue, case, repository, dataset, trace, postmortem, or counterevidence.

## Specificity gate

Reject or rewrite a scenario when any is missing:

- actor and work setting;
- trigger and business object;
- named business system or system class;
- realistic input and inspectable output;
- failure cost or risk;
- constraints and human authority boundary;
- AI-specific failure mode;
- decision/handoff after the AI output;
- validation that can produce a failing result.

Reject repeated `upload → ask → copy` interactions even when the nouns change.

Reject placeholders such as `TODO`, `TBD`, `N/A`, `某职业`, `某系统`, or labels copied into values. `semantic_contract` makes decision authority and measurable failure explicit. `measurement_status=unmeasured` is allowed for honest desk research, but cannot support `production-validated` claims.

## Proof ladder

- `hypothesis`: plausible idea without sufficient evidence.
- `desk-researched`: triangulated public evidence, no execution.
- `fixture-tested`: runnable synthetic/sanitized path with preserved output.
- `live-tested`: live model or target system tested within stated scope.
- `practitioner-reviewed`: relevant practitioner reviewed scenario realism and artifact utility.
- `production-validated`: deployed outcome measured with provenance.

Never collapse these levels. Synthetic fixture proof demonstrates mechanics and failure detection, not market prevalence, enterprise fit, or production ROI.

## Course mapping

Every task has one `scenario_id`. Every course records one or more scenario IDs. The chain must remain inspectable:

`source → scenario → task → technology adapter → learner artifact → validation evidence → course/video claim`
