import pytest
from orchestrator.research.scientist import (
    ResearchScientistEngine,
    LiteratureComparator,
    ConceptualExperimentPlanner,
    default_research_scientist_engine,
)

@pytest.mark.asyncio
async def test_scientific_research_workflow():
    engine = ResearchScientistEngine()
    report = await engine.execute_scientific_research(question="Quantum context compression algorithms")
    assert report.question == "Quantum context compression algorithms"
    assert len(report.hypotheses) == 1
    assert report.hypotheses[0].label == "PROPOSED_HYPOTHESIS"
    assert len(report.experiment_plans) == 1
    assert "CERTIFIED_SAFE" in report.experiment_plans[0].safety_certification

def test_literature_comparator():
    comparator = LiteratureComparator()
    docs = [
        {"title": "Paper A", "objective": "Optimize transformers", "quality_score": 0.9},
        {"title": "Paper B", "objective": "State space models", "quality_score": 0.88},
    ]
    comp = comparator.compare_documents(docs)
    assert len(comp.items_compared) == 2
    assert "Paper A" in comp.objectives

def test_dangerous_experiment_guard():
    planner = ConceptualExperimentPlanner()
    with pytest.raises(ValueError, match="Dangerous physical/biological experimentation is strictly prohibited"):
        planner.plan_experiment(research_question="Synthesize hazardous biohazard pathogen")
