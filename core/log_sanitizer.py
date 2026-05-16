import hashlib

def sanitize_data(data: dict) -> dict:
    record = data.copy()
    if "problem" in record and record["problem"]:
        record["problem"] = hashlib.sha256(record["problem"].encode()).hexdigest()[:16]
    if "code" in record and record["code"]:
        record["code"] = f"<code: {len(record['code'])} chars>"
    if "result" in record and isinstance(record["result"], str) and len(record["result"]) > 20:
        record["result"] = record["result"][:20] + "..."
    return record
