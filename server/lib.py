import os
from werkzeug.utils import secure_filename

from models import *
from socket_events import socketio

def save_file(file, sender_id):
    filename = secure_filename(file.filename)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FILES_DIR = os.path.join(BASE_DIR, 'static', 'files')

    if not os.path.exists(FILES_DIR):
        os.makedirs(FILES_DIR)

    sender_folder = os.path.join(FILES_DIR, str(sender_id))

    if not os.path.exists(sender_folder):
        os.makedirs(sender_folder)

    file_path = os.path.join(sender_folder, filename)

    file.save(file_path)
    return file_path

def send_message_to_recipent(msg, recipient_id, group_id):
    if group_id:
        members = [member for member in Group.query.get(group_id).members if member.id!=msg.sender_id]
        members = [str(member.id) for member in members]
    else:
        members = [str(recipient_id)]
    for member in members:
        socketio.emit('send_message', {
            "id": msg.id,
            "content": msg.content,
            "file_path": msg.file_path,
            "is_file": msg.is_file,
            "timestamp": str(msg.timestamp),
            "sender_id": msg.sender_id,
            "sender_name": msg.sender.username,
            "recipient_id": msg.recipient_id,
            "group_id": msg.group_id
        }, room=member)