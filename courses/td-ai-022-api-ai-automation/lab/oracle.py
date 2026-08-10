"""Independent release rules: deliberately does not import or inspect the service implementation."""

def check_case(case, actual):
    issues = []
    kind = case["kind"]
    if kind == "contract":
        if case["operation_id"] not in {"cancelOrder", "getTask", "orderEvents"}:
            issues.append("operationId missing")
    elif kind in {"business", "permission", "idempotency"}:
        if set(actual) < {"status", "refund_count", "state"}:
            issues.append("schema oracle failed")
        elif not isinstance(actual["status"], int) or not isinstance(actual["refund_count"], int):
            issues.append("schema type oracle failed")
        for key, expected in case["expected"].items():
            if actual.get(key) != expected:
                issues.append(f"{key}: expected {expected!r}, actual {actual.get(key)!r}")
    elif kind == "async":
        if actual != case["expected"]["states"]:
            issues.append("illegal async transition")
    elif kind == "sse":
        if [e["type"] for e in actual] != case["expected"]["events"]:
            issues.append("SSE event order/type oracle failed")
        if sum(e["terminal"] for e in actual) != case["expected"]["terminal_count"]:
            issues.append("SSE terminal cardinality oracle failed")
    return issues
