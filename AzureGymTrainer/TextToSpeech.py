import pyttsx3

def BotSpeak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
