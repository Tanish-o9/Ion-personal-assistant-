from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class KnowledgeNode(BaseModel):
    id: str
    label: str
    node_type: str # user, project, task, document, topic, fact
    properties: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeEdge(BaseModel):
    source_id: str
    target_id: str
    relation_type: str # user_prefers, user_working_on, project_contains, document_related_to, task_belongs_to, fact_supported_by

class PersonalKnowledgeGraph:
    """
    Lightweight user-isolated personal knowledge graph linking users, projects, tasks, documents, and facts.
    """
    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []

    def add_node(self, node: KnowledgeNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, source_id: str, target_id: str, relation_type: str) -> None:
        edge = KnowledgeEdge(source_id=source_id, target_id=target_id, relation_type=relation_type)
        self.edges.append(edge)

    def get_user_relationships(self, user_id: str) -> List[Dict[str, Any]]:
        rel_list = []
        for edge in self.edges:
            if edge.source_id == user_id or edge.target_id == user_id:
                src = self.nodes.get(edge.source_id)
                tgt = self.nodes.get(edge.target_id)
                rel_list.append({
                    "relation": edge.relation_type,
                    "source": src.label if src else edge.source_id,
                    "target": tgt.label if tgt else edge.target_id,
                })
        return rel_list

    def clear_user_graph(self, user_id: str) -> int:
        removed_edges = [e for e in self.edges if e.source_id == user_id or e.target_id == user_id]
        self.edges = [e for e in self.edges if e not in removed_edges]
        return len(removed_edges)

default_knowledge_graph = PersonalKnowledgeGraph()
