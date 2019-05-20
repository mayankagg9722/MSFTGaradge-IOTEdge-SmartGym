from main import socketio, emit
# from flask_socketio import SocketIO,emit

def emitfunction(data):
    emit("pysend",{"data":data})