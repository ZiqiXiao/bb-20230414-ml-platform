from flask import Response, flash, render_template, request, redirect, url_for, jsonify, send_from_directory, session, send_file
import os
import importlib
import threading
import pandas as pd
from werkzeug.utils import secure_filename
from app.utils.model_utils import train_scheduler, training, predict
import traceback
import json

from config import Config

def init_utils(app, socketio):
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    @app.route('/upload-file', methods=['POST'])
    def upload_file():
        file = request.files['file']
        folder = request.form['folder']
        
        if folder == 'train':
            target_folder = Config.UPLOAD_TRAIN_FOLDER
        elif folder == 'predict':
            target_folder = Config.UPLOAD_PREDICT_FOLDER
        else:
            app.logger.warning(f"Invalid folder received: {folder}")
            return jsonify(status='failure')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(target_folder, filename))
            app.logger.info(f"File uploaded: {filename}")
            return jsonify(status='success')
        else:
            app.logger.warning(f"File upload failed for: {file.filename if file else 'No file received'}")
            return jsonify(status='failure')