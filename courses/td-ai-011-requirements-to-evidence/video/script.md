# 视频脚本

“三份文档放进模型，十秒就能得到测试用例。但 PRD 说已发货不能取消，旧技术方案说可以。你让谁来决定？”

运行冲突命令，展示 `BLOCKED/2`。打开 Requirement Contract，指出每条规则的 source_ref 和 UNKNOWN。再运行 baseline、mutation、repair，展示 409 被错误改成 202 时测试返回 1。最后说明：AI 负责提取和生成候选；业务规则、关键 Oracle 和发布由责任人决定。
