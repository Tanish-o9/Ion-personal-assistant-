from typing import Dict

class EmotionEngine:
    """
    Manages detection of user sentiment/mood and shapes assistant responses accordingly.
    """
    def __init__(self):
        self.moods = {
            "happy": {"pitch": 1.2, "speed": 1.1},
            "calm": {"pitch": 1.0, "speed": 1.0},
            "serious": {"pitch": 0.9, "speed": 0.9},
            "empathetic": {"pitch": 1.0, "speed": 0.8},
            "excited": {"pitch": 1.3, "speed": 1.2},
        }
        self.current_mood = "calm"

    def detect_mood(self, text: str) -> Dict[str, float]:
        keywords = {
            "sad": "empathetic",
            "urgent": "serious",
            "great": "happy",
            "wow": "excited",
            "error": "serious",
            "bug": "serious",
            "help": "empathetic",
        }
        for word, mood in keywords.items():
            if word in text.lower():
                self.current_mood = mood
                break
        return self.moods.get(self.current_mood, self.moods["calm"])

    def shape_response(self, text: str) -> str:
        # Simple tone modifier; will be expanded with persistent PersonaState in Phase 4
        return text
