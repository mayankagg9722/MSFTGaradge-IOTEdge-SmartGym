import random
import queue
global_queue = queue.Queue()
botlistening = False
accuracy_queue = queue.Queue()
conv_queue = queue.Queue()
botlog_queue = queue.Queue()

botAnswers = {
    "greeting":["Hi, I am your digital smart trainer. What is your name?"],
    "exerciseQuestion":"Hey {} , would you like to do a plank ?",
    "positiveSentiment":["Great, get in the position for plank and we will start in."],
    "negativeSentiment":["Sorry to know that. Well, Have a nice day."],
    "saysomething":["Sorry, I didn't get you. Please repeat."],
    "quit":["Sorry, something bad occured. I am quitting."],
    "funnyRepeat":["Talk less and work hard in the gym. Please repeat again."]
}


def getRandomBotAnswers(arr):
    rand_idx = random.randrange(len(arr))
    return arr[rand_idx]