from orchestrator.skills.models import Skill
from orchestrator.skills.registry import SkillRegistry

def register_builtin_skills(registry: SkillRegistry) -> None:
    # 1. Research Skill
    research_skill = Skill(
        name="research_skill",
        description="Multi-step web research, source ranking, and evidence synthesis workflow.",
        capabilities=["research", "web_search", "synthesize"],
        required_tools=["web_search", "web_fetch"],
        risk_level="medium",
        version="v1",
    )
    registry.register(research_skill)

    # 2. Knowledge Search Skill
    knowledge_skill = Skill(
        name="knowledge_skill",
        description="Vector knowledge base retrieval, scope filtering, and document lookup.",
        capabilities=["knowledge", "rag", "vector_search"],
        required_tools=["knowledge_search"],
        risk_level="low",
        version="v1",
    )
    registry.register(knowledge_skill)

    # 3. Document Analysis Skill
    doc_skill = Skill(
        name="document_analysis_skill",
        description="Multimodal document and image visual context extraction.",
        capabilities=["document_analysis", "multimodal", "ocr"],
        required_tools=[],
        risk_level="low",
        version="v1",
    )
    registry.register(doc_skill)

    # 4. Coding Assistance Skill
    coding_skill = Skill(
        name="coding_assistance_skill",
        description="Assists with code generation, math calculations, and technical design.",
        capabilities=["coding", "math", "calculator"],
        required_tools=["calculator"],
        risk_level="low",
        version="v1",
    )
    registry.register(coding_skill)
