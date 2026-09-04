import os
import uuid
import base64
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Header, Query, status, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import init_db, UserRepository, ConversationRepository, JobRepository, engine
from api.middleware import RequestTracingMiddleware
from orchestrator.graph import build_orchestrator_graph
from orchestrator.llm_client import LLMClient
from orchestrator.voice import VoiceRequest, default_voice_manager
from orchestrator.multimodal import MultimodalInput, default_multimodal_processor
from orchestrator.memory import default_memory_manager
from orchestrator.auth import (
    User,
    hash_password,
    verify_password,
    create_token,
    verify_token,
    default_user_store,
    default_session_store,
)
from orchestrator.jobs import default_job_manager
from orchestrator.automation import AutomationCreateRequest, default_automation_manager
from orchestrator.approval import default_approval_manager
from orchestrator.observability import (
    jarvis_logger,
    default_metrics,
    get_current_request_id,
)
from orchestrator.security import (
    ALLOWED_ORIGINS,
    RATE_LIMIT_LOGIN,
    RATE_LIMIT_CHAT,
    RATE_LIMIT_UPLOAD,
    MAX_UPLOAD_SIZE_MB,
    MAX_WS_MESSAGE_SIZE_BYTES,
    MAX_CONCURRENT_JOBS_PER_USER,
    MAX_WS_CONNECTIONS_PER_USER,
    ALLOWED_MIME_TYPES,
    ALLOWED_FILE_EXTENSIONS,
    default_rate_limiter,
    SecurityHeadersMiddleware,
    InputSanitizer,
)
from orchestrator.cache import default_cache, make_cache_key

load_dotenv()
init_db()  # Initialize database schema and ORM tables

claude_api_key = os.getenv("CLAUDE_API_KEY")
hf_api_key = os.getenv("HF_API_KEY")

llm_client = LLMClient(claude_api_key=claude_api_key, hf_api_key=hf_api_key)
graph_app = build_orchestrator_graph(llm_client)

from api.routes_v4_2 import router as v4_2_router
from api.routes_v4_3 import router as v4_3_router
from api.routes_v5_0 import router as v5_0_router

app = FastAPI(
    title="Jarvis Orchestrator API",
    description="Multi-agent orchestrator service for Jarvis using LangGraph + FastAPI + PostgreSQL.",
    version="5.0.0",
)

app.include_router(v4_2_router)
app.include_router(v4_3_router)
app.include_router(v5_0_router)




app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestTracingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = get_current_request_id() or "unknown"
    jarvis_logger.error(f"Unhandled exception: {str(exc)}", extra={"request_id": req_id, "error": str(exc)})
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again.", "request_id": req_id},
    )

class AuthRequestPayload(BaseModel):
    username: str
    password: str

class MultimodalFileItem(BaseModel):
    input_type: str
    filename: str
    mime_type: Optional[str] = "application/octet-stream"
    content_base64: str

class ChatRequestPayload(BaseModel):
    session_id: Optional[str] = None
    text: str
    files: Optional[List[MultimodalFileItem]] = None

class ChatResponsePayload(BaseModel):
    session_id: str
    response: str
    intent: str
    emotion_state: Dict[str, Any]

class VoicePayload(BaseModel):
    session_id: Optional[str] = None
    audio_base64: str
    audio_format: Optional[str] = "wav"

class JobCreatePayload(BaseModel):
    session_id: Optional[str] = None
    job_type: str
    payload_data: Optional[str] = ""

def get_message_content(msg: Any) -> str:
    if hasattr(msg, "content"):
        return getattr(msg, "content", "") or ""
    if isinstance(msg, dict):
        return msg.get("content", "") or ""
    return str(msg)

async def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header.",
        )
    token = authorization.split(" ", 1)[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        )

    user = default_user_store.get_by_id(payload["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists.",
        )
    return user

# --- Observability & Health Endpoints ---

@app.get("/health")
async def health_endpoint():
    return {"status": "ok", "service": "JARVIS Orchestrator", "version": "2.0.0"}

@app.get("/ready")
async def readiness_endpoint():
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    return {
        "status": "ready" if db_status == "healthy" else "degraded",
        "database": db_status,
        "service": "JARVIS Orchestrator",
    }

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics_endpoint():
    return default_metrics.to_prometheus_format()

@app.get("/monitoring/summary")
async def monitoring_summary_endpoint(current_user: User = Depends(get_current_user)):
    return {
        "service": "JARVIS Orchestrator",
        "user_id": current_user.id,
        "metrics": default_metrics.get_summary(),
    }

# --- Auth Endpoints ---

@app.post("/auth/register")
@app.post("/api/auth/register")
async def register_endpoint(request: Request, payload: AuthRequestPayload):
    try:
        client_ip = request.client.host if request.client else "unknown"
        if not default_rate_limiter.is_allowed(f"auth:{client_ip}", max_requests=RATE_LIMIT_LOGIN, window_seconds=60):
            raise HTTPException(status_code=429, detail="Too many registration requests. Please try again later.")

        username = (payload.username or "").strip()
        password = (payload.password or "").strip()

        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required.")

        p_hash = hash_password(password)
        user = default_user_store.register_user(username=username, password_hash=p_hash)
        token = create_token(user_id=user.id, username=user.username)

        return {"token": token, "user": user.to_dict()}
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        jarvis_logger.error(f"Registration exception: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/auth/login")
@app.post("/api/auth/login")
async def login_endpoint(request: Request, payload: AuthRequestPayload):
    try:
        client_ip = request.client.host if request.client else "unknown"
        if not default_rate_limiter.is_allowed(f"auth:{client_ip}", max_requests=RATE_LIMIT_LOGIN, window_seconds=60):
            raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")

        username = (payload.username or "").strip()
        password = (payload.password or "").strip()

        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required.")

        user = default_user_store.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password.")

        token = create_token(user_id=user.id, username=user.username)
        return {"token": token, "user": user.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        jarvis_logger.error(f"Login exception: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/auth/me")
@app.get("/api/auth/me")
async def get_me_endpoint(current_user: User = Depends(get_current_user)):
    return {"user": current_user.to_dict()}

# --- User Resource Endpoints ---

@app.get("/conversations")
async def get_conversations(current_user: User = Depends(get_current_user)):
    convs = ConversationRepository.get_user_conversations(current_user.id)
    return [
        {
            "session_id": c.session_id,
            "title": c.title,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in convs[:50]
    ]

@app.get("/conversations/{session_id}/messages")
async def get_session_messages(session_id: str, current_user: User = Depends(get_current_user)):
    if not default_session_store.verify_ownership(session_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied: Cannot access another user's session.")

    msgs = ConversationRepository.get_session_messages(session_id)
    return [
        {
            "id": m.id,
            "session_id": m.session_id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at,
        }
        for m in msgs[:100]
    ]

@app.get("/memory/{user_id}")
async def get_user_memories(user_id: str, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: Cannot access another user's memories.")

    records = default_memory_manager.get_memories(user_id=user_id, limit=50)
    return [r.to_dict() for r in records]

@app.delete("/memory/{user_id}/{memory_id}")
async def delete_user_memory(user_id: str, memory_id: str, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: Cannot modify another user's memories.")

    success = default_memory_manager.delete_memory(memory_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory record not found.")

    profile_cache_key = f"profile:{user_id}"
    default_cache.delete(profile_cache_key)

    return {"status": "success", "deleted_id": memory_id}

@app.get("/profile/{user_id}")
async def get_user_profile(user_id: str, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: Cannot access another user's profile.")

    cache_key = f"profile:{user_id}"
    cached_profile = default_cache.get(cache_key)
    if cached_profile is not None:
        return cached_profile

    memories = default_memory_manager.get_memories(user_id=user_id, limit=50)
    preferences = [m.content for m in memories if m.memory_type == "preference"]
    projects = [m.content for m in memories if m.memory_type == "project"]
    instructions = [m.content for m in memories if m.memory_type == "instruction"]

    profile_data = {
        "user_id": current_user.id,
        "username": current_user.username.capitalize(),
        "total_memories": len(memories),
        "preferences": preferences,
        "projects": projects,
        "instructions": instructions,
        "status": "Active",
    }

    default_cache.set(cache_key, profile_data, ttl_seconds=300)
    return profile_data

# --- Background Jobs Endpoints ---

@app.post("/jobs")
async def create_background_job(payload: JobCreatePayload, current_user: User = Depends(get_current_user)):
    user_jobs = default_job_manager.get_user_jobs(current_user.id)
    active_count = sum(1 for j in user_jobs if j.status in {"pending", "running"})
    if active_count >= MAX_CONCURRENT_JOBS_PER_USER:
        raise HTTPException(status_code=429, detail=f"Maximum concurrent job limit ({MAX_CONCURRENT_JOBS_PER_USER}) reached.")

    session_id = payload.session_id or str(uuid.uuid4())
    if not default_session_store.verify_ownership(session_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied: Session belongs to another user.")

    job = default_job_manager.submit_job(
        user_id=current_user.id,
        session_id=session_id,
        job_type=payload.job_type,
        payload_data=payload.payload_data or "",
    )
    return job.to_dict()

@app.get("/jobs")
async def list_user_jobs(current_user: User = Depends(get_current_user)):
    jobs = default_job_manager.get_user_jobs(current_user.id)
    return [j.to_dict() for j in jobs[:50]]

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str, current_user: User = Depends(get_current_user)):
    job = default_job_manager.get_job(job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or access denied.")
    return job.to_dict()

@app.post("/jobs/{job_id}/cancel")
async def cancel_job_endpoint(job_id: str, current_user: User = Depends(get_current_user)):
    success = default_job_manager.cancel_job(job_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or access denied.")
    return {"status": "success", "cancelled_job_id": job_id}

# --- Phase 25 Automation Endpoints ---

@app.post("/automations")
async def create_automation_endpoint(payload: AutomationCreateRequest, current_user: User = Depends(get_current_user)):
    auto_dict = default_automation_manager.create_automation(
        user_id=current_user.id,
        name=payload.name,
        workflow_text=payload.workflow_text,
        description=payload.description,
        schedule_cron=payload.schedule_cron,
        tz=payload.timezone,
    )
    return auto_dict

@app.get("/automations")
async def list_automations_endpoint(current_user: User = Depends(get_current_user)):
    return default_automation_manager.list_automations(current_user.id)

@app.get("/automations/{automation_id}")
async def get_automation_endpoint(automation_id: str, current_user: User = Depends(get_current_user)):
    auto = default_automation_manager.get_automation(automation_id, current_user.id)
    if not auto:
        raise HTTPException(status_code=404, detail="Automation not found or access denied.")
    return auto

@app.post("/automations/{automation_id}/pause")
async def pause_automation_endpoint(automation_id: str, current_user: User = Depends(get_current_user)):
    success = default_automation_manager.pause_automation(automation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Automation not found or access denied.")
    return {"status": "success", "paused_id": automation_id}

@app.post("/automations/{automation_id}/resume")
async def resume_automation_endpoint(automation_id: str, current_user: User = Depends(get_current_user)):
    success = default_automation_manager.resume_automation(automation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Automation not found or access denied.")
    return {"status": "success", "resumed_id": automation_id}

@app.post("/automations/{automation_id}/run")
async def run_automation_endpoint(automation_id: str, current_user: User = Depends(get_current_user)):
    result = default_automation_manager.run_automation(automation_id, current_user.id)
    if not result:
        raise HTTPException(status_code=400, detail="Automation not found, disabled, or access denied.")
    return result

@app.delete("/automations/{automation_id}")
async def delete_automation_endpoint(automation_id: str, current_user: User = Depends(get_current_user)):
    success = default_automation_manager.delete_automation(automation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Automation not found or access denied.")
    return {"status": "success", "deleted_id": automation_id}

# --- Phase 26 Human-in-the-Loop Approval Endpoints ---

@app.get("/approvals")
async def list_approvals_endpoint(status_filter: Optional[str] = Query(None), current_user: User = Depends(get_current_user)):
    return default_approval_manager.list_approvals(current_user.id, status_filter=status_filter)

@app.get("/approvals/{approval_id}")
async def get_approval_endpoint(approval_id: str, current_user: User = Depends(get_current_user)):
    appr = default_approval_manager.get_approval(approval_id, current_user.id)
    if not appr:
        raise HTTPException(status_code=404, detail="Approval request not found or access denied.")
    return appr

@app.post("/approvals/{approval_id}/approve")
async def approve_endpoint(approval_id: str, current_user: User = Depends(get_current_user)):
    success = default_approval_manager.approve(approval_id, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Approval request not pending or access denied.")
    return {"status": "success", "approved_id": approval_id}

@app.post("/approvals/{approval_id}/reject")
async def reject_endpoint(approval_id: str, current_user: User = Depends(get_current_user)):
    success = default_approval_manager.reject(approval_id, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Approval request not pending or access denied.")
    return {"status": "success", "rejected_id": approval_id}

# --- Core Chat, Voice & WebSocket Endpoints ---

@app.post("/chat", response_model=ChatResponsePayload)
async def chat_endpoint(payload: ChatRequestPayload, current_user: User = Depends(get_current_user)):
    if not default_rate_limiter.is_allowed(f"chat:{current_user.id}", max_requests=RATE_LIMIT_CHAT, window_seconds=60):
        raise HTTPException(status_code=429, detail="Chat rate limit exceeded. Please wait a moment.")

    session_id = payload.session_id or str(uuid.uuid4())
    if not default_session_store.verify_ownership(session_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied: Session belongs to another user.")

    ConversationRepository.create_or_get_conversation(session_id, current_user.id)
    ConversationRepository.save_message(session_id, "user", payload.text)

    config = {"configurable": {"thread_id": session_id}}
    visual_context = None
    document_context = None

    if payload.files:
        if len(payload.files) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 files per request allowed.")

        multimodal_items = []
        for file_item in payload.files:
            ext = os.path.splitext(file_item.filename)[1].lower()
            if ext not in ALLOWED_FILE_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"File extension '{ext}' is not supported.")

            try:
                c_bytes = base64.b64decode(file_item.content_base64)
                if len(c_bytes) > (MAX_UPLOAD_SIZE_MB * 1024 * 1024):
                    raise HTTPException(status_code=413, detail=f"File '{file_item.filename}' exceeds max size ({MAX_UPLOAD_SIZE_MB} MB).")

                mm_input = MultimodalInput(
                    input_type=file_item.input_type,
                    content_bytes=c_bytes,
                    filename=file_item.filename,
                    mime_type=file_item.mime_type,
                )
                multimodal_items.append(mm_input)
            except HTTPException as he:
                raise he
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Invalid file payload '{file_item.filename}': {str(exc)}")

        mm_context = default_multimodal_processor.process_inputs(multimodal_items, user_query=payload.text)
        visual_context = mm_context.visual_context or None
        document_context = mm_context.document_context or None

    inputs = {
        "messages": [{"role": "user", "content": payload.text}],
        "session_id": session_id,
        "user_id": current_user.id,
        "active_memory": [],
        "pending_action": None,
        "tool_round_count": 0,
        "visual_context": visual_context,
        "document_context": document_context,
    }

    try:
        final_state = await graph_app.ainvoke(inputs, config=config)
        messages = final_state.get("messages", [])
        last_response = get_message_content(messages[-1]) if messages else "No response generated."

        ConversationRepository.save_message(session_id, "assistant", last_response)

        return ChatResponsePayload(
            session_id=session_id,
            response=last_response,
            intent=final_state.get("intent", "chat"),
            emotion_state=final_state.get("emotion_state", {}),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(exc)}")

@app.post("/voice")
async def voice_endpoint(payload: VoicePayload, current_user: User = Depends(get_current_user)):
    session_id = payload.session_id or str(uuid.uuid4())
    if not default_session_store.verify_ownership(session_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied: Session belongs to another user.")

    ConversationRepository.create_or_get_conversation(session_id, current_user.id)

    try:
        audio_bytes = base64.b64decode(payload.audio_base64)
        if len(audio_bytes) > (MAX_UPLOAD_SIZE_MB * 1024 * 1024):
            raise HTTPException(status_code=413, detail=f"Audio size exceeds maximum limit ({MAX_UPLOAD_SIZE_MB} MB).")
    except HTTPException as he:
        raise he
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid base64 audio encoding: {str(exc)}")

    try:
        voice_req = VoiceRequest(
            audio_bytes=audio_bytes,
            session_id=session_id,
            user_id=current_user.id,
            audio_format=payload.audio_format or "wav",
        )
        voice_res = await default_voice_manager.process_voice_request(voice_req)
        ConversationRepository.save_message(session_id, "user", voice_res.transcript)
        ConversationRepository.save_message(session_id, "assistant", voice_res.response_text)
        return voice_res.to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Voice pipeline failure: {str(exc)}")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, token: Optional[str] = Query(None)):
    payload = verify_token(token) if token else None
    if not payload:
        default_metrics.record_ws_error()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload["user_id"]
    if not default_session_store.verify_ownership(session_id, user_id):
        default_metrics.record_ws_error()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if not default_rate_limiter.is_allowed(f"ws_conn:{user_id}", max_requests=MAX_WS_CONNECTIONS_PER_USER, window_seconds=60):
        default_metrics.record_ws_error()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    default_metrics.record_ws_connection(+1)
    ConversationRepository.create_or_get_conversation(session_id, user_id)
    config = {"configurable": {"thread_id": session_id}}

    try:
        while True:
            data = await websocket.receive_json()
            default_metrics.record_ws_message("received")

            if not default_rate_limiter.is_allowed(f"ws_msg:{user_id}", max_requests=60, window_seconds=60):
                await websocket.send_json({"event": "error", "message": "WebSocket message rate limit exceeded."})
                continue

            if data.get("action") == "cancel" or data.get("type") == "cancel":
                default_voice_manager.cancel_session(session_id)
                await websocket.send_json({"event": "cancelled", "session_id": session_id})
                default_metrics.record_ws_message("sent")
                continue

            if "audio_base64" in data:
                audio_b64 = data.get("audio_base64", "")
                await websocket.send_json({"event": "speech_started", "session_id": session_id})
                default_metrics.record_ws_message("sent")

                try:
                    audio_bytes = base64.b64decode(audio_b64)
                    voice_req = VoiceRequest(audio_bytes=audio_bytes, session_id=session_id, user_id=user_id)
                    voice_res = await default_voice_manager.process_voice_request(voice_req)

                    ConversationRepository.save_message(session_id, "user", voice_res.transcript)
                    ConversationRepository.save_message(session_id, "assistant", voice_res.response_text)

                    await websocket.send_json({"event": "transcript", "text": voice_res.transcript})
                    await websocket.send_json({"event": "speech_finished", "session_id": session_id})
                    await websocket.send_json({
                        "event": "audio_chunk",
                        "audio_base64": base64.b64encode(voice_res.audio_bytes).decode("ascii"),
                        "text": voice_res.response_text,
                    })
                    await websocket.send_json({
                        "event": "final_answer",
                        "session_id": session_id,
                        "text": voice_res.response_text,
                    })
                    default_metrics.record_ws_message("sent")
                except Exception as exc:
                    default_metrics.record_ws_error()
                    await websocket.send_json({"event": "error", "message": str(exc)})
                continue

            user_text = data.get("text", "")
            if not user_text and "files" not in data:
                continue

            ConversationRepository.save_message(session_id, "user", user_text or "Uploaded file")
            await websocket.send_json({"event": "thinking", "data": "Processing input..."})
            default_metrics.record_ws_message("sent")

            visual_context = None
            document_context = None

            if "files" in data and isinstance(data["files"], list):
                mm_items = []
                for f_item in data["files"]:
                    try:
                        c_bytes = base64.b64decode(f_item.get("content_base64", ""))
                        mm_input = MultimodalInput(
                            input_type=f_item.get("input_type", "image"),
                            content_bytes=c_bytes,
                            filename=f_item.get("filename", "file"),
                            mime_type=f_item.get("mime_type", "image/png"),
                        )
                        mm_items.append(mm_input)
                    except Exception as exc:
                        await websocket.send_json({"event": "error", "message": f"Multimodal file error: {str(exc)}"})

                mm_ctx = default_multimodal_processor.process_inputs(mm_items, user_query=user_text)
                if mm_ctx.visual_context:
                    visual_context = mm_ctx.visual_context
                    await websocket.send_json({"event": "image_processed", "data": visual_context})
                    default_metrics.record_ws_message("sent")
                if mm_ctx.document_context:
                    document_context = mm_ctx.document_context
                    await websocket.send_json({"event": "document_processed", "data": document_context})
                    default_metrics.record_ws_message("sent")

            inputs = {
                "messages": [{"role": "user", "content": user_text or "Process uploaded file"}],
                "session_id": session_id,
                "user_id": user_id,
                "active_memory": [],
                "pending_action": None,
                "tool_round_count": 0,
                "visual_context": visual_context,
                "document_context": document_context,
            }

            async for event in graph_app.astream(inputs, config=config):
                for node_name, node_output in event.items():
                    if isinstance(node_output, dict):
                        if "active_memory" in node_output and node_output["active_memory"]:
                            await websocket.send_json({
                                "event": "memory_retrieved",
                                "data": node_output["active_memory"]
                            })
                            default_metrics.record_ws_message("sent")
                        if "current_plan" in node_output and node_output["current_plan"]:
                            await websocket.send_json({
                                "event": "plan_created",
                                "data": node_output["current_plan"]
                            })
                            default_metrics.record_ws_message("sent")
                        if "intent" in node_output:
                            await websocket.send_json({
                                "event": "thinking",
                                "data": f"Routed intent: {node_output['intent']}"
                            })
                            default_metrics.record_ws_message("sent")
                        if "tool_calls" in node_output and node_output["tool_calls"]:
                            await websocket.send_json({
                                "event": "tool_call",
                                "data": node_output["tool_calls"][0]
                            })
                            default_metrics.record_ws_message("sent")
                        if "tool_results" in node_output and node_output["tool_results"]:
                            await websocket.send_json({
                                "event": "tool_result",
                                "data": node_output["tool_results"][0]
                            })
                            default_metrics.record_ws_message("sent")
                        if "research_sources" in node_output and node_output["research_sources"]:
                            await websocket.send_json({
                                "event": "sources_retrieved",
                                "data": node_output["research_sources"]
                            })
                            default_metrics.record_ws_message("sent")
                        if "plan_results" in node_output and node_output["plan_results"]:
                            await websocket.send_json({
                                "event": "step_completed",
                                "data": node_output["plan_results"]
                            })
                            default_metrics.record_ws_message("sent")

            state = await graph_app.aget_state(config=config)
            messages = state.values.get("messages", [])
            final_text = get_message_content(messages[-1]) if messages else ""

            ConversationRepository.save_message(session_id, "assistant", final_text)

            await websocket.send_json({
                "event": "final_answer",
                "session_id": session_id,
                "text": final_text,
                "emotion": state.values.get("emotion_state", {}),
            })
            default_metrics.record_ws_message("sent")
    except WebSocketDisconnect:
        default_metrics.record_ws_connection(-1)
    except Exception as exc:
        default_metrics.record_ws_error()
        default_metrics.record_ws_connection(-1)
        await websocket.send_json({"event": "error", "message": str(exc)})
        await websocket.close()
