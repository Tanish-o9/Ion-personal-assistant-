import pytest
from orchestrator.adaptation import (
    ModelRegistry,
    ModelRegistryEntry,
    DatasetVersion,
    DatasetCase,
    AdaptationExperimentEngine,
)
from orchestrator.evaluation import EvaluationPlatform

def test_model_registration_and_promotion_guard():
    reg = ModelRegistry()
    entry = ModelRegistryEntry(
        model_id="gpt-4o-custom",
        provider="OpenAI",
        version="1.1.0",
        status="evaluation",
    )
    reg.register_model(entry)

    # Rejects production promotion if evaluation_pass_rate is None or below threshold
    with pytest.raises(ValueError):
        reg.promote_status("gpt-4o-custom", "production", min_pass_rate=90.0)

    # Set pass rate to 95.0% -> promotion succeeds
    entry.evaluation_pass_rate = 95.0
    assert reg.promote_status("gpt-4o-custom", "production", min_pass_rate=90.0) is True

def test_adaptation_experiment_execution():
    eval_plat = EvaluationPlatform()
    exp_engine = AdaptationExperimentEngine(eval_plat)

    dataset = DatasetVersion(
        dataset_id="ds_1",
        version="1.0.0",
        authorized_by="admin_user",
        cases=[
            DatasetCase(case_id="c1", input_prompt="Write Python function", expected_output="def foo(): pass"),
        ],
    )
    model_entry = ModelRegistryEntry(model_id="gemini-1.5-pro", provider="Google", version="1.5.0")

    run = exp_engine.run_adaptation_experiment(dataset, model_entry)
    assert run.pass_rate_pct == 100.0
    assert model_entry.evaluation_pass_rate == 100.0
