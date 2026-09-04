import os
from dotenv import load_dotenv
from speech import listen_for_wake_word, transcribe_speech
from memory import MemorySystem
from emotion import EmotionEngine
from ai import AIEngine

load_dotenv()

def main():
    memory = MemorySystem()
    emotion = EmotionEngine()
    ai = AIEngine(
        claude_api_key=os.getenv('CLAUDE_API_KEY'),
        hf_api_key=os.getenv('HF_API_KEY'),
    )

    while True:
        if listen_for_wake_word():
            query = transcribe_speech()
            memory.update_short_term("last_query", query)
            mood = emotion.detect_mood(query)
            response = ai.get_response(query)
            print(f"[{emotion.current_mood.upper()} MODE] {response}")

if __name__ == "__main__":
    main()
