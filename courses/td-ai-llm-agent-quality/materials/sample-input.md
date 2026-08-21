# Synthetic sample input

TD-T13 输入是合成的退款 Agent 版本实验：dataset=`refund-v1`、Prompt=`p1`、retriever=`r1`、tools=`read-only`、scorer=`s1`、repeats=3，候选只允许改变 model。候选版本的 blockers 必须为 0；如果同时改 model 和 retriever，就应由 `SINGLE-VARIABLE` 阻断，而不是把结果归因给模型。
