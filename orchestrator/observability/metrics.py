import time
from typing import Dict, Any
from collections import defaultdict

class MetricsCollector:
    """
    Centralized metrics collection system for API requests, LLM calls, tools, background jobs, WebSockets, Cache, and Agent Learning.
    """
    def __init__(self):
        # Request metrics
        self.request_count = defaultdict(int)       # (endpoint, status) -> count
        self.request_latency_sum = defaultdict(float) # endpoint -> total_ms
        self.request_errors = defaultdict(int)      # endpoint -> count

        # LLM metrics
        self.llm_requests = 0
        self.llm_failures = 0
        self.llm_fallbacks = 0
        self.llm_latency_sum = 0.0

        # Tool metrics
        self.tool_calls = defaultdict(int)         # tool_name -> count
        self.tool_failures = defaultdict(int)      # tool_name -> count
        self.tool_latency_sum = defaultdict(float) # tool_name -> total_ms

        # Background Job metrics
        self.jobs_created = defaultdict(int)       # job_type -> count
        self.jobs_completed = defaultdict(int)     # job_type -> count
        self.jobs_failed = defaultdict(int)        # job_type -> count
        self.jobs_cancelled = defaultdict(int)     # job_type -> count

        # WebSocket metrics
        self.ws_active_connections = 0
        self.ws_messages_received = 0
        self.ws_messages_sent = 0
        self.ws_errors = 0

        # Cache metrics
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_errors = 0

        # Learning metrics
        self.learning_records = defaultdict(int)   # (task_type, outcome) -> count

    def record_request(self, endpoint: str, status_code: int, duration_ms: float) -> None:
        self.request_count[(endpoint, status_code)] += 1
        self.request_latency_sum[endpoint] += duration_ms
        if status_code >= 400:
            self.request_errors[endpoint] += 1

    def record_llm(self, model: str, duration_ms: float, success: bool, is_fallback: bool = False) -> None:
        self.llm_requests += 1
        self.llm_latency_sum += duration_ms
        if not success:
            self.llm_failures += 1
        if is_fallback:
            self.llm_fallbacks += 1

    def record_tool(self, tool_name: str, duration_ms: float, success: bool) -> None:
        self.tool_calls[tool_name] += 1
        self.tool_latency_sum[tool_name] += duration_ms
        if not success:
            self.tool_failures[tool_name] += 1

    def record_job(self, job_type: str, status: str) -> None:
        if status == "created" or status == "pending":
            self.jobs_created[job_type] += 1
        elif status == "completed":
            self.jobs_completed[job_type] += 1
        elif status == "failed":
            self.jobs_failed[job_type] += 1
        elif status == "cancelled":
            self.jobs_cancelled[job_type] += 1

    def record_ws_connection(self, delta: int) -> None:
        self.ws_active_connections = max(0, self.ws_active_connections + delta)

    def record_ws_message(self, direction: str) -> None:
        if direction == "received":
            self.ws_messages_received += 1
        elif direction == "sent":
            self.ws_messages_sent += 1

    def record_ws_error(self) -> None:
        self.ws_errors += 1

    def record_cache_hit(self) -> None:
        self.cache_hits += 1

    def record_cache_miss(self) -> None:
        self.cache_misses += 1

    def record_cache_error(self) -> None:
        self.cache_errors += 1

    def record_learning(self, task_type: str, outcome: str) -> None:
        self.learning_records[(task_type, outcome)] += 1

    def get_summary(self) -> Dict[str, Any]:
        total_requests = sum(self.request_count.values())
        avg_llm_latency = (self.llm_latency_sum / self.llm_requests) if self.llm_requests > 0 else 0.0
        total_cache_ops = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_cache_ops * 100.0) if total_cache_ops > 0 else 0.0

        return {
            "requests": {
                "total_requests": total_requests,
                "total_errors": sum(self.request_errors.values()),
            },
            "llm": {
                "total_requests": self.llm_requests,
                "failures": self.llm_failures,
                "fallbacks": self.llm_fallbacks,
                "avg_latency_ms": round(avg_llm_latency, 2),
            },
            "tools": {
                "total_calls": sum(self.tool_calls.values()),
                "failures": sum(self.tool_failures.values()),
                "by_tool": dict(self.tool_calls),
            },
            "jobs": {
                "created": sum(self.jobs_created.values()),
                "completed": sum(self.jobs_completed.values()),
                "failed": sum(self.jobs_failed.values()),
                "cancelled": sum(self.jobs_cancelled.values()),
            },
            "websocket": {
                "active_connections": self.ws_active_connections,
                "messages_received": self.ws_messages_received,
                "messages_sent": self.ws_messages_sent,
                "errors": self.ws_errors,
            },
            "cache": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "errors": self.cache_errors,
                "hit_rate_pct": round(hit_rate, 2),
            },
            "learning": {
                "total_records": sum(self.learning_records.values()),
            },
        }

    def to_prometheus_format(self) -> str:
        lines = []
        lines.append("# HELP jarvis_requests_total Total HTTP requests handled.")
        lines.append("# TYPE jarvis_requests_total counter")
        for (ep, status), count in self.request_count.items():
            lines.append(f'jarvis_requests_total{{endpoint="{ep}",status="{status}"}} {count}')

        lines.append("# HELP jarvis_llm_requests_total Total LLM requests.")
        lines.append("# TYPE jarvis_llm_requests_total counter")
        lines.append(f"jarvis_llm_requests_total {self.llm_requests}")

        lines.append("# HELP jarvis_cache_hits_total Total cache hits.")
        lines.append("# TYPE jarvis_cache_hits_total counter")
        lines.append(f"jarvis_cache_hits_total {self.cache_hits}")

        lines.append("# HELP jarvis_cache_misses_total Total cache misses.")
        lines.append("# TYPE jarvis_cache_misses_total counter")
        lines.append(f"jarvis_cache_misses_total {self.cache_misses}")

        lines.append("# HELP jarvis_ws_active_connections Current active WebSockets.")
        lines.append("# TYPE jarvis_ws_active_connections gauge")
        lines.append(f"jarvis_ws_active_connections {self.ws_active_connections}")

        return "\n".join(lines) + "\n"

default_metrics = MetricsCollector()
