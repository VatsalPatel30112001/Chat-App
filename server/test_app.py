import os
import pytest
from io import BytesIO
from flask_jwt_extended import create_access_token

from models import *
from database import db
from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config.from_object('config.Config')
    with flask_app.app_context():
        db.create_all() 
        yield flask_app
        db.session.remove()  
        db.drop_all()  

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_header(app):
    with app.app_context(): 
        user = User(username="testuser", email="test@example.com", password_hash="testpassword")
        db.session.add(user)
        db.session.commit() 
        access_token = create_access_token(identity=user.id) 
        return {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

def test_signup(client):
    response = client.post('/api/signup', json={
        'username': 'testuser1',
        'email': 'testuser1@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User created successfully'
    
    user = User.query.filter_by(username='testuser1').first()
    assert user is not None
    assert user.email == 'testuser1@example.com'

    response = client.post('/api/signup', json={
        'username': 'testuser2',
        'email': 'testuser2@example.com'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Missing required fields'

def test_login(client):
    client.post('/api/signup', json={
        'username': 'testuser1',
        'email': 'testuser1@example.com',
        'password': 'password123'
    })

    response = client.post('/api/login', json={
        'username': 'testuser1',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert response.json['id'] == User.query.filter_by(username='testuser1').first().id

    response = client.post('/api/login', json={
        'username': 'testuser1'
    })
    assert response.status_code == 400
    assert response.json['message'] == 'Missing required fields'

    response = client.post('/api/login', json={
        'username': 'testuser1',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid credentials'

def test_create_group(client, auth_header):
    with client.application.app_context():
        test_user = User.query.filter_by(username='testuser').first()

        response = client.post('/api/create-group', json={
            'group_name': 'Test Group',
            'member_ids': [test_user.id]
        }, headers=auth_header)
        assert response.status_code == 201
        assert response.json['message'] == 'Group created successfully'
        assert response.json['new_group']['group_name'] == 'Test Group'
        assert response.json['new_group']['group_id'] is not None

        response = client.post('/api/create-group', json={
            'member_ids': [test_user.id]
        }, headers=auth_header)
        assert response.status_code == 400
        assert response.json['error'] == 'Group name and member IDs are required'

        response = client.post('/api/create-group', json={
            'group_name': 'Another Group'
        }, headers=auth_header)
        assert response.status_code == 400
        assert response.json['error'] == 'Group name and member IDs are required'

def test_get_message_history(client, auth_header):
    with client.application.app_context():
        sender_user = User.query.filter_by(username="testuser").first()
        recipient_user = User(username="recipient_user", email="recipient@example.com", password_hash="testpassword")
        
        db.session.add(recipient_user)
        db.session.commit()
        
        client.post('/api/send-message', json={
            'recipient_id': recipient_user.id,
            'message': 'Hello, this is a test message!'
        }, headers=auth_header)

        client.post('/api/send-message', json={
            'recipient_id': sender_user.id,
            'message': 'Hi, this is a reply to the test message.'
        }, headers={'Authorization': f'Bearer {create_access_token(identity=recipient_user.id)}'}) 
        
        response = client.get(f'/api/message-history?recipient_id={recipient_user.id}', headers=auth_header)

        assert response.status_code == 200
        assert isinstance(response.json, list)

def test_send_message(client, auth_header):
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()

        response = client.post('/api/send-message', json={
            'recipient_id': user.id,
            'message': 'Hello, this is a test message!'
        }, headers=auth_header)

        assert response.status_code == 201
        assert response.json['message'] == 'Message sent successfully'

def test_join_group(client, auth_header):
    test_group = Group(group_name="Test Group")
    db.session.add(test_group)
    db.session.commit()

    test_user = User.query.first()

    response = client.post('/api/join-group', json={
        'group_id': test_group.id,
        'user_id': test_user.id
    }, headers=auth_header)

    assert response.status_code == 200
    assert response.json == {"message": "User added to group successfully", "group_id": test_group.id}

    response = client.post('/api/join-group', json={
        'group_id': None,
        'user_id': test_user.id
    }, headers=auth_header)

    assert response.status_code == 400
    assert response.json == {"error": "Group ID and User ID are required"}

def test_download_file(client, auth_header):
    test_file_path = os.path.join(os.getcwd(), 'testfile.txt')
    with open(test_file_path, 'w') as f:
        f.write("This is a test file.")

    response = client.post(f'/api/download-file', json={
        'file_path': test_file_path
    }, headers=auth_header)
    assert response.status_code, 200

    response = client.post(f'/api/download-file', headers=auth_header)
    assert response.status_code == 400

    os.remove(test_file_path)
