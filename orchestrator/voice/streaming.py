"""
Phase 68: Natural Voice 2.0 Streaming & Interruption Manager.
"""

import enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from orchestrator.resources import default_resource_manager

class VoiceEventType(str, enum.Enum):
    WAKE_DETECTED = "WAKE_DETECTED"
    LISTEN_STARTED = "LISTEN_STARTED"
    SPEECH_STARTED = "SPEECH_STARTED"
    SPEECH_ENDED = "SPEECH_ENDED"
    END_OF_TURN = "END_OF_TURN"
    TRANSCRIPT_PARTIAL = "TRANSCRIPT_PARTIAL"
    TRANSCRIPT_FINAL = "TRANSCRIPT_FINAL"
    RESPONSE_STARTED = "RESPONSE_STARTED"
    AUDIO_CHUNK = "AUDIO_CHUNK"
    RESPONSE_FINISHED = "RESPONSE_FINISHED"
    SPEAKING_STARTED = "SPEAKING_STARTED"
    SPEAKING_FINISHED = "SPEAKING_FINISHED"
    INTERRUPTED = "INTERRUPTED"

class VoiceStreamEvent(BaseModel):
    session_id: str
    event_type: VoiceEventType
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class VoiceStreamingPipeline:
    """Manages low-latency real-time voice streaming over WebSockets with interruption handling and resource budget tracking."""

    def __init__(self):
        self._active_tts_streams: Dict[str, bool] = {}  # session_id -> is_playing

    def handle_user_speech_start(self, session_id: str, user_id: str) -> VoiceStreamEvent:
        """Triggers immediate interruption and cancellation of active TTS audio playback."""
        is_interrupted = self.cancel_active_tts(session_id)
        return VoiceStreamEvent(
            session_id=session_id,
            event_type=VoiceEventType.INTERRUPTED if is_interrupted else VoiceEventType.SPEECH_STARTED,
            payload={"was_tts_active": is_interrupted}
        )

    def process_streaming_transcript(self, session_id: str, text_chunk: str, is_final: bool = False) -> VoiceStreamEvent:
        return VoiceStreamEvent(
            session_id=session_id,
            event_type=VoiceEventType.TRANSCRIPT_FINAL if is_final else VoiceEventType.TRANSCRIPT_PARTIAL,
            payload={"transcript": text_chunk, "is_final": is_final}
        )

    def start_tts_stream(self, session_id: str, user_id: str, audio_duration_seconds: float) -> VoiceStreamEvent:
        self._active_tts_streams[session_id] = True

        # Track usage in resource manager
        default_resource_manager.record_usage(
            user_id=user_id,
            input_tokens=int(audio_duration_seconds * 10),
            output_tokens=int(audio_duration_seconds * 10)
        )

        return VoiceStreamEvent(
            session_id=session_id,
            event_type=VoiceEventType.RESPONSE_STARTED,
            payload={"audio_duration_seconds": audio_duration_seconds}
        )

    def cancel_active_tts(self, session_id: str) -> bool:
        if self._active_tts_streams.get(session_id, False):
            self._active_tts_streams[session_id] = False
            return True
        return False

    def is_tts_active(self, session_id: str) -> bool:
        return self._active_tts_streams.get(session_id, False)

default_voice_streaming_pipeline = VoiceStreamingPipeline()
