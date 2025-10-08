import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

connected_clients = set()

@app.route('/')
def index():
    return "WebSocket Server is running!"

@socketio.on('connect')
def handle_connect(sid, environ):
    print('Client connected:', sid)
    connected_clients.add(sid)

@socketio.on('disconnect')
def handle_disconnect(sid):
    print('Client disconnected:', sid)
    connected_clients.discard(sid)

def send_periodic_message():
    while True:
        for sid in list(connected_clients):
            socketio.emit('server_message', {'data': '定時訊息：' + time.strftime('%Y-%m-%d %H:%M:%S')}, to=sid)
        socketio.sleep(60)

socketio.start_background_task(send_periodic_message)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
