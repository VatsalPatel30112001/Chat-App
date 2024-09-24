from flask import request
from flask_socketio import SocketIO, join_room, leave_room

from models import *
from middleware import token_required

socketio = SocketIO()

def info_message(sender, message, id):
    users = [user.id for user in User.query.all() if str(user.id)!=str(id)]
    for user in users:
        socketio.emit('send_message', {
            "info":message,
            "sender_name": sender.username
        }, room=str(user))

def register_socket_events(socketio: SocketIO):
    @socketio.on('connect')
    def handle_connect():
        id = request.args.get('id')
        if id:
            sender = User.query.get(int(id))
            join_room(str(id))
            info_message(sender, f'{sender.username} has joined.', id)

    @socketio.on('disconnect')
    def handle_disconnect():
        id = request.args.get('id')
        if id:
            sender = User.query.get(int(id))
            leave_room(str(id))
            info_message(sender, f'{sender.username} has left.', id)
