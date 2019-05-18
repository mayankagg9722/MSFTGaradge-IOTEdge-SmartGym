
import speech_recognition as sr

def GoogleListening():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("start")
        audio = r.listen(source)
        print("end")
    try:
        print("text:"+r.recognize_google(audio))
        return r.recognize_google(audio)
    except:
        print("exception")
