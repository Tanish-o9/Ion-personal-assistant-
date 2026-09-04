import time
import pytest
from fastapi.testclient import TestClient

from orchestrator.voice.wake_word import WakeWordDetector
from orchestrator.voice.streaming import VoiceEventType
from api.main import app

def test_hey_ion_wake_phrase_detection():
    detector = WakeWordDetector()
    assert detector.is_wake_word_detected("Hey Ion, what's the weather today?")
    assert detector.is_wake_word_detected("Hey Ion")
    assert detector.is_wake_word_detected("ion explain docker")
    assert not detector.is_wake_word_detected("Hey Jarvis")
    assert not detector.is_wake_word_detected("random noise text")

def test_hands_free_voice_event_types():
    assert VoiceEventType.WAKE_DETECTED == "WAKE_DETECTED"
    assert VoiceEventType.LISTEN_STARTED == "LISTEN_STARTED"
    assert VoiceEventType.END_OF_TURN == "END_OF_TURN"
    assert VoiceEventType.SPEAKING_STARTED == "SPEAKING_STARTED"
    assert VoiceEventType.SPEAKING_FINISHED == "SPEAKING_FINISHED"

def test_websocket_hands_free_events():
    client = TestClient(app)

    # Register user
    reg_res = client.post("/auth/register", json={"username": "handsfree_user", "password": "password123"}).json()
    token = reg_res["token"]

    # Test WebSocket connection & events
    with client.websocket_connect(f"/ws/handsfree-session-1?token={token}") as websocket:
        # Send wake_detected event
        websocket.send_json({"action": "wake_detected"})
        msg1 = websocket.receive_json()
        assert msg1["event"] == "wake_detected"
        assert msg1["wake_phrase"] == "Hey Ion"

        # Send reset_wake event
        websocket.send_json({"action": "reset_wake"})
        msg2 = websocket.receive_json()
        assert msg2["event"] == "wake_listening"
