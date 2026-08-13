# 讲解脚本

1. **cold-open-failure**：展示 TD-AG-02 的禁止工具调用和 `failed_oracle_ids`，问“最终回答正确，为什么仍必须失败？”
2. **stakes-and-promise**：说明架构边界、独立 Oracle 和四证据环，交付 11 页 artifact 链。
3. **before-after**：对比只验文本与 outcome/step/trajectory + 权限/状态/业务 Oracle。
4. **plain-mental-model**：把 Agent 讲成会调用工具的实习生，把 trace 讲成工作记录、Oracle 讲成验收单、owner 讲成签字人。
5. **guided-demo**：运行 TD-AG-00 baseline，打开状态和 Oracle，再运行 fault。
6. **failure-diagnosis**：用 `failed_oracle_ids` 回到首个破坏点，不接受“模型不稳定”的空泛归因。
7. **learner-practice**：恢复 repair，检查权限、预算、stop_state 和 Evidence/Inference/Unknown。
8. **transfer-challenge**：迁移到内部事故总结 Agent，重做业务 Oracle、风险总体、工具权限和 rollback。
9. **artifact-handoff**：展示 course manifest、研究九件包、报告和 NOT_RUN 边界。
