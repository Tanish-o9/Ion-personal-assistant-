import time
from typing import Dict, List
from collections import defaultdict
from orchestrator.observability import jarvis_logger

class SlidingWindowRateLimiter:
    """
    In-memory sliding window rate limiter for API endpoints and WebSocket messages.
    """
    def __init__(self):
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        """
        Checks if the request key has exceeded max_requests within window_seconds.
        """
        now = time.time()
        cutoff = now - window_seconds

        # Remove timestamps older than window_seconds
        timestamps = [ts for ts in self._requests[key] if ts > cutoff]
        self._requests[key] = timestamps

        if len(timestamps) >= max_requests:
            jarvis_logger.warning(
                f"Rate limit triggered for key '{key}' ({len(timestamps)}/{max_requests} reqs in {window_seconds}s)",
                extra={"event": "rate_limit_triggered", "key": key},
            )
            return False

        self._requests[key].append(now)
        return True

    def reset(self) -> None:
        self._requests.clear()

default_rate_limiter = SlidingWindowRateLimiter()
