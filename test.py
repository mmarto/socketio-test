#!/usr/bin/env python3

async_mode = 'threading'

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

if async_mode is None:
    async_mode = 'threading'

print('async_mode is ' + async_mode)

if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()

from threading import Thread
from flask import Flask, render_template, session, request
#from flask import make_response
from flask_socketio import SocketIO, emit, disconnect
import pandas as pd
import numpy as np
import time
#import random
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure
#from matplotlib.dates import DateFormatter
#import datetime
#from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

contectedClients = set()

def background_thread():
    '''Send server generated events to clients.'''
    global contectedClients
    count = 0
    while True:
        time.sleep(5)
        print('contectedClients: {}'.format(len(contectedClients)))
        if len(contectedClients) > 0:
            count +1
            df = pd.DataFrame(np.random.randint(0,100,size=(5,4)), columns=list('ABCD'))
            print(df.to_json(orient='split'))
            p = df.plot()
            fig = p.get_figure()
            fig.savefig('static/simple.png')
#            socketio.emit('my response', {'data': df.to_html(classes='table'), 'count': count}, namespace='/test')
            socketio.emit('my response 3', {'data': df.to_json(orient='split')}, namespace='/test')

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('index.html')

#@app.route("/simple.png")
#def simple():
#    fig = Figure()
#    fig.set_facecolor('white')
#    fig.set_figwidth(14)
#    ax = fig.add_subplot(111)
#    x = []
#    y = []
#    now = datetime.datetime.now()
#    delta = datetime.timedelta(days=1)
#    for i in range(10):
#        x.append(now)
#        now += delta
#        y.append(random.randint(0,100))
#    ax.plot_date(x, y, '-')
#    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
#    fig.autofmt_xdate()
#    canvas = FigureCanvas(fig)
#    png_output = BytesIO()
#    canvas.print_png(png_output)
#    response = make_response(png_output.getvalue())
#    response.headers['Content-Type'] = 'image/png'
#    return response



@socketio.on('my event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response 2', {'data': message['data'], 'count': session['receive_count']})

@socketio.on('my broadcast event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response 2', {'data': message['data'], 'count': session['receive_count']}, broadcast=True)

@socketio.on('disconnect request', namespace='/test')
def disconnect_request():
    global contectedClients
    session['receive_count'] = session.get('receive_count', 0) + 1
    contectedClients.discard(request.sid)
    emit('my response 2', {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global contectedClients
    contectedClients.add(request.sid)
    print(request.sid)
    emit('my response 2', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    global contectedClients 
    contectedClients.discard(request.sid)
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    #socketio.run(app, host='dev302', debug=True)
    socketio.run(app, debug=True)
