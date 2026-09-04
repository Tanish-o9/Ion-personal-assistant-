import uuid
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from orchestrator.evaluation.models import EvaluationCase, EvaluationResult, EvaluationRun
from orchestrator.observability import jarvis_logger

class EvaluationPlatform:
    """
    Framework executing objective evaluation benchmarks across JARVIS capabilities,
    detecting regressions against baseline runs, and measuring latency/accuracy metrics.
    """
    def __init__(self):
        self.runs_history: List[EvaluationRun] = []

    def evaluate_case(self, case: EvaluationCase, actual_output: str, tool_used: Optional[str] = None, latency_ms: float = 100.0) -> EvaluationResult:
        passed = True
        failure_reasons = []

        if case.expected_tool and tool_used != case.expected_tool:
            passed = False
            failure_reasons.append(f"Tool mismatch: expected '{case.expected_tool}', got '{tool_used}'")

        if case.expected_keywords:
            missing = [kw for kw in case.expected_keywords if kw.lower() not in actual_output.lower()]
            if missing:
                passed = False
                failure_reasons.append(f"Missing expected keywords: {missing}")

        if latency_ms > case.max_latency_ms:
            passed = False
            failure_reasons.append(f"Latency limit exceeded: {latency_ms:.1f}ms > {case.max_latency_ms}ms")

        return EvaluationResult(
            case_id=case.case_id,
            category=case.category,
            passed=passed,
            actual_output=actual_output,
            actual_tool_used=tool_used,
            latency_ms=round(latency_ms, 2),
            failure_reason="; ".join(failure_reasons) if failure_reasons else None,
        )

    def run_benchmark_suite(self, cases: List[EvaluationCase], outputs_map: Dict[str, Dict[str, Any]]) -> EvaluationRun:
        results: List[EvaluationResult] = []
        for case in cases:
            out_info = outputs_map.get(case.case_id, {"output": "", "tool": None, "latency": 50.0})
            res = self.evaluate_case(
                case=case,
                actual_output=out_info.get("output", ""),
                tool_used=out_info.get("tool"),
                latency_ms=out_info.get("latency", 50.0),
            )
            results.append(res)

        total = len(results)
        passed_cnt = sum(1 for r in results if r.passed)
        failed_cnt = total - passed_cnt
        pass_rate = (passed_cnt / total * 100.0) if total > 0 else 0.0
        avg_lat = sum(r.latency_ms for r in results) / total if total > 0 else 0.0

        run = EvaluationRun(
            run_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_cases=total,
            passed_cases=passed_cnt,
            failed_cases=failed_cnt,
            pass_rate_pct=round(pass_rate, 2),
            avg_latency_ms=round(avg_lat, 2),
            results=results,
        )
        self.runs_history.append(run)
        return run

    def detect_regression(self, baseline_run: EvaluationRun, current_run: EvaluationRun) -> Dict[str, Any]:
        has_regression = False
        notes = []

        if current_run.pass_rate_pct < baseline_run.pass_rate_pct:
            has_regression = True
            notes.append(f"Pass rate dropped from {baseline_run.pass_rate_pct}% to {current_run.pass_rate_pct}%")

        if current_run.avg_latency_ms > (baseline_run.avg_latency_ms * 1.25):
            has_regression = True
            notes.append(f"Average latency degraded from {baseline_run.avg_latency_ms}ms to {current_run.avg_latency_ms}ms")

        return {
            "has_regression": has_regression,
            "baseline_pass_rate": baseline_run.pass_rate_pct,
            "current_pass_rate": current_run.pass_rate_pct,
            "notes": notes,
        }

default_evaluation_platform = EvaluationPlatform()
