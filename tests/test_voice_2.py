"""
Unit Tests for Phase 68: Natural Voice 2.0 Streaming & Interruption.
"""

import pytest
from orchestrator.voice import (
    VoiceStreamingPipeline,
    VoiceEventType,
)

def test_voice_streaming_and_interruption():
    pipe = VoiceStreamingPipeline()
    session_id = "sess_voice_1"
    user_id = "user_voice_1"

    # Start TTS stream
    evt_start = pipe.start_tts_stream(session_id, user_id, audio_duration_seconds=5.0)
    assert evt_start.event_type == VoiceEventType.RESPONSE_STARTED
    assert pipe.is_tts_active(session_id) is True

    # User speaks while TTS is playing -> INTERRUPTED & TTS cancelled
    evt_speech = pipe.handle_user_speech_start(session_id, user_id)
    assert evt_speech.event_type == VoiceEventType.INTERRUPTED
    assert evt_speech.payload["was_tts_active"] is True
    assert pipe.is_tts_active(session_id) is False

def test_streaming_transcript_events():
    pipe = VoiceStreamingPipeline()
    session_id = "sess_voice_2"

    evt_partial = pipe.process_streaming_transcript(session_id, "Hello JARVIS", is_final=False)
    assert evt_partial.event_type == VoiceEventType.TRANSCRIPT_PARTIAL
    assert evt_partial.payload["is_final"] is False

    evt_final = pipe.process_streaming_transcript(session_id, "Hello JARVIS, what is the weather?", is_final=True)
    assert evt_final.event_type == VoiceEventType.TRANSCRIPT_FINAL
    assert evt_final.payload["is_final"] is True
