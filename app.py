import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return "Hello, WebSocket!"

@socketio.on('message')
def handle_message(data):
    print('Received:', data)
    socketio.emit('response', {'data': 'Received: ' + str(data)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
