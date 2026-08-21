"""Deterministic offline labs for LLM/Judge/Agent/Workflow quality pages."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ("TD-T13", "TD-T14", "TD-T15", "TD-T16", "TD-T17", "TD-T18", "TD-T19", "TD-W01", "TD-W02", "TD-W03")

BASELINES: dict[str, dict[str, Any]] = {
    "TD-T13": {"locks":{"dataset":"v1","prompt":"p1","retriever":"r1","tools":"read-only","scorer":"s1"},"candidate":{"changed":["model"],"blockers":0},"repeats":3},
    "TD-T14": {"human":{"double_labeled":True,"agreement":0.8},"judge":{"order_ab":"A","order_ba":"A","fact_blocker_caught":True,"self_approval":False}},
    "TD-T15": {"outcome":{"correct":True},"steps":{"prohibited_calls":0,"authorized":True},"trajectory":{"terminated":True,"budget_ok":True,"trace_complete":True}},
    "TD-T16": {"identity":{"user_verified":True,"scope":"refund:propose"},"call":{"tool":"refund_proposal","amount":10,"idempotency_key":"r-42","write_executed":False},"approval":{"human":True}},
    "TD-T17": {"input":{"untrusted":True},"retrieval":{"tenant":"tenant-a"},"tool":{"scope":"order:read:self","write_executed":False},"output":{"secret":False,"cross_tenant":False}},
    "TD-T18": {"plan":{"risk_id":"REFUND-07"},"test":{"business_oracle":"state=manual_review","kills_backend_fault":True,"trace":True},"browser":{"sandbox":True,"write_permission":False}},
    "TD-T19": {"patch":{"locator_only":True,"oracle_deleted":False,"expected_changed":False},"regression":{"kills_known_mutation":True},"approval":{"human_required":True}},
    "TD-W01": {"components":{"router":"workflow","policy_selector":"agent","audit_writer":"worker"},"state_owners":{"workflow":"orchestrator","worker":"queue","agent":"agent-loop"}},
    "TD-W02": {"message":{"id":"msg-42","deliveries":2},"effect":{"idempotency_key":"audit-42","writes":1},"loop":{"iterations":4,"max_iterations":5,"stop_reason":"human_handoff"},"handoff":{"owner":"reviewer"}},
    "TD-W03": {"single":{"token_budget":1000,"tool_scope":"read","tasks":20},"multi":{"token_budget":1000,"tool_scope":"read","tasks":20},"repeats":5,"human_interventions":0},
}

def state(topic: str, mode: str) -> dict[str, Any]:
    value = copy.deepcopy(BASELINES[topic])
    if mode != "fault":
        return value
    if topic == "TD-T13": value["candidate"]["changed"] = ["model", "retriever"]
    elif topic == "TD-T14": value["judge"]["order_ba"] = "B"; value["judge"]["fact_blocker_caught"] = False
    elif topic == "TD-T15": value["steps"]["prohibited_calls"] = 1
    elif topic == "TD-T16": value["identity"]["user_verified"] = False; value["call"]["write_executed"] = True
    elif topic == "TD-T17": value["output"]["cross_tenant"] = True; value["tool"]["write_executed"] = True
    elif topic == "TD-T18": value["test"]["business_oracle"] = "button_visible"; value["test"]["kills_backend_fault"] = False
    elif topic == "TD-T19": value["patch"]["oracle_deleted"] = True; value["regression"]["kills_known_mutation"] = False
    elif topic == "TD-W01": value["components"]["audit_writer"] = "agent"
    elif topic == "TD-W02": value["effect"]["writes"] = 2; value["loop"]["iterations"] = 7; value["loop"]["stop_reason"] = None
    elif topic == "TD-W03": value["multi"]["token_budget"] = 2000
    return value

def checks(topic: str, s: dict[str, Any]) -> dict[str, bool]:
    if topic == "TD-T13": return {"SINGLE-VARIABLE":len(s["candidate"]["changed"])==1,"LOCKS-COMPLETE":len(s["locks"])==5,"RISK-BLOCKER":s["candidate"]["blockers"]==0,"REPEATED-RUNS":s["repeats"]>=3}
    if topic == "TD-T14": return {"HUMAN-CALIBRATION":s["human"]["double_labeled"],"POSITION-STABLE":s["judge"]["order_ab"]==s["judge"]["order_ba"],"FACT-BLOCKER":s["judge"]["fact_blocker_caught"],"NO-SELF-APPROVAL":not s["judge"]["self_approval"]}
    if topic == "TD-T15": return {"OUTCOME":s["outcome"]["correct"],"STEP-SAFETY":s["steps"]["prohibited_calls"]==0 and s["steps"]["authorized"],"TRAJECTORY":all(s["trajectory"].values())}
    if topic == "TD-T16": return {"AUTH-BEFORE-ACTION":s["identity"]["user_verified"],"LEAST-PRIVILEGE":s["identity"]["scope"]=="refund:propose","NO-DIRECT-WRITE":not s["call"]["write_executed"],"HUMAN-APPROVAL":s["approval"]["human"]}
    if topic == "TD-T17": return {"TENANT-ISOLATION":not s["output"]["cross_tenant"],"NO-SECRET":not s["output"]["secret"],"NO-WRITE":not s["tool"]["write_executed"],"MIN-SCOPE":s["tool"]["scope"]=="order:read:self"}
    if topic == "TD-T18": return {"RISK-TRACE":bool(s["plan"]["risk_id"]),"BUSINESS-ORACLE":s["test"]["business_oracle"]=="state=manual_review","MUTATION-KILLED":s["test"]["kills_backend_fault"],"SANDBOX":s["browser"]["sandbox"] and not s["browser"]["write_permission"]}
    if topic == "TD-T19": return {"LOCATOR-ONLY":s["patch"]["locator_only"],"ORACLE-PRESERVED":not s["patch"]["oracle_deleted"] and not s["patch"]["expected_changed"],"MUTATION-KILLED":s["regression"]["kills_known_mutation"],"HUMAN-GATE":s["approval"]["human_required"]}
    if topic == "TD-W01": return {"ROUTER-CLASSIFIED":s["components"]["router"]=="workflow","AGENT-CLASSIFIED":s["components"]["policy_selector"]=="agent","WORKER-CLASSIFIED":s["components"]["audit_writer"]=="worker","STATE-OWNERS":len(set(s["state_owners"].values()))==3}
    if topic == "TD-W02": return {"IDEMPOTENT-EFFECT":s["effect"]["writes"]==1,"BOUNDED-LOOP":s["loop"]["iterations"]<=s["loop"]["max_iterations"],"STOP-RECORDED":bool(s["loop"]["stop_reason"]),"HANDOFF-OWNER":bool(s["handoff"]["owner"])}
    return {"SAME-TOKEN-BUDGET":s["single"]["token_budget"]==s["multi"]["token_budget"],"SAME-TOOLS":s["single"]["tool_scope"]==s["multi"]["tool_scope"],"SAME-TASKS":s["single"]["tasks"]==s["multi"]["tasks"],"REPEATED":s["repeats"]>=3,"NO-HUMAN-CONFOUND":s["human_interventions"]==0}

def report(topic: str, mode: str) -> dict[str, Any]:
    s=state(topic,mode); result=[{"oracle_id":k,"passed":bool(v)} for k,v in checks(topic,s).items()]; failed=[x["oracle_id"] for x in result if not x["passed"]]
    return {"topic_id":topic,"mode":mode,"maturity":"fixture-tested","verdict":"PASS" if not failed else "FAIL","expected_exit_code":0 if not failed else 1,"failed_oracle_ids":failed,"state_hash":hashlib.sha256(json.dumps(s,sort_keys=True,separators=(",",":")).encode()).hexdigest(),"checks":result,"state":s,"not_run":["live model","live browser agent","live tool backend","live queue","practitioner review"]}

def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--topic",choices=TOPICS,required=True); p.add_argument("--phase",choices=["baseline","fault","repair","cycle"],required=True); p.add_argument("--report"); p.add_argument("--report-dir"); a=p.parse_args()
    if a.phase=="cycle":
        if not a.report_dir: p.error("cycle requires --report-dir")
        target=ROOT/a.report_dir; observed=[]
        for phase in ("baseline","fault","repair"):
            r=report(a.topic,phase); write(target/(phase+".json"),r); observed.append(r["expected_exit_code"])
        summary={"topic_id":a.topic,"observed_exit_codes":observed,"expected_exit_codes":[0,1,0],"verdict":"PASS" if observed==[0,1,0] else "FAIL","maturity":"fixture-tested"}; write(target/"cycle-summary.json",summary); print(json.dumps(summary)); return 0 if summary["verdict"]=="PASS" else 1
    if not a.report: p.error("single phase requires --report")
    r=report(a.topic,a.phase); write(ROOT/a.report,r); print(json.dumps({"topic_id":a.topic,"phase":a.phase,"verdict":r["verdict"],"failed":r["failed_oracle_ids"]})); return r["expected_exit_code"]

if __name__=="__main__": raise SystemExit(main())
