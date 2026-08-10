# Profession Decomposition Protocol

## Controlling idea

Do not divide a profession by tools or generic skills. Divide it by real work, decisions, artifacts, and failure costs; then map AI into that structure.

## Five-axis profession map

Create `research/profession-map.json` with these axes:

1. **Role variants**: seniority, specialization, industry, company stage, and work setting.
2. **Work domains**: stable responsibility areas such as intake, planning, execution, verification, release/handoff, monitoring, and improvement.
3. **Business events**: what triggers the work and what decision closes it.
4. **Work objects and artifacts**: inputs, systems, records, code, data, reports, approvals, and outputs that can be inspected.
5. **Decision rights and failures**: who may decide, what AI may do, what remains human, observable failure, and business impact.

Every work domain records:

`domain_id,name,job_result,business_events,artifacts,systems,decision_rights,failure_costs,ai_lanes,scenario_ids,evidence_ids`

## From profession to courses

Use this chain:

`role variant -> work domain -> business event -> current workflow -> artifact -> failure -> AI intervention -> AI-specific failure -> learner proof -> reusable material`

Reject a course idea when any link is missing.

## Coverage rules

- Map at least five work domains and the end-to-end lifecycle before selecting topics.
- Every high-priority scenario belongs to one primary domain and may name secondary domains.
- Every domain has profession evidence and at least one explicit non-AI baseline.
- Do not assume all role variants share the same pain. Preserve applicability and exclusion fields.
- Course sequencing follows cognitive and workflow dependency, not tool popularity.

## Learning progression

Use four levels:

1. `L1-see-and-run`: recognize the AI-specific problem and reproduce one visible result.
2. `L2-control-and-check`: constrain inputs/outputs, add checks, and explain a failure.
3. `L3-integrate-and-transfer`: connect the workflow to real systems and adapt it to a neighboring scenario.
4. `L4-operate-and-govern`: versioning, CI, observability, cost, privacy, drift, approval, and incident response.

A series must not jump to agents or production governance before the learner can run and inspect the bounded task.

## Course portfolio test

For 10-20 courses, verify:

- no work domain is represented only by repeated “upload -> ask -> copy” lessons;
- all relevant AI lanes are covered;
- at least one course teaches a negative case in every major work domain;
- prerequisites form a valid progression;
- each course hands off a reusable artifact used again later;
- advanced courses integrate artifacts from earlier levels instead of restarting from blank prompts.
