import pytest
from orchestrator.memory import (
    MemoryManager,
    PersonalKnowledgeGraph,
    KnowledgeNode,
    EntityResolver,
)

def test_memory_manager_creation_and_update():
    mgr = MemoryManager()
    rec1 = mgr.save_memory("u1", "I prefer Python for backend", memory_type="preference", importance=4)
    assert rec1.memory_type == "preference"

    # Update preference
    rec2 = mgr.save_memory("u1", "I prefer TypeScript for backend", memory_type="preference", importance=4)
    assert rec2.content == "I prefer TypeScript for backend"

def test_personal_knowledge_graph():
    pkg = PersonalKnowledgeGraph()
    user_node = KnowledgeNode(id="user_1", label="User 1", node_type="user")
    proj_node = KnowledgeNode(id="proj_1", label="JARVIS Project", node_type="project")

    pkg.add_node(user_node)
    pkg.add_node(proj_node)
    pkg.add_edge("user_1", "proj_1", "user_working_on")

    rels = pkg.get_user_relationships("user_1")
    assert len(rels) == 1
    assert rels[0]["relation"] == "user_working_on"

def test_entity_resolver():
    user_projects = [
        {"id": "p1", "name": "JARVIS Engine"},
        {"id": "p2", "name": "JARVIS Dashboard"},
    ]
    docs = ["architecture.md", "walkthrough.md"]

    # Ambiguous match (both have JARVIS) -> returns ambiguous True
    proj, is_ambiguous = EntityResolver.resolve_reference("JARVIS", user_projects, docs)
    assert is_ambiguous is True

    # Exact match -> returns project
    proj_exact, is_ambiguous_2 = EntityResolver.resolve_reference("Engine", user_projects, docs)
    assert is_ambiguous_2 is False
    assert proj_exact["name"] == "JARVIS Engine"
