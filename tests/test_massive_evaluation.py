import pytest
from orchestrator.evaluation.benchmark_suite import (
    EvalCategory, EvalTestCase, EvalDataset, BenchmarkSuite,
    BaselineVsCandidateEngine, MatrixEvaluator
)

def test_benchmark_suite_execution():
    suite = BenchmarkSuite()
    dataset = EvalDataset(
        id="ds-1",
        name="Functional Chat",
        category=EvalCategory.FUNCTIONAL,
        cases=[
            EvalTestCase(id="c1", prompt="What is 2+2?", expected_output="4"),
            EvalTestCase(id="c2", prompt="Capital of France?", expected_output="Paris"),
        ]
    )
    suite.register_dataset(dataset)

    def mock_exec(prompt: str) -> str:
        if "2+2" in prompt:
            return "4"
        return "Paris"

    report = suite.run_benchmark("ds-1", "jarvis-v5", mock_exec)
    assert report.passed is True
    assert report.metrics["correctness"].score == 0.95

def test_baseline_vs_candidate_regression():
    engine = BaselineVsCandidateEngine()
    suite = BenchmarkSuite()
    dataset = EvalDataset(id="ds-1", name="Functional Chat", cases=[EvalTestCase(id="c1", prompt="2+2", expected_output="4")])
    suite.register_dataset(dataset)

    base_report = suite.run_benchmark("ds-1", "v1.0", lambda p: "4")
    cand_report = suite.run_benchmark("ds-1", "v2.0", lambda p: "4")

    res = engine.compare_runs(base_report, cand_report)
    assert res["gate_passed"] is True
    assert res["recommendation"] == "PROMOTE"

def test_matrix_evaluator():
    matrix = MatrixEvaluator()
    results = matrix.evaluate_matrix(
        capabilities=["chat", "rag"],
        models=["jarvis-v5"],
        environments=["staging"]
    )
    assert len(results) == 2
    assert results[0]["passed"] is True
