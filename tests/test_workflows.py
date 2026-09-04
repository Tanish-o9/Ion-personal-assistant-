"""
Unit Tests for Phase 60: Visual Workflow Builder.
"""

import pytest
from database.connection import init_db
from orchestrator.workflows import (
    WorkflowEngine,
    WorkflowValidator,
    WorkflowDefinition,
    WorkflowNode,
    WorkflowEdge,
    WorkflowNodeType,
)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_workflow_validation_dag_and_cycle_detection():
    # Valid DAG
    n1 = WorkflowNode(id="node_1", type=WorkflowNodeType.TRIGGER, label="Start Trigger")
    n2 = WorkflowNode(id="node_2", type=WorkflowNodeType.LLM, label="Process Prompt")
    e1 = WorkflowEdge(id="edge_1", source_node_id="node_1", target_node_id="node_2")

    wf_valid = WorkflowDefinition(id="wf_1", user_id="u1", name="Valid Workflow", nodes=[n1, n2], edges=[e1])
    res_valid = WorkflowValidator.validate_workflow(wf_valid)
    assert res_valid["is_valid"] is True

    # Cycle DAG -> Invalid
    e2 = WorkflowEdge(id="edge_2", source_node_id="node_2", target_node_id="node_1")
    wf_cycle = WorkflowDefinition(id="wf_2", user_id="u1", name="Cycle Workflow", nodes=[n1, n2], edges=[e1, e2])
    res_cycle = WorkflowValidator.validate_workflow(wf_cycle)
    assert res_cycle["is_valid"] is False
    assert "cycle" in res_cycle["errors"][0]

def test_workflow_creation_and_execution():
    we = WorkflowEngine()
    user_id = "user_wf_1"

    nodes = [
        {"id": "n1", "type": "TRIGGER", "label": "HTTP Webhook Trigger"},
        {"id": "n2", "type": "RESEARCH", "label": "Web Search Node"}
    ]
    edges = [
        {"id": "e1", "source_node_id": "n1", "target_node_id": "n2"}
    ]

    wf = we.create_workflow(user_id=user_id, name="Auto Research Flow", nodes=nodes, edges=edges)
    assert wf["id"].startswith("wf_")

    exec_res = we.execute_workflow(wf["id"], user_id, {"input": "AI news"})
    assert exec_res["status"] == "success"
    assert "n1" in exec_res["node_results"]
    assert "n2" in exec_res["node_results"]
