#!/usr/bin/env python3
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1] / "data"
shutil.copyfile(root / "candidate-good.jsonl", root / "candidate-current.jsonl")
print("candidate-current.jsonl reset to known-good snapshot")
