from .utils import *

def init_main_routes(app, socketio):
    # mian page, to chose whether to train or predict
    @app.route('/', methods=['GET', 'POST'])
    def main():
        return render_template('main.html')