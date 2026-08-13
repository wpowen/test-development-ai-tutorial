#!/usr/bin/env python3
"""Deterministic TD-F01 capability self-check. No model or network is used."""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).parent
PHASE_INPUTS = {
    "baseline": ROOT / "inputs/learner-profile.json",
    "fault": ROOT / "inputs/learner-profile-fault.json",
    "repair": ROOT / "inputs/learner-profile-repair.json",
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate(profile, phase):
    checks = {
        "responsibility_is_risk_evidence": profile.get("responsibility") == "make_quality_risk_visible_and_decidable",
        "requirements_and_design_are_both_test_basis": set(profile.get("test_basis", [])) >= {"requirements", "technical_design"},
        "authority_conflicts_block_execution": profile.get("authority_conflict_action") == "BLOCKED",
        "independent_oracle": profile.get("oracle_source") not in {"implementation_output", "model_output", "same_function_under_test"},
        "method_follows_risk": profile.get("method_selection") == "risk_and_failure_mode",
        "artifacts_have_owner_and_consumer": bool(profile.get("artifact_owner")) and bool(profile.get("downstream_consumer")),
        "human_release_owner": profile.get("release_decider") == "named_human_owner",
        "ai_is_bounded": profile.get("ai_permission") == "candidate_generation_and_evidence_aggregation",
        "production_feedback_returns_to_assets": profile.get("production_feedback") == "regression_and_eval_assets",
    }
    failed = [name for name, passed in checks.items() if not passed]
    expected_failure = phase == "fault"
    status = "FAIL_EXPECTED" if failed and expected_failure else "PASS_FIXTURE" if not failed else "FAIL_UNEXPECTED"
    return {
        "page_id": "TD-F01",
        "phase": phase,
        "status": status,
        "provider": "none",
        "model_status": "NOT_RUN",
        "checks": checks,
        "failed_checks": failed,
        "evidence_boundary": "deterministic fixture only; no practitioner, integration, live, publication, or production evidence",
    }


def write_report(report_path, payload):
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_phase(phase, report_path):
    result = evaluate(load_json(PHASE_INPUTS[phase]), phase)
    write_report(report_path, result)
    print(json.dumps(result, ensure_ascii=False))
    return 1 if result["failed_checks"] else 0


def run_cycle(report_path):
    phase_reports = []
    phase_dir = Path(report_path).parent
    exit_codes = {}
    for phase in ("baseline", "fault", "repair"):
        result = evaluate(load_json(PHASE_INPUTS[phase]), phase)
        write_report(phase_dir / f"TD-F01-{phase}.json", result)
        phase_reports.append(result)
        exit_codes[phase] = 1 if result["failed_checks"] else 0
    cycle_ok = exit_codes == {"baseline": 0, "fault": 1, "repair": 0}
    cycle = {
        "page_id": "TD-F01",
        "status": "PASS_FIXTURE" if cycle_ok else "FAIL_UNEXPECTED",
        "expected_exit_codes": {"baseline": 0, "fault": 1, "repair": 0},
        "observed_exit_codes": exit_codes,
        "phases": phase_reports,
        "provider": "none",
        "model_status": "NOT_RUN",
        "evidence_boundary": "deterministic fixture only; no practitioner, integration, live, publication, or production evidence",
    }
    write_report(report_path, cycle)
    print(json.dumps(cycle, ensure_ascii=False))
    return 0 if cycle_ok else 1


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    phase = subparsers.add_parser("phase")
    phase.add_argument("--phase", choices=tuple(PHASE_INPUTS), required=True)
    phase.add_argument("--report", required=True)
    cycle = subparsers.add_parser("cycle")
    cycle.add_argument("--report", required=True)
    args = parser.parse_args()
    if args.command == "phase":
        raise SystemExit(run_phase(args.phase, args.report))
    raise SystemExit(run_cycle(args.report))


if __name__ == "__main__":
    main()
