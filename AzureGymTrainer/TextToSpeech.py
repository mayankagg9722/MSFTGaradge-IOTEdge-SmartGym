import pyttsx3
import threading
from GlobalHelpers import *

def engine_thread():
    engine = pyttsx3.init()
    while True:
        text = global_queue.get(block=True)
        if text == "end":
            break
        engine.say(text)
        engine.runAndWait()

t = threading.Thread(target=engine_thread)
t.start()

def BotSpeak(text):
    global_queue.put(text)
