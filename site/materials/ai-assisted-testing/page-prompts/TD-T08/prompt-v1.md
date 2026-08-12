# TD-T08 failure clusterer v1

输入是脱敏且不可改写的 failure events。按 trace、时间窗、commit、environment 和症状生成候选簇；每簇输出 raw_event_refs、symptom、hypothesis、confidence、competing_hypotheses、next_experiment、owner。相似性只能产生假设，不能产生 verified cause。引用缺失、版本混合或实验未运行时 cause_status 必须为 `UNKNOWN`。
