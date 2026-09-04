import base64
from typing import Any, Dict, Optional

class VoiceRequest:
    """
    Represents an incoming voice interaction request.
    """
    def __init__(
        self,
        audio_bytes: bytes,
        session_id: str,
        user_id: str = "default_user",
        audio_format: str = "wav",
    ):
        if not audio_bytes or len(audio_bytes) == 0:
            audio_bytes = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"

        self.audio_bytes = audio_bytes
        self.session_id = session_id
        self.user_id = user_id
        self.audio_format = audio_format.lower().strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "audio_format": self.audio_format,
            "audio_size_bytes": len(self.audio_bytes),
            "audio_base64": base64.b64encode(self.audio_bytes).decode("ascii"),
        }

class VoiceResponse:
    """
    Represents the output of a voice interaction pipeline.
    """
    def __init__(
        self,
        session_id: str,
        transcript: str,
        response_text: str,
        audio_bytes: bytes,
        duration_ms: float = 0.0,
    ):
        self.session_id = session_id
        self.transcript = transcript
        self.response_text = response_text
        self.audio_bytes = audio_bytes
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "transcript": self.transcript,
            "response_text": self.response_text,
            "audio_size_bytes": len(self.audio_bytes),
            "audio_base64": base64.b64encode(self.audio_bytes).decode("ascii"),
            "duration_ms": self.duration_ms,
        }

class AudioChunk:
    """
    Represents an incremental streaming audio chunk.
    """
    def __init__(self, chunk_index: int, audio_bytes: bytes, is_final: bool = False):
        self.chunk_index = chunk_index
        self.audio_bytes = audio_bytes
        self.is_final = is_final

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_index": self.chunk_index,
            "audio_size_bytes": len(self.audio_bytes),
            "audio_base64": base64.b64encode(self.audio_bytes).decode("ascii"),
            "is_final": self.is_final,
        }
