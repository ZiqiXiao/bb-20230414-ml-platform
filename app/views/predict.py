from .utils import *

def init_predict_routes(app, socketio):
    @app.route('/predict-prepare', methods=['GET', 'POST'])
    def predict_prepare():
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
    
    # Page for monitoring the training progress
    @app.route('/predict-progress', methods=['POST', 'GET'])
    def predict_progress():
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
    
    # socketio event handler for starting the training process
    @socketio.on('start_predict')
    def handle_start_predict(data):
        filename = data['filename']
        model_name = data['model_name']
        model_path = data['model_path']
        model_class = data['model_class']

        thread = threading.Thread(target=predict, args=(app, filename, model_class, model_name, model_path, socketio))
        thread.start()

    @app.route('/predict_result/<filename>')
    def download_predict_result(filename):
        return send_from_directory(Config.PREDICT_RESULT_FOLDER, filename, as_attachment=True)