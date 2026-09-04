# ION AI Assistant

This repository contains the **ION AI** voice assistant backend and a modern React + TypeScript frontend control center.

## Primary Identity & Voice Activation

- **Assistant Name**: **ION**
- **Primary Voice Wake Phrase**: **“Hey Ion”**

---

## Project Structure

- `server.py` — FastAPI backend exposing `/api/chat`, `/api/voice`, `/api/memory`, `/api/analytics`, `/api/emotion`, `/api/history`
- `ai.py` — AI engine integration with Claude and Hugging Face fallback
- `memory.py` — Short-term and long-term memory store
- `emotion.py` — Emotion detection engine
- `speech.py` — Wake word ("Hey Ion") and speech transcription utilities
- `main.py` — Local voice assistant runner loop
- `orchestrator/` — Unified Intelligence Runtime (`IONUnifiedRuntime`), Capability Router, Global Reliability Engine, and Security Boundaries
- `frontend/` — React frontend control center

---

## Setup

1. Install backend Python dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```

2. Configure API keys in `.env`:
   ```text
   CLAUDE_API_KEY=your_claude_key
   HF_API_KEY=your_hf_key
   ION_WAKE_PHRASE="Hey Ion"
   ```

3. Run the backend API server:
   ```powershell
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

4. Start the frontend:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

5. Open the frontend at `http://localhost:4173` and use the ION Control Center.

---

## Notes

- The frontend proxies `/api` requests to the FastAPI backend via Vite.
- The backend uses the `AIEngine`, `EmotionEngine`, and `MemorySystem` classes coordinated via `IONUnifiedRuntime`.
- `main.py` remains available for local voice-triggered assistant use with **"Hey Ion"**.
