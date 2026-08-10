#!/usr/bin/env python3
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1] / "data"
shutil.copyfile(root / "candidate-regressed.jsonl", root / "candidate-current.jsonl")
print("injected hallucination, citation, refusal, tool-use, latency, and cost regressions")
