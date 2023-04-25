from .utils import *

def init_main_routes(app: object, socketio: object):
    """Initiation of main page route.

    Args:
        app (object): The instance of flask app.
        socketio (object): The instance of socket.
    """    
    # mian page, to chose whether to train or predict
    @app.route('/main', methods=['GET', 'POST'])
    @app.route('/', methods=['GET', 'POST'])
    def main():
          return main_route()


def main_route():
        """Return the template of the main page.

        Route:
            - GET, POST: /main
            - GET, POST: /

        Returns:
            Rendered template of the main.html page.
        """        
        return render_template('main.html')