"""
ION Assistant — Voice Wake Word Configuration & Detection Engine.
Primary Wake Phrase: "Hey Ion"
"""
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

PRIMARY_WAKE_PHRASE: str = os.getenv("ION_WAKE_PHRASE", "Hey Ion")
DEFAULT_PHONETIC_VARIANTS: List[str] = [
    v.strip().lower() for v in os.getenv("ION_WAKE_VARIANTS", "hey iron, hey ian").split(",") if v.strip()
]

class WakeWordDetector:
    """
    Wake word detector for ION assistant.
    Primary wake phrase: "Hey Ion"
    Phonetic variants (e.g. "hey iron", "hey ian") are configurable via ION_WAKE_VARIANTS env.
    """
    def __init__(self, wake_phrase: Optional[str] = None, phonetic_variants: Optional[List[str]] = None):
        self.wake_phrase = wake_phrase or PRIMARY_WAKE_PHRASE
        self.phonetic_variants = phonetic_variants or DEFAULT_PHONETIC_VARIANTS
        self.accepted_phrases = list(set([self.wake_phrase.lower().strip()] + [v.lower().strip() for v in self.phonetic_variants]))

    def is_wake_word_detected(self, text: str) -> bool:
        """
        Returns True if the primary wake phrase "Hey Ion" is detected in input text.
        Returns False for standalone "ion", legacy "Hey Jarvis", or unrelated conversation.
        """
        if not text:
            return False
        normalized = text.lower().strip()
        return any(phrase in normalized for phrase in self.accepted_phrases)

    def get_wake_word_config(self) -> Dict[str, Any]:
        return {
            "primary_wake_phrase": self.wake_phrase,
            "accepted_wake_words": self.accepted_phrases,
            "engine": "ION_WAKE_WORD_ENGINE_V1",
            "custom_model_required": False
        }

default_wake_word_detector = WakeWordDetector()
