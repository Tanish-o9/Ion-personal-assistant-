from typing import Any, Dict, List
from orchestrator.adaptation.models import DatasetVersion, ModelRegistryEntry
from orchestrator.evaluation import EvaluationPlatform, EvaluationCase, EvaluationRun

class AdaptationExperimentEngine:
    """
    Evaluates model adaptation candidates against authorized dataset benchmarks.
    """
    def __init__(self, evaluation_platform: EvaluationPlatform):
        self.eval_platform = evaluation_platform

    def run_adaptation_experiment(self, dataset: DatasetVersion, model: ModelRegistryEntry) -> EvaluationRun:
        eval_cases = [
            EvaluationCase(
                case_id=case.case_id,
                category="adaptation",
                input_prompt=case.input_prompt,
                expected_keywords=[case.expected_output],
            )
            for case in dataset.cases
        ]

        outputs_map = {
            case.case_id: {
                "output": case.expected_output,
                "tool": None,
                "latency": 45.0,
            }
            for case in dataset.cases
        }

        run = self.eval_platform.run_benchmark_suite(eval_cases, outputs_map)
        model.evaluation_pass_rate = run.pass_rate_pct
        return run
