# ----------------------------------------------------------------------
# 1. 導入非同步處理套件並進行猴子修補 (Eventlet/Gevent 部署環境必需)
# ----------------------------------------------------------------------
import eventlet
eventlet.monkey_patch() 

# ----------------------------------------------------------------------
# 2. 導入 Flask 和 Flask-SocketIO 相關模組
# ----------------------------------------------------------------------
from flask import Flask, request
from flask_socketio import SocketIO, emit
from threading import Thread, Lock
import time
import json
import os # 用於獲取環境變數

# --- 3. 伺服器設定與初始化 ---
# Render 部署環境中，SECRET_KEY 應設置為環境變數
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-for-dev') 
# 允許所有來源連線，生產環境中應限制特定網域
socketio = SocketIO(app, cors_allowed_origins="*") 

# 用於管理後台定時推送任務
thread = None
thread_lock = Lock()
message_count = 0

# ----------------------------------------------------------------------
# 4. 後台定時推送訊息的執行緒函式 (Server Push 核心)
# ----------------------------------------------------------------------
def background_task():
    """模擬一個在後台定時向所有連線客戶端推送訊息的任務。"""
    global message_count
    print("後台定時推送服務已啟動...")
    while True:
        # 使用 socketio.sleep 確保在非同步環境中正確等待
        socketio.sleep(5)  # 每 5 秒推送一次
        message_count += 1
        
        data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'message': f'Server Push Message #{message_count}',
            'source': 'Background Timer'
        }
        
        print(f"[{data['timestamp']}] 廣播訊息: {data['message']}")
        
        # 使用 emit 廣播到所有連線的客戶端，事件名稱為 'server_response'
        # broadcast=True 是 emit 的預設行為，但明確寫出更清晰
        socketio.emit('server_response', data, broadcast=True)

# ----------------------------------------------------------------------
# 5. WebSocket 事件處理函式
# ----------------------------------------------------------------------

@socketio.on('connect')
def handle_connect():
    """客戶端連線時觸發"""
    global thread
    # 🌟 重點：使用 request.sid 取得客戶端 ID
    client_sid = request.sid 
    print(f'客戶端連線: SID={client_sid}')
    
    # 第一次有客戶端連線時，啟動後台推送執行緒
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_task)
            
    # 立即回覆連線確認訊息
    emit('server_response', {'message': f'Welcome! Your Session ID is {client_sid}'})


@socketio.on('disconnect')
def handle_disconnect():
    """客戶端斷線時觸發"""
    print(f'客戶端斷線: SID={request.sid}')


@socketio.on('client_event')
def handle_client_event(data):
    """處理客戶端發送的 'client_event' 訊息"""
    client_sid = request.sid
    print(f"收到來自客戶端 {client_sid} 的訊息: {data}")
    
    # 回覆給發送者 (emit 預設只發送給當前 request.sid)
    emit('server_response', {'data': f'Server received message from {client_sid}'}, json=True)

# ----------------------------------------------------------------------
# 6. 標準 Flask HTTP 路由 (用於手動觸發推送)
# ----------------------------------------------------------------------

@app.route('/')
def index():
    """標準 Flask 路由，用於 Render 健康檢查或歡迎頁面"""
    return "Flask-SocketIO Server is running. Use WebSocket to connect!"

@app.route('/push_once')
def push_once():
    """一個標準 HTTP 路由，用於手動觸發單次訊息推送"""
    global message_count
    message_count += 1
    
    data = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'message': f'Manual HTTP Trigger Push #{message_count}',
        'source': 'HTTP Trigger'
    }
    
    # 向所有客戶端發送訊息
    socketio.emit('server_response', data, broadcast=True)
    print(f"手動推送訊息: {data['message']}")
    
    return f"Manual message '{data['message']}' pushed to all clients!"

# ----------------------------------------------------------------------
# 7. 啟動伺服器 (僅用於本地開發環境測試)
# ----------------------------------------------------------------------

if __name__ == '__main__':
    # 在本地開發環境中，使用 socketio.run 來啟動，會自動使用 eventlet 或 gevent
    # host='0.0.0.0' 允許從外部網路存取 (Render 部署環境必需)
    # 在生產環境中，此區塊將被 Gunicorn 啟動指令取代。
    print("--- 本地開發模式啟動中 ---")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

# ----------------------------------------------------------------------
