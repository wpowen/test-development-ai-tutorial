"""Topic entry: least-privilege ephemeral namespace and bounded cleanup."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import quality_platform

state = quality_platform.state()
evidence = {"topic":"ephemeral-namespace-cleanup","namespace":state["k8s"]["namespace"],"ttl_seconds":state["k8s"]["ttl"],"roles":state["k8s"]["roles"],"isolated":state["k8s"]["namespace"] != "default","cluster_admin_denied":"cluster-admin" not in state["k8s"]["roles"],"cleanup":"owner+TTL"}
print(json.dumps(evidence, ensure_ascii=False))
raise SystemExit(0 if evidence["isolated"] and evidence["cluster_admin_denied"] and evidence["ttl_seconds"] > 0 else 1)
