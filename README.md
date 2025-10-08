安裝套件：
pip install flask flask-socketio gunicorn eventlet

requirements.txt:

Flask
Flask-SocketIO
gunicorn
eventlet

Render 啟動指令：

Running 'gunicorn --worker-class eventlet -w 1 server:app'

（假設你的檔案名為 server.py，且 Flask 應用實例命名為 app。）
