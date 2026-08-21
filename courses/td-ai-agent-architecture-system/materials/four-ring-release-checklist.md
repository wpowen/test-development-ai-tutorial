# 四证据环发布检查单

1. Offline CI：确定性合同与独立 Oracle。
2. Sandbox replay：真实边界的隔离回放。
3. Shadow/Canary：真实流量但不可逆副作用隔离。
4. Online sampling：采样、回滚、人工 owner。

任何一环未执行，状态为 NOT_RUN；硬红线失败即 BLOCKED。
