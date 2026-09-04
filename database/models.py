import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, Float, DateTime, ForeignKey, Boolean
from database.connection import Base

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(String, default=utc_now_iso)

class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    session_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, default="New Conversation")
    created_at = Column(String, default=utc_now_iso)
    updated_at = Column(String, default=utc_now_iso)

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False) # user, assistant, system, tool
    content = Column(Text, nullable=False)
    created_at = Column(String, default=utc_now_iso)

class MemoryModel(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    content = Column(Text, nullable=False)
    memory_type = Column(String, default="preference") # preference, project, profile, instruction
    importance = Column(Integer, default=3)
    created_at = Column(String, default=utc_now_iso)

class ProfileModel(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    preferences = Column(Text, default="[]") # JSON string
    projects = Column(Text, default="[]")    # JSON string
    instructions = Column(Text, default="[]")# JSON string
    updated_at = Column(String, default=utc_now_iso)

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="pending") # pending, running, completed, failed, cancelled
    created_at = Column(String, default=utc_now_iso)

class TaskStepModel(Base):
    __tablename__ = "task_steps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id"), index=True, nullable=False)
    step_order = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="pending")
    result = Column(Text, nullable=True)

class ResearchSourceModel(Base):
    __tablename__ = "research_sources"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=True)
    url = Column(String, nullable=False)
    snippet = Column(Text, nullable=True)
    created_at = Column(String, default=utc_now_iso)

class FileMetadataModel(Base):
    __tablename__ = "files_metadata"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    created_at = Column(String, default=utc_now_iso)

class JobModel(Base):
    __tablename__ = "background_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    job_type = Column(String, nullable=False) # research, document_ingestion, long_task
    status = Column(String, default="pending") # pending, running, completed, failed, cancelled
    progress = Column(Integer, default=0)
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(String, default=utc_now_iso)
    started_at = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)

class AutomationModel(Base):
    __tablename__ = "automations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    workflow_text = Column(Text, nullable=False)
    schedule_cron = Column(String, default="0 9 * * 1") # e.g. every Monday 9am
    timezone = Column(String, default="UTC")
    enabled = Column(Boolean, default=True)
    next_run_at = Column(String, nullable=True)
    last_run_at = Column(String, nullable=True)
    created_at = Column(String, default=utc_now_iso)
    updated_at = Column(String, default=utc_now_iso)

class AutomationExecutionModel(Base):
    __tablename__ = "automation_executions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    automation_id = Column(String, ForeignKey("automations.id"), index=True, nullable=False)
    job_id = Column(String, nullable=True)
    status = Column(String, default="pending") # pending, running, completed, failed, approval_required
    approval_status = Column(String, default="approved") # approved, pending_approval, rejected
    result_summary = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(String, default=utc_now_iso)
    completed_at = Column(String, nullable=True)

class ApprovalModel(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    job_id = Column(String, nullable=True)
    action_type = Column(String, nullable=False)
    action_summary = Column(Text, nullable=False)
    risk_level = Column(String, default="medium") # low, medium, high, blocked
    status = Column(String, default="pending") # pending, approved, rejected, expired, cancelled
    created_at = Column(String, default=utc_now_iso)
    expires_at = Column(String, nullable=False)
    resolved_at = Column(String, nullable=True)
    resolved_by = Column(String, nullable=True)

class LearningRecordModel(Base):
    __tablename__ = "learning_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    task_id = Column(String, nullable=True)
    task_type = Column(String, nullable=False) # chat, research, coding, document, multi_step
    skill_used = Column(String, nullable=True)
    tools_used = Column(Text, default="[]") # JSON string array
    outcome = Column(String, default="success") # success, partial_success, failed, cancelled
    failure_reason = Column(Text, nullable=True)
    latency_ms = Column(Float, default=0.0)
    cost_usd = Column(Float, default=0.0)
    user_feedback = Column(String, nullable=True) # positive, negative
    feedback_reason = Column(Text, nullable=True)
    created_at = Column(String, default=utc_now_iso)

class WorkspaceModel(Base):
    __tablename__ = "workspaces"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    org_id = Column(String, nullable=True)
    created_at = Column(String, default=utc_now_iso)

class WorkspaceMemberModel(Base):
    __tablename__ = "workspace_members"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id"), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    role = Column(String, default="EDITOR") # OWNER, EDITOR, VIEWER
    joined_at = Column(String, default=utc_now_iso)

class WorkspaceInvitationModel(Base):
    __tablename__ = "workspace_invitations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id"), index=True, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="EDITOR")
    expires_at = Column(String, nullable=False)
    created_at = Column(String, default=utc_now_iso)

class OrganizationModel(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    policies_json = Column(Text, default="{}") # JSON org policies
    created_at = Column(String, default=utc_now_iso)

class OrganizationMemberModel(Base):
    __tablename__ = "organization_members"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, ForeignKey("organizations.id"), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    role = Column(String, default="MEMBER") # ORG_OWNER, ORG_ADMIN, MEMBER
    joined_at = Column(String, default=utc_now_iso)

class GoalModel(Base):
    __tablename__ = "goals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    workspace_id = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    success_criteria = Column(Text, default="[]") # JSON list of criteria strings
    status = Column(String, default="DRAFT") # DRAFT, PLANNED, RUNNING, WAITING_FOR_APPROVAL, WAITING_FOR_USER, PAUSED, COMPLETED, FAILED, CANCELLED
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    max_steps = Column(Integer, default=20)
    max_budget_usd = Column(Float, default=5.0)
    consumed_budget_usd = Column(Float, default=0.0)
    checkpoint_state = Column(Text, default="{}") # JSON checkpoint state
    created_at = Column(String, default=utc_now_iso)
    updated_at = Column(String, default=utc_now_iso)

class WorkflowModel(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    workspace_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    version = Column(Integer, default=1)
    nodes_json = Column(Text, default="[]") # JSON array of workflow nodes
    edges_json = Column(Text, default="[]") # JSON array of workflow edges
    is_enabled = Column(Boolean, default=True)
    created_at = Column(String, default=utc_now_iso)
    updated_at = Column(String, default=utc_now_iso)

class ConnectorModel(Base):
    __tablename__ = "connectors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    version = Column(String, default="1.0.0")
    capabilities_json = Column(Text, default="[]")
    permissions_json = Column(Text, default="[]")
    risk_level = Column(String, default="LOW")
    is_enabled = Column(Boolean, default=True)
    created_at = Column(String, default=utc_now_iso)

class ConnectorCredentialModel(Base):
    __tablename__ = "connector_credentials"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    connector_id = Column(String, ForeignKey("connectors.id"), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    encrypted_token_metadata = Column(Text, nullable=False)
    status = Column(String, default="ACTIVE")
    created_at = Column(String, default=utc_now_iso)

class CausalModel(Base):
    __tablename__ = "causal_models"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    graph_json = Column(Text, default="{}")
    evidence_json = Column(Text, default="[]")
    created_at = Column(String, default=utc_now_iso)

class SimulationModel(Base):
    __tablename__ = "simulations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    workspace_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    initial_state_json = Column(Text, default="{}")
    rules_json = Column(Text, default="[]")
    scenarios_json = Column(Text, default="[]")
    status = Column(String, default="IDLE")
    created_at = Column(String, default=utc_now_iso)

class SimulationRunModel(Base):
    __tablename__ = "simulation_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String, ForeignKey("simulations.id"), index=True, nullable=False)
    scenario_type = Column(String, default="BASELINE")
    seed = Column(Integer, default=42)
    iterations = Column(Integer, default=100)
    results_json = Column(Text, default="{}")
    metrics_json = Column(Text, default="{}")
    created_at = Column(String, default=utc_now_iso)

class DecisionExperimentModel(Base):
    __tablename__ = "decision_experiments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    question = Column(Text, nullable=False)
    baseline_json = Column(Text, default="{}")
    alternatives_json = Column(Text, default="[]")
    matrix_json = Column(Text, default="{}")
    recommendation_json = Column(Text, default="{}")
    created_at = Column(String, default=utc_now_iso)

class ImprovementCandidateModel(Base):
    __tablename__ = "improvement_candidates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    target_component = Column(String, nullable=False)
    problem_statement = Column(Text, nullable=False)
    proposed_change_json = Column(Text, default="{}")
    version = Column(String, default="1.0.0")
    evaluation_status = Column(String, default="UNTESTED")
    gate_results_json = Column(Text, default="{}")
    approval_status = Column(String, default="PENDING")
    rollback_state_json = Column(Text, default="{}")
    created_at = Column(String, default=utc_now_iso)

class EvaluationSnapshotModel(Base):
    __tablename__ = "evaluation_snapshots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String, ForeignKey("improvement_candidates.id"), index=True, nullable=False)
    dataset_version = Column(String, default="v1")
    metrics_json = Column(Text, default="{}")
    created_at = Column(String, default=utc_now_iso)

class DeviceModel(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    workspace_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    capabilities_json = Column(Text, default="[]")
    status = Column(String, default="OFFLINE")
    metadata_json = Column(Text, default="{}")
    permissions_json = Column(Text, default="[]")
    is_enabled = Column(Boolean, default=True)
    created_at = Column(String, default=utc_now_iso)
    updated_at = Column(String, default=utc_now_iso)

class EnvironmentModel(Base):
    __tablename__ = "environments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    workspace_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    device_ids_json = Column(Text, default="[]")
    policies_json = Column(Text, default="{}")
    created_at = Column(String, default=utc_now_iso)
    updated_at = Column(String, default=utc_now_iso)

class SceneModel(Base):
    __tablename__ = "scenes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    environment_id = Column(String, ForeignKey("environments.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    actions_json = Column(Text, default="[]")
    is_enabled = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(String, default=utc_now_iso)

class DeviceAuditEventModel(Base):
    __tablename__ = "device_audit_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    workspace_id = Column(String, nullable=True)
    device_id = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)
    risk_level = Column(String, default="LOW")
    approval_status = Column(String, default="NOT_REQUIRED")
    status = Column(String, default="COMPLETED")
    metadata_json = Column(Text, default="{}")
    created_at = Column(String, default=utc_now_iso)





class OrganizationPolicyModel(Base):
    __tablename__ = "org_policies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), index=True, nullable=False)
    workspace_id = Column(String, nullable=True)
    allowed_models_json = Column(Text, default="[]")
    allowed_providers_json = Column(Text, default="[]")
    allowed_connectors_json = Column(Text, default="[]")
    allowed_capabilities_json = Column(Text, default="[]")
    max_budget_json = Column(Text, default="{}")
    data_residency_region = Column(String, default="us-east-1")
    security_rules_json = Column(Text, default="{}")
    updated_at = Column(String, default=utc_now_iso)

class EnterpriseAuditEventModel(Base):
    __tablename__ = "enterprise_audit_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, index=True, nullable=False)
    workspace_id = Column(String, nullable=True)
    user_id = Column(String, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    metadata_json = Column(Text, default="{}")
    created_at = Column(String, default=utc_now_iso)

class EvaluationDatasetModel(Base):
    __tablename__ = "eval_datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    version = Column(String, default="1.0.0")
    category = Column(String, default="FUNCTIONAL")
    cases_json = Column(Text, default="[]")
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=utc_now_iso)

class EvaluationRunModel(Base):
    __tablename__ = "eval_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey("eval_datasets.id"), index=True, nullable=False)
    candidate_id = Column(String, nullable=True)
    model_name = Column(String, default="jarvis-v5")
    metrics_json = Column(Text, default="{}")
    passed = Column(Boolean, default=True)
    created_at = Column(String, default=utc_now_iso)

class PlatformReleaseManifestModel(Base):
    __tablename__ = "platform_release_manifests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    version = Column(String, default="5.0.0")
    git_commit = Column(String, default="head")
    schema_version = Column(String, default="v5.0")
    status = Column(String, default="READY") # READY, READY_WITH_LIMITATIONS, BLOCKED
    checklist_json = Column(Text, default="{}")
    security_status_json = Column(Text, default="{}")
    metrics_json = Column(Text, default="{}")
    created_at = Column(String, default=utc_now_iso)








