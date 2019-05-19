from flask import Flask, render_template, redirect, url_for, request,jsonify
from GymTrainerBot import *
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("template.html")

@app.route("/bot")
def startTrainerBot():
    startBot()
    return "nothing just run bot"

@app.route("/botintro")
def startTrainerBotIntro():
    greet = startBotGreeting()
    return jsonify(buttonName = "Your Name?",botanswers=greet)

@app.route("/humanIntro")
def startTrainerHumanIntro():
    greet = humanIntroduction()
    return jsonify(buttonName = "Hey there!",botanswers=greet)

@app.route("/askExercise")
def startTrainerAskExercise():
    greet = askExercise()
    return jsonify(buttonName = "Lets do it!",botanswers=greet)

if __name__ == "__main__":
    app.run(debug=True) 