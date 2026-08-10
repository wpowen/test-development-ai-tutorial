#!/usr/bin/env python3
"""Create an honest, incomplete shell for an AI-native career course package."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path


LEDGER_COLUMNS = ["id", "title", "creator", "source_type", "platform", "language", "year", "url", "access_date", "evidence_tier", "relevance", "credibility", "used_for", "limitations"]
COMPETITOR_COLUMNS = ["id", "platform", "offering", "audience", "promise", "ai_lane", "modules", "hands_on_artifact", "execution_proof", "assessment", "freshness", "commercial_model", "url", "access_date", "gap", "claim_status"]
SEARCH_LOG_COLUMNS = ["id", "query", "language", "research_lane", "surface_attempt_id", "search_surface", "run_at", "result_count", "selected_source_ids", "opened_urls", "exclusion_notes", "status"]
COVERAGE_COLUMNS = ["cell_id", "profession_domain_id", "layer_kind", "specialization_kind", "learner_level", "topic", "required_by_source_ids", "competitor_ids", "course_ids", "learner_artifact", "exit_assessment", "evidence_status", "coverage_status", "priority", "gap_reason", "decision"]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--career-slug", required=True)
    parser.add_argument("--career-name", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.output
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty directory: {root}")
    root.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    write(root / "career-profile.md", f"# {args.career_name} × AI\n\nStatus: scaffold; research not run.\n\n## Role reality\n\nTODO\n\n## AI transformation thesis\n\nTODO\n\n## Boundaries\n\nTODO")
    write(root / "course-map.md", f"# {args.career_name} × AI course map\n\nNo course has passed AI-centrality or utility gates.")
    write(root / "learning-architecture.md", f"""# {args.career_name} × AI learning architecture

Status: scaffold; research not run.

## Learner transformation

TODO

## Professional baseline

TODO

## AI foundations

TODO

## Capability transition matrix

TODO

## Learning stages

TODO

## Specialization tracks

TODO

## Benchmark literacy

TODO

## Exit gates

TODO
""")
    write(root / "curriculum-gap-analysis.md", f"""# {args.career_name} × AI curriculum gap analysis

Status: scaffold; the six-system audit has not run.

## Research corpus

TODO

## Industry body of knowledge

TODO

## Real work and practitioner evidence

TODO

## Existing course supply

TODO

## AI technology and benchmark frontier

TODO

## Coverage matrix

TODO

## Missing and overrepresented topics

TODO

## Expert review

### Profession veteran

TODO

### AI systems engineer

TODO

### Evaluation and quality expert

TODO

### Curriculum designer

TODO

### Market and learner researcher

TODO

### Adversarial critic

TODO

## Curriculum decisions

TODO

## Remaining unknowns

Research and review have not run.
""")
    write(root / "research/evidence-matrix.md", "# Evidence matrix\n\n## Evidence\n\nNone.\n\n## Competitor observations\n\nNone.\n\n## Vendor claims\n\nNone.\n\n## Inference\n\nNone.\n\n## Unknown\n\nResearch not run.")
    write(root / "research/ai-capability-map.md", "# AI capability map\n\n- use-ai-for-work: TODO\n- test-ai-systems: TODO\n- agentize-work: TODO\n- build-ai-quality-system: TODO")
    for path, columns in [
        (root / "research/source-ledger.csv", LEDGER_COLUMNS),
        (root / "research/competitor-matrix.csv", COMPETITOR_COLUMNS),
        (root / "research/search-log.csv", SEARCH_LOG_COLUMNS),
        (root / "research/curriculum-coverage-matrix.csv", COVERAGE_COLUMNS),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            csv.writer(handle).writerow(columns)
    write(root / "research/search-plan.json", json.dumps({
        "profession": args.career_slug,
        "generated_at": today,
        "research_question": f"How AI changes {args.career_name}",
        "freshness_required": True,
        "run_scope": "full",
        "available_surfaces": [],
        "query_families": [],
        "freshness_policy": [],
        "stop_conditions": ["BLOCKED-FRESHNESS"],
        "run_status": "planned",
    }, ensure_ascii=False, indent=2))
    write(root / "research/technology-radar.json", json.dumps({"profession": args.career_slug, "technologies": []}, ensure_ascii=False, indent=2))
    write(root / "research/scenarios.json", json.dumps({"profession": args.career_slug, "scenarios": []}, ensure_ascii=False, indent=2))
    write(root / "research/competency-transition-map.json", json.dumps({
        "profession_id": args.career_slug,
        "architecture_profile": "ai-enabled-practitioner",
        "audience": "TODO",
        "as_of": today,
        "professional_baseline": {},
        "ai_foundations": {},
        "transition_matrix": [],
        "learning_stages": [],
        "specialization_tracks": [],
        "source_ids": [],
    }, ensure_ascii=False, indent=2))
    (root / "courses").mkdir()
    write(root / "tasks.json", json.dumps({"career_id": args.career_slug, "tasks": []}, ensure_ascii=False, indent=2))
    write(root / "curriculum.json", json.dumps({"career_id": args.career_slug, "courses": []}, ensure_ascii=False, indent=2))
    write(root / "tools/tool-registry.json", json.dumps({"last_verified": today, "tools": []}, ensure_ascii=False, indent=2))
    write(root / "validation-report.md", "# Validation report\n\nVerdict: FAIL-STRUCTURE (scaffold only).\n\n## Evidence\n\nNone.\n\n## Inference\n\nNone.\n\n## Unknown\n\nAll professional and AI claims.\n\n## Professional utility verdict\n\nNot evaluated.\n\n## Not tested\n\nResearch, lab, model, and practitioner review.")
    write(root / "update-log.md", f"# Update log\n\n- {today}: Created fail-closed AI-native scaffold.")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
