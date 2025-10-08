from flask import Flask, request
from flask_socketio import SocketIO, emit
from threading import Thread, Lock
import time
import json

# --- 伺服器設定 ---
app = Flask(__name__)
# 必須設定 SECRET_KEY
app.config['SECRET_KEY'] = 'a_very_secret_key'
# cors_allowed_origins="*" 允許所有來源連線，開發時使用
socketio = SocketIO(app, cors_allowed_origins="*")

# 用於儲存後台執行緒的引用和鎖定
thread = None
thread_lock = Lock()
message_count = 0

# --- 後台定時推送訊息的執行緒函式 ---
def background_task():
    """模擬一個在後台定時向客戶端推送訊息的任務。"""
    global message_count
    print("後台推送服務啟動...")
    while True:
        # 使用 socketio.sleep 確保在非同步環境中正確等待
        socketio.sleep(60)  # 每 5 秒推送一次
        message_count += 1

        data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'message': f'Server Push Message #{message_count}',
            'source': 'Background Timer'
        }

        print(f"[{data['timestamp']}] 廣播訊息: {data['message']}")

        # 使用 emit 廣播到所有連線的客戶端，事件名稱為 'server_response'
        socketio.emit('server_response', data)

# --- WebSocket 事件處理函式 ---

@socketio.on('connect')
def handle_connect():
    """客戶端連線時觸發"""
    global thread
    print(f'客戶端連線: SID={request.sid}')

    # 第一次有客戶端連線時，啟動後台推送執行緒
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_task)

@socketio.on('disconnect')
def handle_disconnect():
    """客戶端斷線時觸發"""
    print(f'客戶端斷線: SID={request.sid}')

@socketio.on('client_event')
def handle_client_event(data):
    """處理客戶端發送的 'client_event' 訊息"""
    print(f"收到來自客戶端的訊息: {data}")
    # 可以選擇回覆給發送者
    emit('server_response', {'data': 'Server received your message!'}, json=True)

# --- 標準 Flask HTTP 路由 (用於手動觸發推送) ---

@app.route('/push_once')
def push_once():
    """一個標準 HTTP 路由，用於手動觸發單次訊息推送"""
    global message_count
    message_count += 1

    data = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'message': f'Manual Push Message #{message_count}',
        'source': 'HTTP Trigger'
    }

    # 向所有客戶端發送訊息
    socketio.emit('server_response', data)
    print(f"手動推送訊息: {data['message']}")

    return f"Manual message '{data['message']}' pushed to all clients!"

# --- 啟動伺服器 ---

if __name__ == '__main__':
    # 使用 socketio.run 來啟動伺服器，而不是 app.run
    # host='0.0.0.0' 允許從外部網路存取 (如果部署在 Render 上，必須使用 '0.0.0.0')
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
