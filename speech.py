try:
    import speech_recognition as sr
except ImportError:
    sr = None

def listen_for_wake_word(wake_word="hey ion"):
    if sr is None:
        print("speech_recognition library not available. Skipping mic listener.")
        return False
    try:
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            print("Listening for wake word 'Hey Ion'...")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
        text = recognizer.recognize_google(audio).lower()
        return wake_word.lower() in text or "ion" in text
    except Exception:
        return False

def transcribe_speech():
    if sr is None:
        return ""
    try:
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            print("Listening...")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
        return recognizer.recognize_google(audio)
    except Exception:
        return ""
