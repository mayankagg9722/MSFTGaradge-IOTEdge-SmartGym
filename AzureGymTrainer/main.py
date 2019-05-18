from flask import Flask, render_template, redirect, url_for, request
from GymTrainerBot import *
app = Flask(__name__)

conversation = []

@app.route("/")
def home():
    return render_template("button.html",buttonName = "Start Training",botanswers=conversation)

@app.route("/bot")
def startTrainerBot():
    startBot()
    return "nothing just run bot"

# @app.route("/botintro", methods=['POST'])
# def startTrainerBotIntro():
#     greet = startBotGreeting()
#     conversation.append(greet)
#     startTrainerHumanIntro()
#     startTrainerAskExercise()
#     return render_template("button.html",buttonName = "Your Name?",botanswers=conversation)

# @app.route("/humanIntro")
# def startTrainerHumanIntro():
#     greet = humanIntroduction()
#     conversation.append(greet)
#     return render_template("button.html",buttonName = "Hey there!",botanswers=conversation)

# @app.route("/askExercise", methods=['POST'])
# def startTrainerAskExercise():
#     greet = askExercise()
#     conversation.append(greet)
#     return render_template("button.html",buttonName = "Lets do it!",botanswers=conversation)

if __name__ == "__main__":
    app.run(debug=True) 