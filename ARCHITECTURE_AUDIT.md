# Architecture Audit & Migration Plan: Jarvis at Scale

## Step 1 — Audit of Existing Files

### 1. `ai.py`
- **What it does:** Defines the `AIEngine` class which manages LLM calls with a multi-tiered fallback strategy: Anthropic Claude API -> Hugging Face Inference API -> Local `transformers` model (`gpt2`) -> fallback string message.
- **External Services / APIs:**
  - Anthropic API (`https://api.anthropic.com/v1/messages` using `claude-3-5-sonnet-20241022`)
  - Hugging Face Inference API (`https://api-inference.huggingface.co/models/{model}`)
  - Local PyTorch/Transformers pipeline (`gpt2` on CUDA or CPU)
- **State Persisted:** None (stateless in-memory `local_generator` instance cache).
- **Status:** Reusable core logic. Will be refactored into `orchestrator/llm_client.py` as an async client with retries and structured output support.

### 2. `server.py`
- **What it does:** FastAPI REST backend providing routes for `/api/chat`, `/api/voice`, `/api/memory`, `/api/analytics`, `/api/emotion`, and `/api/history`. Contains inline fallback classes for `EmotionEngine` and `MemorySystem` if module imports fail.
- **External Services / APIs:** Direct wrapper around `ai.py`, `memory.py`, and `emotion.py`.
- **State Persisted:** In-memory lists (`conversation_history`, `emotion_history`) and counters (`api_usage_counter`, `response_time_total`).
- **Status:** Reusable REST routing patterns. Will be migrated and upgraded into `api/` (with FastAPI routes and WebSocket support `/ws/{session_id}`) and integrated with Redis/PostgreSQL.

### 3. `main.py`
- **What it does:** CLI entry point running an infinite `while True` loop: listening for wake word -> transcribing speech -> updating short-term memory -> detecting mood -> querying AI engine -> printing response.
- **External Services / APIs:** Uses `speech.py`, `memory.py`, `emotion.py`, `ai.py`.
- **State Persisted:** Indirectly via `memory.py`.
- **Status:** Legacy synchronous loop. Will be replaced by `voice/daemon.py` for continuous voice streaming and retained as `main.py --text-mode` for typed CLI testing against `orchestrator/`.

### 4. `speech.py`
- **What it does:** Provides `listen_for_wake_word()` and `transcribe_speech()` functions using `speech_recognition` (Google Speech Recognition API) and PyAudio microphone capture.
- **External Services / APIs:** Google Speech Recognition API (via `speech_recognition`).
- **State Persisted:** None.
- **Status:** Basic single-shot STT. Will be upgraded into `voice/` service (wake word engine with Porcupine/openWakeWord, VAD with `webrtcvad`/Silero, and sentence-level TTS with barge-in support).

### 5. `memory.py`
- **What it does:** Implements `MemorySystem` managing an in-memory `short_term` dictionary and a file-backed `long_term` JSON database (`long_term.json`).
- **External Services / APIs:** None.
- **State Persisted:** JSON file (`long_term.json`).
- **Status:** Simple file storage. Will be replaced by `memory/` using Redis (short-term & checkpoints) and PostgreSQL + pgvector (long-term semantic & episodic vector search).

### 6. `emotion.py`
- **What it does:** Implements `EmotionEngine` mapping keyword triggers ("sad", "urgent", "great", "wow") to mood parameters (`pitch`, `speed`) and maintaining `current_mood`.
- **External Services / APIs:** None.
- **State Persisted:** In-memory state (`current_mood`).
- **Status:** Keyword-based mood detector. Will be upgraded into `orchestrator/emotion_engine.py` with persistent `PersonaState` stored in PostgreSQL and tone shaping in response generation.

### 7. `check_server.py`
- **What it does:** Simple health-check utility script making a GET request to `http://127.0.0.1:8001/api/analytics`.
- **External Services / APIs:** Local HTTP endpoint.
- **State Persisted:** None.
- **Status:** Utility script. Will be migrated to `tests/` or integrated into `infra/` health checks.

### 8. `fast_chat_test.py`
- **What it does:** Test script posting a sample question to `http://127.0.0.1:8001/api/chat`.
- **External Services / APIs:** Local HTTP endpoint.
- **State Persisted:** None.
- **Status:** Utility test script. Replaced by `tests/test_orchestrator.py` and `tests/smoke_test.py`.

### 9. `run_model_fast.py`
- **What it does:** Duplicate helper script posting a chat request to `http://127.0.0.1:8001/api/chat`.
- **External Services / APIs:** Local HTTP endpoint.
- **State Persisted:** None.
- **Status:** Duplicate script / dead code. Will be consolidated into `tests/`.

### 10. `test_claude.py`
- **What it does:** Standalone test script verifying Anthropic Claude API key presence and basic completion via `ai.AIEngine`.
- **External Services / APIs:** Anthropic Claude API.
- **State Persisted:** None.
- **Status:** Utility script. Migrated into `tests/test_orchestrator.py`.

### 11. `requirements.txt`
- **What it does:** Lists current Python dependencies (`SpeechRecognition`, `pyaudio`, `pyttsx3`, `gTTS`, `requests`, `simplejson`, `transformers`, `torch`, `httpx`, `snowboy`, `webrtcvad`, `python-dotenv`, `fastapi`, `uvicorn`, `pydantic`).
- **External Services / APIs:** N/A.
- **Status:** Baseline dependency list. Needs upgrading to include `langgraph`, `langgraph-checkpoint-redis`, `sqlalchemy`, `asyncpg`, `pgvector`, `redis`, `playwright`, `pydantic-settings`, etc.

### 12. `frontend/`
- **What it does:** React + Vite + Tailwind CSS dashboard UI containing chat interface, memory view, and analytics components.
- **External Services / APIs:** Talks to `server.py` on port 8001.
- **State Persisted:** Client UI state.
- **Status:** Will be upgraded in Phase 9 into a real-time React dashboard with live WebSocket event streaming, confirmation modals, memory browser, and audit viewer.

---

## Step 2 — Target Directory Layout

```
jarvis/
  orchestrator/        <- brain: LangGraph supervisor graph, intent routing, llm_client, emotion_engine
  voice/               <- wake word, streaming STT, TTS with barge-in, voice daemon
  memory/              <- Redis (short-term & checkpoints) + PostgreSQL/pgvector (long-term semantic)
  executor/            <- sandboxed action execution layer with permission tiers (0-3) and plugins
  agents/              <- specialized sub-agents (coder, research, system, scheduler)
  api/                 <- FastAPI application (REST + WebSocket endpoints)
  frontend/            <- React + Vite real-time dashboard UI
  infra/               <- docker-compose.yml, secrets management, database migrations, setup scripts
  tests/               <- unit tests, integration tests, and smoke test suite
  ARCHITECTURE_AUDIT.md
  requirements.txt
  .env.example
```

---

## Step 3 — Migration Mapping Matrix

| Existing File | Target Location | Disposition & Reusability |
|---|---|---|
| `ai.py` | `orchestrator/llm_client.py` | Refactor into async Anthropic Claude client with Hugging Face fallback and backoff retry logic. |
| `speech.py` | `voice/` (`wake_word.py`, `listener.py`, `speaker.py`, `daemon.py`) | Upgrade single-shot speech recognition into continuous wake-word detection, streaming STT, VAD, and barge-in TTS. |
| `memory.py` | `memory/` (`short_term.py`, `long_term.py`, `models.py`, `migrate_json.py`) | Replace JSON storage with Redis (working memory/checkpoints) and PostgreSQL + pgvector (embeddings and recall). Include one-time JSON migration script. |
| `emotion.py` | `orchestrator/emotion_engine.py` | Upgrade keyword matching into persistent `PersonaState` dataclass + response shape modifier. |
| `server.py` | `api/` (`main.py`, `audit_routes.py`) | Upgrade FastAPI REST API and add WebSocket `/ws/{session_id}` for streaming graph events and live confirmations. |
| `main.py` | `voice/daemon.py` & `main.py` | `voice/daemon.py` becomes primary voice loop. `main.py` retained with `--text-mode` flag for CLI testing. |
| `check_server.py` | `infra/` / `tests/smoke_test.py` | Refactor into automated health check & smoke test. |
| `fast_chat_test.py` | `tests/test_orchestrator.py` | Consolidate into pytest suite. |
| `run_model_fast.py` | `tests/test_orchestrator.py` | Remove duplicate file; consolidate test cases. |
| `test_claude.py` | `tests/test_orchestrator.py` | Consolidate LLM API test into pytest suite. |
| `requirements.txt` | `requirements.txt` | Expand with LangGraph, Redis, pgvector, SQLAlchemy, Playwright, websockets dependencies. |
| `.env` | `.env.example` & `infra/secrets.py` | Create validated template `.env.example` and Pydantic secrets configuration loader. |

---

## Step 4 — Dependency Baseline & Audit

### Imports Found Across Workspace:
- `requests` (used in `ai.py`)
- `transformers`, `torch` (used in `ai.py` for optional local model execution)
- `logging` (standard library, `ai.py`)
- `fastapi`, `pydantic`, `uvicorn` (used in `server.py`)
- `dotenv` / `python-dotenv` (used in `server.py`, `main.py`, `test_claude.py`)
- `time`, `os`, `json`, `datetime`, `random`, `urllib` (standard library)
- `speech_recognition` (used in `speech.py`)

### Dependency Audit Checklist:
1. **Installed / Declared in `requirements.txt`:**
   - `SpeechRecognition`, `pyaudio`, `pyttsx3`, `gTTS`, `requests`, `simplejson`, `transformers`, `torch`, `httpx`, `snowboy`, `webrtcvad`, `python-dotenv`, `fastapi`, `uvicorn`, `pydantic`.
2. **Missing Dependencies for Scaled Target Architecture:**
   - `langgraph`, `langgraph-checkpoint-redis`, `langchain-anthropic` (for Orchestrator)
   - `websockets` (for real-time streaming WS in FastAPI)
   - `sqlalchemy`, `asyncpg`, `pgvector`, `redis`, `alembic` (for Memory System v2)
   - `playwright` (for Executor browser plugin)
   - `pytest`, `pytest-asyncio` (for test suite)
3. **Flagged Unused / Obsolete Dependencies:**
   - `snowboy` (legacy Python 2/3 wake word library, unsupported on modern platforms — will replace with `pvporcupine` or `openwakeword`).
