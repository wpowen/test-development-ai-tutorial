# Advanced Quality fixture lab

Run `python3 advanced_quality_lab.py verify-packages`, then `suite --phase baseline`, `suite --phase fault`, and `suite --phase repair`. Expected suite exits are 0/1/0. The lab is deterministic and stdlib-only; it does not call a model, provider, online experiment, accessibility device, security scanner, or production system. Each fault is a negative control, not proof of production fairness, safety, reliability, or business efficacy.

