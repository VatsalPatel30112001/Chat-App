import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from lib import *
from models import *
from socket_events import socketio
from middleware import token_required

api = Blueprint('api', __name__)

@api.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password or not email:
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "Username or email already exists"}), 400

    new_user = User(
        username=username,
        password_hash=generate_password_hash(password), 
        email=email
    )

    db.session.add(new_user)
    db.session.commit()

    for user in User.query.all():
        if user.id!=new_user.id:
            socketio.emit('send_message', {
                "new_user" : {
                    'user_id': new_user.id,
                    'user_name': username
                }
            }, room=str(user.id))

    return jsonify({"message": "User created successfully"}), 201

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing required fields"}), 400

    user = User.query.filter_by(username=username).first()
    socketio.emit('send_message', {'data': data}, room=str(user.id))

    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token, id= user.id), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@api.route('/validate-token', methods=['POST'])
@token_required
def validate_token():
    return jsonify({'status':'success'}), 200

@api.route('/create-group', methods=['POST'])
@token_required
def create_group():
    data = request.json
    group_name = data.get('group_name')
    member_ids = data.get('member_ids') 

    if not group_name or not member_ids:
        return jsonify({"error": "Group name and member IDs are required"}), 400

    new_group = Group(group_name=group_name)

    members = User.query.filter(User.id.in_(member_ids)).all()
    new_group.members.extend(members) 

    db.session.add(new_group)
    db.session.commit()
    
    for user in User.query.all():
        if user not in new_group.members:
            socketio.emit('send_message', {
                'new_group':{
                    'group_id': new_group.id,
                    'group_name': new_group.group_name,
                    'is_member': False
                },
                'created_by': User.query.get(member_ids[0]).username
            }, room=str(user.id))

    return jsonify({"message": "Group created successfully", 
                    "new_group":{
                        "group_id": new_group.id, 
                        "group_name":new_group.group_name, 
                        "is_member":True
                        }
                    }), 201

@api.route('/join-group', methods=['POST'])
@token_required
def join_group():
    data = request.json
    group_id = data.get('group_id')
    user_id = data.get('user_id')

    if not group_id or not user_id:
        return jsonify({"error": "Group ID and User ID are required"}), 400

    group = Group.query.get(group_id)
    user = User.query.get(user_id)

    if not group:
        return jsonify({"error": "Group not found"}), 404
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user in group.members:
        return jsonify({"error": "User is already a member of the group"}), 400

    group.members.append(user)
    db.session.commit()

    return jsonify({"message": "User added to group successfully", "group_id": group.id}), 200

@api.route('/send-message', methods=['POST'])
@token_required
@jwt_required()
def send_message():
    sender_id = get_jwt_identity()
    if 'file' in request.files:
        file = request.files['file']
        file_path = save_file(file, sender_id) 
        content = os.path.basename(file_path) 
        is_file = True
    else:
        content = request.form.get('content')
        is_file = request.form.get('is_file', False)
        file_path = None 

    recipient_id = request.form.get('recipient_id') 
    recipient_id = None if recipient_id=="null" else recipient_id

    group_id = request.form.get('group_id')
    group_id = None if group_id=="null" else group_id

    msg = Message(
        content=content,
        is_file=is_file,
        sender_id=sender_id,
        recipient_id=recipient_id,
        group_id=group_id,
        file_path=file_path
    )

    db.session.add(msg)
    db.session.commit()

    if (not recipient_id or str(recipient_id)!=str(sender_id)):
        send_message_to_recipent(msg, recipient_id, group_id)

    return jsonify(
        {
            "message": "Message sent successfully", 
            "id": msg.id,
            "new_message":{
                "id": msg.id,
                "content": msg.content,
                "file_path": msg.file_path,
                "is_file": msg.is_file,
                "timestamp": msg.timestamp,
                "sender_id": msg.sender_id,
                "sender_name": msg.sender.username,
                "recipient_id": msg.recipient_id,
                "group_id": msg.group_id
            }
        }), 201

@api.route('/message-history', methods=['GET'])
@token_required
@jwt_required()
def get_message_history():
    sender_id = get_jwt_identity()
    group_id = request.args.get('group_id', type=int)
    recipient_id = request.args.get('recipient_id', type=int)

    if group_id is not None:
        messages = Message.query.filter_by(group_id=group_id).order_by(Message.timestamp.asc()).all()
    elif sender_id is not None and recipient_id is not None:
        messages = Message.query.filter(
            ((Message.sender_id == sender_id) & (Message.recipient_id == recipient_id)) |
            ((Message.sender_id == recipient_id) & (Message.recipient_id == sender_id))
        ).order_by(Message.timestamp.asc()).all()
    else:
        return jsonify({"error": "Missing parameters"}), 400

    message_list = [
        {
            "id": msg.id,
            "content": msg.content,
            "file_path": msg.file_path,
            "is_file": msg.is_file,
            "timestamp": msg.timestamp,
            "sender_id": msg.sender_id,
            "sender_name": msg.sender.username,
            "recipient_id": msg.recipient_id,
            "group_id": msg.group_id
        }
        for msg in messages
    ]

    return jsonify(message_list), 200

@api.route('/all-users-and-groups', methods=['GET'])
@token_required
@jwt_required()
def get_users_and_groups():
    sender_id = get_jwt_identity()
    groups = Group.query.all()
    resp_groups = []
    for group in groups:
        resp_groups.append({
            'group_id': group.id,
            'group_name': group.group_name,
            'is_member': any(member.id == sender_id for member in group.members)
        })

    users = User.query.all()
    resp_users = []
    for user in users:
        if user.id==sender_id:
            resp_users.insert(0, {
                'user_id':user.id,
                'user_name':f'You({user.username})'
            })
        else:
            resp_users.append({
                'user_id':user.id,
                'user_name':user.username
            })

    resp = {
        'groups':resp_groups,
        'users':resp_users
    }

    return jsonify(resp), 200

@api.route('/download-file', methods=['POST'])
@token_required
def download_file():
    file_path = request.json.get('file_path')

    if not file_path: 
        return jsonify({"error": "file_path is required"}), 400
        
    return send_file(file_path, as_attachment=True), 200
