import json
from datetime import datetime
from core.log_sanitizer import sanitize_data

class MetricsLogger:
    def __init__(self, log_file: str = "metrics.jsonl"):
        self.log_file = log_file

    def log(self, data: dict):
        record = sanitize_data(data)
        record["timestamp"] = datetime.now().isoformat()
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
