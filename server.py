from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
import time
import os

from ai import AIEngine
try:
    from emotion import EmotionEngine
except Exception:
    # Fallback minimal EmotionEngine to avoid import-time failures
    class EmotionEngine:
        def __init__(self):
            self.current_mood = 'calm'

        def detect_mood(self, text):
            return {'pitch': 1.0, 'speed': 1.0}

try:
    from memory import MemorySystem
except Exception:
    # Minimal fallback MemorySystem if import fails
    import json

    class MemorySystem:
        def __init__(self, long_term_file="long_term.json"):
            self.short_term = {}
            self.long_term_file = long_term_file
            self.long_term = {}

        def update_short_term(self, key, value):
            self.short_term[key] = value

        def update_long_term(self, key, value):
            self.long_term[key] = value
            try:
                with open(self.long_term_file, "w") as f:
                    json.dump(self.long_term, f)
            except Exception:
                pass

        def get_context(self):
            return {**self.long_term, **self.short_term}

load_dotenv()

app = FastAPI(
    title='Ion AI Assistant API',
    description='Backend API for Ion voice assistant and dashboard integration.',
    version='1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

from database import init_db
from orchestrator.auth import (
    hash_password,
    verify_password,
    create_token,
    verify_token,
    default_user_store,
)
from fastapi import Request

init_db()

class AuthPayload(BaseModel):
    username: str
    password: str

@app.post("/auth/register")
@app.post("/api/auth/register")
def register_auth(payload: AuthPayload):
    try:
        username = (payload.username or "").strip()
        password = (payload.password or "").strip()
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required.")
        
        existing = default_user_store.get_by_username(username)
        if existing:
            raise HTTPException(status_code=400, detail="User already exists. Please login instead.")
        
        p_hash = hash_password(password)
        user = default_user_store.register_user(username=username, password_hash=p_hash)
        token = create_token(user_id=user.id, username=user.username)
        return {"token": token, "user": user.to_dict()}
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"[AUTH ERROR] Registration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@app.post("/auth/login")
@app.post("/api/auth/login")
def login_auth(payload: AuthPayload):
    try:
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
        print(f"[AUTH ERROR] Login failed: {e}")
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@app.get("/auth/me")
@app.get("/api/auth/me")
def me_auth(request: Request):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization token.")
        token_str = auth_header.split(" ")[1]
        tok_payload = verify_token(token_str)
        if not tok_payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token.")
        user = default_user_store.get_by_id(tok_payload.get("sub", ""))
        if not user:
            raise HTTPException(status_code=401, detail="User not found.")
        return {"user": user.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth error: {str(e)}")

class ChatRequest(BaseModel):
    question: str
    context: List[Dict[str, str]] = []
    model: str = 'claude'

class ChatMessage(BaseModel):
    id: str
    role: str
    content: str
    createdAt: str

class ChatResponse(BaseModel):
    message: ChatMessage
    responseTimeMs: float

class MemoryEntryPayload(BaseModel):
    category: str
    title: str
    value: str

class VoiceRequest(BaseModel):
    audioInput: str
    model: str = 'claude'

class VoiceResponse(BaseModel):
    message: ChatMessage
    responseTimeMs: float

class EmotionRecord(BaseModel):
    id: str
    label: str
    confidence: float
    createdAt: str

class AnalyticsSummary(BaseModel):
    totalConversations: int
    memoryEntries: int
    apiUsage: int
    avgResponseTime: float
    emotionDistribution: Dict[str, int]
    mostUsedCommands: List[str]

claude_api_key = os.getenv('CLAUDE_API_KEY', 'YOUR_CLAUDE_KEY')
hf_api_key = os.getenv('HF_API_KEY', 'YOUR_HF_KEY')

engine = AIEngine(claude_api_key=claude_api_key, hf_api_key=hf_api_key)
memory_system = MemorySystem()
emotion_engine = EmotionEngine()

conversation_history: List[Dict[str, str]] = []
emotion_history: List[EmotionRecord] = []
api_usage_counter = 0
response_time_total = 0.0

@app.post('/api/chat', response_model=ChatResponse)
def post_chat(payload: ChatRequest):
    global api_usage_counter, response_time_total
    start_time = time.time()
    prompt = payload.question
    if payload.context:
        context_text = '\n'.join([f"{item.get('role')}:{item.get('content')}" for item in payload.context])
        prompt = f"{context_text}\nUser: {payload.question}"

    emotion_params = emotion_engine.detect_mood(payload.question)
    response_text = engine.get_response(prompt, model=payload.model)
    if response_text is None:
        raise HTTPException(status_code=502, detail='Unable to reach AI model service.')

    chat_message = {
        'id': str(int(time.time() * 1000)),
        'role': 'assistant',
        'content': response_text,
        'createdAt': datetime.utcnow().isoformat() + 'Z',
    }
    conversation_history.append(chat_message)
    memory_system.update_short_term('last_question', payload.question)
    memory_system.update_short_term('last_response', response_text)

    api_usage_counter += 1
    duration_ms = (time.time() - start_time) * 1000
    response_time_total += duration_ms

    record = EmotionRecord(
        id=str(len(emotion_history) + 1),
        label=emotion_engine.current_mood,
        confidence=0.9,
        createdAt=datetime.utcnow().isoformat() + 'Z',
    )
    emotion_history.append(record)

    return ChatResponse(
        message=ChatMessage(**chat_message),
        responseTimeMs=round(duration_ms, 2),
    )

@app.post('/api/voice', response_model=VoiceResponse)
def post_voice(payload: VoiceRequest):
    global api_usage_counter, response_time_total
    start_time = time.time()
    user_prompt = payload.audioInput

    emotion_engine.detect_mood(user_prompt)
    response_text = engine.get_response(user_prompt, model=payload.model)
    if response_text is None:
        raise HTTPException(status_code=502, detail='Voice model service unavailable.')

    chat_message = {
        'id': str(int(time.time() * 1000)),
        'role': 'assistant',
        'content': response_text,
        'createdAt': datetime.utcnow().isoformat() + 'Z',
    }
    conversation_history.append(chat_message)
    memory_system.update_short_term('last_voice_input', payload.audioInput)
    memory_system.update_short_term('last_voice_response', response_text)

    api_usage_counter += 1
    duration_ms = (time.time() - start_time) * 1000
    response_time_total += duration_ms

    record = EmotionRecord(
        id=str(len(emotion_history) + 1),
        label=emotion_engine.current_mood,
        confidence=0.9,
        createdAt=datetime.utcnow().isoformat() + 'Z',
    )
    emotion_history.append(record)

    return VoiceResponse(
        message=ChatMessage(**chat_message),
        responseTimeMs=round(duration_ms, 2),
    )

@app.get('/api/memory')
def get_memory():
    results = []
    for index, (key, value) in enumerate({**memory_system.long_term, **memory_system.short_term}.items(), start=1):
        results.append({
            'id': str(index),
            'category': 'long-term' if key in memory_system.long_term else 'short-term',
            'title': key,
            'value': str(value),
            'createdAt': datetime.utcnow().isoformat() + 'Z',
        })
    return results

@app.post('/api/memory')
def post_memory(payload: MemoryEntryPayload):
    if payload.category == 'long-term':
        memory_system.update_long_term(payload.title, payload.value)
    else:
        memory_system.update_short_term(payload.title, payload.value)
    return {'status': 'success', 'entry': payload.dict()}

@app.get('/api/analytics', response_model=AnalyticsSummary)
def get_analytics():
    distribution: Dict[str, int] = {}
    for record in emotion_history:
        distribution[record.label] = distribution.get(record.label, 0) + 1

    return AnalyticsSummary(
        totalConversations=len(conversation_history),
        memoryEntries=len(memory_system.long_term) + len(memory_system.short_term),
        apiUsage=api_usage_counter,
        avgResponseTime=round(response_time_total / api_usage_counter, 2) if api_usage_counter else 0.0,
        emotionDistribution=distribution,
        mostUsedCommands=['Summarize notes', 'Schedule meeting', 'Brief executive summary'],
    )

@app.get('/api/emotion')
def get_emotion():
    return {
        'current': {
            'label': emotion_engine.current_mood,
            'confidence': 0.9,
        },
        'history': [record.dict() for record in emotion_history[-12:]],
    }

@app.get('/api/history')
def get_history():
    return conversation_history

# Phase 55 Goal Endpoints
from orchestrator.goals import default_goal_manager, GoalCreatePayload, GoalStatus

@app.post('/api/goals')
def create_goal(payload: GoalCreatePayload, user_id: str = "default_user"):
    goal = default_goal_manager.create_goal(user_id=user_id, payload=payload)
    default_goal_manager.plan_goal(goal.id, user_id=user_id)
    return default_goal_manager.get_goal(goal.id, user_id=user_id)

@app.get('/api/goals/{goal_id}')
def get_goal(goal_id: str, user_id: str = "default_user"):
    goal = default_goal_manager.get_goal(goal_id, user_id=user_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@app.post('/api/goals/{goal_id}/step')
def step_goal(goal_id: str, user_id: str = "default_user"):
    goal = default_goal_manager.step_goal(goal_id, user_id=user_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@app.post('/api/goals/{goal_id}/pause')
def pause_goal(goal_id: str, user_id: str = "default_user"):
    return default_goal_manager.pause_goal(goal_id, user_id=user_id)

@app.post('/api/goals/{goal_id}/resume')
def resume_goal(goal_id: str, user_id: str = "default_user"):
    return default_goal_manager.resume_goal(goal_id, user_id=user_id)

@app.post('/api/goals/{goal_id}/cancel')
def cancel_goal(goal_id: str, user_id: str = "default_user"):
    return default_goal_manager.cancel_goal(goal_id, user_id=user_id)

@app.post('/api/goals/{goal_id}/retry')
def retry_goal(goal_id: str, user_id: str = "default_user"):
    return default_goal_manager.retry_goal(goal_id, user_id=user_id)

# Phase 56-65 Unified Platform Endpoints
from orchestrator.workspaces import default_organization_manager
from orchestrator.connectors import default_connector_registry
from orchestrator.analytics import default_analytics_engine
from orchestrator.workflows import default_workflow_engine
from orchestrator.marketplace import default_marketplace_manager
from orchestrator.platform.unified import default_unified_pipeline

@app.get('/api/organizations/{org_id}')
def get_organization(org_id: str, user_id: str = "default_user"):
    org = default_organization_manager.get_organization(org_id, user_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@app.get('/api/connectors')
def list_connectors():
    return [c.dict() for c in default_connector_registry.list_connectors()]

@app.get('/api/analytics/summary')
def get_analytics_summary(user_id: str = "default_user"):
    return default_analytics_engine.compute_summary(user_id=user_id).dict()

@app.get('/api/marketplace/capabilities')
def list_marketplace_capabilities():
    return [c.dict() for c in default_marketplace_manager.discover_capabilities()]

@app.post('/api/workflows')
def create_workflow(payload: Dict[str, Any], user_id: str = "default_user"):
    return default_workflow_engine.create_workflow(
        user_id=user_id,
        name=payload.get("name", "Untitled Workflow"),
        nodes=payload.get("nodes", []),
        edges=payload.get("edges", []),
        description=payload.get("description", "")
    )

@app.post('/api/platform/execute')
def execute_unified_capability(payload: Dict[str, Any], user_id: str = "default_user"):
    res = default_unified_pipeline.execute_capability(
        user_id=user_id,
        capability_name=payload.get("capability_name", "web_search"),
        capability_type=payload.get("capability_type", "tool"),
        payload=payload.get("payload", {})
    )
    return res.dict()


