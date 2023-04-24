"""
This is the main entry point for the application.

from app import create_app

app, socketio = create_app()

if __name__ == '__main__':  
    socketio.run(app)
"""

from app import create_app


app, socketio = create_app()

if __name__ == '__main__':  
    socketio.run(app)