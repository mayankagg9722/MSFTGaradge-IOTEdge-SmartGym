from AzureSpeechRecognition import *
from LUISIntent import *
from TextToSpeech import *
from GoogleSpeechRecognition import *
from GlobalHelpers import *
import sys

def AzureContinuousListening():
    res = None
    while(res==None):
        # or use google listening
        res = AzureListening()
        if(res!=None):
            return res
        BotSpeak(getRandomBotAnswers(botAnswers["saysomething"]))

def AzureListeningAndCheckIntent():
    res = AzureContinuousListening()
    responseIntentJson = GetIntent(res)
    if(responseIntentJson!=None):
        intent  = CheckIntent(responseIntentJson)
        if(intent!=None):
            return intent,responseIntentJson
    BotSpeak(getRandomBotAnswers(botAnswers["funnyRepeat"]))
    return None,None

def AzureContinuousIntentFetching():
    intent,responseIntentJson = None,None
    while(intent==None or responseIntentJson==None):
        intent,responseIntentJson = AzureListeningAndCheckIntent()
    return intent,responseIntentJson

def mapIntent(intent,responseIntentJson,expectedIntent):
    if(intent=="Introduction" and expectedIntent==intent):
        personname = getNameEntity(responseIntentJson)
        intrGreet = botAnswers["exerciseQuestion"]
        intrGreet = intrGreet.format(personname)
        BotSpeak(intrGreet)
    elif(intent=="ExerciseSentiment" and expectedIntent==intent):
        role = CheckExerciseSentimentRole(responseIntentJson)
        if(role):
            BotSpeak(getRandomBotAnswers(botAnswers["positiveSentiment"]))
        else:
            BotSpeak(getRandomBotAnswers(botAnswers["negativeSentiment"]))
    else:
        intent,responseIntentJson = AzureContinuousIntentFetching()
        mapIntent(intent,responseIntentJson,expectedIntent)
