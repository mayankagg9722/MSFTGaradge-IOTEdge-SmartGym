import pyttsx3
import requests
import azure.cognitiveservices.speech as speechsdk
import speech_recognition as sr
import random
import sys

speech_key, service_region = "4c80a4fb678f438eb068f0e22fbf076e", "southcentralus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

personname=""


botAnswers = {
    "greeting":["Hi, I am your digital smart trainer. What is your name?"],
    "exerciseQuestion":"Hey {} , would you like to do plank.",
    "positiveSentiment":["Great, get in the position for plank and we will start in."],
    "negativeSentiment":["Sorry to know that. Well, Have a nice day."],
    "saysomething":["Sorry, I didn't get you. Please repeat."],
    "quit":["Sorry, something bad occured. I am quitting."]
}



def AzureListening():
    print("azure listening...")
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    return ""

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

def GetIntent(query):
    headers = {
        'Ocp-Apim-Subscription-Key': 'b9523925e0784f64bf36fa3cc1f5801e',
    }
    params ={
        'q': query,
        'timezoneOffset': '0',
        'verbose': 'false',
        'spellCheck': 'false',
        'staging': 'false',
    }
    try:
        r = requests.get('https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/b6562490-dde2-4693-ac26-66128a5ca9df',headers=headers, params=params)
        print(r.json())
        return r.json()
    except:
        return "exception" 

def CheckIntent(res):
    return res["topScoringIntent"]["intent"]

def BotSpeak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def getRandomBotAnswers(arr):
    rand_idx = random.randrange(len(arr))
    return arr[rand_idx]

def getNameEntity(resJson):
    global personname
    entArr = resJson["entities"]
    for ent in entArr:
        if(ent["type"]=="builtin.personName"):
            print ("working"+ent["entity"])
            personname =  ent["entity"]
            return

def CheckExerciseSentimentRole(resJson):
    entArr = resJson["entities"]
    for ent in entArr:
        if(ent["role"] and ent["role"]=="positive"):
            return True
    return False

def AzureListeningAndCheckIntent():
    res = ""
    while(res==""):
        res = AzureListening()
        if(res==""):
            BotSpeak(getRandomBotAnswers(botAnswers["saysomething"]))
    responseIntentJson = GetIntent(res)
    if(responseIntentJson=="exception"):
        BotSpeak(getRandomBotAnswers(botAnswers["quit"]))
        return False
    intent  = CheckIntent(responseIntentJson)
    return intent,responseIntentJson

def startBot():
    BotSpeak(getRandomBotAnswers(botAnswers["greeting"]))
    
    intent,responseIntentJson = AzureListeningAndCheckIntent()

    if(intent=="Introduction"):
        getNameEntity(responseIntentJson)
        intrGreet = botAnswers["exerciseQuestion"]
        intrGreet = intrGreet.format(personname)
        print(intrGreet)
        BotSpeak(intrGreet)
    else:
        BotSpeak(getRandomBotAnswers(botAnswers["quit"]))
        return False
    
    intent,responseIntentJson = AzureListeningAndCheckIntent()

    if(intent=="ExerciseSentiment"):
        role = CheckExerciseSentimentRole(responseIntentJson)
        if(role):
            BotSpeak(getRandomBotAnswers(botAnswers["positiveSentiment"]))
        else:
            BotSpeak(getRandomBotAnswers(botAnswers["negativeSentiment"]))


flagScript = startBot()
if flagScript:
    sys.exit("done and dusted")
else:
    startBot()