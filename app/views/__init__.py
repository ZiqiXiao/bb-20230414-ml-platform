from .main import init_main_routes
from .train import init_train_routes
from .predict import init_predict_routes
from .model_admin import init_model_admin_routes

def init_routes(app, socketio):
    init_main_routes(app, socketio)
    init_train_routes(app, socketio)
    init_predict_routes(app, socketio)
    init_model_admin_routes(app, socketio)