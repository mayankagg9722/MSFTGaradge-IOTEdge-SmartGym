from flask import Flask, render_template, redirect, url_for
from GymTrainerBot import *
import threading
app = Flask(__name__)
@app.route("/")
def home():
    return render_template("template.html",buttonName = "START TRAINING")
@app.route("/forward", methods=['POST'])
def startTrainerBot():
    x = threading.Thread(target=startBot)  
    x.start()
    return render_template("template.html",buttonName = "Get Ready...")
if __name__ == "__main__":
    app.run(debug=True) 