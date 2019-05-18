from TextToSpeech import *
from GlobalHelpers import *
from AzureHelpers import *

def startBotGreeting():
    greet = getRandomBotAnswers(botAnswers["greeting"])
    BotSpeak(greet)
    return greet

def humanIntroduction():
    intent,responseIntentJson = AzureContinuousIntentFetching()
    intrGreet = mapIntent(intent,responseIntentJson,"Introduction")
    BotSpeak(intrGreet)
    return intrGreet

def askExercise():
    intent,responseIntentJson = AzureContinuousIntentFetching()
    execGreet = mapIntent(intent,responseIntentJson,"ExerciseSentiment")
    BotSpeak(execGreet)
    return execGreet

def startBot():
    # Greet Stage
    BotSpeak(getRandomBotAnswers(botAnswers["greeting"]))
    # Name Stage
    intent,responseIntentJson = AzureContinuousIntentFetching()
    mapIntent(intent,responseIntentJson,"Introduction")
    # Exercise Stage
    intent,responseIntentJson = AzureContinuousIntentFetching()
    mapIntent(intent,responseIntentJson,"ExerciseSentiment")
    
# startBot()
