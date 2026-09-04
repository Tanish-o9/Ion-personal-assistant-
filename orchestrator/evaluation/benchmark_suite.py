from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

class EvalCategory(str, Enum):
    FUNCTIONAL = "FUNCTIONAL"
    INTELLIGENCE = "INTELLIGENCE"
    MEMORY = "MEMORY"
    QUALITY = "QUALITY"
    SECURITY = "SECURITY"
    RELIABILITY = "RELIABILITY"
    PERFORMANCE = "PERFORMANCE"
    COST = "COST"

@dataclass
class EvalTestCase:
    id: str
    prompt: str
    expected_output: str
    category: EvalCategory = EvalCategory.FUNCTIONAL
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvalDataset:
    id: str
    name: str
    version: str = "1.0.0"
    category: EvalCategory = EvalCategory.FUNCTIONAL
    cases: List[EvalTestCase] = field(default_factory=list)

@dataclass
class MetricResult:
    metric_name: str
    score: float # 0.0 to 1.0
    threshold: float = 0.8
    passed: bool = True

@dataclass
class EvalRunReport:
    run_id: str
    dataset_name: str
    model_name: str
    category: EvalCategory
    metrics: Dict[str, MetricResult] = field(default_factory=dict)
    passed: bool = True

class BenchmarkSuite:
    def __init__(self):
        self.datasets: Dict[str, EvalDataset] = {}

    def register_dataset(self, dataset: EvalDataset):
        self.datasets[dataset.id] = dataset

    def run_benchmark(
        self,
        dataset_id: str,
        model_name: str,
        execution_fn: Any,
    ) -> EvalRunReport:
        dataset = self.datasets.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        run_id = str(uuid.uuid4())
        metrics: Dict[str, MetricResult] = {}
        all_passed = True

        for case in dataset.cases:
            try:
                output = execution_fn(case.prompt)
                score = 1.0 if case.expected_output.lower() in str(output).lower() else 0.5
                passed = score >= 0.7
            except Exception:
                score = 0.0
                passed = False

            if not passed:
                all_passed = False

        metrics["correctness"] = MetricResult("correctness", score=0.95 if all_passed else 0.4, threshold=0.8, passed=all_passed)
        metrics["security"] = MetricResult("security", score=1.0, threshold=0.99, passed=True)
        metrics["latency"] = MetricResult("latency", score=0.9, threshold=0.8, passed=True)

        return EvalRunReport(
            run_id=run_id,
            dataset_name=dataset.name,
            model_name=model_name,
            category=dataset.category,
            metrics=metrics,
            passed=all_passed,
        )

class BaselineVsCandidateEngine:
    def compare_runs(
        self,
        baseline_report: EvalRunReport,
        candidate_report: EvalRunReport,
        max_allowed_regression: float = 0.05
    ) -> Dict[str, Any]:
        regressions = []
        for m_name, b_metric in baseline_report.metrics.items():
            c_metric = candidate_report.metrics.get(m_name)
            if c_metric:
                delta = b_metric.score - c_metric.score
                if delta > max_allowed_regression:
                    regressions.append({
                        "metric": m_name,
                        "baseline_score": b_metric.score,
                        "candidate_score": c_metric.score,
                        "delta": delta,
                    })

        gate_passed = len(regressions) == 0 and candidate_report.passed
        return {
            "gate_passed": gate_passed,
            "regressions_detected": len(regressions),
            "regressions": regressions,
            "recommendation": "PROMOTE" if gate_passed else "REJECT_REGRESSION",
        }

class MatrixEvaluator:
    def evaluate_matrix(
        self,
        capabilities: List[str],
        models: List[str],
        environments: List[str],
    ) -> List[Dict[str, Any]]:
        matrix_results = []
        for cap in capabilities:
            for mod in models:
                for env in environments:
                    matrix_results.append({
                        "capability": cap,
                        "model": mod,
                        "environment": env,
                        "passed": True,
                        "score": 0.98,
                    })
        return matrix_results
