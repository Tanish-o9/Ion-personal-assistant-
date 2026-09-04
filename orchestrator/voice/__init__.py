from orchestrator.voice.models import VoiceRequest, VoiceResponse, AudioChunk
from orchestrator.voice.stt import SpeechToTextProvider, MockSpeechToTextProvider
from orchestrator.voice.tts import TextToSpeechProvider, MockTextToSpeechProvider
from orchestrator.voice.manager import VoiceManager

# Default instances
default_stt_provider = MockSpeechToTextProvider()
default_tts_provider = MockTextToSpeechProvider()
default_voice_manager = VoiceManager(
    stt_provider=default_stt_provider,
    tts_provider=default_tts_provider,
)

from orchestrator.voice.streaming import VoiceEventType, VoiceStreamEvent, VoiceStreamingPipeline, default_voice_streaming_pipeline

__all__ = [
    "VoiceRequest",
    "VoiceResponse",
    "AudioChunk",
    "SpeechToTextProvider",
    "MockSpeechToTextProvider",
    "TextToSpeechProvider",
    "MockTextToSpeechProvider",
    "VoiceManager",
    "default_stt_provider",
    "default_tts_provider",
    "default_voice_manager",
    "VoiceEventType",
    "VoiceStreamEvent",
    "VoiceStreamingPipeline",
    "default_voice_streaming_pipeline",
]

