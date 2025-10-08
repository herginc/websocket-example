import socketio  # pip install python-socketio
import time

# --- 客戶端設定與事件處理 ---

sio = socketio.Client()

@sio.event
def connect():
    """連線成功時觸發"""
    print("--- 成功連線到伺服器 ---")
    # 連線後，可以主動發送訊息給伺服器 (事件名稱: 'client_event')
    sio.emit('client_event', {'data': 'Hello from Python Client!'})

@sio.event
def disconnect():
    """斷線時觸發"""
    print("--- 伺服器連線已中斷 ---")

@sio.on('server_response')
def on_server_response(data):
    """接收伺服器主動推送的 'server_response' 訊息"""
    # 伺服器推送的訊息會在這裡被接收
    print(f"\n[SERVER PUSH] 接收到新訊息:")
    print(f"  時間: {data.get('timestamp')}")
    print(f"  來源: {data.get('source')}")
    print(f"  內容: {data.get('message')}")
    print("-" * 30)
    
# --- 連線與執行 ---

if __name__ == '__main__':
    try:
        server_url = 'https://miniature-yodel-x4g6jrg47rvc99vr-5000.app.github.dev/'

        # 連線到伺服器 (預設使用 WebSocket)
        # sio.connect('http://localhost:5000')
        sio.connect(server_url)
        
        # 讓客戶端保持執行，以持續接收伺服器的推送
        # sio.wait() 會阻塞直到斷線，但無法捕捉 KeyboardInterrupt (Ctrl+C)
        # 這裡使用一個迴圈來保持程式執行，並允許 Ctrl+C 中斷
        while True:
            time.sleep(1) 
            
    except socketio.exceptions.ConnectionError as e:
        print(f"連線錯誤: 請確認 server.py 伺服器是否已啟動並運行在 {server_url}。錯誤: {e}")
    except KeyboardInterrupt:
        print("\n客戶端中斷連線...")
        sio.disconnect()
    except Exception as e:
        print(f"發生未知錯誤: {e}")
        sio.disconnect()
