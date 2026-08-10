# Offline RAG/LLM Quality Gate Lab

This lab proves the evaluation workflow without an API key. It evaluates recorded candidate outputs, injects a meaningful regression, and requires the gate to turn red.

```bash
python3 scripts/reset_candidate.py
python3 scripts/evaluate.py --report reports/baseline.json
python3 scripts/inject_regression.py
python3 scripts/evaluate.py --report reports/mutation.json
python3 scripts/reset_candidate.py
python3 scripts/evaluate.py --report reports/repair.json
```

The second evaluator command must exit non-zero. A snapshot run proves the harness and test sensitivity; it does not prove a live model's quality.
