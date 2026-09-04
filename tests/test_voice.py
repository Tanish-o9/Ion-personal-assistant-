import base64
import pytest
from fastapi.testclient import TestClient

from orchestrator.voice.models import VoiceRequest, VoiceResponse
from orchestrator.voice.stt import MockSpeechToTextProvider
from orchestrator.voice.tts import MockTextToSpeechProvider
from orchestrator.voice.manager import VoiceManager
from orchestrator.llm_client import LLMClient, LLMResponse
from orchestrator.graph import build_orchestrator_graph
from api.main import app

class MockLLM(LLMClient):
    async def generate(self, messages, system_prompt=None, model_name="claude-3-5-sonnet-20241022"):
        return LLMResponse(
            text="The answer is 100, sir.",
            model_used="mock-llm",
            token_count=10,
            latency_ms=5.0,
        )

# ---------------------------------------------------------------------------
# 1. STT Provider Unit Tests
# ---------------------------------------------------------------------------

def test_stt_provider_valid_and_empty():
    stt = MockSpeechToTextProvider()

    # Empty audio error
    with pytest.raises(ValueError, match="Invalid or empty audio input"):
        stt.transcribe(b"")

    # Transcribe text payload embedded in audio bytes
    text_audio = "What is 50 + 50?".encode("utf-8")
    res = stt.transcribe(text_audio)
    assert res == "What is 50 + 50?"

def test_hey_ion_wake_word_detection():
    from orchestrator.voice.wake_word import WakeWordDetector
    detector = WakeWordDetector()
    assert detector.is_wake_word_detected("Hey Ion, what is the status?")
    assert detector.is_wake_word_detected("Hey Ion")
    assert not detector.is_wake_word_detected("ion start research")
    assert not detector.is_wake_word_detected("Hey Jarvis")

# ---------------------------------------------------------------------------
# 2. TTS Provider Unit Tests
# ---------------------------------------------------------------------------

def test_tts_provider_valid_and_empty():
    tts = MockTextToSpeechProvider()

    # Empty text error
    with pytest.raises(ValueError, match="text must be a non-empty string"):
        tts.synthesize("")

    # Synthesize valid text to WAV header
    wav_bytes = tts.synthesize("Hello sir")
    assert len(wav_bytes) >= 44
    assert wav_bytes[:4] == b"RIFF"
    assert wav_bytes[8:12] == b"WAVE"

# ---------------------------------------------------------------------------
# 3. VoiceManager End-to-End & Cancellation Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_voice_manager_pipeline_and_cancellation():
    mock_llm = MockLLM()
    graph_app = build_orchestrator_graph(mock_llm)
    manager = VoiceManager(graph_app=graph_app)

    audio_bytes = "What is 20 * 5?".encode("utf-8")
    req = VoiceRequest(audio_bytes=audio_bytes, session_id="v-session-1", user_id="v_user_1")

    res = await manager.process_voice_request(req)
    assert res.session_id == "v-session-1"
    assert res.transcript == "What is 20 * 5?"
    assert "100" in res.response_text
    assert len(res.audio_bytes) >= 44

    # Cancellation test
    manager.cancel_session("v-session-2")
    req2 = VoiceRequest(audio_bytes=audio_bytes, session_id="v-session-2", user_id="v_user_1")
    res2 = await manager.process_voice_request(req2)
    assert res2.response_text == "[Session Interrupted]"
    assert res2.audio_bytes == b""

# ---------------------------------------------------------------------------
# 4. REST API Test (POST /voice)
# ---------------------------------------------------------------------------

def test_api_post_voice_endpoint():
    client = TestClient(app)
    reg_res = client.post("/auth/register", json={"username": "voice_user", "password": "voicepassword"}).json()
    token = reg_res["token"]

    raw_audio = "Calculate 25 * 4".encode("utf-8")
    b64_audio = base64.b64encode(raw_audio).decode("ascii")

    response = client.post(
        "/voice",
        json={
            "session_id": "v-session-api",
            "audio_base64": b64_audio,
            "audio_format": "wav",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "v-session-api"
    assert data["transcript"] == "Calculate 25 * 4"
    assert "audio_base64" in data
    assert len(data["audio_base64"]) > 0
