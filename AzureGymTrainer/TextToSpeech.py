import pyttsx3
import threading

def BotSpeak(text):
    engine = pyttsx3.init()
    # rate = engine.getProperty('rate')
    # engine.setProperty('rate', rate-10)
    engine.say(text)
    engine.runAndWait()

def BotSpeakAsync(text):
    x  = threading.Thread(target=BotSpeak,args=(text,))
    x.start()