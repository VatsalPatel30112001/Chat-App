from flask import Flask
from database import db
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from api import api
from socket_events import register_socket_events, socketio

app = Flask(__name__)
CORS(app)
app.config.from_object('config.Config')
db.init_app(app)
socketio.init_app(app, cors_allowed_origins='*')

with app.app_context():
    db.create_all()

jwt = JWTManager(app)
app.register_blueprint(api, url_prefix='/api') 

register_socket_events(socketio)

if __name__ == '__main__':
    socketio.run(app, debug=True)