import random

class EmotionEngine:
    def __init__(self):
        self.moods = {
            "happy": {"pitch": 1.2, "speed": 1.1},
            "calm": {"pitch": 1.0, "speed": 1.0},
            "serious": {"pitch": 0.9, "speed": 0.9},
            "empathetic": {"pitch": 1.0, "speed": 0.8},
            "excited": {"pitch": 1.3, "speed": 1.2},
            # ... add up to 12 moods
        }
        self.current_mood = "calm"

    def detect_mood(self, text):
        keywords = {
            "sad": "empathetic",
            "urgent": "serious",
            "great": "happy",
            "wow": "excited"
        }
        for word, mood in keywords.items():
            if word in text.lower():
                self.current_mood = mood
                return self.mood_params()
        return self.mood_params()

    def mood_params(self):
        return self.moods[self.current_mood]
