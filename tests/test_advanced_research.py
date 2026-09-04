import pytest
from orchestrator.research.decomposer import ResearchDecomposer
from orchestrator.research.engine import default_advanced_research_engine

def test_query_decomposition():
    # Simple query -> bypasses decomposition
    q_simple = "weather in Paris"
    sub_simple = ResearchDecomposer.decompose_query(q_simple)
    assert len(sub_simple) == 1

    # Complex comparison query -> decomposes into subqueries
    q_complex = "compare React vs Vue framework performance and ecosystem"
    sub_complex = ResearchDecomposer.decompose_query(q_complex)
    assert len(sub_complex) >= 2

@pytest.mark.asyncio
async def test_advanced_research_engine_execution():
    res = await default_advanced_research_engine.execute_research(
        query="compare Python vs Rust performance",
        session_id="sess_res_1",
    )
    assert res["query"] == "compare Python vs Rust performance"
    assert len(res["subqueries"]) >= 1
    assert "evidence_map" in res
