#!/usr/bin/env python3
"""
TIFShrink 本地桌面应用
打包后双击此文件即可运行，自动启动服务并打开处理界面
"""

import sys
import os

# ==================== 关键：设置模块搜索路径 ====================
# PyInstaller 打包后，文件解压到 sys._MEIPASS 指向的临时目录
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    # 必须把 BASE_DIR 加入 Python 模块搜索路径，否则 import server 会失败
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

# 服务端口
PORT = 18765
SERVER_URL = f'http://127.0.0.1:{PORT}'

# 临时文件目录
UPLOAD_DIR = os.path.join(os.path.expanduser('~'), 'TIFShrink_Uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==================== 预加载 Flask ====================
try:
    from server import app as flask_app
    print('[TIFShrink] ✅ Flask 服务模块加载成功')
except Exception as e:
    print(f'[TIFShrink] ❌ Flask 加载失败: {e}')
    input('按回车退出...')
    sys.exit(1)

# ==================== 启动 WSGI 服务器 ====================
try:
    from wsgiref.simple_server import WSGIServer, make_server
    from socketserver import ThreadingMixIn

    # 使用 ThreadingTCPServer，避免阻塞
    class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
        daemon_threads = True

    httpd = make_server('127.0.0.1', PORT, flask_app, ThreadingWSGIServer)
    print(f'[TIFShrink] 🌐 服务运行中 → {SERVER_URL}')

except OSError as e:
    if 'Address already in use' in str(e):
        print(f'[TIFShrink] ⚠️ 端口 {PORT} 已被占用，尝试其他端口...')
        PORT = 0  # 让系统自动分配端口
        httpd = make_server('127.0.0.1', PORT, flask_app, ThreadingWSGIServer)
        PORT = httpd.server_address[1]
        SERVER_URL = f'http://127.0.0.1:{PORT}'
        print(f'[TIFShrink] 🌐 服务运行中 → {SERVER_URL}')
    else:
        raise

# ==================== 自动打开浏览器 ====================
import webbrowser, time
def open_browser():
    time.sleep(1.5)
    webbrowser.open(SERVER_URL)

import threading
threading.Thread(target=open_browser, daemon=True).start()

# ==================== 主界面 ====================
print('=' * 50)
print('  TIFShrink Pro  本地版')
print('=' * 50)
print()
print(f'  ✅ 已打开浏览器: {SERVER_URL}')
print(f'  📁 临时文件目录: {UPLOAD_DIR}')
print()
print('  关闭此窗口即可退出程序')
print('=' * 50)

# 保持运行
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print('\n[TIFShrink] 正在关闭...')
    sys.exit(0)