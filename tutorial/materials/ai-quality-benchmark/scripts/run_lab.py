#!/usr/bin/env python3
"""Deterministic quality/benchmark contract lab; no model or network calls."""
import argparse, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--topic",required=True); parser.add_argument("--phase",choices=("baseline","fault","repair"),required=True); args=parser.parse_args()
    contracts=json.loads((ROOT/"configs/topic-contracts.json").read_text(encoding="utf-8"))
    if args.topic not in contracts: raise SystemExit(f"unknown topic: {args.topic}")
    contract=contracts[args.topic]; observed=dict(contract["baseline_observations"]); injected=None
    if args.phase=="fault":
        injected=contract["mutation"]; observed[injected["field"]]=injected["fault_value"]
    checks=[{"field":field,"expected":expected,"actual":observed.get(field),"status":"PASS" if observed.get(field)==expected else "FAIL"} for field,expected in contract["expected"].items()]
    verdict="PASS" if all(row["status"]=="PASS" for row in checks) else "FAIL"
    report={"schema_version":"1.0.0","topic_id":args.topic,"phase":args.phase,"evidence_level":"offline-deterministic-fixture","release_candidate_level":"fixture-only","model_execution":"NOT_RUN","enterprise_integration":"NOT_RUN","practitioner_review":"NOT_RUN","publication":"NOT_RUN","production":"NOT_RUN","verdict":verdict,"decision":contract["decision"],"checks":checks,"injected_mutation":injected,"remaining_unknowns":contract["remaining_unknowns"]}
    target=ROOT/"reports"/args.topic/f"{args.phase}.json"; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"topic_id":args.topic,"phase":args.phase,"verdict":verdict,"report":str(target.relative_to(ROOT))},ensure_ascii=False)); return 0 if verdict=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())
