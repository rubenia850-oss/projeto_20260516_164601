import time
from typing import Dict, Any, Optional
from langgraph.checkpoint.memory import MemorySaver

class ManagedMemorySaver:
    def __init__(self, max_checkpoints_per_thread: int = 50, ttl_seconds: int = 3600):
        self.memory = MemorySaver()
        self.max_checkpoints = max_checkpoints_per_thread
        self.ttl = ttl_seconds
        self._access_times: Dict[str, float] = {}

    def get(self, config: Dict[str, Any]) -> Optional[Any]:
        thread_id = config.get("configurable", {}).get("thread_id")
        if thread_id:
            self._touch(thread_id)
            self._prune(thread_id)
        return self.memory.get(config)

    def put(self, config: Dict[str, Any], state: Any) -> None:
        thread_id = config.get("configurable", {}).get("thread_id")
        if thread_id:
            self._touch(thread_id)
            self._prune(thread_id)
        self.memory.put(config, state)

    def _touch(self, thread_id: str):
        self._access_times[thread_id] = time.time()

    def _prune(self, thread_id: str):
        now = time.time()
        expired = [tid for tid, t in self._access_times.items() if now - t > self.ttl]
        for tid in expired:
            self._access_times.pop(tid, None)
