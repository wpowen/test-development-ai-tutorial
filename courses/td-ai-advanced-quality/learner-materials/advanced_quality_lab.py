#!/usr/bin/env python3
"""Deterministic advanced-quality fixture runner. No model or network calls."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
TOPICS=["TD-X602","TD-X101","TD-X501","TD-X502","TD-X601","TD-X603","TD-X604","TD-X805"]
FAULTS={"TD-X602":"training_snapshot_drift","TD-X101":"unsigned_dependency","TD-X501":"cross_modal_mismatch","TD-X502":"locale_accessibility_gap","TD-X601":"aggregate_only_self_judge","TD-X603":"cross_user_stale_cache","TD-X604":"fallback_protocol_drift","TD-X805":"biased_sample_guardrail_regression"}

def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
def digest(p): return "sha256:"+hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def verify(topic):
    base=ROOT/"page-prompts"/topic
    names=["manifest.json","prompt-v1.md","critic-v1.md","input.json","schema.json","eval.json","mutation.json","model-config.json"]
    errors=[f"missing {n}" for n in names if not (base/n).is_file()]
    if errors:return errors
    m=load(f"page-prompts/{topic}/manifest.json")
    if m.get("version")!="1.0.0" or m.get("model_evidence")!="NOT_RUN":errors.append("manifest/version boundary")
    kinds={x.get("kind") for x in load(f"page-prompts/{topic}/eval.json").get("cases",[])}
    if kinds!={"positive","boundary","conflict","missing","unauthorized","refusal","truncation","paraphrase"}:errors.append("eval coverage")
    return errors

def run(topic,phase,report):
    errors=verify(topic)
    fault=phase=="fault"
    checks={
      "TD-X602":{"versions_pinned":not fault,"lineage_complete":not fault,"holdout_sealed":not fault,"rollback_candidate":True},
      "TD-X101":{"sbom_complete":True,"dependency_signed":not fault,"critical_findings_owned":not fault,"architecture_boundary_checked":True},
      "TD-X501":{"all_modalities_present":True,"cross_modal_alignment":not fault,"oracle_independent":not fault,"counterexample_preserved":True},
      "TD-X502":{"required_locales_covered":not fault,"keyboard_and_name_gate":not fault,"rtl_checked":True,"translation_owner":True},
      "TD-X601":{"group_slices_reported":not fault,"harm_blockers_separate":not fault,"independent_human_sample":not fault,"disagreement_preserved":True},
      "TD-X603":{"consent_and_ttl":True,"user_isolation":not fault,"cache_version_current":not fault,"deletion_receipt":True},
      "TD-X604":{"capability_match":not fault,"protocol_schema_pinned":not fault,"fallback_policy_preserved":not fault,"side_effect_gate":True},
      "TD-X805":{"assignment_integrity":not fault,"guardrails_pass":not fault,"human_sample_representative":not fault,"rollback_ready":True},
    }[topic]
    failed=[k for k,v in checks.items() if not v]
    status="FAIL" if failed else "PASS"
    payload={"schema_version":"1.0","topic_id":topic,"phase":phase,"status":status,"evidence_scope":"deterministic-offline-fixture","model_evidence":"NOT_RUN","prompt_manifest_hash":digest(f"page-prompts/{topic}/manifest.json"),"checks":checks,"failed_checks":failed,"fault_id":FAULTS[topic] if fault else None,"human_decision_required":True,"limitations":["synthetic inputs","no model/provider/production integration","no practitioner review"]}
    p=ROOT/report;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"topic":topic,"phase":phase,"status":status,"report":report},ensure_ascii=False))
    return 1 if failed else 0

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="cmd",required=True)
    s.add_parser("verify-packages")
    r=s.add_parser("run");r.add_argument("--topic",choices=TOPICS,required=True);r.add_argument("--phase",choices=["baseline","fault","repair"],required=True);r.add_argument("--report",required=True)
    q=s.add_parser("suite");q.add_argument("--phase",choices=["baseline","fault","repair"],required=True)
    a=p.parse_args()
    if a.cmd=="verify-packages":
      e={t:verify(t) for t in TOPICS};e={k:v for k,v in e.items() if v};print(json.dumps({"status":"PASS" if not e else "BLOCKED","model_evidence":"NOT_RUN","errors":e},ensure_ascii=False));return 0 if not e else 2
    if a.cmd=="run":return run(a.topic,a.phase,a.report)
    codes=[run(t,a.phase,f"reports/{t.lower()}-{a.phase}.json") for t in TOPICS]
    return 1 if a.phase=="fault" and all(c==1 for c in codes) else (0 if a.phase!="fault" and all(c==0 for c in codes) else 2)
if __name__=="__main__":raise SystemExit(main())

