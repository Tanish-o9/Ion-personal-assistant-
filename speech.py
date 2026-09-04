import speech_recognition as sr

def listen_for_wake_word(wake_word="hey ion"):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Listening for wake word 'Hey Ion'...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio).lower()
        return wake_word.lower() in text or "ion" in text
    except sr.UnknownValueError:
        return False

def transcribe_speech():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
