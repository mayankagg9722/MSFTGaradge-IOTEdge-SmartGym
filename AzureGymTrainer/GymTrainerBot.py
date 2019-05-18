from TextToSpeech import *
from GlobalHelpers import *
from AzureHelpers import *

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
