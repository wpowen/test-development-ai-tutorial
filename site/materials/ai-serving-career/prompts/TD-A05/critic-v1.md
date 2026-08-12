# TD-A05 critic prompt v1

逐条检查来源、版本、独立 Oracle、Evidence/Inference/Unknown、成熟度和禁止承诺。必须拒绝：忽略 queue_time，仅因 GPU 利用率同步升高便把 root_cause 标为 gpu。 保留：托管服务内部队列、GPU profiler 和真实 KV cache eviction 不可见。
