import os
import logging
from logging.handlers import TimedRotatingFileHandler
from config import Config

def setup_logger(app: object):
    """Setup logger for the app. Current day log will be filed as app.log, the next day log will be filed as app.log.date, and so on.

    Args:
        app (object): Flask app object
    """    
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler = TimedRotatingFileHandler(os.path.join(Config.LOG_FOLDER, 'app.log'), when='midnight', interval=1)
    log_handler.setLevel(logging.DEBUG)
    log_handler.setFormatter(log_formatter)

    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.DEBUG)