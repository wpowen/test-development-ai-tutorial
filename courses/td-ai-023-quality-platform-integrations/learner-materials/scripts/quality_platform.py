"""Public, standalone learner runner; Python standard library only."""
import argparse, hashlib, hmac, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOOD, OLD = "a" * 40, "b" * 40

def state(mutation=None):
    body = json.dumps({"id":"jira-evt-42","issue":"PROJ-42"}, sort_keys=True).encode(); secret = b"fixture-webhook-secret"
    signature = hmac.new(secret, body, hashlib.sha256).hexdigest()
    s = {"webhook":{"verified":hmac.compare_digest(signature, hmac.new(secret, body, hashlib.sha256).hexdigest())},"inbox":{"accepted":1,"duplicates":1},"candidate":{"approved":True,"auto":False},"run":{"sha":GOOD},"gitlab":{"head":GOOD},"junit":{"present":True,"failed":0},"k8s":{"namespace":"quality-run-42","roles":["namespace-job-runner"],"ttl":900},"writeback":{"jira":1,"gitlab":1},"notice":"PROJ-42 sha aaaaaaaa PASS artifact://junit/run-42","audit":{"previous":"genesis","event":"gate:PASS"}}
    if mutation == "stale_sha": s["run"]["sha"] = OLD
    if mutation == "replay": s["inbox"]["accepted"] = 2
    if mutation == "rbac": s["k8s"]["roles"].append("cluster-admin")
    if mutation == "missing-report": s["junit"]["present"] = False
    s["audit"]["hash"] = hashlib.sha256((s["audit"]["previous"] + s["audit"]["event"]).encode()).hexdigest()
    return s

def check(s):
    expected_audit = hashlib.sha256((s["audit"]["previous"] + s["audit"]["event"]).encode()).hexdigest()
    checks = [("WEBHOOK-SIGNATURE", s["webhook"]["verified"]), ("INBOX-DEDUPE", s["inbox"] == {"accepted":1,"duplicates":1}), ("AI-HUMAN-BOUNDARY", s["candidate"] == {"approved":True,"auto":False}), ("SHA-BINDING", s["run"]["sha"] == s["gitlab"]["head"]), ("JUNIT-COMPLETE", s["junit"] == {"present":True,"failed":0}), ("K8S-BOUNDARY", s["k8s"]["namespace"] != "default" and "cluster-admin" not in s["k8s"]["roles"] and s["k8s"]["ttl"] > 0), ("WRITEBACK-IDEMPOTENCY", s["writeback"] == {"jira":1,"gitlab":1}), ("NOTIFICATION-REDACTION", "token" not in s["notice"].lower() and "secret" not in s["notice"].lower()), ("AUDIT-CHAIN", s["audit"]["hash"] == expected_audit)]
    return [{"oracle_id": k, "passed": bool(v)} for k, v in checks]

def main():
    p = argparse.ArgumentParser(); p.add_argument("mode", choices=["baseline","mutation","repair","replay","rbac","missing-report"]); p.add_argument("--report", required=True); a = p.parse_args()
    mutation = {"mutation":"stale_sha","replay":"replay","rbac":"rbac","missing-report":"missing-report"}.get(a.mode)
    r = check(state(mutation)); failed = [x["oracle_id"] for x in r if not x["passed"]]
    out = {"mode":a.mode,"verdict":"PASS" if not failed else "FAIL","exit_code":0 if not failed else 1,"failed_oracle_ids":failed,"checks":r,"state":state(mutation),"not_run":["live Jira/GitLab/K8s/ChatOps","real model","tier/version compatibility"]}
    path = ROOT / a.report; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(out, indent=2)+"\n")
    print(json.dumps({"verdict":out["verdict"],"failed_oracle_ids":failed}))
    return out["exit_code"]

if __name__ == "__main__": raise SystemExit(main())
