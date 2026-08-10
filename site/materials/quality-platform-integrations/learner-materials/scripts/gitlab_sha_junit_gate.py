"""Topic entry: current GitLab HEAD binding and JUnit completeness gate."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import quality_platform

state = quality_platform.state()
evidence = {"topic":"gitlab-sha-junit","commit_sha":state["run"]["sha"],"head_sha":state["gitlab"]["head"],"sha_matches":state["run"]["sha"] == state["gitlab"]["head"],"junit_present":state["junit"]["present"],"junit_failed":state["junit"]["failed"]}
print(json.dumps(evidence, ensure_ascii=False))
raise SystemExit(0 if evidence["sha_matches"] and evidence["junit_present"] and evidence["junit_failed"] == 0 else 1)
