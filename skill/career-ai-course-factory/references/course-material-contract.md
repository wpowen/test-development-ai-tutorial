# AI-Native Course and Material Contract

## Career package

```text
career-package/
├── career-profile.md
├── tasks.json
├── curriculum.json
├── course-map.md
├── human-review/                 # primary interface for user review
│   ├── README.md
│   ├── 01-调研思路与主要结论.md
│   ├── 02-成果清单与课程地图.md
│   └── 03-细化样课.md
├── tutorial/                     # primary learner-facing product
│   ├── README.md
│   ├── course-tree.md
│   ├── page-template.md
│   ├── tutorial-site.json
│   └── index.html                # self-contained, opens without a server
├── research/
│   ├── source-ledger.csv
│   ├── search-plan.json
│   ├── search-log.csv
│   ├── channel-coverage.json
│   ├── profession-map.json
│   ├── github-artifacts.csv
│   ├── github-runs/               # structured run evidence for selected repositories
│   ├── job-signals.csv
│   ├── learner-signals.csv
│   ├── technology-radar.json
│   ├── scenarios.json
│   ├── evidence-matrix.md
│   ├── competitor-matrix.csv
│   └── ai-capability-map.md
├── tools/tool-registry.json
├── courses/<course-id>/
│   ├── course-manifest.json
│   ├── course.md
│   ├── lab/                       # runnable default path
│   ├── materials/
│   │   ├── quickstart.md
│   │   ├── reusable-skill.md
│   │   ├── sample-input.md
│   │   ├── expected-output.md
│   │   ├── verification-checklist.md
│   │   └── material-provenance.json
│   ├── evidence/execution-evidence.json
│   └── video/
│       ├── brief.md
│       ├── script.md
│       ├── storyboard.md
│       └── lesson-experience.json
├── validation-report.md
└── update-log.md
```

## Course manifest

Each exemplar has machine-readable fields:

```json
{
  "course_id": "stable-id",
  "title": "AI-native outcome",
  "scenario_ids": ["stable-scenario-id"],
  "ai_lane": "test-ai-systems",
  "ai_centrality_score": 5,
  "professional_value_score": 5,
  "system_under_test": "RAG customer-support assistant",
  "ai_roles": ["system-under-test", "judge"],
  "learner_artifact": ["eval dataset", "CI gate", "failure report"],
  "tool_adapters": ["promptfoo", "offline-snapshot"],
  "default_path_requires_credentials": false,
  "baseline_comparison": true,
  "failure_injection": true,
  "execution_proof": "evidence/execution-evidence.json",
  "status": "fixture-tested",
  "evidence_ids": ["S01"]
}
```

## Human-readable review contract

Do not hand a user a directory of JSON and CSV files as the result. The four files under `human-review/` are mandatory for a complete package and must be written as coherent reader-facing Chinese when the user works in Chinese.

The review layer summarizes machine evidence without hiding its status. It must let a reviewer answer, without opening JSON:

1. How was the profession decomposed and searched?
2. What conclusions are evidence, inference, or unknown?
3. What work domains, scenarios, and course opportunities were found?
4. Which courses are only planned and which were actually run?
5. What exactly happens in the refined lesson, what does the learner do, and how is success checked?

JSON/CSV remain the source of truth for validation; Markdown is the source of truth for human review. When they conflict, fail validation and repair the human summary.

The learner-facing source of truth is the tutorial viewer and its course tree. Human-review files explain the research and product decision; tutorial files deliver the learning experience. A complete package needs both.

## Course lesson requirements

`course.md` must contain:

- learner and prerequisites;
- profession-specific problem and AI centrality proof;
- system under test or AI-enabled workflow;
- baseline and target state;
- input, dataset, model/tool adapter, and output contracts;
- exact commands or interaction steps;
- metrics and decision thresholds;
- traceability from source/problem to checks;
- human review gate and privacy boundary;
- AI-specific failure modes;
- failure injection and expected red result;
- repair and expected green result;
- exercise, learner artifact, assessment, and next course;
- evidence status and what was not tested.

The lesson experience must follow `teaching-experience-protocol.md`: visible failure, stakes, before/after, one plain mental model, guided demo, deliberate failure diagnosis, learner practice, transfer challenge, and artifact handoff. The machine-readable arc lives in `video/lesson-experience.json`.

Each required `course.md` section needs substantive, section-specific content; the Commands section contains a runnable code block and Failure injection defines an observable failing result. Marker headings and long generic prose do not satisfy the contract.

## Runnable material gate

The default path must work without hidden context. Supply:

1. sanitized or synthetic input/data;
2. pinned tool/model version or access date;
3. install and run commands;
4. expected machine-readable output;
5. a meaningful defect/mutation command;
6. expected failing evidence;
7. repair/reset path;
8. verification checklist;
9. optional live adapter when credentials are needed;
10. explicit limits of fixture, live, and practitioner evidence.

Every learner-facing file must be listed in `materials/material-provenance.json` with its source IDs, scenario IDs, generation lineage, usage/license boundary, validation status and evidence, synthetic-data flag, and limitations.

“Paste this prompt into any AI” is not a runnable lab unless the lesson specifically evaluates prompt behavior across defined cases and versions.

## Video contract

The video must visibly show:

- the professional failure or risk;
- the AI system/workflow and input;
- the artifact or metric produced;
- a deliberate regression causing a red result;
- the repair and green result;
- what the learner can download and run;
- the human decision that AI cannot make.

Do not show illustrative UI as execution proof. Do not use “实测有效” unless the preserved evidence supports that exact scope.
