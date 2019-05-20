from flask import Flask, render_template, redirect, url_for, request,jsonify
from flask_socketio import SocketIO,emit
from GymTrainerBot import *
import TextToSpeech as tts
import demo
import threading
# import mayank
# import threading
# from GlobalHelpers import accuracy_queue

app = Flask(__name__)
socketio = SocketIO(app)
# import demo
# import mayank
# demo = None
def queueMessageEmit():
    while True:
        text = accuracy_queue.get(block=True)
        socketio.emit("pysend", {"data": text})

def convMessageEmit():
    while True:
        conv = conv_queue.get(block=True)
        socketio.emit("convsend", {"data": conv})

def botLogMessageEmit():
    while True:
        botlog = botlog_queue.get(block=True)
        socketio.emit("botlog", {"data": botlog})

@socketio.on('connect')
def handle_connection():
    socketio.start_background_task(target=queueMessageEmit)
    socketio.start_background_task(target=convMessageEmit)
    socketio.start_background_task(target=botLogMessageEmit)
    

# def sendPySend():
#     while True:
#         text = accuracy_queue.get(blo
# @socketio.on('uisend')
# def handle_my_custom_event(json):
#     print('received call from UI: ' + str(json))
#     emit("pysend",{"data":"I am Python calling to UI"})


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
    conv_queue.put("False")
    return jsonify(buttonName = "Your Name?",botanswers=greet)

@app.route("/humanIntro")
def startTrainerHumanIntro():
    greet = humanIntroduction()
    conv_queue.put("False")
    return jsonify(buttonName = "Hey there!",botanswers=greet)

@app.route("/askExercise")
def startTrainerAskExercise():
    greet = askExercise()
    conv_queue.put("False")
    conv_queue.put("doingexercise")
    print("greet")
    if greet!=None and "Great" in greet:
        vid = 'mayank back raise.mp4'
        vid = None
        demo.start_planks(0, vid)
    return "nothing"

@app.route("/trainer")
def startTrainerForced():
    vid = 'mayank back raise.mp4'
    vid = None
    demo.start_planks(0, vid)
    return "nothing"

if __name__ == "__main__":
    # app.run(debug=True) 
    tts.init()
    socketio.run(app)