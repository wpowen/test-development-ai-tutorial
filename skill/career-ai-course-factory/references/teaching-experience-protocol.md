# Teaching Experience Protocol

## Outcome

The learner should feel that a practitioner is guiding them through one real task, not reading a research report. Preserve rigor while making the proof visible early.

Do not imitate a named living creator's exact voice, catchphrases, pacing signature, or script. When a reference creator is reliably identified, extract only high-level observable mechanisms and record the source and confidence. If identity or content cannot be verified, mark it unknown and use the evidence-based lesson pattern below.

Treat a creator identity as reliable only when one stable public profile and one independent cross-check agree on the account. Otherwise switch to category-level samples. Label every style observation `direct-observation`, `title-or-snippet-inference`, or `unknown`.

## One lesson, one job result

Each lesson has one learner-visible result, one artifact, one failure, and one transfer task. A lesson is incomplete if the learner only watches the instructor succeed.

Create `video/lesson-experience.json` for every built exemplar.

## Required lesson arc

Use the following ordered stages:

1. `cold-open-failure`: show the professional failure, bad output, red metric, or costly decision first.
2. `stakes-and-promise`: state who has the problem, why it matters, and what the learner will produce.
3. `before-after`: show the old workflow and the AI-native target without hiding tradeoffs.
4. `plain-mental-model`: explain one new idea with a work-relevant analogy and a boundary.
5. `guided-demo`: run the smallest complete example while showing input, action, output, and check.
6. `failure-diagnosis`: deliberately break it; ask the learner to predict the signal before revealing it.
7. `learner-practice`: provide a partially completed task, not a second passive demo.
8. `transfer-challenge`: change one business condition, dataset, system, or policy so copying is insufficient.
9. `artifact-handoff`: give the Skill/template/data/checklist, exact run path, verification, limits, and next lesson.

For a 60-90 second concept preview, compress the same logic to: low-barrier or self-diagnosis hook -> one problem -> one model or analogy -> one example -> one audience choice -> one take-away rule. The preview attracts and diagnoses; it does not replace the runnable lab lesson.

The transfer stage must record `source_context`, `target_context`, `invariant`, `must_change` (at least two adaptations), and `success_criterion`. The target must agree with the course manifest. A stage label plus generic prose is not transfer evidence.

## Interaction and pacing

- Put visible evidence before architecture exposition.
- Explain a term only when the learner needs it to complete the next action.
- Insert a prediction, choice, diagnosis, or retrieval prompt at least every two conceptual segments.
- Prefer short chapters with one complete action; split when a segment introduces a second independent outcome.
- Use screen recordings, code, data, diagrams, and before/after artifacts only when they support the current decision.
- Editing energy is not learning evidence. Retention claims require measured learner data.

## Beginner scaffolding

For `L1`:

- start from a prepared fixture;
- show exact commands and expected output;
- annotate the first successful example;
- provide one meaningful mutation;
- provide a reset path;
- avoid hidden credentials;
- state what the AI cannot decide.

Fade support across levels: completed example -> missing step -> failure diagnosis -> transfer to a new context -> integrated production workflow.

## Material handoff

Every downloadable artifact must appear in `materials/material-provenance.json` with:

`material_id,path,purpose,source_ids,scenario_ids,generated_from,license_or_usage,validation_status,validation_evidence,contains_synthetic_data,limitations`

The lesson must show where the material fits, how to run it, what success looks like, how it fails, and what the learner is expected to modify.

## Presentation quality gate

Reject or rewrite when:

- the hook is a generic promise rather than a visible professional problem;
- more than two consecutive stages are passive explanation;
- no learner prediction or action occurs;
- the failure is cosmetic or unrelated to the acceptance criterion;
- the transfer task can be completed by replacing nouns in the prompt;
- downloadable files are mentioned but not mapped, licensed, and validated;
- the video claims “学会”“提升”“有效” without learner or workflow evidence.
