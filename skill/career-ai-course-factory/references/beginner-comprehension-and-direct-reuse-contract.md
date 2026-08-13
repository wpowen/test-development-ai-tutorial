# Beginner Comprehension and Direct Reuse Contract

## Two separate questions

Validate both:

1. Can a beginner form the correct mental model and diagnose a failure?
2. Can the learner take the supplied artifact into a new bounded context and adapt it safely?

Readable prose alone proves neither. An agent editorial pass is not target-learner evidence.

## Required artifact

Create `research/learner-usability-reuse.json` with an exact record for every promised page.

Each page records:

- `display_number`, prerequisites, assumed knowledge, and every technical term used;
- definitions introduced on the page, in plain language, before first use;
- one mental model, worked example, counterexample or invalid-use example;
- one learner action with a repository-owned input and an observable expected result;
- one failure symptom, diagnosis path, repair, and rerun check;
- at least one comprehension check with expected answer and common misconception;
- at least one reusable artifact contract.

A term may be used only when it was introduced on the same page or an earlier prerequisite page. Foundation concepts such as model, token, prompt, context, embedding, RAG, agent, tool call, workflow, Oracle, dataset, slice, metric, latency, throughput, and trace must be explicit prerequisite nodes when downstream pages use them.

## Reusable artifact contract

Every claimed reusable artifact names:

`artifact_id,path,purpose,inputs,editable_fields,outputs,adaptation_steps,validation,limitations,owner`

The path must resolve in the learner release. Inputs and outputs must be inspectable. Editable fields explain what the learner may change and what must remain invariant. Adaptation steps include how to bind a new scenario, update the Oracle or threshold owner, run validation, and interpret failure. A command without expected evidence, a prompt without manifest/input/schema/eval, or a checklist without decision owner is not directly reusable.

## Beginner evidence boundary

Static gates may establish `designed-for-beginner` and clean-room fixture usability. Only observed target learners can establish learner comprehension or transfer. Record learner validation as `NOT_RUN`, `PASS`, `FAIL`, or `BLOCKED`; `PASS` must link to the independent learner evidence lane and its sample, tasks, observations, failures, and revisions.

## Anti-bypass tests

Fail when a term appears before explanation, a page relies on hidden prerequisites, an example has no expected observation, a failure has no repair, a reusable artifact lacks editable fields or validation, or “小白可懂/拿来即用” is claimed from author review alone.
