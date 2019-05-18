from TextToSpeech import *
from GlobalHelpers import *
from AzureHelpers import *

def startBot():
    # Greet Stage
    BotSpeak(getRandomBotAnswers(botAnswers["greeting"]))
    # Name Stage
    intent,responseIntentJson = AzureContinuousIntentFetching()
    mapIntent(intent,responseIntentJson)
    # Exercise Stage
    intent,responseIntentJson = AzureContinuousIntentFetching()
    mapIntent(intent,responseIntentJson)


startBot()
