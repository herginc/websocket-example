from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return "WebSocket Server is running!"

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    emit('response', {'data': 'Message received: ' + str(data)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
