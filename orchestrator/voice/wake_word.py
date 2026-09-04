"""
ION Assistant — Voice Wake Word Configuration & Detection Engine.
Primary Wake Phrase: "Hey Ion"
"""
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

PRIMARY_WAKE_PHRASE: str = os.getenv("ION_WAKE_PHRASE", "Hey Ion")
WAKE_WORDS: List[str] = [PRIMARY_WAKE_PHRASE.lower(), "ion"]

class WakeWordDetector:
    """
    Wake word detector for ION assistant.
    Primary wake phrase: "Hey Ion"
    """
    def __init__(self, wake_phrase: Optional[str] = None):
        self.wake_phrase = wake_phrase or PRIMARY_WAKE_PHRASE
        self.accepted_phrases = [self.wake_phrase.lower(), "ion", "hey ion"]

    def is_wake_word_detected(self, text: str) -> bool:
        """
        Returns True if the primary wake phrase "Hey Ion" or accepted ION wake word is detected in input text.
        Returns False for legacy wake phrases like "Hey Jarvis".
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
