from flask import Flask, render_template, redirect, url_for, request,jsonify
from flask_socketio import SocketIO,emit
from GymTrainerBot import *
# import demo
import threading

app = Flask(__name__)
# socketio = SocketIO(app)
# def queueMessageEmit():
    # while True:
        # text = accuracy_queue.get(block=True)
        # conv = conv_queue.get(block=True)
        # socketio.emit("pysend", {"data": text})
        # socketio.emit("convsend", {"data": conv})

# @socketio.on('connect')
# def handle_connection():
#     socketio.start_background_task(target=queueMessageEmit,daemon=True)

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
    # if "Great" in greet:
        # demo.start_planks(0)
    return jsonify(buttonName = "Lets do it!",botanswers=greet)

@app.route("/trainer")
def startTrainerForced():
    # demo.start_planks(1)
    return "nothing"

if __name__ == "_main_":
    app.run(debug=True) 
    # socketio.run(app)