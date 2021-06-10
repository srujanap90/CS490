from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask import Blueprint
from flask import g
from flaskr.db import get_db


bp = Blueprint("chat", __name__)
socketio = SocketIO()

# @bp.route('/chat')
# def chat():
#     sender = g.user['username']
#     getter = request.args.get('getter')
#     db = get_db()
    
#     users = db.execute(
#         "SELECT id, username"
#         " FROM user"
#         " WHERE username =?",
#         (getter,)    
#     ).fetchall()
#     msg=""
#     if len(users)==0:
#         msg="no such user, please try again"
#         return render_template('chat/index.html',msg=msg)
#     elif sender and getter:
#         return render_template('chat/chat.html', sender=sender, getter=getter)
#     else:
#         return redirect(url_for('chat.home'))

# @socketio.on('join')
# def join(data):
#     print(data)
#     join_room(data['room'])
#     socketio.emit('join_message', data, room=data['room'])

# @socketio.on('send_message')
# def send_message(data):
#     socketio.emit('receive_message', data, room=data['room'])


# if __name__ == '__main__':
#     socketio.run(app, debug=True)


@bp.route('/home')
def home():
    return render_template('chat/index.html')
@bp.route('/orginate')
def orginate():
    socketio.emit('server orginated', 'Something happened on the server!')
    return '<h1>Sent!</h1>'

@socketio.on('message from user', namespace='/messages')
def receive_message_from_user(message):
    print('USER MESSAGE: {}'.format(message))
    emit('from flask', message.upper(), broadcast=True)

@socketio.on('username', namespace='/private')
def receive_username(username):
    users[username] = request.sid
    #users.append({username : request.sid})
    #print(users)
    print('Username added!')

@socketio.on('private_message', namespace='/private')
def private_message(payload):
    recipient_session_id = users[payload['username']]
    message = payload['message']

    emit('new_private_message', message, room=recipient_session_id)
