# TD-QP02 GitLab SHA/JUnit SOP

以 `project_id+mr_iid+commit_sha+run_id` 触发并回读 Pipeline、Job 和 JUnit artifact。先比较当前 HEAD，再校验 artifact hash、producer、必跑套件和 failed count；缺报告、旧 SHA、pipeline 不一致都 fail-closed。状态只写当前 SHA，不能由旧绿色状态覆盖新提交。
