import time
import logging
from typing import Any, Dict, Optional, Set

from orchestrator.voice.models import VoiceRequest, VoiceResponse
from orchestrator.voice.stt import SpeechToTextProvider, MockSpeechToTextProvider
from orchestrator.voice.tts import TextToSpeechProvider, MockTextToSpeechProvider
from orchestrator.graph import build_orchestrator_graph
from orchestrator.llm_client import LLMClient

logger = logging.getLogger(__name__)

def get_message_content(msg: Any) -> str:
    if hasattr(msg, "content"):
        return getattr(msg, "content", "") or ""
    if isinstance(msg, dict):
        return msg.get("content", "") or ""
    return str(msg)

class VoiceManager:
    """
    Coordinates real-time voice pipeline: Audio -> STT -> Graph Orchestrator -> TTS -> Audio Response.
    Shares session_id and user_id state with the text orchestrator.
    """
    def __init__(
        self,
        stt_provider: Optional[SpeechToTextProvider] = None,
        tts_provider: Optional[TextToSpeechProvider] = None,
        graph_app: Optional[Any] = None,
    ):
        self.stt_provider = stt_provider or MockSpeechToTextProvider()
        self.tts_provider = tts_provider or MockTextToSpeechProvider()

        if graph_app is None:
            llm_client = LLMClient()
            self.graph_app = build_orchestrator_graph(llm_client)
        else:
            self.graph_app = graph_app

        self._cancelled_sessions: Set[str] = set()

    def cancel_session(self, session_id: str) -> None:
        """
        Marks a session as cancelled to interrupt active TTS/playback.
        """
        if session_id:
            self._cancelled_sessions.add(session_id)

    def is_cancelled(self, session_id: str) -> bool:
        """
        Checks if a session cancellation signal was received.
        """
        return session_id in self._cancelled_sessions

    def clear_cancellation(self, session_id: str) -> None:
        """
        Clears cancellation flag for a session.
        """
        self._cancelled_sessions.discard(session_id)

    async def process_voice_request(self, request: VoiceRequest) -> VoiceResponse:
        """
        Executes the end-to-end voice pipeline for a VoiceRequest.
        """
        start_time = time.time()

        # Step 1: Speech-to-Text Transcription
        transcript = self.stt_provider.transcribe(request.audio_bytes, audio_format=request.audio_format)
        logger.info("Voice STT Transcribed: '%s' (session_id=%s)", transcript, request.session_id)

        if self.is_cancelled(request.session_id):
            return VoiceResponse(
                session_id=request.session_id,
                transcript=transcript,
                response_text="[Session Interrupted]",
                audio_bytes=b"",
                duration_ms=(time.time() - start_time) * 1000,
            )

        # Step 2: Pass transcript to LangGraph orchestrator (shares session_id & user_id state)
        config = {"configurable": {"thread_id": request.session_id}}
        inputs = {
            "messages": [{"role": "user", "content": transcript}],
            "session_id": request.session_id,
            "user_id": request.user_id,
            "active_memory": [],
            "pending_action": None,
            "tool_round_count": 0,
        }

        final_state = await self.graph_app.ainvoke(inputs, config=config)
        messages = final_state.get("messages", [])
        response_text = get_message_content(messages[-1]) if messages else "I processed your request, sir."

        if self.is_cancelled(request.session_id):
            return VoiceResponse(
                session_id=request.session_id,
                transcript=transcript,
                response_text=response_text,
                audio_bytes=b"",
                duration_ms=(time.time() - start_time) * 1000,
            )

        # Step 3: Text-to-Speech Synthesis
        audio_response_bytes = self.tts_provider.synthesize(response_text)
        elapsed_ms = (time.time() - start_time) * 1000

        return VoiceResponse(
            session_id=request.session_id,
            transcript=transcript,
            response_text=response_text,
            audio_bytes=audio_response_bytes,
            duration_ms=elapsed_ms,
        )
