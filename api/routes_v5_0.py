from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from orchestrator.platform.global_routing import (
    default_region_registry, RegionRouter, GlobalFailoverEngine, COMPONENT_AUDIT_MAP
)
from orchestrator.multimodal.unified_context import (
    InteractionRequest, UnifiedMultimodalContext, ModalityRouter, CrossModalEvidenceTree
)
from orchestrator.auth.enterprise_policy import (
    EnterprisePolicyManager, EnterprisePolicy, EnterpriseAuditLogger
)
from orchestrator.evaluation.benchmark_suite import (
    BenchmarkSuite, MatrixEvaluator
)
from orchestrator.platform.jarvis_5_integration import (
    UnifiedRequestLifecycleManager
)

router = APIRouter(prefix="/api/v5.0", tags=["JARVIS 5.0 Master Platform"])

# Singletons for API
region_router = RegionRouter(default_region_registry)
failover_engine = GlobalFailoverEngine(default_region_registry)
modality_router = ModalityRouter()
policy_manager = EnterprisePolicyManager()
audit_logger = EnterpriseAuditLogger()
eval_matrix = MatrixEvaluator()
lifecycle_manager = UnifiedRequestLifecycleManager()

class GlobalRouteSchema(BaseModel):
    user_region: str
    workspace_policy: Optional[str] = None
    required_capability: Optional[str] = None

class MultimodalRequestSchema(BaseModel):
    user_id: str
    session_id: str
    text: Optional[str] = None
    images: List[str] = []
    documents: List[Dict[str, Any]] = []

class PolicySchema(BaseModel):
    organization_id: str
    workspace_id: Optional[str] = None
    allowed_models: List[str] = ["gpt-4o", "claude-3-5-sonnet", "jarvis-v5"]
    allowed_providers: List[str] = ["openai", "anthropic", "local"]
    max_monthly_budget_usd: float = 5000.0

@router.get("/global/regions")
async def get_regions():
    return {"regions": [r.__dict__ for r in default_region_registry.list_healthy_regions()]}

@router.post("/global/route")
async def route_region(req: GlobalRouteSchema):
    try:
        selected = region_router.select_region(
            user_region=req.user_region,
            workspace_residency_policy=req.workspace_policy,
            required_capability=req.required_capability,
        )
        return {"selected_region": selected, "status": "ROUTED"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/multimodal/modalities")
async def determine_modalities(req: MultimodalRequestSchema):
    interaction = InteractionRequest(
        user_id=req.user_id,
        session_id=req.session_id,
        text=req.text,
        images=req.images,
        documents=req.documents,
    )
    modalities = modality_router.determine_required_modalities(interaction)
    return {"required_modalities": modalities}

@router.post("/enterprise/policies")
async def create_policy(req: PolicySchema):
    policy = EnterprisePolicy(
        organization_id=req.organization_id,
        workspace_id=req.workspace_id,
        allowed_models=req.allowed_models,
        allowed_providers=req.allowed_providers,
        max_monthly_budget_usd=req.max_monthly_budget_usd,
    )
    policy_manager.set_policy(policy)
    return {"status": "UPDATED", "organization_id": req.organization_id}

@router.get("/evaluation/matrix")
async def get_evaluation_matrix():
    matrix = eval_matrix.evaluate_matrix(
        capabilities=["chat", "rag", "vision", "voice", "devices"],
        models=["jarvis-v5", "gpt-4o"],
        environments=["staging", "production"]
    )
    return {"matrix_results": matrix}

@router.get("/system/status")
async def get_system_status():
    return {
        "platform_version": "5.0.0",
        "milestones_completed": "1-95",
        "global_regions": len(default_region_registry.list_healthy_regions()),
        "status": "READY",
    }
