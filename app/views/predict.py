from .utils import *

def init_predict_routes(app, socketio):
    """Initiation of predict page routes.

    Args:
        app (object): The instance of flask app.
        socketio (object): The instance of socket.
    """
    @app.route('/predict-prepare', methods=['GET', 'POST'])
    def predict_prepare():
        return predict_prepare_route()
    
    # Page for monitoring the training progress
    @app.route('/predict-progress', methods=['POST', 'GET'])
    def predict_progress():
        return predict_progress_route()
    
    # socketio event handler for starting the training process
    @socketio.on('start-predict')
    def handle_start_predict(data):
        return handle_start_predict_route(data, app, socketio)

    @app.route('/predict-result/<filename>')
    def download_predict_result(filename):
        return download_predict_result_route(filename)
    

def predict_prepare_route():
    """The function of the page for preparing the prediction.
    Get the uploaded file name and the model name from the frontend.
    Query the model path and model class from the database.
    Then redirect to the page for monitoring the prediction progress with model class, model name and model path.

    Route:
        - GET, POST: /predict-prepare

    Returns:
        json: Return the json of the redirect url.
        Or the page of the prediction preparation.
    """    
    if request.method == 'POST':
        # 获取上传的文件名称、模型名称
        filename = request.form['filename']
        model_name = request.form['model_name']

        from app.database import ModelTable
        model_path = ModelTable.query.filter_by(model_name=model_name).first().model_path
        model_class = ModelTable.query.filter_by(model_name=model_name).first().model_class

        redirect_url = url_for('predict_progress', filename=filename, model_class=model_class, model_name=model_name, model_path=model_path)
        return jsonify({"redirect_url": redirect_url})
        
    from app.database import ModelTable
    model_names = ModelTable.query.with_entities(ModelTable.model_name).distinct().all()
    return render_template('predict_prepare.html', model_names=model_names)

def predict_progress_route():
    """The function of the page for monitoring the prediction progress. 
    If prediction fails it will show the error message.
    If prediction success it will show the download link of the prediction result.

    Route:
        - GET, POST: /predict-progress

    Returns:
        The page of the prediction progress.
    """    
    if request.method == 'POST':
        # Check if the uploaded file is allowed
        filename = secure_filename(request.files['file'].filename)
        model_name = request.form['model_name']
        model_path = request.form['model_path']
        model_class = request.form['model_class']
    elif request.method == 'GET':
        filename = request.args.get('filename')
        model_name = request.args.get('model_name')
        model_path = request.args.get('model_path')
        model_class = request.args.get('model_class')
    return render_template('predict_progress.html', filename=filename, model_class=model_class, model_name=model_name, model_path=model_path)

def handle_start_predict_route(data:object = None, app:object = None, socketio: object = None):
    """Start a thread to predict.

    Args:
        data (object, optional): The request from the frontend. Defaults to None.
        app (object, optional): The instance of flask app. Defaults to None.
        socketio (object, optional): The instance of socket. Defaults to None.
    """    
    filename = data['filename']
    model_name = data['model_name']
    model_path = data['model_path']
    model_class = data['model_class']

    thread = threading.Thread(target=predict, args=(app, filename, model_class, model_name, model_path, socketio))
    thread.start()

def download_predict_result_route(filename: str):
    """The function of downloading the prediction result.

    Args:
        filename (str): The name of prediction result file.

    Returns:
        The file of prediction result.
    """    
    return send_from_directory(Config.PREDICT_RESULT_FOLDER, filename, as_attachment=True)