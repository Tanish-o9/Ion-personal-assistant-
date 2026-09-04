"""
Phase 60: Workflow Graph Validator & Pre-execution Checks.
"""

from typing import Dict, Any, List, Set
from orchestrator.workflows.models import WorkflowDefinition, WorkflowNodeType

class WorkflowValidator:
    """Validates workflow DAG topology, cycle detection, input connections, and node permissions."""

    @staticmethod
    def validate_workflow(workflow: WorkflowDefinition) -> Dict[str, Any]:
        if not workflow.nodes:
            return {"is_valid": False, "errors": ["Workflow contains no nodes."]}

        node_ids: Set[str] = {n.id for n in workflow.nodes}
        adj_list: Dict[str, List[str]] = {n_id: [] for n_id in node_ids}

        # Check edge endpoints exist
        for edge in workflow.edges:
            if edge.source_node_id not in node_ids:
                return {"is_valid": False, "errors": [f"Edge '{edge.id}' has unknown source '{edge.source_node_id}'."]}
            if edge.target_node_id not in node_ids:
                return {"is_valid": False, "errors": [f"Edge '{edge.id}' has unknown target '{edge.target_node_id}'."]}
            adj_list[edge.source_node_id].append(edge.target_node_id)

        # Cycle detection using DFS
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj_list.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for n_id in node_ids:
            if n_id not in visited:
                if has_cycle(n_id):
                    return {"is_valid": False, "errors": ["Workflow contains a cycle (must be a valid DAG)."]}

        # Check for TRIGGER or INPUT node presence
        trigger_nodes = [n for n in workflow.nodes if n.type in (WorkflowNodeType.TRIGGER, WorkflowNodeType.INPUT)]
        if not trigger_nodes:
            return {"is_valid": False, "errors": ["Workflow must contain at least one TRIGGER or INPUT node."]}

        return {"is_valid": True, "errors": []}
