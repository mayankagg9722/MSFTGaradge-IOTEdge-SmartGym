from AzureSpeechRecognition import *
from LUISIntent import *
from TextToSpeech import *
from GoogleSpeechRecognition import *
from GlobalHelpers import *

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
        if(personname==None):
            personname=""
        intrGreet = botAnswers["exerciseQuestion"]
        intrGreet = intrGreet.format(personname)
        return intrGreet
    elif(intent=="ExerciseSentiment" and expectedIntent==intent):
        role = CheckExerciseSentimentRole(responseIntentJson)
        if(role):
            return getRandomBotAnswers(botAnswers["positiveSentiment"])
        else:
            return getRandomBotAnswers(botAnswers["negativeSentiment"])
    else:
        intent,responseIntentJson = AzureContinuousIntentFetching()
        mapIntent(intent,responseIntentJson,expectedIntent)
