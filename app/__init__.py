from flask import Flask, session
from flask_session import Session
# from flask_cors import CORS
from config import Config
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from app.views import init_routes
from app.utils.log_utils import setup_logger


db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = config_class.SECRET_KEY
    # CORS(app)
    socketio = SocketIO(app) # 创建SocketIO实例

    # Setup logging
    setup_logger(app)

    # Initialize Session
    Session(app)

    # Initialize database
    db.init_app(app)

    # Initialize routes  
    init_routes(app, socketio)

    @app.route('/test/')
    def test_page():
        return '<h1>I am rich</h1>'
    
    # 在 app 上下文中创建所有数据库表
    with app.app_context():
        from app.database import ModelTable
        db.create_all()

    return app, socketio