import os
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)

class SpeechToTextProvider(ABC):
    """
    Abstract interface for Speech-to-Text (STT) providers.
    """
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, audio_format: str = "wav") -> str:
        pass

class MockSpeechToTextProvider(SpeechToTextProvider):
    """
    Default mock/offline STT provider for fast testing and local execution without API keys.
    Respects STT_API_KEY and STT_PROVIDER if configured.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("STT_API_KEY")
        self.provider_name = os.getenv("STT_PROVIDER", "mock").lower()

    def transcribe(self, audio_bytes: bytes, audio_format: str = "wav") -> str:
        if not audio_bytes or len(audio_bytes) == 0:
            raise ValueError("Invalid or empty audio input for transcription.")

        # Attempt to decode string content embedded in test audio payloads
        try:
            decoded = audio_bytes.decode("utf-8", errors="ignore").strip()
            if decoded and any(c.isalnum() for c in decoded) and len(decoded) > 2:
                return decoded
        except Exception:
            pass

        # Default fallback transcript for binary test audio
        return "Hello Ion, what is 20 * 5?"
