import os
import struct
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)

class TextToSpeechProvider(ABC):
    """
    Abstract interface for Text-to-Speech (TTS) providers.
    """
    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        pass

class MockTextToSpeechProvider(TextToSpeechProvider):
    """
    Default mock/offline TTS provider that synthesizes valid WAV audio bytes.
    Respects TTS_API_KEY and TTS_PROVIDER if configured.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TTS_API_KEY")
        self.provider_name = os.getenv("TTS_PROVIDER", "mock").lower()

    def _generate_wav_header(self, sample_rate: int = 16000, num_samples: int = 1600) -> bytes:
        """
        Generates a valid 44-byte RIFF/WAV header for PCM audio.
        """
        bytes_per_sample = 2
        data_size = num_samples * bytes_per_sample
        file_size = 36 + data_size

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            file_size,
            b"WAVE",
            b"fmt ",
            16,             # Subchunk1Size (16 for PCM)
            1,              # AudioFormat (1 for PCM)
            1,              # NumChannels (Mono)
            sample_rate,    # SampleRate
            sample_rate * bytes_per_sample, # ByteRate
            bytes_per_sample, # BlockAlign
            16,             # BitsPerSample
            b"data",
            data_size,
        )
        # Generate dummy silence PCM samples
        pcm_data = b"\x00\x00" * num_samples
        return header + pcm_data

    def synthesize(self, text: str) -> bytes:
        if not text or not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string for TTS synthesis.")

        # Length of audio proportional to text length
        num_samples = max(1600, len(text) * 100)
        return self._generate_wav_header(num_samples=num_samples)
