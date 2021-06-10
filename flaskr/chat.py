from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
from flask import Blueprint

# app = Flask(__name__)
# app.secret_key = "cs490"
socketio = SocketIO()
bp=Blueprint("chat",__name__)

@bp.route('/home')
def home():
    return render_template('chat/index.html')

@bp.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat/chat.html', username=username, room=room)
    else:
        return redirect(url_for('chat.home'))

@socketio.on('join')
def join(data):
    join_room(data['room'])
    socketio.emit('join_message', data, room=data['room'])

@socketio.on('send_message')
def send_message(data):
    socketio.emit('receive_message', data, room=data['room'])


# if __name__ == '__main__':
#     socketio.run(app, debug=True)